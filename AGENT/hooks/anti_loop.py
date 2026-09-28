#!/usr/bin/env python3
"""Detect repeated tool calls and return an OpenCode-compatible decision."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

WINDOW_SIZE = 24
EXACT_REPEAT_LIMIT = 8
SAME_TARGET_LIMIT = 7
EXACT_REPEAT_COOLDOWN_SECONDS = 60

# ── Initialization Gate ──────────────────────────────────────────────────────
INIT_MARKER = "INIT_COMPLETED"
SESSION_DIR_NAME = "session"


def today_session_path() -> Path:
    """Return the path to today's session file, creating parent dirs if needed."""
    root = workspace_root()
    session_dir = root / "AGENT" / "memories_agent" / SESSION_DIR_NAME
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir / f"session_{datetime.now():%Y-%m-%d}.md"


def is_initialized() -> bool:
    """Check if today's session file exists and contains INIT_COMPLETED marker."""
    session_file = today_session_path()
    if not session_file.exists():
        return False
    try:
        content = session_file.read_text(encoding="utf-8")
        return INIT_MARKER in content
    except OSError:
        return False


def workspace_root() -> Path:
    configured = os.environ.get("WORKSPACE_ROOT")
    return Path(configured).expanduser().resolve() if configured else Path.cwd().resolve()


def paths() -> tuple[Path, Path]:
    root = workspace_root()
    state_dir = root / "AGENT" / "state"
    error_log = root / "AGENT" / "memories_agent" / "errors" / f"error-log_{datetime.now():%Y-%m-%d}.md"
    state_dir.mkdir(parents=True, exist_ok=True)
    error_log.parent.mkdir(parents=True, exist_ok=True)
    return state_dir / "vscode_agent_anti_loop_state.json", error_log


def load_state(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"calls": [], "last_exact_reset": {}}


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def payload() -> dict[str, Any]:
    try:
        value = json.load(sys.stdin)
        return value if isinstance(value, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def signature(tool_name: str, tool_input: Any) -> str:
    encoded = json.dumps(tool_input, ensure_ascii=False, sort_keys=True, default=str)
    return f"{tool_name}::{encoded}"


def target(tool_input: Any) -> str:
    if not isinstance(tool_input, dict):
        return ""
    for key in ("filePath", "path", "target", "uri"):
        value = tool_input.get(key)
        if isinstance(value, str):
            return value
    return ""


def decision(reason: str, message: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
            "loopResetReason": reason,
            "message": message,
        }
    }, ensure_ascii=False))


def log_event(error_log: Path, reason: str, tool_name: str, tool_input: Any) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = (
        f"\n### 🔴 Anti-loop: {reason}\n"
        f"**Час:** {timestamp}\n"
        f"**Tool:** `{tool_name}`\n"
        f"**Вхід:** `{json.dumps(tool_input, ensure_ascii=False, default=str)}`\n\n---\n"
    )
    with error_log.open("a", encoding="utf-8") as stream:
        stream.write(entry)


def main() -> int:
    # ── Initialization Gate Check ──────────────────────────────────────────────
    if not is_initialized():
        decision(
            "INIT_REQUIRED",
            "🔴 БЛОВАННЯ: Ініціалізація не пройдена. Спочатку прочитайте AGENT/agents/Comfy-smart-lady.md та створіть файл сесії."
        )
        return 0

    data = payload()
    tool_name = data.get("tool_name") or data.get("tool")
    tool_input = data.get("tool_input", data.get("args", {}))
    if not isinstance(tool_name, str) or not tool_name or tool_name == "unknown":
        return 0

    state_path, error_log = paths()
    state = load_state(state_path)
    now = time.time()
    current_signature = signature(tool_name, tool_input)
    current_target = target(tool_input)
    calls = [call for call in state.get("calls", []) if now - call.get("time", 0) <= 1800]
    calls.append({"signature": current_signature, "tool": tool_name, "target": current_target, "time": now})
    state["calls"] = calls[-WINDOW_SIZE:]

    exact_count = sum(call["signature"] == current_signature for call in state["calls"])
    # current_target може бути порожнім рядком — тоді генератор видавав би суміш
    # "" (str) та bool, що ламає sum() (TypeError) і типізатор. Рахуємо суму
    # лише коли є ціль, і Bool'и повертаються послідовно.
    target_count = 0
    if current_target:
        target_count = sum(
            call["tool"] == tool_name and call["target"] == current_target
            for call in state["calls"]
        )
    last_reset = state.setdefault("last_exact_reset", {}).get(tool_name, 0)
    reason = ""
    if exact_count >= EXACT_REPEAT_LIMIT and now - last_reset >= EXACT_REPEAT_COOLDOWN_SECONDS:
        reason = f"EXACT REPEAT ({exact_count} однакових викликів)"
        state["calls"] = []
        state["last_exact_reset"][tool_name] = now
    elif target_count >= SAME_TARGET_LIMIT:
        reason = f"SAME TARGET ({target_count} викликів для {current_target})"
        state["calls"] = []

    save_state(state_path, state)
    if reason:
        log_event(error_log, reason, tool_name, tool_input)
        decision(reason, f"Loop detected: {reason}. Змініть підхід.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
