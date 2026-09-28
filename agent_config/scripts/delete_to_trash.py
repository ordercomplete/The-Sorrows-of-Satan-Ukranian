#!/usr/bin/env python3
"""
delete_to_trash.py — Обов'язкова Корзина для видалених файлів агента/проєкту.

Принцип:
    Замість безповоротного видалення (Remove-Item / os.remove) файл або папку
    ПЕРЕНОСЯТЬ у Корзину і фіксують у deletion_log.md відповідної корзини.

Дві корзини (маршрутизація автоматична):
    AGENT/trash/  — файли Агента (структура Агента: папки AGENT_DIRS +
                     найточніше — target_paths з agent_config/manifest.json)
    trash/        — файли проєкту (решту)

Робочий каталог визначається від розташування самого скрипта:
    agent_config/scripts/delete_to_trash.py  →  корінь проєкту = parents[2]

Тому інсталяційні копії працюють у будь-якій папці (без жорстких шляхів).

Використання:
    python agent_config/scripts/delete_to_trash.py <шлях1> [шлях2 ...] [--reason "причина"]
    python agent_config/scripts/delete_to_trash.py ./tmp.txt --reason "тимчасовий файл"
    python agent_config/scripts/delete_to_trash.py --dry-run ./foo.py --reason "перевірка"

Приклади:
    # файл Агента -> AGENT/trash/
    python agent_config/scripts/delete_to_trash.py AGENT/memories/session/session_2026-01-01.md
    # файл проєкту -> trash/ у корені
    python agent_config/scripts/delete_to_trash.py ./backup/tmp/ ./agent.log --reason "очищення тесту"
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Корінь проєкту: скрипт лежить у <root>/agent_config/scripts/
_WORKSPACE = Path(__file__).resolve().parents[2]
AGENT_ROOT = _WORKSPACE / "AGENT"

# Папки структури Агента, що розповсюджуються через manifest (дистрибутивні).
# Це ДРУГИЙ рівень точності визначення «файл Агента»: файл, розташований у
# будь-якій із цих папок, вважається файлом Агента.
AGENT_DIRS = ("AGENT", ".github", ".clinerules", ".continue", ".opencode", "agent_config")

# Дві корзини:
#   AGENT/trash/  — файли Агента (структура Агента: папки AGENT_DIRS + manifest.json)
#   trash/        — файли проєкту (решту)
TRASH_AGENT_DIR = AGENT_ROOT / "trash"
TRASH_PROJECT_DIR = _WORKSPACE / "trash"

ALL_TRASH_DIRS = (TRASH_AGENT_DIR, TRASH_PROJECT_DIR)


def _load_agent_manifest_paths(ws: Path) -> set:
    """Найточніший набір шляхів файлів Агента з manifest.json (target_paths).

    manifest.json регенерується через update-manifest.py --apply щоразу, коли
    додається новий файл структури Агента, тому цей набір постійно актуальний.
    Повертає порожню множину, якщо manifest відсутній/нечитається.
    """
    mf = ws / "agent_config" / "manifest.json"
    if not mf.exists():
        return set()
    try:
        data = json.loads(mf.read_text(encoding="utf-8-sig"))
    except Exception:
        return set()
    paths = set()
    for sect in ("files", "root_files", "stub_files"):
        for rel, cfg in (data.get(sect) or {}).items():
            paths.add(rel.replace("/", os.sep))
            tps = cfg.get("target_paths") if isinstance(cfg, dict) else None
            if isinstance(tps, list):
                for t in tps:
                    paths.add(str(t).replace("/", os.sep))
    return paths

LOG_HEADER = (
    "# Корзина видалених файлів — deletion_log.md\n\n"
    "| Дата | Шлях файлу (оригінал) | Фактичне місце в trash | Хто | Причина |\n"
    "|------|------------------------|------------------------|-----|---------|\n"
)


def _resolve_workspace(custom_root: str | None) -> tuple:
    """Обчислити корінь проєкту та корзини.

    За замовчуванням — від розташування скрипта (parents[2]). Якщо заданий
    `--root` — використовується він (режим видалення з довільного таргету).
    """
    if custom_root:
        ws = Path(custom_root).expanduser().resolve()
    else:
        ws = Path(__file__).resolve().parents[2]
    agent_root = ws / "AGENT"
    trash_agent = agent_root / "trash"
    trash_project = ws / "trash"
    return ws, agent_root, trash_agent, trash_project, (trash_agent, trash_project)


# Глобальні значення за замовчуванням (може перевизначити --root у main)
_WORKSPACE, AGENT_ROOT, TRASH_AGENT_DIR, TRASH_PROJECT_DIR, ALL_TRASH_DIRS = (
    _resolve_workspace(None)
)


def choose_trash(path: Path,
                 agent_root: Path | None = None,
                 trash_agent: Path | None = None,
                 trash_project: Path | None = None,
                 agent_manifest_paths: set | None = None) -> Path:
    """Визначити Корзину для файлу. Точність — по спаданню:

    1. manifest.json (target_paths) — точний список файлів структури Агента;
    2. папки Агента (AGENT_DIRS) — дистрибутивні каталоги;
    3. fallback — розміщення (AGENT/ → агентська, решта → проєктна).

    Повертає trash_agent для файлу Агента, інакше trash_project.
    """
    agent_root = agent_root or AGENT_ROOT
    trash_agent = trash_agent or TRASH_AGENT_DIR
    trash_project = trash_project or TRASH_PROJECT_DIR

    # Відносний шлях до кореня проєкту (ws = agent_root.parent)
    ws = agent_root.parent
    try:
        rel = path.resolve().relative_to(ws.resolve())
    except (ValueError, OSError):
        rel = None

    if rel is not None:
        rel_posix = rel.as_posix()
        # 1) manifest — максимальна точність
        if agent_manifest_paths and rel_posix in {p.replace(os.sep, "/") for p in agent_manifest_paths}:
            return trash_agent
        # 2) папки Агента
        top = rel.parts[0] if rel.parts else ""
        if top in AGENT_DIRS:
            return trash_agent

    # 3) fallback: розміщення
    try:
        if path.resolve().is_relative_to(agent_root.resolve()):
            return trash_agent
    except OSError:
        pass
    return trash_project


def log_deletion(trash_dir: Path, original: Path, destination: Path, reason: str) -> None:
    """Дописати рядок у deletion_log.md відповідної корзини."""
    trash_dir.mkdir(parents=True, exist_ok=True)
    log_file = trash_dir / "deletion_log.md"
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = f"| {ts} | `{original}` | `{destination}` | delete_to_trash.py | {reason} |\n"
    if not log_file.exists():
        log_file.write_text(LOG_HEADER, encoding="utf-8")
    with log_file.open("a", encoding="utf-8") as f:
        f.write(line)


def move_to_trash(path: Path, reason: str, dry_run: bool,
                  agent_root: Path | None = None,
                  trash_agent: Path | None = None,
                  trash_project: Path | None = None,
                  all_trash: tuple | None = None,
                  agent_manifest_paths: set | None = None) -> str:
    """Перенести файл/папку у відповідну Корзину. Повертає фактичне місце призначення."""
    if not path.exists():
        return f"❌ не знайдено: {path}"

    agent_root = agent_root or AGENT_ROOT
    trash_agent = trash_agent or TRASH_AGENT_DIR
    trash_project = trash_project or TRASH_PROJECT_DIR
    all_trash = all_trash or ALL_TRASH_DIRS

    trash_dir = choose_trash(path, agent_root, trash_agent, trash_project, agent_manifest_paths)

    # Запобігання повторного переносу (вже в одній із Корзин)
    try:
        resolved = Path(path).resolve()
        if any(resolved == t.resolve() for t in all_trash):
            return "⚠️ джерело вже в Корзині"
    except OSError:
        pass

    ts = datetime.now().strftime("%Y-%m-%d")
    dst = trash_dir / (ts + "_" + path.name)

    # Якщо така назва вже є — додаємо час, щоб не перезатерти
    if dst.exists():
        hms = datetime.now().strftime("%H-%M-%S")
        dst = trash_dir / (ts + "_" + hms + "_" + path.name)

    if dry_run:
        print(f"📋 [DRY-RUN] {path} -> {dst}")
        return str(dst)

    trash_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(path), str(dst))
    log_deletion(trash_dir, path, dst, reason)
    print(f"✅ {path} -> {dst}")
    return str(dst)


def main() -> int:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Відправляє видалені файли в Корзину + лог: AGENT/* -> AGENT/trash/, решта -> trash/ у корені"
    )
    parser.add_argument("paths", nargs="+", help="Шляхи до файлів/папок, які видаляти")
    parser.add_argument("--reason", default="", help="Причина видалення (записається в лог)")
    parser.add_argument("--dry-run", action="store_true", help="Показати що зміниться без переносу")
    parser.add_argument("--root", default=None,
                        help="Корінь проєкту для маршрутизації корзин (за замовчуванням — розташування скрипта)")
    args = parser.parse_args()

    agent_root = AGENT_ROOT
    trash_agent = TRASH_AGENT_DIR
    trash_project = TRASH_PROJECT_DIR
    all_trash = ALL_TRASH_DIRS
    if args.root:
        _, agent_root, trash_agent, trash_project, all_trash = _resolve_workspace(args.root)

    # Точна структура Агента (manifest.json) для максимума точності маршрутизації
    agent_manifest_paths = _load_agent_manifest_paths(agent_root.parent)

    for raw in args.paths:
        p = Path(raw).expanduser()
        if not p.exists():
            print(f"❌ Не знайдено: {raw}")
            continue
        # Пропускаємо самі Корзини / бази
        try:
            resolved = Path(raw).resolve()
            if any(resolved.is_relative_to(t.resolve()) for t in all_trash):
                print(f"⚠️ Пропускаю вже-в-Корзині: {raw}")
                continue
        except Exception:
            pass
        move_to_trash(p, args.reason or "", args.dry_run,
                      agent_root, trash_agent, trash_project, all_trash, agent_manifest_paths)

    print(
        "\n✅ Готово. Логи: "
        + str(trash_agent / "deletion_log.md")
        + " , "
        + str(trash_project / "deletion_log.md")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())