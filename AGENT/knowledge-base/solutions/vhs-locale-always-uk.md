### VHS переклад показувався при будь-якій мові через відсутній return 'en'
**Дата:** 2026-08-03 19:33
**Контекст:** `custom_nodes/comfyui-videohelpersuite/web/js/VHS.settings.js`, функція `getVHSLocale()`
**Рішення/Патерн:**
- Проблема: `getVHSLocale()` перевіряв тільки `if (lang === 'uk' || lang?.startsWith('uk')) return 'uk';` — при `lang === 'en'` не було `return`, тому функція падала до `navigator.language` (мова браузера). Якщо браузер український → завжди повертала 'uk' при будь-якій мові ComfyUI.
- Правильний патерн (як у LoRA Manager `getLoraManagerLocale()`):
  1. Найвищий пріоритет: `app.ui.settings.getSettingValue('Comfy.Locale')`
  2. Fallback: `app.extensionManager.setting.get('Comfy.Locale')`
  3. ОБОВ'ЯЗКОВО: `if (lang === 'en') return 'en';` після перевірки 'uk'
  4. Останній fallback: `navigator.language`
- Для DOM override: при locale='en' треба явно повертати англійські назви (`ENGLISH_NAMES`/`ENGLISH_TOOLTIPS`), інакше раніше застосований український текст не відновиться.
**Джерело:** лог консолі браузера — LoRA Manager/TTS/rgthree бачили зміну 'uk'→'en', VHS логувала тільки `[VHS] English/Ukrainian translations loaded`
