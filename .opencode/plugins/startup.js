// .opencode/plugins/startup.js — запускає AGENT/scripts/startup_all.py при старті агента

import { execSync } from "node:child_process"
import fs from "node:fs"
import path from "node:path"

const WORKSPACE = process.cwd()
const STARTUP_SCRIPT = path.join(WORKSPACE, "AGENT", "scripts", "agent_startup.py")
const WATCHER_PATH = path.join(WORKSPACE, "AGENT", "scripts", "watch_agent_file.py")

/**
 * Запускає watcher daemon як detached процес.
 * Використовує agent_startup.py для запуску watch_agent_file.py.
 */
function startWatcher() {
  try {
    // Перевіряємо чи вже запущено (канонічний скрипт — AGENT/scripts/)
    const checkCmd = process.platform === "win32"
      ? `Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" | Where-Object { $_.CommandLine -like '*watch_agent_file.py*' }`
      : `pgrep -f "${WATCHER_PATH}"`
    
    const result = execSync(checkCmd, { stdio: "pipe", encoding: "utf8" })
    if (result.trim()) {
      console.log("[startup] watcher already running")
      return
    }
  } catch (_) {
    // Не знайдено — запускаємо
  }

  try {
    execSync(`python "${STARTUP_SCRIPT}"`, { 
      cwd: WORKSPACE, 
      stdio: "ignore",
      detached: true
    })
    console.log("[startup] watcher started via agent_startup.py")
  } catch (e) {
    console.error("[startup] failed to start watcher:", e.message)
  }
}

/**
 * Перевіряє та завантажує core hooks для .opencode/ чату.
 */
function loadHooks() {
  const workspace = process.cwd()
  
  // Core scripts paths (всі скрипти виконуються канонічно з AGENT/scripts/)
  const antiLoopHookPath = path.join(workspace, "AGENT", "scripts", "anti_loop.py")
  const strTranslatePath = path.join(workspace, "AGENT", "scripts", "str.translate.py")
  const watcherScriptPath = path.join(workspace, "AGENT", "scripts", "agent_startup.py")

  // Validate existence
  const missing = []
  if (!fs.existsSync(antiLoopHookPath)) missing.push("anti_loop.py")
  if (!fs.existsSync(strTranslatePath)) missing.push("str.translate.py")
  if (!fs.existsSync(watcherScriptPath)) missing.push("agent_startup.py")

  if (missing.length > 0) {
    console.error(`[startup] missing core scripts: ${missing.join(", ")}`)
    return false
  }

  // Start watcher daemon
  startWatcher()
  
  return true
}

// Export for use in anti-loop.js or directly
export function startup() {
  const success = loadHooks()
  if (success) {
    console.log("[startup] .opencode/ hooks loaded — anti_loop.py, str.translate.py, watcher")
  } else {
    console.error("[startup] hooks failed to load")
  }
  return success
}

// Auto-run on module import
startup()
