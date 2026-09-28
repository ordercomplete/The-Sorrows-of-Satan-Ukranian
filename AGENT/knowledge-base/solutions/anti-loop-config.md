### Налаштування anti_loop.py для small-steps підходу
**Дата:** 2026-07-31 15:00
**Контекст:** `AGENT/scripts/anti_loop.py` — хук проти циклів, який блокує повторювані виклики tool.
**Рішення:** збільшила пороги для сумісності з small-steps підходом:
- WINDOW_SIZE: 16 → 24 (багато дрібних кроків)
- EXACT_REPEAT_LIMIT: 3 → 5 (read→edit→verify не блокується)
- SAME_TARGET_LIMIT: 4 → 7 (один файл: прочитала→відредагувала→перевірила = нормально)
- OSCILLATION_LIMIT: 4 → 6 (A-B-A-B має бути справжнім циклом)
- TOOL_FLOOD_LIMIT: 7 → 10 (small-steps робить багато викликів одного tool)
- NO_PROGRESS_WINDOW: 8 → 12 (за 8 кроків small-steps може зробити одну задачу)
**Джерело:** власний аналіз протиріч між small-steps і anti_loop.py
