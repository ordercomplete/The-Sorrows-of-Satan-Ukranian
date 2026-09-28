# Механічні цикли EXACT REPEAT (reset→repeat→reset) — 2026-08-14 16:30
**Контекст:** `AGENT/scripts/anti_loop.py`, детекція EXACT REPEAT

**Проблема:** `EXACT_REPEAT_LIMIT = 5` + `RESET_ON_LOOP = True` створювали механічне коло. Після reset state очищується, agent повторює той самий tool call → знову 4 виклики → знову спрацьовує EXACT REPEAT → знову reset. Цикли кожні 20-40 секунд.

**Рішення (вже застосовано):**
1. `EXACT_REPEAT_LIMIT` збільшено з **5 до 8** — agent має більше простору для дій перед reset
2. Додано **cooldown 60 сек** між спрацюваннями одного tool — запобігає механічним циклам
3. Додано відстеження `last_exact_reset` timestamp в state

**Дані:** error-log показував цикли #2-#9 (tools read/edit) кожні 20-40 сек, всі з exact_count = 4.
