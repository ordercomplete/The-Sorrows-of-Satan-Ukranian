#!/usr/bin/env python3
"""rename_memories.py — Namespacing папки `memories` у хост-проєкті.

При інсталяції / старті Агента перейменовує папку `memories/` (загальні
процеси проєкту, див. AGENT/agents/Comfy-smart-lady.md) у
`memories_{<ім'я кріневої папки проєкту>}`, наприклад `memories_Under-word-app`.

Мета:
- уникає суміщення `memories/` різних проєктів, у яких працює один Агент;
- ім'я папки однозначно вказує, до якого проєкту належить історія.

Ідемпотентно та безпечно (ніколи не видаляє, не перезаписує, не торкає
`AGENT/memories_agent/` — це внутрішня пам'ять агента, інша папка):
- `memories/` має, а `memories_{proj}` нема  -> перейменовує;
- `memories_{proj}` вже є -> пропускає (не перетирає);
- `memories/` нема -> нічого не робить.

Робочий каталог динамічний: AGENT/scripts/rename_memories.py -> parents[2] = корінь проєкту.
Тому скрипт працює в будь-якій папці (без жорстких шляхів).

Використання:
    python AGENT/scripts/rename_memories.py            # auto: root = workspace root
    python AGENT/scripts/rename_memories.py --root PATH  # перевізити в довільний проєкт
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path


def _project_root() -> Path:
    """Корінь проєкту (= 2 рівні вгору від цього скрипта: AGENT/scripts/ -> root)."""
    return Path(__file__).resolve().parents[2]


def _log(result: str) -> None:
    """Аудиторний запис у AGENT/state/rename_memories.log (локальний, .gitignore‑ований)."""
    try:
        state_dir = _project_root() / "AGENT" / "state"
        state_dir.mkdir(parents=True, exist_ok=True)
        log_path = state_dir / "rename_memories.log"
        prev = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
        log_path.write_text(
            f"{prev}{datetime.now():%Y-%m-%d %H:%M}    {result}\n",
            encoding="utf-8",
        )
    except Exception:
        # Логування — лише bonus; не повинно ламати старт агента.
        pass


def rename_memories(root: Path | None = None) -> str:
    """Одномуражоване перейменування <root>/memories -> <root>/memories_{root.name}.

    `root` — для тестів / ручного запуску у довільному проєкті; за замовчуванням
    = канонічний корінь проєкту (батьківська папка AGENT/).
    Повертає рядок‑звіт дії.
    """
    root = (root or _project_root()).resolve()
    project_name = root.name
    src = root / "memories"
    dst = root / f"memories_{project_name}"

    # Немає папки memories — нічого робити (наприклад, вже перейменовано або
    # її не було створено для цього проєкту).
    if not src.is_dir():
        return f"skip: '{src.name}' not found (root={project_name})"

    # Вже namespaced або конфліктна папка — не перетираємо (безпека).
    if dst.exists():
        return f"skip: '{dst.name}' already exists (root={project_name})"

    src.rename(dst)
    return f"renamed: '{src.name}' -> '{dst.name}' (root={project_name})"


def main() -> int:
    # type-safe UTF-8 output (важливо для українських символів у логах)
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Rename project 'memories' -> 'memories_{project_root_name}' (idempotent)."
    )
    parser.add_argument(
        "--root", default=None,
        help="Project root (default: auto from script location AGENT/scripts/).",
    )
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve() if args.root else None
    result = rename_memories(root)
    print(f"[rename_memories] {result}")
    if root is None:
        _log(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
