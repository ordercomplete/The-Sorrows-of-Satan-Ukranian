# Автоматичний перезапуск чату після помилки Vercel AI Gateway

**Мета:** Після помилок `"Failed to create stream: inference request failed: ..."`, система автоматично перезавантажує потік або перемикає на фолбек-модель без втручання користувача.

---

## План реалізації з трьох варіантів

### 🎯 Варіант 1 — Обгортка потоку з колбеком помилки

**Пріоритет:** 🥇 Швидкий MVP  
**Оцінка часу:** ~2-3 години  

#### Крок 1.1: Створити `AutoRestartStreamClient.ts`

**Файл:** `.opencode/src/utils/AutoRestartStreamClient.ts`

```typescript
// Інтерфейс опцій
interface AutoRestartOptions {
    modelId: string;
    maxAttempts: number;          // скільки разів робити спробу перед фолбеком
    initialDelayMs: number;       // початкова затримка між повторами (default 3000)
    maxDelayMs: number;           // капіт затримки в мілісекундах (default 30000)
    exponentialBase?: number;     // множник backoff (default 2.0)
    onStreamStart?: () => void;   // колбек перед кожним новим потоком
    onStreamError?: (attempt: number, error: Error) => void;
    onMaxAttemptsReached?: (finalError: Error) => void;
}

class AutoRestartStreamClient {
    private createSseClient: () => AsyncGenerator<string, never, unknown>;
    private options: AutoRestartOptions;

    constructor(createSseClient: () => AsyncGenerator, opts: Partial<AutoRestartOptions> = {}) {
        this.createSseClient = createSseClient;
        this.options = {
            maxAttempts: 3,
            initialDelayMs: 3000,
            maxDelayMs: 30000,
            exponentialBase: 2.0,
            ...opts
        };
    }

    public createAutoStream(): AsyncGenerator<string> {
        let attempt = 0;
        
        const streamWithRetry = async function* () {
            while (attempt < this.options.maxAttempts) {
                try {
                    this.options.onStreamStart?.();
                    yield* this.createSseClient();
                    return; // успішно завершився без помилок
                } catch (error: any) {
                    const isStreamError = error.message?.includes('inference request failed') ||
                                          error.message?.includes('failed to send request');
                    
                    if (!isStreamError) throw error;

                    attempt++;
                    this.options.onStreamError?.(attempt, error);

                    if (attempt >= this.options.maxAttempts) {
                        this.options.onMaxAttemptsReached?.(error);
                        // Після останньої спроби: або кидаємо помилку, або перемикаємо модель
                        throw new Error(`Auto-restart exhausted after ${attempt} attempts`);
                    }

                    const delay = Math.min(
                        this.options.initialDelayMs * 
                            Math.pow(this.options.exponentialBase ?? 2.0, attempt - 1),
                        this.options.maxDelayMs
                    );
                    
                    await sleep(delay);
                }
            }
        };

        return streamWithRetry.call(this);
    }
}
```

#### Крок 1.2: Інтегрувати в `.opencode/src/client.ts`

Обгорнути виклик `createSseClient()` з обробником помилок, який логить спроби та запускає перезапуск.

**✅ Критерії успіху Варіанту 1:**

- [ ] Лог у консоль: `[AutoRestart] Attempt ${n}, delay ${delay}ms — restarting stream for model ${modelId}`  
- [ ] Після помилки Vercel AI Gateway потік автоматично перезапущений.
- [ ] Максимум 3 спроби з експоненціальним backoff (3000 → 6000 → 12000 мс).
- [ ] При `onMaxAttemptsReached` — чіткий лог: `[AutoRestart] Exhausted after N attempts. Fallback to model X`.

---

### 🎯 Варіант 2 — Конфігурація fallback-моделей через config-schema.json

**Пріоритет:** 🥈 Гнучкість, працює разом з варіантом 1  
**Оцінка часу:** ~1 година  

#### Крок 2.1: Розширити конфіг у `AGENT/chats/opencode/config-schema.json` (лінії 172-254)

```json
{
    "model": {
        "id": "private/longcat-2.0",
        "variant": "standard"
    },
    "provider": {
        "options": {
            "apiKey": "...",
            "baseURL": "...",
            "timeout": 60000,
            "chunkTimeout": 3000,
            
            // --- Нові поля для фолбек-логіки ---
            "fallbackModels": [
                "private/longcat-2.0",      // основна
                "vercel/gemini-1.5-pro",    // tier-1 fallback
                "anthropic/claude-3.7-sonnet"  // tier-2 fallback
            ],
            "streamFailureThreshold": 3,   // скільки помилок потоку перед перемиканням
            "resetConversationOnModelSwitch": true,
            "modelSwitchDelayMs": 5000     // затримка перед фолбеком у мс
        }
    }
}
```

#### Крок 2.2: Модифікувати `AutoRestartStreamClient` на підтримку fallbackModels

Додати логіку: після `maxAttempts` помилок потоку автоматично вибрати наступну модель із списку `fallbackModels` і перепідключити клієнт.

**✅ Критерії успіху Варіанту 2:**

- [ ] Конфіг читається динамічно без редагування коду.
- [ ] Після 3 помилок потоку — автоматичне перемикання на `fallbackModels[0]` → `fallbackModels[1]` і т.д.
- [ ] При успішному фолбеку чат-контекст скидається (за умови `resetConversationOnModelSwitch = true`).

---

### 🎯 Варіант 3 — Використовувати Effect SDK Schedule.exponential + retry

**Пріоритет:** 🥉 Найелегантніший, але потребує навичок Effect  
**Оцінка часу:** ~1 година  

#### Крок 3.1: Перейти на `Effect.retry` замість власного циклу

```typescript
import { Effect, Schedule, pipe } from 'effect';

const createStreamWithEffect = (modelId: string) => {
    const streamEffect = /* ваш Effect з fetch + SSE parsing */;
    
    // schedule.exponential(500, 1.5).pipe(Schedule.recurs(3))
    const retrySchedule = pipe(
        Schedule.exponential(500, 1.5),
        Schedule.both(Schedule.recurs(3)), // максимум 3 повторення
        Schedule.both(Schedule.jittered)   // додати випадковість у backoff
    );
    
    const retriedStream = Effect.retry(streamEffect, retrySchedule);
    
    return Effect.runSync(retriedStream.pipe(
        Effect.tapError((e) => 
            console.error(`[Effect Retry] Attempt failed: ${e.message}`)
        )
    ));
};
```

#### Крок 3.2: Поєднати з fallbackModels (варіант 2)

Effect не вміє сам перемикати моделі, тому треба обгорнути `streamEffect` у функцію, яка перемикає клієнт після кожної невдалої спроби.

**✅ Критерії успіху Варіанту 3:**

- [ ] Використано Effect SDK Schedule.exponential замість `Math.pow`.
- [ ] Backoff автоматично збільшується від 500 мс до максимуму.
- [ ] Можливе налаштування через конфіг (через параметри, що передаються в Effect).

---

## Матриця порівняння

| Варіант | Швидкість | Гнучкість | Інвезивність | Залежить від Effect SDK | Рекомендується для |
| --------- | ----------- | ----------- | -------------- | ------------------------ | --------------------- |
| 1 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | Ні | Швидкий прототип + MVP |
| 2 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Ні | Гнучка конфігу без коду |
| 3 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | Так | Команди, що вже використовують Effect |

---

## Перший крок: реалізувати Варіант 1 і перевірити

**Що робимо:**

1. Створюємо `AutoRestartStreamClient.ts` у `.opencode/src/utils/`.
2. Обгортаємо виклик `createSseClient()` з `maxAttempts = 3`, `initialDelayMs = 3000`.
3. Додаємо лог-колбек: `[AutoRestart] Attempt ${n}, delay ${delay}ms — restarting stream for model ${modelId}`.
4. Перевіряємо на реальній помилці Vercel AI Gateway — чи потік перезапущений автоматично?

**Мітка:** після завершення Варіанту 1 робимо демо-запит і показуємо лог. Якщо працює — переходимо до варіанту 2 (додавання fallbackModels).
