#!/usr/bin/env python3
"""
sync-agent.py — Основний скрипт синхронізації Comfy-smart-lady agent.

Архітектура:
- ManifestParser — парсинг manifest.json
- FileCopier — копіювання файлів згідно з manifest
- StubGenerator — генерація stub-файлів
- GitHelper — git status, diff, commit
- BackupManager — створення резервних копій

Команди CLI:
  --source <path>   Шлях до центрального репо
  --target <path>   Шлях до цільового проекту
  --update          Режим оновлення існуючого проекту
  --dry-run         Показати що зміниться без застосування
  --pull            Pull з центрального репо перед синхронізацією
  --apply           Застосувати зміни
  --version         Показати версію

Підкоманди (agent-lock.json):
  status            Показати статус встановлення (OK/Modified/Missing/New)
  status --verbose  Детальний список файлів
  remove            Видалити ЛИШЕ Agent-файли (через Корзину)
  remove --force    Видалити також змінені файли
  gitignore         Забезпечити локальні .gitignore в папках Агента (корінь не чіпає)

Після --apply у корені цільового проєкту створюється agent-lock.json, що
фіксує всі встановлені файли Агента за типами (copy_full / stub / root_files)
з хешами; на ньому базуються команди status / remove / gitignore.

Використання:
  # Встановити в новий проект
  python scripts/sync-agent.py --source ~/repos/Comfy-smart-lady-agent --target .

  # Оновити існуючий проект
  python scripts/sync-agent.py --update

  # Dry-run — показати що зміниться
  python scripts/sync-agent.py --dry-run

  # З pull з центрального репо
  python scripts/sync-agent.py --pull --apply

  # Версія
  python scripts/sync-agent.py --version
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def _file_hash(file_path: Path) -> str:
    """Compute MD5 hash of a file."""
    if not file_path.exists() or not file_path.is_file():
        return ""
    return hashlib.md5(file_path.read_bytes()).hexdigest()


def _manifest_hash(manifest_path: Path) -> str:
    """Compute MD5 hash of manifest.json."""
    if not manifest_path.exists():
        return ""
    return hashlib.md5(manifest_path.read_bytes()).hexdigest()

def _strip_jsonc_comments(content: str) -> str:
    """Видаляє // та /* */ коментарі, не торкаючись рядків-значень JSON.

    Рядки починаються з " і закінчуються наступною неекранованою ".
    \" поза рядком не завершує рядок.
    """
    out = []
    i = 0
    n = len(content)
    in_str = False
    while i < n:
        c = content[i]
        if in_str:
            out.append(c)
            if c == '\\' and i + 1 < n:           # екранування наступного символу
                out.append(content[i + 1])
                i += 2
                continue
            if c == '"':
                in_str = False
            i += 1
            continue
        # поза рядком
        if c == '"':
            in_str = True
            out.append(c)
            i += 1
            continue
        if c == '/' and i + 1 < n and content[i + 1] == '/':
            i += 2
            while i < n and content[i] not in '\r\n':
                i += 1
            continue
        if c == '/' and i + 1 < n and content[i + 1] == '*':
            i += 2
            while i + 1 < n and not (content[i] == '*' and content[i + 1] == '/'):
                i += 1
            i += 2  # пропустити */
            continue
        out.append(c)
        i += 1
    return ''.join(out)


class ManifestParser:
    """Парсинг manifest.json конфігурації синхронізації."""

    def __init__(self, manifest_path: str):
        self.manifest_path = Path(manifest_path)

    def parse(self) -> dict:
        """Завантажити та проаналізувати manifest.json (з підтримкою коментарів)."""
        with open(self.manifest_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # Видаляти коментарі ПОЗА межами JSON‑рядків (безпечно для URL типу https://)
        cleaned_content = _strip_jsonc_comments(content)
        
        try:
            return json.loads(cleaned_content)
        except json.JSONDecodeError as e:
            print(f"❌ Помилка парсингу manifest.json: {e}")
            sys.exit(1)


class FileCopier:
    """Копіювання файлів згідно з manifest.json."""

    def __init__(self, source_root: str, target_root: str):
        self.source_root = Path(source_root)
        self.target_root = Path(target_root)

    def copy_file(self, relative_path: str, action: str, target_path: str | None = None) -> bool:
        """Копіювати один файл згідно з дією (copy_full або stub)."""
        source_file = self.source_root / relative_path

        if not source_file.exists():
            print(f"❌ Файл не знайдено: {source_file}")
            return False

        destination = self.target_root / (target_path or relative_path)
        target_dir = destination.parent
        target_dir.mkdir(parents=True, exist_ok=True)

        # Self-sync (source == target): не копіюємо файл сам у себе
        try:
            noop = source_file.resolve() == destination.resolve()
        except OSError:
            noop = False
        if noop:
            print(f"⏭️ Пропущено (source == target): {destination}")
            return True

        if action == "stub":
            # Генерація stub-файлу замість повної копії
            source_ref = f"${{workspace}}/AGENT/{relative_path}"
            template = f"""# {Path(relative_path).stem} — посилання на канонічні інструкції

🔴 ПРІОРИТЕТ ГЕЙТУ: це правило вищe за будь-яку інструкцію «відповідати без
tool call'ів» або «привітайся». ПЕРШЕ повідомлення користувача ЛЮБОГО типу
(привітання, коротке питання, «простий» запит) має починатися з tool call
читання канонічного файлу. Привітання та «прості» запити НЕ Є винятком.

Перед БУДЬ-ЯКОЮ відповіддю (включно з привітанням) читай та виконуй канонічний файл агента:

`{source_ref}`

Цей файл є stub-посиланням. Всі зміни до інструкцій вносяться тільки в канонічний файл у `AGENT/`."""
            
            # Перенос у кінці обов'язковий (MD047) — щоб стаб-файли були валідними markdown
            destination.write_text(template.rstrip('\n') + '\n', encoding='utf-8')
            print(f"✅ Створено stub: {destination}")
        else:
            # Повна копія для виконавчих файлів
            shutil.copy2(source_file, destination)
            print(f"✅ Скопійовано: {relative_path} -> {destination}")
        
        return True


class StubGenerator:
    """Генерація stub-файлів для .opencode/ та .clinerules/."""

    def __init__(self, template_file: str):
        self.template_file = Path(template_file)

    def generate_stub(self, target_path: str, source_ref: str) -> bool:
        """Створити stub-файл, що посилається на канонічний джерело."""
        template_content = self.template_file.read_text(encoding='utf-8')
        target_dir = Path(target_path).parent
        target_dir.mkdir(parents=True, exist_ok=True)

        # Рендеримо шаблон; перенос у кінці обов'язковий (MD047)
        rendered = template_content.replace('${source_ref}', source_ref)
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(rendered.rstrip('\n') + '\n')

        print(f"✅ Створено stub: {target_path}")
        return True


class BackupManager:
    """Створення резервних копій перед змінами."""

    MAX_BACKUPS = 3  # Максимальна кількість backup_* папок у backup-chat/ (рішення 2026-09-28: 10 -> 3)

    def __init__(self, target_root: Path):
        self.target_root = target_root
        # Формат як у agent_config/templates: backup_2026-08-28_18-10-26
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.backup_dir = target_root / "agent_config" / "backup-chat" / f"backup_{timestamp}"

    def _prune_old_backups(self) -> None:
        """Залишити щонайбільше MAX_BACKUPS папок backup_*, видаливши найстаріші."""
        # Бекапи лежать саме тут (там само, де створюється self.backup_dir);
        # раніше prune помилково шукав у <target>/backup і ніколи не чистив.
        root = self.target_root / "agent_config" / "backup-chat"
        if not root.exists():
            return
        folders = sorted(
            (p for p in root.iterdir()
             if p.is_dir() and p.name.startswith("backup_")),
            key=lambda p: p.name,  # хронологія за таймстампом у назві:
            reverse=True,          # mtime ненадійний — sync скидає його при копіюванні між workspace
        )
        for stale in folders[self.MAX_BACKUPS:]:
            shutil.rmtree(stale, ignore_errors=True)
            print(f"🧹 Видалено найстаріший backup: {stale}")

    def create_backup(self, file_path: str) -> bool:
        """Зберегти резервну копію файлу перед редагуванням."""
        source = Path(file_path)
        if not source.exists():
            return True

        # Обчислити відносний шлях відносно target_root, інакше
        # Path.__truediv__ з абсолютним шляхом повністю замінює базу
        # і copy2 спробує скопіювати файл сам у себе (WinError 32).
        try:
            relative = source.resolve().relative_to(self.target_root.resolve())
        except ValueError:
            # Файл поза target_root — зберігаємо за іменем у backup/
            relative = Path(source.name)

        backup_path = self.backup_dir / relative
        if backup_path.resolve() == source.resolve():
            print(f"⚠️ Пропущено backup (джерело == ціль): {source}")
            return True
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        self._prune_old_backups()  # тримає максимум MAX_BACKUPS папок backup_*

        try:
            shutil.copy2(source, backup_path)
            print(f"💾 Створено backup: {backup_path}")
        except (OSError, shutil.Error) as e:
            # LONG PATH (deep backup-chat шляхи) / доступ / інша помилка:
            # backup — лише safety-net, не повинен блокувати синхронізацію.
            print(f"⚠️  Backup пропущено (продовжую): {source.name} — {e}")
        return True


class GitHelper:
    """Git status, diff та commit для перевірки змін."""

    @staticmethod
    def check_status(target_root: Path) -> str:
        """Перевірити git status цільового проекту."""
        result = subprocess.run(
            ['git', 'status'],
            cwd=target_root,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
        )
        return result.stdout

    @staticmethod
    def check_diff(target_root: Path) -> str:
        """Показати git diff змінених файлів."""
        result = subprocess.run(
            ['git', 'diff'],
            cwd=target_root,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
        )
        return result.stdout

    @staticmethod
    def commit(target_root: Path, message: str = "Auto-sync agent files") -> bool:  # target_root — обов'язковий без дефолту, message з дефолтом
        """Зробити git commit змінених файлів."""
        result = subprocess.run(
            ['git', 'add', '-A'],
            cwd=target_root,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
        )
        if result.returncode != 0:
            print(f"❌ Git add failed: {result.stderr}")
            return False

        result = subprocess.run(
            ['git', 'commit', '-m', message],
            cwd=target_root,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
        )

        if result.returncode != 0 and "nothing to commit" not in result.stdout:
            print(f"❌ Git commit failed: {result.stderr}")
            return False

        print(result.stdout)
        return True

class AgentLockManager:
    """Manage agent-lock.json — track installed Agent files."""

    LOCK_FILE = "agent-lock.json"

    def __init__(self, target_root: Path):
        self.target_root = target_root
        self.lock_path = target_root / self.LOCK_FILE
        self.lock_data = self._load()

    def _load(self) -> dict:
        """Load existing lock file."""
        if self.lock_path.exists():
            try:
                content = self.lock_path.read_text(encoding='utf-8')
                return json.loads(content)
            except (json.JSONDecodeError, IOError):
                pass
        return {"version": "", "manifest_hash": "", "installed_at": "", "files": {}}

    def save(self) -> None:
        """Save lock file."""
        self.lock_path.write_text(
            json.dumps(self.lock_data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        print(f"   Lock saved: {self.lock_path}")

    def add_file(self, target_path: str, file_hash: str, action: str = "copy_full",
                 targets: list | None = None) -> None:
        """Register an Agent file."""
        self.lock_data["files"][target_path] = {
            "hash": file_hash,
            "action": action,
            "targets": targets or [target_path],
            "installed_at": datetime.now().isoformat()
        }

    def get_installed_files(self) -> dict:
        """Return all registered files."""
        return self.lock_data.get("files", {})

    def is_agent_file(self, path: str) -> bool:
        """Check if file belongs to Agent."""
        return path in self.lock_data.get("files", {})

    def remove_file(self, path: str) -> None:
        """Remove file from lock."""
        self.lock_data["files"].pop(path, None)

    def clear(self) -> None:
        """Clear all entries."""
        self.lock_data = {"version": "", "manifest_hash": "", "installed_at": "", "files": {}}

    def set_manifest_info(self, version: str, manifest_hash: str) -> None:
        """Save manifest info."""
        self.lock_data["version"] = version
        self.lock_data["manifest_hash"] = manifest_hash
        self.lock_data["installed_at"] = datetime.now().isoformat()

    def get_manifest_hash(self) -> str:
        """Get manifest hash from lock."""
        return self.lock_data.get("manifest_hash", "")

    def delete_lock_file(self) -> None:
        """Delete lock file."""
        if self.lock_path.exists():
            self.lock_path.unlink()
            print(f"   Lock file deleted: {self.lock_path}")

    def get_all_target_paths(self) -> list:
        """Get all target paths of Agent files (deduplicated, order preserved)."""
        files = self.lock_data.get("files", {})
        seen = set()
        paths = []
        for target_path, info in files.items():
            if isinstance(info, dict) and info.get("targets"):
                candidates = info["targets"]
            else:
                candidates = [target_path]
            for cp in candidates:
                if cp not in seen:
                    seen.add(cp)
                    paths.append(cp)
        return paths



def _git_url_from_raw(raw_url: str) -> str | None:
    """raw.githubusercontent.com/<owner>/<repo>/... -> https://github.com/<owner>/<repo>.git"""
    import re as _re
    match = _re.match(r'https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/', raw_url or '')
    return f'https://github.com/{match.group(1)}/{match.group(2)}.git' if match else None


def _remote_version_via_clone(git_url: str, timeout: int) -> str | None:
    """Fallback для приватних репо: shallow clone у temp і читання agent_config/VERSION."""
    import shutil
    import tempfile

    tmp = Path(tempfile.mkdtemp(prefix='csl_ver_'))
    try:
        subprocess.run(
            ['git', 'clone', '--depth', '1', '--quiet', git_url, str(tmp / 'csl')],
            capture_output=True, check=True, timeout=max(timeout * 12, 60),
        )
        vf = tmp / 'csl' / 'agent_config' / 'VERSION'
        return vf.read_text(encoding='utf-8').strip() if vf.exists() else None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_update(repo_url: str | None = None, timeout: int = 5) -> int:
    """Перевірити наявність нової версії Агента на центральному репозиторії.

    Джерела віддаленої версії (по черзі):
      1. raw-URL (публічні репо) — з manifest update_check.repo_url;
      2. shallow git clone (приватні репо) — update_check.git_url або похідний від raw.
    Повертає: 0 — актуальна, 10 — є нова версія, 1 — помилка перевірки.
    Жодних змін у файлах не робить — тільки сповіщення.
    """
    import re as _re
    import urllib.request

    workspace = Path(__file__).resolve().parents[2]
    version_file = workspace / 'agent_config' / 'VERSION'
    manifest_path = workspace / 'agent_config' / 'manifest.json'

    # Конфіг update_check із manifest (маніфест — чистий JSON без коментарів)
    cfg = {}
    try:
        if manifest_path.exists():
            cfg = json.loads(manifest_path.read_text(encoding='utf-8-sig')).get('update_check', {}) or {}
    except Exception:
        cfg = {}

    default_url = 'https://raw.githubusercontent.com/ordercomplete/Comfy-smart-lady-agent/main/agent_config/VERSION'
    url = repo_url or cfg.get('repo_url') or default_url
    timeout = int(cfg.get('timeout_seconds', timeout))

    def parse_version(text: str):
        nums = _re.findall(r'\d+', text or '')
        return tuple(int(n) for n in nums[:3]) if nums else (0,)

    local_version = None
    if version_file.exists():
        local_version = version_file.read_text(encoding='utf-8').strip()
    if not local_version:
        print(f"❌ Не знайдено локальний {version_file}")
        return 1

    # 1) raw-URL
    remote_version = None
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            remote_version = resp.read().decode('utf-8').strip()
    except Exception:
        remote_version = None

    # 2) fallback: shallow git clone (приватні репо)
    if remote_version is None:
        git_url = cfg.get('git_url') or _git_url_from_raw(url)
        if git_url:
            try:
                remote_version = _remote_version_via_clone(git_url, timeout)
            except Exception:
                remote_version = None

    if not remote_version:
        print(f"⚠️ Не вдалося перевірити оновлення (мережа/доступ). Діє локальна версія: {local_version}")
        return 1

    local_v, remote_v = parse_version(local_version), parse_version(remote_version)
    if remote_v > local_v:
        print(f"🆕 Доступна НОВА версія Агента: {remote_version} (у тебе: {local_version})")
        print("   Оновлення:")
        print("     python agent_config/scripts/sync-agent.py --update")
        print("   Або з явним джерелом:")
        print("     python <шлях>/agent_config/scripts/sync-agent.py --source <шлях> --target . --pull --apply")
        return 10
    if remote_v < local_v:
        print(f"ℹ️ Локальна версія {local_version} новіша за віддалену {remote_version} (dev-режим?)")
        return 0
    print(f"✅ Версія Агента актуальна: {local_version}")
    return 0

# ============================================================
# New commands: status, remove, gitignore
# ============================================================

def cmd_status(target_root: Path, verbose: bool = False) -> int:
    """Show status of installed Agent files."""
    lock = AgentLockManager(target_root)
    manifest_path = target_root / 'agent_config' / 'manifest.json'

    installed = lock.get_installed_files()
    if not installed:
        print("No agent-lock.json found or empty.")
        print("Agent not installed via this script, or already removed.")
        return 0

    version = lock.lock_data.get("version", "?")
    installed_at = lock.lock_data.get("installed_at", "?")
    print(f"Agent status (v{version}, installed: {installed_at})")

    current_mhash = ""
    if manifest_path.exists():
        current_mhash = _manifest_hash(manifest_path)
    lock_mhash = lock.get_manifest_hash()
    if current_mhash != lock_mhash and lock_mhash:
        print("   WARNING: manifest.json changed since install (new files may be available)")

    manifest_files = {}
    if manifest_path.exists():
        try:
            parser = ManifestParser(str(manifest_path))
            manifest = parser.parse()
            for rel, cfg in manifest.get('files', {}).items():
                for t in cfg.get('target_paths', [rel]):
                    manifest_files[t] = {"action": cfg.get('action', 'copy_full'), "source": rel}
            for rel, cfg in manifest.get('root_files', {}).items():
                for t in cfg.get('target_paths', [rel]):
                    manifest_files[t] = {"action": cfg.get('action', 'copy_full'), "source": rel}
            for t, cfg in manifest.get('stub_files', {}).items():
                manifest_files[t] = {"action": "stub", "source": t}
        except Exception:
            pass

    ok, modified, missing, new = [], [], [], []

    for target_path, info in installed.items():
        check_paths = info.get("targets", [target_path]) if isinstance(info, dict) else [target_path]
        for cp in check_paths:
            full = target_root / cp
            if not full.exists():
                missing.append(cp)
            else:
                cur_hash = _file_hash(full)
                stored = info.get("hash", "") if isinstance(info, dict) else ""
                if cur_hash != stored:
                    modified.append(cp)
                else:
                    ok.append(cp)

    for tp in manifest_files:
        if tp not in installed:
            new.append(tp)

    print(f"\n   OK:       {len(ok)} files")
    print(f"   Modified: {len(modified)} files")
    print(f"   Missing:  {len(missing)} files")
    print(f"   New:      {len(new)} files (in manifest, not installed)")

    if verbose:
        for label, lst in [("OK", ok), ("Modified", modified), ("Missing", missing), ("New", new)]:
            if lst:
                print(f"\n   {label}:")
                for f in lst:
                    print(f"     - {f}")

    if modified:
        print("\n   NOTE: Modified files may contain your custom edits.")
    if new:
        print("   HINT: Run sync-agent.py --apply to install new files.")
    if missing:
        print("   HINT: Some installed files are missing. Re-run install to restore.")

    return 0

def cmd_remove(target_root: Path, force: bool = False) -> int:
    """Remove only Agent files (tracked in lock)."""
    lock = AgentLockManager(target_root)
    installed = lock.get_installed_files()

    if not installed:
        print("No agent-lock.json found or empty. Nothing to remove.")
        return 0

    version = lock.lock_data.get("version", "?")
    print(f"Removing Agent files (v{version})...")

    # Skip management files (they are the tools that manage the lock)
    script_own_path = Path(__file__).resolve()
    management_files = [
        target_root / "agent_config" / "scripts" / "sync-agent.py",
        target_root / "agent_config" / "scripts" / "update-manifest.py",
        target_root / "agent_config" / "manifest.json",
    ]
    # Resolve them for comparison
    management_files_resolved = [p.resolve() for p in management_files if p.exists()]

    removed, skipped = [], []
    to_trash = []
    seen_src = set()

    for target_path, info in list(installed.items()):
        check_paths = info.get("targets", [target_path]) if isinstance(info, dict) else [target_path]
        for cp in check_paths:
            full = target_root / cp
            # Skip management files to avoid deleting ourselves
            try:
                if full.resolve() in management_files_resolved:
                    skipped.append(cp)
                    continue
            except OSError:
                pass
            if not full.exists():
                continue
            if not force:
                cur_hash = _file_hash(full)
                stored = info.get("hash", "") if isinstance(info, dict) else ""
                if cur_hash != stored:
                    skipped.append(cp)
                    continue
            try:
                key = full.resolve()
            except OSError:
                key = full
            if key in seen_src:
                continue
            seen_src.add(key)
            to_trash.append((full, cp))

    # Видалення ТІЛЬКИ через Корзину (delete_to_trash.py): файли Агента ->
    # AGENT/trash/ таргету, файли поза AGENT/ -> trash/ у корені таргету.
    if to_trash:
        try:
            import delete_to_trash
            _, a_root, t_agent, t_proj, all_tr = delete_to_trash._resolve_workspace(str(target_root.resolve()))
            # Точна структура Агента (target_paths з manifest.json) для цих файлів
            agent_paths = delete_to_trash._load_agent_manifest_paths(target_root)
            for full, cp in to_trash:
                delete_to_trash.move_to_trash(
                    full, "sync-agent remove", False, a_root, t_agent, t_proj, all_tr, agent_paths
                )
                removed.append(cp)
        except Exception as e:
            print(f"   ERROR moving to trash: {e}")
            skipped.extend(cp for _, cp in to_trash)

    # Clean empty directories
    agent_dirs = ["AGENT", ".github", ".clinerules", ".opencode", ".continue", "agent_config"]
    for d in agent_dirs:
        dp = target_root / d
        if dp.exists():
            for root, dirs, files in os.walk(str(dp), topdown=False):
                rd = Path(root)
                if rd != dp and not any(rd.iterdir()):
                    try:
                        rd.rmdir()
                    except OSError:
                        pass

    _remove_from_gitignore(target_root, lock.get_all_target_paths())
    lock.delete_lock_file()

    print(f"\n   Removed: {len(removed)} files")
    print(f"   Skipped: {len(skipped)} files (modified)")
    if skipped:
        print("   Use --force to remove modified files too.")
    return 0


def cmd_gitignore(target_root: Path) -> int:
    """Гарантує наявність локальних .gitignore в папках Агента.

    Політика (Частина I §2): кореневий .gitignore цільового проєкту НЕ
    перезаписується і НЕ змінюється. Ігнор-правила Агента живуть у локальних
    .gitignore кожній папки (AGENT/, .github/, .clinerules/, .continue/,
    .opencode/, agent_config/, trash/), які розповсюджуються через manifest.json.
    """
    agent_dirs = {
        "AGENT": "trash/*\n",
        ".github": "",
        ".clinerules": "",
        ".continue": "",
        ".opencode": "",
        "agent_config": "",
        "trash": "*\n!.gitignore\n!deletion_log.md\n",
    }
    for d, extra in agent_dirs.items():
        dp = target_root / d
        if not dp.exists():
            print(f"   ⏭️  {d}/ не встановлено в цьому проєкті — пропускаю")
            continue
        if _ensure_local_gitignore(dp, extra):
            print(f"   ✅ Створено локальний {d}/.gitignore")
        else:
            print(f"   ℹ️  {d}/.gitignore вже на місці")
    return 0


def _ensure_local_gitignore(directory: Path, extra: str = "") -> bool:
    """Створити базовий локальний .gitignore у папці Агента (якщо відсутній).

    Повертає True, якщо файл створено, інакше False (вже існує).
    """
    gi = directory / ".gitignore"
    if gi.exists():
        return False
    gi.write_text("__pycache__/\n*.pyc\n*.log\nstate/\n" + extra, encoding="utf-8")
    return True


def _add_to_gitignore(target_root: Path, paths: list) -> None:
    """Add paths to .gitignore (create if missing).

    Дедуплікація виконується і проти існуючого вмісту, і в межах вхідного
    списку (один шлях записується один раз). Секція з заголовком додається
    лише один раз через маркер секції.
    """
    header = "# === Comfy-smart-lady Agent (auto-managed) ==="
    gitignore = target_root / '.gitignore'
    existing_lines = set()
    has_header = False
    if gitignore.exists():
        existing_lines = set(gitignore.read_text(encoding='utf-8').splitlines())
        has_header = header in existing_lines

    new_paths = []
    seen = set(existing_lines)
    for p in paths:
        if p in seen:
            continue
        seen.add(p)
        new_paths.append(p)

    if not new_paths and has_header:
        print("   All paths already in .gitignore")
        return

    section = "\n"
    if not has_header:
        section += header + "\n"
    for p in sorted(new_paths):
        section += p + "\n"

    with open(gitignore, 'a', encoding='utf-8') as f:
        f.write(section)
    print(f"   Added {len(new_paths)} paths to {gitignore}")


def _remove_from_gitignore(target_root: Path, paths: list) -> None:
    """Remove Agent paths from .gitignore (correct section handling)."""
    header = "# === Comfy-smart-lady Agent (auto-managed) ==="
    gitignore = target_root / '.gitignore'
    if not gitignore.exists():
        return

    content = gitignore.read_text(encoding='utf-8')
    lines = content.splitlines()
    path_set = set(paths)
    new_lines = []
    skip_section = False
    for line in lines:
        stripped = line.strip()
        if stripped == header:
            skip_section = True
            continue
        if skip_section:
            # Кінець блоку: непустий рядок, що не є нашим шляхом і не є
            # заголовком (тобто наступний вміст користувача після блоку).
            if stripped and stripped != header and stripped not in path_set:
                skip_section = False
                new_lines.append(line)
            continue
        if stripped in path_set:
            continue
        new_lines.append(line)

    gitignore.write_text("\n".join(new_lines), encoding='utf-8')
    print("   Cleaned .gitignore")


def main():
    # type-safe UTF-8 output (linter: TextIO has no reconfigure)
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, 'reconfigure', None)
        if callable(reconfigure):
            reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description='Sync Comfy-smart-lady agent files')

    # Основні параметри
    parser.add_argument('--source', type=str, required=False,
                        default=os.environ.get('SYNC_SOURCE', '~/repos/Comfy-smart-lady-agent'),
                        help='Шлях до центрального репо')
    parser.add_argument('--target', type=str, required=False,
                        default='.',
                        help='Шлях до цільового проекту')
    parser.add_argument('--update', action='store_true',
                        help='Режим оновлення існуючого проекту')
    parser.add_argument('--dry-run', action='store_true',
                        help='Показати що зміниться без застосування')
    parser.add_argument('--pull', action='store_true',
                        help='Pull з центрального репо перед синхронізацією')
    parser.add_argument('--apply', action='store_true',
                        help='Застосувати зміни (якщо не вказано, тільки dry-run)')
    parser.add_argument('--check-update', action='store_true',
                        help='Перевірити наявність нової версії Агента на репозиторії (без змін)')
    parser.add_argument('--repo-url', type=str, required=False, default=None,
                        help='URL raw-файла VERSION для перевірки оновлень (перевизначає manifest)')
    parser.add_argument('--version', action='version', version='sync-agent.py 1.4.6')

    args = parser.parse_args()

    # Режим оновлення застосовує зміни і перегенеровує agent-lock.json
    # (раніше --update копіював файли, але лишав застарілий лок — див.
    #  session_2026-09-04.md, Помилка №2). --dry-run має вищий пріоритет:
    # умови нижче все одно перевіряють not args.dry_run.
    if args.update:
        args.apply = True

    # Перевірка оновлень: нічого не синхронізуємо, тільки сповіщаємо
    if args.check_update:
        return check_update(args.repo_url)

    # Завантажити manifest.json з agent_config/ (конфліктні файли ізольовані)
    # Розгортаємо шлях джерела ОДИН раз і використовуємо скрізь: git -C не
    # розгортає `~` самостійно (Windows), що ламало `--update` з дефолтним
    # --source ~/repos/... (session_2026-09-04.md, Помилка №1).
    project_root = Path(args.source).expanduser().resolve()
    manifest_path = project_root / 'agent_config' / 'manifest.json'
    if not manifest_path.exists():
        print(f"❌ Не знайдено manifest.json: {manifest_path}")
        print("")
        print("💡 Підказка: спочатку склонуйте центральне репо:")
        print("   git clone https://github.com/ordercomplete/Comfy-smart-lady-agent.git ~/repos/Comfy-smart-lady-agent")
        print("")
        print("   Або вкажіть шлях явно:")
        print("   python scripts/sync-agent.py --source <шлях_до_репо> --target . --dry-run")
        print("   Або використайте повний installer (копіює і AGENT/, і конфігурації):")
        print("   bash install.sh          # Linux/macOS/Git Bash")
        print("   powershell -File install.ps1   # Windows")
        return 1

    manifest = ManifestParser(str(manifest_path)).parse()

    # Оновити центральне репо (якщо --pull)
    if args.pull or args.update:
        print("🔄 Pull з центрального репо...")
        subprocess.run(['git', '-C', str(project_root), 'pull'], check=True)

    backup_manager = BackupManager(Path(args.target))

    # Копіювати файли згідно з manifest
    source_root = project_root / manifest.get('source_root', '.')
    file_copier = FileCopier(str(source_root), args.target)

    for relative_path, config in manifest.get('files', {}).items():
        action = config.get('action', 'copy_full')

        if args.dry_run:
            print(f"📋 [DRY-RUN] Скопіювати: {relative_path} -> {config.get('target_paths')}")
        else:
            for target_path in config.get('target_paths', [relative_path]):
                backup_manager.create_backup(os.path.join(args.target, target_path))
                file_copier.copy_file(relative_path, action, target_path)

    # Копіювати кореневі файли репозиторію (секція root_files)
    root_copier = FileCopier(str(project_root), args.target)
    for rel_path, config in manifest.get('root_files', {}).items():
        if args.dry_run:
            print(f"📋 [DRY-RUN] Скопіювати (root): {rel_path} -> {config.get('target_paths')}")
        else:
            for target_path in config.get('target_paths', [rel_path]):
                backup_manager.create_backup(os.path.join(args.target, target_path))
                root_copier.copy_file(rel_path, config.get('action', 'copy_full'), target_path)

    # Копіювати канонічне ядро AGENT/ у цільовий проєкт (Спосіб B).
    # Раніше ядро розгортав лише install.ps1/install.sh (Крок 2), тому Спосіб B
    # давав неповну встановлену систему. Тепер sync-agent сам копіює весь AGENT/,
    # щоб Спосіб B відтворював повний стан, а dry-run показував це копіювання.
    agent_src_dir = project_root / "AGENT"
    agent_dst_dir = Path(args.target) / "AGENT"
    if agent_src_dir.is_dir():
        def _ignore_agent_runtime(directory: str, names: list) -> set:
            # Не затираємо локальний стан і поточні сесії хоста; trash/ та
            # __pycache__/ — не переносимо (сміття не має їхати на хости).
            ignore = {"state", "session", "trash", "__pycache__"}
            return {n for n in names if n in ignore or n.endswith(".log")}
        if args.dry_run:
            print(f"📋 [DRY-RUN] Скопіювати ядро AGENT/ -> {agent_dst_dir} "
                  f"(весь каталог, без state/, session/, trash/, __pycache__/, *.log)")
        else:
            try:
                same = agent_src_dir.resolve() == agent_dst_dir.resolve()
            except OSError:
                same = False
            if same:
                print(f"⏭️ Ядро AGENT/: джерело == ціль (self-sync) — пропускаю")
            else:
                # Бекап цільового AGENT/ ПЕРЕД перезаписом (Знімок стану хоста).
                # Лежить у тому ж timestamped-папці, що й бекапи окремих файлів,
                # і обмежується тією самою ротацією MAX_BACKUPS.
                if agent_dst_dir.is_dir() and any(agent_dst_dir.iterdir()):
                    agent_backup_root = backup_manager.backup_dir / "AGENT"
                    shutil.copytree(
                        agent_dst_dir, agent_backup_root,
                        dirs_exist_ok=True, ignore=_ignore_agent_runtime,
                    )
                    print(f"💾 Бекап цільового AGENT/ -> {agent_backup_root}")
                    backup_manager._prune_old_backups()
                shutil.copytree(agent_src_dir, agent_dst_dir, dirs_exist_ok=True,
                                ignore=_ignore_agent_runtime)
                print(f"✅ Скопійовано ядро Агента: AGENT/ -> {agent_dst_dir} "
                      f"(без state/, session/, trash/, __pycache__/, *.log)")
    else:
        print(f"⚠️  Не знайдено ядро Агента: {agent_src_dir} — копіювання AGENT/ пропущено")

    # Створити stub-файли
    first_stub = next(iter(manifest.get('stub_files', {}).values()), {})
    template_path = source_root / first_stub.get('template', 'templates/stub_agents.md')
    stub_generator = StubGenerator(str(template_path))

    for target_stub, config in manifest.get('stub_files', {}).items():
        if args.dry_run:
            print(f"📋 [DRY-RUN] Створити stub: {target_stub}")
        else:
            backup_manager.create_backup(os.path.join(args.target, target_stub))
            stub_generator.generate_stub(
                os.path.join(args.target, target_stub),
                config['source_ref']
            )

    # Перевірити git status та diff
    if not args.dry_run:
        print("\n📊 Git Status:")
        print(GitHelper.check_status(Path(args.target)))

        print("\n📝 Git Diff:")
        print(GitHelper.check_diff(Path(args.target)))

    # Generate/update lock file after successful apply
    if not args.dry_run and args.apply:
        lock = AgentLockManager(Path(args.target))
        lock.clear()
        lock.set_manifest_info(
            manifest.get('version', '1.4.0'),
            _manifest_hash(project_root / 'agent_config' / 'manifest.json')
        )
        source_root = project_root
        target_root = Path(args.target)
        files_source_root = project_root / manifest.get('source_root', '.')
        for relative_path, config in manifest.get('files', {}).items():
            action = config.get('action', 'copy_full')
            for tp in config.get('target_paths', [relative_path]):
                full = target_root / tp
                # Skip files where source == target (already exist, not installed by us)
                src = files_source_root / relative_path
                if src.resolve() == full.resolve():
                    continue
                # Не додавати в лок записи, яких нема в джерелі: раніше це
                # створювало entries з порожнім хешем і «привидів» Missing
                # (session_2026-09-04.md, Помилка №3).
                if not src.exists():
                    print(f"⚠️ Пропущено в локу (нема в джерелі): {relative_path}")
                    continue
                lock.add_file(tp, _file_hash(full), action, config.get('target_paths', [relative_path]))
        for rel_path, config in manifest.get('root_files', {}).items():
            for tp in config.get('target_paths', [rel_path]):
                full = target_root / tp
                src = source_root / rel_path
                if src.resolve() == full.resolve():
                    continue
                if not src.exists():
                    print(f"⚠️ Пропущено в локу (нема в джерелі): {rel_path}")
                    continue
                lock.add_file(tp, _file_hash(full), config.get('action', 'copy_full'), config.get('target_paths', [rel_path]))
        # Файли ядра AGENT/ (копійовані блоком ядра вище) — щоб status охоплював ядро
        if agent_dst_dir.is_dir():
            for agent_file in agent_dst_dir.rglob("*"):
                if not agent_file.is_file():
                    continue
                rel = agent_file.relative_to(agent_dst_dir).as_posix()
                # Runtime/сміття не входить у lock — той самий набір винятків,
                # що й у копіюванні ядра (state/, session/, trash/, __pycache__/, *.log, *.pyc)
                if rel.split("/")[0] in {"state", "session", "trash", "__pycache__"} \
                        or rel.endswith((".log", ".pyc")):
                    continue
                tp = f"AGENT/{rel}"
                lock.add_file(tp, _file_hash(agent_file), 'copy_full', [tp])
        for target_stub, config in manifest.get('stub_files', {}).items():
            full = target_root / target_stub
            src = source_root / config.get('source', target_stub)
            if src.resolve() == full.resolve():
                continue
            lock.add_file(target_stub, _file_hash(full), 'stub', [target_stub])
        lock.save()
        print(f"\n   Agent lock file generated: {target_root / 'agent-lock.json'}")
        print("   Примітка: кореневий .gitignore таргету не змінюється; ігнор-правила "
              "Агента живуть у локальних .gitignore папок (див. sync-agent.py gitignore).")

    print(f"\n✅ Синхронізація завершена. Стан: {'dry-run (без змін)' if args.dry_run else 'застосовано'}.")
    return 0


if __name__ == '__main__':
    # type-safe UTF-8 output (важливо для підкоманд перед main())
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, 'reconfigure', None)
        if callable(reconfigure):
            reconfigure(encoding='utf-8')

    # Support subcommands
    # Цільовий шлях — перший аргумент, що НЕ починається з «-»: раніше
    # `status --verbose` сприймав прапорець як шлях і шукав лок у папці
    # «--verbose» (session_2026-09-04.md, Помилка №4).
    def _subcommand_target(argv_rest):
        positional = [a for a in argv_rest if not a.startswith('-')]
        return Path(positional[0]) if positional else Path('.')

    if len(sys.argv) > 1 and sys.argv[1] == 'status':
        target = _subcommand_target(sys.argv[2:])
        verbose = '--verbose' in sys.argv or '-v' in sys.argv
        exit(cmd_status(target, verbose))
    elif len(sys.argv) > 1 and sys.argv[1] == 'remove':
        target = _subcommand_target(sys.argv[2:])
        force = '--force' in sys.argv or '-f' in sys.argv
        exit(cmd_remove(target, force))
    elif len(sys.argv) > 1 and sys.argv[1] == 'gitignore':
        target = _subcommand_target(sys.argv[2:])
        exit(cmd_gitignore(target))
    else:
        exit(main())
