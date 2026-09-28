// .opencode/plugins/anti-loop.js
// Anti-loop hook: перехоплює tool call ДО виконання, передає дані в Python-скрипт

import { spawn } from "node:child_process"

export default async function AntiLoop() {
  return {
    "tool.execute.before": async (input, output) => {
      try {
        const workspace = process.cwd()
        const hookPath = `${workspace}/AGENT/scripts/anti_loop.py`

        // Формуємо дані для Python-скрипта
        const payload = {
          tool_name: input?.tool || "unknown",
          tool_input: input?.args || {},
        }

        const result = await new Promise((resolve) => {
          const child = spawn(
            "python",
            [hookPath],
            {
              cwd: workspace,
              stdio: ["pipe", "pipe", "ignore"],
              windowsHide: true,
            }
          )

          let stdout = ""
          child.stdout.on("data", (chunk) => {
            stdout += chunk.toString()
          })

          child.on("close", () => resolve(stdout))
          child.on("error", () => resolve("")) // не падаємо, якщо скрипт недоступний

          // Передаємо дані в stdin
          child.stdin.write(JSON.stringify(payload))
          child.stdin.end()
        })

        // Якщо Python-скрипт повернув рішення — застосовуємо
        if (result) {
          try {
            const decision = JSON.parse(result)
            const hookOutput = decision?.hookSpecificOutput
            if (hookOutput?.permissionDecision === "deny") {
              throw new Error(hookOutput.permissionDecisionReason || "Tool call blocked by anti-loop")
            }
            // Якщо allow + loopResetReason — виводимо повідомлення в чат
            if (hookOutput?.loopResetReason) {
              console.log(`[anti-loop] ${hookOutput.message || hookOutput.loopResetReason}`)
            }
          } catch (e) {
            if (e instanceof SyntaxError) {
              // Не JSON — ігноруємо
            } else {
              throw e
            }
          }
        }
      } catch (e) {
        // Якщо це наша помилка deny — пробрашуємо
        if (e?.message?.includes("anti-loop")) {
          throw e
        }
        // Інші помилки ігноруємо, щоб не ламати агента
      }
    },
  }
}