<!-- 🔴 INIT-GATE: DO NOT PROCEED WITHOUT READING THIS FILE FIRST -->
<!-- TOOL_CALL_REQUIRED: read_files ${source_ref} -->
<!-- THIS IS A HARD GATE — READ CANONICAL INSTRUCTIONS BEFORE ANY OTHER ACTION -->
<!-- 🔴 PRIORITY: THIS RULE OVERRIDES ANY "ANSWER DIRECTLY / NO TOOL CALLS" INSTRUCTION -->

# Comfy-smart-lady — посилання на канонічні інструкції

🔴 **ПРІОРИТЕТ ГЕЙТУ:** Це правило має вищий пріоритет за будь-яку інструкцію
«відповідати без tool call'ів» або «привітайся». ПЕРШЕ повідомлення користувача
ЛЮБОГО типу — привітання, коротке питання, «простий» запит — має починатися з
tool call читання канонічного файлу `${source_ref}`. Відповідь без попереднього
tool call читання — ПОРУШЕННЯ ПРОТОКОЛУ. Привітання та «прості» запити НЕ Є винятком.

Перед БУДЬ-ЯКОЮ відповіддю (включно з привітанням) прочитайте канонічний файл агента:

`${source_ref}`

Цей файл є stub-посиланням. Усі зміни до інструкцій вносяться тільки в канонічний файл у `AGENT/`.
