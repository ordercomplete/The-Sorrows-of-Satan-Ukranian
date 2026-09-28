"""Ручна ротація знімків AGENT/ — тримає щонайбільше MAX_BACKUPS архівів.

Корекції:
- Шлях до backup-agent/ визначається від розташування самого скрипта
  (agent_config/scripts/), а не від поточної директорії запуску — раніше
  запуск не з кореня workspace не знаходив жодного архіву.
- Сортування за ім'ям (таймстамп у назві AGENT_YYYY-MM-DD_HH-MM-SS),
  а не за mtime: sync-agent.py копіює знімки між workspace-ами і скидає
  mtime, через що порядок "найстаріших" був непередбачуваний.
"""
from pathlib import Path
import shutil
import time

SCRIPT_DIR = Path(__file__).resolve().parent        # agent_config/scripts/
BACKUP_DIR = SCRIPT_DIR.parent / "backup-agent"     # agent_config/backup-agent/
CHAT_DIR = SCRIPT_DIR.parent / "backup-chat"        # agent_config/backup-chat/
MAX_BACKUPS = 3  # Ліміт і для backup-agent/*.zip, і для папок backup-chat/ (рішення 2026-09-28: 10 -> 3)

files = sorted(BACKUP_DIR.glob("AGENT_*.zip"), key=lambda p: p.name, reverse=True)
to_delete = files[MAX_BACKUPS:]

if not files:
    print(f"Знімків не знайдено у: {BACKUP_DIR}")

for f in to_delete:
    for attempt in range(5):
        try:
            time.sleep(2)
            f.unlink()
            print(f"Видалено: {f.name}")
            break
        except OSError as e:
            print(f"Спроба {attempt+1}/5 помилка для {f.name}: {e}")

remaining = len(list(BACKUP_DIR.glob("AGENT_*.zip")))
print(f"\nЗалишилось архівів: {remaining} (ліміт: {MAX_BACKUPS})")

# --- Ротація папок backup-chat (backup_YYYY-MM-DD_HH-MM-SS) ---
# Той самий механізм, що й для AGENT_*.zip: сортування за ім'ям,
# бо sync-agent.py скидає mtime при копіюванні папок між workspace-ами.
chat_folders = sorted(
    (p for p in CHAT_DIR.iterdir() if p.is_dir() and p.name.startswith("backup_")),
    key=lambda p: p.name,
    reverse=True,
) if CHAT_DIR.is_dir() else []

for d in chat_folders[MAX_BACKUPS:]:
    for attempt in range(5):
        try:
            time.sleep(2)
            shutil.rmtree(d)
            print(f"Видалено chat-бекап: {d.name}")
            break
        except OSError as e:
            print(f"Спроба {attempt+1}/5 помилка для {d.name}: {e}")

remaining_chat = len([p for p in CHAT_DIR.iterdir() if p.is_dir() and p.name.startswith("backup_")]) if CHAT_DIR.is_dir() else 0
print(f"Залишилось chat-бекапів: {remaining_chat} (ліміт: {MAX_BACKUPS})")
