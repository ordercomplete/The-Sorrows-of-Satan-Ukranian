#!/usr/bin/env python3
"""Track Vercel AI Gateway errors and trigger actions when threshold is reached.

This hook monitors tool outputs for Vercel AI Gateway error patterns.
When consecutive errors exceed a threshold, it logs the event and can
trigger a restart action.

Similar pattern to anti_loop.py but for API/stream errors instead of loops.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Configuration
ERROR_THRESHOLD = 3  # Number of consecutive Vercel errors before action
ERROR_WINDOW_SECONDS = 300  # 5 minutes window for counting errors
STATE_FILE_NAME = "vscode_agent_vercel_error_state.json"

# Vercel AI Gateway error patterns
VERCEL_ERROR_PATTERNS = [
    "Failed to create stream",
    "inference request failed",
    "failed to invoke model",
    "failed to send request",
    "giving up after",
    "ai-gateway.vercel.sh",
    "failed to generate stream from Vercel",
    "POST https://ai-gateway.vercel.sh",
]


def workspace_root() -> Path:
    configured = os.environ.get("WORKSPACE_ROOT")
    return Path(configured).expanduser().resolve() if configured else Path.cwd().resolve()


def paths() -> tuple[Path, Path]:
    root = workspace_root()
    state_dir = root / "AGENT" / "state"
    error_log = root / "AGENT" / "memories_agent" / "errors" / f"error-log_{datetime.now():%Y-%m-%d}.md"
    state_dir.mkdir(parents=True, exist_ok=True)
    error_log.parent.mkdir(parents=True, exist_ok=True)
    return state_dir / STATE_FILE_NAME, error_log


def load_state(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"errors": [], "total_count": 0, "last_action": None}


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def payload() -> dict[str, Any]:
    try:
        value = json.load(sys.stdin)
        return value if isinstance(value, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def contains_vercel_error(text: str) -> tuple[bool, str]:
    """Check if text contains Vercel error patterns. Returns (found, pattern)."""
    if not text:
        return False, ""
    text_lower = text.lower()
    for pattern in VERCEL_ERROR_PATTERNS:
        if pattern.lower() in text_lower:
            return True, pattern
    return False, ""


def generate_error_id(error_text: str) -> str:
    """Generate a short hash for error deduplication."""
    return hashlib.md5(error_text[:200].encode()).hexdigest()[:12]


def log_event(error_log: Path, error_pattern: str, error_text: str, count: int) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    error_id = generate_error_id(error_text)
    entry = (
        f"\n### 🔴 Vercel Error Detected\n"
        f"**Час:** {timestamp}\n"
        f"**Error ID:** {error_id}\n"
        f"**Патерн:** `{error_pattern}`\n"
        f"**Послідовних помилок:** {count}/{ERROR_THRESHOLD}\n"
        f"**Текст:** `{error_text[:150]}...`\n\n---\n"
    )
    with error_log.open("a", encoding="utf-8") as stream:
        stream.write(entry)


def log_action_triggered(error_log: Path, count: int) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = (
        f"\n### ⚠️ Vercel Error Threshold Reached!\n"
        f"**Час:** {timestamp}\n"
        f"**Послідовних помилок:** {count}\n"
        f"**Дія:** Рекомендується перезапуск чату або перемикання моделі\n\n---\n"
    )
    with error_log.open("a", encoding="utf-8") as stream:
        stream.write(entry)


def write_restart_signal(root: Path, error_count: int, pattern: str) -> None:
    """Write a restart signal file for the supervisor to detect."""
    state_dir = root / "AGENT" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    signal_file = state_dir / "vercel_restart_signal.json"
    signal_data = {
        "restartRequested": True,
        "timestamp": datetime.now().isoformat(),
        "errorCount": error_count,
        "pattern": pattern,
        "reason": f"Vercel error threshold reached ({error_count})",
    }
    signal_file.write_text(json.dumps(signal_data, ensure_ascii=False, indent=2), encoding="utf-8")


def decision(should_alert: bool, message: str, error_count: int) -> None:
    """Output decision to stdout for the hook system."""
    output = {
        "hookSpecificOutput": {
            "permissionDecision": "allow",
            "permissionDecisionReason": "Vercel error tracker",
            "message": message,
        },
        "vercelError": {
            "detected": True,
            "count": error_count,
            "shouldAlert": should_alert,
        }
    }
    if should_alert:
        output["hookSpecificOutput"]["permissionDecision"] = "ask"
    print(json.dumps(output, ensure_ascii=False))


def main() -> int:
    data = payload()

    # Extract text to check from various possible payload fields
    texts_to_check = []

    # Check tool output
    tool_output = data.get("tool_output", "")
    if isinstance(tool_output, str):
        texts_to_check.append(tool_output)

    # Check tool input (sometimes errors are echoed back)
    tool_input = data.get("tool_input", data.get("args", {}))
    if isinstance(tool_input, str):
        texts_to_check.append(tool_input)
    elif isinstance(tool_input, dict):
        cmd = tool_input.get("command", "")
        if isinstance(cmd, str):
            texts_to_check.append(cmd)

    # Check for error in output field
    output = data.get("output", "")
    if isinstance(output, str):
        texts_to_check.append(output)

    # Check for error messages
    error = data.get("error", "")
    if isinstance(error, str):
        texts_to_check.append(error)

    # Also check if there's a 'result' field with error
    result = data.get("result", {})
    if isinstance(result, dict):
        result_error = result.get("error", "")
        if isinstance(result_error, str):
            texts_to_check.append(result_error)

    # Check all collected texts for Vercel errors
    vercel_error_found = False
    matched_pattern = ""
    error_text = ""

    for text in texts_to_check:
        found, pattern = contains_vercel_error(text)
        if found:
            vercel_error_found = True
            matched_pattern = pattern
            error_text = text
            break

    if not vercel_error_found:
        decision(False, "No Vercel error detected", 0)
        return 0

    # Vercel error found - update state
    state_path, error_log = paths()
    state = load_state(state_path)
    now = time.time()

    # Add new error entry
    error_entry = {
        "timestamp": now,
        "pattern": matched_pattern,
        "error_id": generate_error_id(error_text),
    }
    state.setdefault("errors", []).append(error_entry)
    state["total_count"] = state.get("total_count", 0) + 1

    # Filter to only recent errors within window
    recent_errors = [
        e for e in state["errors"]
        if now - e.get("timestamp", 0) <= ERROR_WINDOW_SECONDS
    ]
    state["errors"] = recent_errors

    # Count consecutive errors
    consecutive_count = len(recent_errors)

    # Log the error
    log_event(error_log, matched_pattern, error_text, consecutive_count)

    # Check if threshold reached
    should_alert = consecutive_count >= ERROR_THRESHOLD

    if should_alert:
        log_action_triggered(error_log, consecutive_count)
        state["last_action"] = {
            "timestamp": now,
            "action": "threshold_reached",
            "count": consecutive_count,
        }
        # Write restart signal for the supervisor
        root = workspace_root()
        write_restart_signal(root, consecutive_count, matched_pattern)
        # Also write to stderr so supervisor can detect it directly
        print(f"VERCEL_ERROR_TRACKER: restart_requested count={consecutive_count}", file=sys.stderr)

    save_state(state_path, state)

    # Output decision
    if should_alert:
        decision(
            True,
            f"Vercel error threshold reached ({consecutive_count}/{ERROR_THRESHOLD}). "
            f"Consider restarting the chat or switching models.",
            consecutive_count,
        )
    else:
        decision(
            False,
            f"Vercel error detected ({consecutive_count}/{ERROR_THRESHOLD}). "
            f"Pattern: {matched_pattern}",
            consecutive_count,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())