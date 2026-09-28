#!/usr/bin/env python3
"""
update-manifest.py — Авто-генерація/оновлення agent_config/manifest.json.

Мета: коли до агента додаються нові функціональні файли (скліл, хук, плагін,
      знання, скрипт) — вони мають автоматично потрапляти в конфігурацію Агента
      (manifest.json), щоб синхронізація (sync-agent.py) їх розповсюджувала.

Принцип:
    - `files`     : канонічний мапінг «джерело в AGENT/ → цільові оболочки чатів»
                    (.github / .clinerules / .opencode / .continue).
    - `stub_files`: автогенеруються з шаблону templates/stub_agents.md.
    - `root_files`: автозбір:
          * `opencode.json` (корінь, не ччитаємо),
          * файли `agent_config/` (крім backup/, __pycache__/) → туди ж,
          * файли `.continue/*` → у `agent_config/.continue/*`.

Виконання:
    python agent_config/scripts/update-manifest.py --dry-run   # показати
    python agent_config/scripts/update-manifest.py --apply     # перезаписати
"""

import argparse
import json
import io
import os
import sys
from pathlib import Path

# Корінь проєкту: скрит лежить у <root>/agent_config/scripts/
_ROOT = Path(__file__).resolve().parents[2]
AGENT_DIR = _ROOT / "AGENT"
AC_DIR = _ROOT / "agent_config"
MANIFEST = AC_DIR / "manifest.json"

# Правила розповсюдження файлів AGENT/ → оболочки чатів (за замовчуванням)
# СІМ: виконувані скрипти (*.py) виконуються канонічно з AGENT/scripts/ і НЕ
#      копіюються в оболонки чатів (лише виконавчі файли — JS/JSON).
DEFAULT_FILES = {
    ".gitignore": ["AGENT/.gitignore"],
    "agents/Comfy-smart-lady.md": [".github/copilot-instructions.md"],
    "skills/{d}/SKILL.md": [".github/skills/{d}/SKILL.md", ".clinerules/skills/{d}/SKILL.md"],
    "hooks/Loops.json": [".clinerules/hooks/Loops.json", ".continue/hooks/Loops.json", ".github/hooks/Loops.json"],
    "plugin/anti-loop.js": [".opencode/plugins/anti-loop.js"],
    "plugin/startup.js": [".opencode/plugins/startup.js"],
    "knowledge-base/README.md": [".github/knowledge-base/README.md", ".clinerules/knowledge-base/README.md"],
}

# Локальні .gitignore папок агента — розповсюджуються в корінь цільового проєкту
# (правила .gitignore діють на своє піддерево, тому не конфліктують з хостом)
EXTRA_ROOT_FILES = (
    ".github/.gitignore",
    ".clinerules/.gitignore",
    ".continue/.gitignore",
    # Markdownlint (2026-09-28): конфіг правил + шляхи, які не лінтимо.
    # Розповсюджуються в корінь хост-проєкту, щоб лінтер працював однаково всюди.
    ".markdownlint.json",
    ".markdownlintignore",
    # Корзина проєкту в корені: ігнор вмісту + журнал видалень
    "trash/.gitignore",
    "trash/deletion_log.md",
)

# Перевірка нової версії Агента (режим notify: тільки сповіщення, без змін)
UPDATE_CHECK = {
    "repo_url": "https://raw.githubusercontent.com/ordercomplete/Comfy-smart-lady-agent/main/agent_config/VERSION",
    "git_url": "https://github.com/ordercomplete/Comfy-smart-lady-agent.git",
    "mode": "notify",
    "interval_hours": 24,
    "timeout_seconds": 5,
}

STUB_TARGETS = [
    ".opencode/agents/Comfy-smart-lady.md",
    # 2026-09-04: топ-левел .clinerules/*.md — ЄДИНИЙ рівень, який Cline
    # гарантовано завантажує в контекст (підпапки .clinerules/ як правила
    # не читаються). Без цього файлу INIT-GATE не спрацьовує в Cline.
    ".clinerules/agent-startup.md",
    ".clinerules/agents/Comfy-smart-lady.md",
    ".github/agents/Comfy-smart-lady.md",
    ".continue/agents/Comfy-smart-lady.md",
    ".agent/instructions.md",
]

CONTINUE_FILES_REMOVED = (
    # 2026-08-28: дзеркальне копіювання .continue/* -> agent_config/.continue/*
    # прибрано за рішенням користувача. Живою конфігурацією Continue залишається
    # коренева .continue/ (додаток читає її з кореня проєкту); додатковий бекап-
    # шум у backup/ та подвійні записи в root_files manifest більше не потрібні.
)

# SKIP_DIRS: локальні знімки стану, які НЕ розповсюджуються в хост-проєкти.
# backup-chat — історія бекапів чатів (ротується cleanup_backup_agent.py):
# якщо її включити в root_files, кожна ротація в центрі робить manifest
# застарілим, а хости отримують записи-привиди Missing (див.
# session_2026-09-04.md, Помилка №3). backup-agent (zip-бекапи AGENT від
# watcher) навпаки ВХОДИТЬ до manifest root_files: ці файли живуть у репо
# та мають відображатися у структурі Агента.
SKIP_DIRS = {"__pycache__", "trash", "backup-chat"}


def node_skills():
    """Знайти підкаталоги skills у AGENT/skills/, що мають SKILL.md."""
    skills_dir = AGENT_DIR / "skills"
    if not skills_dir.exists():
        return []
    return sorted(p.name for p in skills_dir.iterdir()
                  if p.is_dir() and (p / "SKILL.md").exists())
def build_files():
    """Побудувати секцію 'files' із DEFAULT_FILES і фактичної структури AGENT/."""
    # Інструкції агента розповсюджуються як stub-посилання, щоб усі оболонки
    # чатів читали канонічний файл у AGENT/ (жодних копій в .github/.clinerules).
    STUB_KEYS = {
        "agents/Comfy-smart-lady.md",
        "knowledge-base/README.md",
        "skills/{d}/SKILL.md",
    }
    files = {}
    for key, targets in DEFAULT_FILES.items():
        is_stub = key in STUB_KEYS
        if "{d}" in key:
            for d in node_skills():
                full_key = key.replace("{d}", d)
                entry = {
                    "action": "stub" if is_stub else "copy_full",
                    "target_paths": [t.replace("{d}", d) for t in targets],
                }
                if is_stub:
                    entry["source_ref"] = "${workspace}/AGENT/" + full_key
                files[full_key] = entry
        else:
            action = "stub" if is_stub else "copy_full"
            entry = {"action": action, "target_paths": list(targets)}
            if is_stub:
                entry["source_ref"] = "${workspace}/AGENT/" + key
            files[key] = entry
    return files


def build_stub_files():
    """Повернути stub_files з джерелом на канонічний файл AGENT/."""
    ref = "${workspace}/AGENT/agents/Comfy-smart-lady.md"
    return {t: {"template": "templates/stub_agents.md", "source_ref": ref}
            for t in STUB_TARGETS}


def build_root_files():
    """Автозбір: opencode.json + agent_config/** + локальні .gitignore папок агента."""
    root_files = {}
    oc = _ROOT / "opencode.json"
    if oc.exists():
        root_files["opencode.json"] = {"action": "copy_full", "target_paths": ["opencode.json"]}
    for rel in EXTRA_ROOT_FILES:
        if (_ROOT / rel).exists():
            root_files[rel] = {"action": "copy_full", "target_paths": [rel]}
    if AC_DIR.exists():
        for cur, dirs, fnames in os.walk(AC_DIR):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fn in sorted(fnames):
                p = os.path.relpath(os.path.join(cur, fn), _ROOT).replace("\\", "/")
                root_files[p] = {"action": "copy_full", "target_paths": [p]}
    return root_files


def build_manifest():
    """Зібрати повний manifest із джерел."""
    return {
        "version": _read_version(),
        "agent_name": "Comfy-smart-lady",
        "source_root": "AGENT",
        "update_check": UPDATE_CHECK,
        "files": build_files(),
        "stub_files": build_stub_files(),
        "root_files": build_root_files(),
    }


def _read_version():
    f = AC_DIR / "VERSION"
    return f.read_text(encoding="utf-8").strip() if f.exists() else "1.2.0"


def _write_manifest(manifest):
    with io.open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=4)
def main():
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Авто-оновлення manifest.json зі структури AGENT/ + agent_config/")
    parser.add_argument("--dry-run", action="store_true", help="Показати що буде в manifest без перезапису")
    parser.add_argument("--apply", action="store_true", help="Перезаписати manifest.json")
    args = parser.parse_args()

    manifest = build_manifest()
    print("📋 Новий manifest.json містить:")
    print(f"   version:    {manifest['version']}")
    print(f"   files:      {len(manifest['files'])} записів")
    print(f"   stub_files: {len(manifest['stub_files'])} записів")
    print(f"   root_files: {len(manifest['root_files'])} записів")

    if not args.apply:
        print("\nЩоб перезаписати manifest.json, запусти: python agent_config/scripts/update-manifest.py --apply")
        return 0

    _write_manifest(manifest)
    print(f"✅ manifest.json оновлено: {MANIFEST}")
    return 0


if __name__ == "__main__":
    main()