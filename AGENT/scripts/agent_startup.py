"""Start Comfy-smart-lady session services."""

import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
ANTI_LOOP = WORKSPACE / "AGENT" / "scripts" / "anti_loop.py"
WATCHER = WORKSPACE / "AGENT" / "scripts" / "watch_agent_file.py"
STR_TRANSLATE = WORKSPACE / "AGENT" / "scripts" / "str.translate.py"
MANIFEST = WORKSPACE / "agent_config" / "manifest.json"
SYNC_SCRIPT = WORKSPACE / "agent_config" / "scripts" / "sync-agent.py"
UPDATE_STATE = WORKSPACE / "AGENT" / "state" / "update_check.json"

DEFAULT_UPDATE_CHECK = {
    "mode": "notify",
    "interval_hours": 24,
    "timeout_seconds": 5,
}


def validate_script(script_path: Path) -> None:
    source = script_path.read_text(encoding="utf-8")
    compile(source, str(script_path), "exec")


def watcher_is_running() -> bool:
    if platform.system() == "Windows":
        command = (
            "Get-CimInstance Win32_Process -Filter \"Name = 'python.exe'\" | "
            "Where-Object { $_.CommandLine -like '*watch_agent_file.py*' } | "
            "Select-Object -First 1 -ExpandProperty ProcessId"
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            check=False,
        )
        return bool(result.stdout.strip())

    result = subprocess.run(
        ["pgrep", "-f", str(WATCHER)],
        capture_output=True,
        text=True,
        check=False,
    )
    return bool(result.stdout.strip())


def start_watcher() -> None:
    if watcher_is_running():
        print("watcher already running")
        return

    creation_flags = 0
    if platform.system() == "Windows":
        creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

    subprocess.Popen(
        [sys.executable, str(WATCHER)],
        cwd=WORKSPACE,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creation_flags,
        start_new_session=platform.system() != "Windows",
    )
    print("watcher started")


def check_for_updates() -> None:
    """Тиха перевірка нової версії Агента при старті (режим notify).

    Викликає sync-agent.py --check-update (вся логіка джерел — там).
    - не частіше ніж interval_hours (кеш у AGENT/state/update_check.json);
    - будь-яка помилка мовчки ігнорується — старт агента ніколи не блокується;
    - жодних змін у файлах не робить, тільки друкує підказку.
    """
    try:
        cfg = DEFAULT_UPDATE_CHECK
        if MANIFEST.exists():
            data = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
            cfg = data.get("update_check") or DEFAULT_UPDATE_CHECK
        if cfg.get("mode") != "notify" or not SYNC_SCRIPT.exists():
            return

        # Кеш: не частіше ніж interval_hours
        last_check = 0.0
        if UPDATE_STATE.exists():
            state = json.loads(UPDATE_STATE.read_text(encoding="utf-8"))
            last_check = float(state.get("last_check_ts", 0))
        now = time.time()
        if now - last_check < int(cfg.get("interval_hours", 24)) * 3600:
            return

        result = subprocess.run(
            [sys.executable, str(SYNC_SCRIPT), "--check-update"],
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=int(cfg.get("timeout_seconds", 5)) * 12,
            check=False,
        )
        UPDATE_STATE.parent.mkdir(parents=True, exist_ok=True)
        UPDATE_STATE.write_text(
            json.dumps({"last_check_ts": now, "exit_code": result.returncode}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        if result.returncode == 10 and result.stdout.strip():
            print(result.stdout.strip())
    except Exception:
        # Оновлення — необов'язкова опція: офлайн/таймаут/кривий manifest не ламають старт
        pass


def rename_project_memories() -> None:
    """Одномуражоване перейменування `memories/` -> `memories_{project_root}` під час старту.

    Див. AGENT/scripts/rename_memories.py. Не блокуючий: будь-яка помилка
    мовчки ігнорується (як check_for_updates), бо це лише ініціалізація.
    """
    rename_script = WORKSPACE / "AGENT" / "scripts" / "rename_memories.py"
    if not rename_script.exists():
        return
    try:
        subprocess.run(
            [sys.executable, str(rename_script)],
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except Exception:
        pass


def main() -> int:
    for script_path in (ANTI_LOOP, WATCHER, STR_TRANSLATE):
        if not script_path.exists():
            print(f"missing startup script: {script_path}", file=sys.stderr)
            return 1
        validate_script(script_path)

    rename_project_memories()

    start_watcher()
    print("anti_loop.py, watch_agent_file.py and str.translate.py loaded")
    check_for_updates()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
