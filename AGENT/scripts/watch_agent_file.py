"""Watch the AGENT/ core — full zipped snapshots on any change (integrated into anti_loop hook)."""

import os
import shutil
import time
import sys
import zipfile
from pathlib import Path
from datetime import datetime

# Workspace root: AGENT/scripts/watch_agent_file.py -> parents[2] = workspace root
WORKSPACE = Path(__file__).resolve().parents[2]

AGENT_ROOT = WORKSPACE / "AGENT"
BACKUP_DIR = WORKSPACE / "agent_config"
AGENT_BACKUP_DIR = BACKUP_DIR / "backup-agent"
LOG_FILE = BACKUP_DIR / "watcher_log.txt"

MAX_AGENT_BACKUPS = 3  # Максимальна кількість повних знімків AGENT_*.zip у backup-agent/ (рішення 2026-09-28: 10 -> 3)

# Що не бека́пимо: динамічний стан, логи, кеші
SCAN_EXCLUDE_DIRS = {"state", "trash", "__pycache__"}
SCAN_EXCLUDE_RELDIRS = set()
SCAN_EXCLUDE_SUFFIXES = (".log", ".pyc")


def _is_excluded(rel_path: Path) -> bool:
    """Чи виключено цей відносний шлях (від AGENT/) зі сканування/бекапу."""
    parts = rel_path.parts
    if any(part in SCAN_EXCLUDE_DIRS for part in parts):
        return True
    for ex in SCAN_EXCLUDE_RELDIRS:
        if str(rel_path).replace("\\", "/").startswith(ex):
            return True
    return rel_path.suffix in SCAN_EXCLUDE_SUFFIXES


def scan_agent_hashes() -> dict:
    """Хеші всіх файлів AGENT/ (крім виключених) — {rel_path_str: md5}."""
    hashes = {}
    for p in AGENT_ROOT.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(AGENT_ROOT)
        if _is_excluded(rel):
            continue
        try:
            hashes[rel.as_posix()] = get_file_hash(p)
        except OSError:
            pass
    return hashes


def create_agent_snapshot() -> Path | None:
    """Повний zipped-знімок AGENT/ у agent_config/backup-agent/."""
    if not AGENT_ROOT.is_dir():
        return None
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    AGENT_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = AGENT_BACKUP_DIR / f"AGENT_{timestamp}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in AGENT_ROOT.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(AGENT_ROOT)
            if _is_excluded(rel):
                continue
            zf.write(p, arcname=str(rel))
    log_message(f"SNAPSHOT -> {zip_path}")
    prune_old_agent_backups()
    return zip_path


def prune_old_agent_backups() -> None:
    """Залишити щонайбільше MAX_AGENT_BACKUPS знімків AGENT_*.zip.

    Сортування за ім'ям файлу (таймстамп у назві AGENT_YYYY-MM-DD_HH-MM-SS),
    а не за mtime: sync-agent.py копіює знімки між workspace-ами і скидає
    mtime, через що mtime-сортування давало неправильний порядок "найстаріших".
    Викликається не тільки після власного знімка, а й у кожному циклі
    watcher_loop() — інакше знімки, підтягнуті sync-ом з іншого workspace,
    залишаються понад ліміт.
    """
    if not AGENT_BACKUP_DIR.is_dir():
        return
    files = sorted(AGENT_BACKUP_DIR.glob("AGENT_*.zip"), key=lambda p: p.name, reverse=True)
    for stale in files[MAX_AGENT_BACKUPS:]:
        try:
            stale.unlink()
            log_message(f"🧹 Ротація: видалено зайвий знімок AGENT/ (ліміт {MAX_AGENT_BACKUPS}): {stale.name}")
        except OSError:
            pass


MAX_CHAT_BACKUPS = 3  # Ліміт папок backup_* у agent_config/backup-chat/ (рішення 2026-09-28: 10 -> 3)


def prune_old_chat_backups() -> None:
    """Залишити щонайбільше MAX_CHAT_BACKUPS папок backup_* у backup-chat/.

    Той самий механізм, що й для AGENT_*.zip: sync-agent.py копіює папки
    backup-chat між workspace-ами і скидає mtime, тому сортування за ім'ям
    (backup_YYYY-MM-DD_HH-MM-SS) та prune у кожному циклі watcher'а —
    інакше чужі папки залишаються понад ліміт.
    """
    chat_dir = BACKUP_DIR / "backup-chat"
    if not chat_dir.is_dir():
        return
    folders = sorted(
        (p for p in chat_dir.iterdir() if p.is_dir() and p.name.startswith("backup_")),
        key=lambda p: p.name,
        reverse=True,
    )
    for stale in folders[MAX_CHAT_BACKUPS:]:
        try:
            shutil.rmtree(stale)
            log_message(f"🧹 Ротація: видалено зайвий chat-бекап (ліміт {MAX_CHAT_BACKUPS}): {stale.name}")
        except OSError as e:
            log_message(f"⚠️ Не вдалося видалити chat-бекап {stale.name}: {e}")


def log_message(message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}\n"

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    # Append to log file with UTF-8 encoding (create if missing)
    with LOG_FILE.open("a", encoding="utf-8") as stream:
        stream.write(line)

    try:
        print(line.strip(), flush=True)
    except UnicodeEncodeError:
        pass


def get_file_hash(file_path: Path) -> str | None:
    """Compute MD5 hash for change detection."""
    if not file_path.exists():
        return None

    content = file_path.read_bytes()
    import hashlib
    return hashlib.md5(content).hexdigest()


def watcher_loop() -> None:
    """Main watch loop — runs continuously in background."""
    log_message("=" * 60)
    log_message("AGENT FILE WATCHER STARTED")
    log_message(f"Watching:    {AGENT_ROOT} (без state/, trash/, __pycache__, логів; memories_agent/session/ бекапиться)")
    log_message(f"Snapshots:   {AGENT_BACKUP_DIR}")
    log_message("=" * 60)

    last_agent_hashes = scan_agent_hashes()
    log_message(f"Initial AGENT/ scan: {len(last_agent_hashes)} files tracked")

    # Ротація на старті: якщо sync підтягнув чужі знімки/папки понад ліміт — одразу прибрати
    prune_old_agent_backups()
    prune_old_chat_backups()

    print("\nMonitoring changes... (runs silently in background)\n", flush=True)

    while True:
        try:
            # Моніторинг усього AGENT/ (без state/, trash/, __pycache__, логів)
            current_agent_hashes = scan_agent_hashes()
            if current_agent_hashes != last_agent_hashes:
                log_message(">>> AGENT/ CHANGED!")
                snapshot_path = create_agent_snapshot()
                last_agent_hashes = current_agent_hashes
                print(f"   + AGENT snapshot: {snapshot_path}", flush=True)

            # Ротація щоциклу: знімки та папки, підтягнуті sync-ом з іншого
            # workspace, теж мають обмежуватись лімітами, а не тільки власні
            prune_old_agent_backups()
            prune_old_chat_backups()

            time.sleep(60)  # Check every 60 seconds

        except KeyboardInterrupt:
            log_message("\nWATCHER STOPPED (User)")
            break

        except Exception as e:
            error_msg = f"ERROR: {str(e)}"
            log_message(error_msg)
            print(f"\n   + Checking file...", flush=True)
            time.sleep(5)


def watcher_is_running() -> bool:
    """Check if watcher process is already running (by parsing PID from stdout).

    ВАЖЛИВО: звіряємо шлях САМЕ ПОТОЧНОГО workspace у командному рядку.
    Раніше фільтр ловив будь-який watch_agent_file.py — зокрема watcher
    іншого проєкту (наприклад, D:/GEN/Music_Doc), через що тут main()
    казав "already running", хоча локального демона не було, і бекапи
    накопичувались понад ліміт.
    """
    import platform
    import subprocess

    marker = f"*{WORKSPACE}*watch_agent_file.py*"

    if platform.system() == "Windows":
        command = (
            "Get-CimInstance Win32_Process -Filter \"Name = 'python.exe'\" | "
            f"Where-Object {{ $_.CommandLine -like '{marker}' }} | "
            "Select-Object -First 1 -ExpandProperty ProcessId"
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            check=False,
        )
        # PID надрукований у stdout = процес знайдено; порожній stdout = не запущений.
        # (os.system-код завершення тут не годився: PowerShell повертає 0
        #  навіть коли процес не знайдено, тому main() ніколи не стартував watcher.)
        return bool(result.stdout.strip())

    # Linux/macOS fallback using pgrep (повний шлях до скрипта цього workspace)
    result = subprocess.run(
        ["pgrep", "-f", str(Path(__file__).resolve())],
        capture_output=True,
        text=True,
        check=False,
    )
    return bool(result.stdout.strip())


def main() -> int:
    """Entry point — called from anti_loop hook or directly."""
    # Validate AGENT root exists
    if not AGENT_ROOT.is_dir():
        print(f"[watch_agent_file] missing directory: {AGENT_ROOT}", file=sys.stderr)
        return 1

    # Start watcher loop in a separate process to avoid blocking anti_loop
    import subprocess
    import platform

    if watcher_is_running():
        print("[watch_agent_file] watcher already running")
        return 0

    creation_flags = 0
    if platform.system() == "Windows":
        creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

    proc = subprocess.Popen(
        [sys.executable, str(__file__)],
        cwd=str(WORKSPACE),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creation_flags,
        start_new_session=platform.system() != "Windows",
    )

    print(f"[watch_agent_file] watcher started (PID: {proc.pid})")
    return 0


if __name__ == "__main__":
    # Direct invocation for testing
    watcher_loop()


