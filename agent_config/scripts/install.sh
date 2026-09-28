#!/bin/bash
# install.sh — Повна установка Comfy-smart-lady-agent у поточний проєкт.
#
# Використання:
#   bash install.sh [URL_репозиторію]
#
# Що робить:
#   1. Клонує центральне репо у тимчасову папку
#   2. Копіює канонічне ядро AGENT/ у цільовий проєкт
#   3. Показує dry-run синхронізації
#   4. Застосовує синхронізацію (.github/, .clinerules/, .opencode/)
#   5. Запускає перевірки (py_compile)
#   6. Прибирає тимчасові файли

set -euo pipefail

REPO_URL="${1:-https://github.com/ordercomplete/Comfy-smart-lady-agent.git}"
TARGET_DIR="."
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

echo "🚀 Інсталяція Comfy-smart-lady-agent..."
echo "   Джерело: $REPO_URL"
echo "   Цільова директорія: $(pwd)"

# Перевірка залежностей
command -v git >/dev/null 2>&1 || { echo "❌ git не знайдено"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ python3 не знайдено"; exit 1; }

# 1. Клонувати центральне репо (поверхневий клон — швидше)
echo ""
echo "📥 Крок 1/5: Клонування центрального репозиторію..."
git clone --depth 1 "$REPO_URL" "$TMP_DIR/csl"

# 2. Ядро AGENT/ тепер розгортає sync-agent.py --apply (Крок 4), тож тут не дублюємо.
echo ""
echo "📦 Крок 2/5: Ядро AGENT/ буде розгорнуто синхронізацією (Крок 4)..."

# 3. Dry-run — показати що зміниться
echo ""
echo "🔍 Крок 3/5: Dry-run синхронізації..."
python3 "$TMP_DIR/csl/agent_config/scripts/sync-agent.py" --source "$TMP_DIR/csl" --target "$TARGET_DIR" --dry-run

# 4. Застосувати синхронізацію
echo ""
echo "⚙️  Крок 4/5: Застосування синхронізації..."
python3 "$TMP_DIR/csl/agent_config/scripts/sync-agent.py" --source "$TMP_DIR/csl" --target "$TARGET_DIR" --apply

# 4.5. Перейменовуємо memories -> memories_{project_root} (ідемпотентно)
echo "   🗂️  namespacing memories/ -> memories_{project_root} ..."
python3 "$TARGET_DIR/AGENT/scripts/rename_memories.py"

# 5. Перевірки
echo ""
echo "🧪 Крок 5/5: Перевірка встановлення..."
python3 -m py_compile ./AGENT/scripts/anti_loop.py ./AGENT/scripts/watch_agent_file.py ./AGENT/scripts/str.translate.py && echo "   ✅ core скрипти компілюються"
[ -f ./AGENT/scripts/anti_loop.py ] && echo "   ✅ AGENT/scripts/anti_loop.py на місці"
[ -f ./.clinerules/hooks/Loops.json ] && echo "   ✅ .clinerules/hooks/Loops.json на місці"
[ -f ./.opencode/plugins/anti-loop.js ] || echo "   ⚠️  .opencode/plugins/anti-loop.js відсутній (скопіюйте вручну з центрального репо)"

# Додаткова перевірка (крок 5/5): agent-lock.json та команда status
[ -f ./agent-lock.json ] && echo "   ✅ agent-lock.json створено" || echo "   ⚠️  agent-lock.json відсутній"
echo "   📋 Стан Агента (sync-agent.py status):"
python3 agent_config/scripts/sync-agent.py status

echo ""
echo "✅ Успішно встановлено!"
echo "   Наступні кроки:"
echo "   - Додайте opencode.json у корінь проєкту (якщо використовуєте OpenCode)"
echo "   - Об'єднайте .gitignore з правилами центрального репо"
