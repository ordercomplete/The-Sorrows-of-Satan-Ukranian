"""Centralized agent startup — launches all services from one entry point."""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Workspace root: AGENT/scripts/startup_all.py -> parents[2] = workspace root
WORKSPACE = Path(__file__).resolve().parents[2]

# Core paths
CORE_DIR = WORKSPACE / "AGENT"
HOOKS_DIR = CORE_DIR / "hooks"
SCRIPTS_DIR = CORE_DIR / "scripts"
STATE_DIR = CORE_DIR / "state"
ERROR_LOG_DIR = CORE_DIR / "memories_agent" / "errors"
MANIFEST = WORKSPACE / "agent_config" / "manifest.json"
SYNC_SCRIPT = WORKSPACE / "agent_config" / "scripts" / "sync-agent.py"

# Python scripts to load (всі скрипти виконуються канонічно з AGENT/scripts/)
CORE_SCRIPTS = {
    "anti_loop": SCRIPTS_DIR / "anti_loop.py",
    "watch_agent_file": SCRIPTS_DIR / "watch_agent_file.py",
    "str_translate": SCRIPTS_DIR / "str.translate.py",
}


def validate_script(script_path: Path) -> None:
    """Validate Python syntax of a script."""
    source = script_path.read_text(encoding="utf-8")
    compile(source, str(script_path), "exec")


def watcher_is_running() -> bool:
    """Check if watch_agent_file.py is already running."""
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

    # Linux/macOS fallback using pgrep
    result = subprocess.run(
        ["pgrep", "-f", str(SCRIPTS_DIR / "watch_agent_file.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    return bool(result.stdout.strip())


def start_watcher() -> None:
    """Launch watch_agent_file.py as a detached background process."""
    if watcher_is_running():
        print("watcher already running")
        return

    creation_flags = 0
    if platform.system() == "Windows":
        creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

    proc = subprocess.Popen(
        [sys.executable, str(SCRIPTS_DIR / "watch_agent_file.py")],
        cwd=str(WORKSPACE),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creation_flags,
        start_new_session=platform.system() != "Windows",
    )
    print(f"watcher started (PID: {proc.pid})")


def validate_core_scripts() -> list[str]:
    """Validate all core Python scripts exist and have valid syntax. Returns list of errors."""
    errors = []
    for name, path in CORE_SCRIPTS.items():
        if not path.exists():
            errors.append(f"missing script: {path}")
        else:
            try:
                validate_script(path)
            except SyntaxError as e:
                errors.append(f"syntax error in {name}: {e}")
    return errors


def main() -> int:
    """Main startup routine — validates and starts all services."""
    
    # Validate core scripts
    errors = validate_core_scripts()
    if errors:
        for err in errors:
            print(f"[ERROR] {err}", file=sys.stderr)
        return 1
    
    # Start watcher daemon
    start_watcher()
    
    # Report status
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"✅ Core scripts loaded — {timestamp}")
    print("   - anti_loop.py: tool call interceptor")
    print("   - watch_agent_file.py: AGENT/ file watcher (60s interval)")
    print("   - str.translate.py: layout converter for accidental eng-type text")
    print(f"   PID: {watcher_is_running()}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
