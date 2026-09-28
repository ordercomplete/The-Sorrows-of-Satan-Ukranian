from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AGENT_DIR = ROOT / "AGENT"
OUTPUT = AGENT_DIR / "agent-catalog.html"


def read_markdown(path: Path) -> str:
    raw = path.read_bytes()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp1251", errors="replace")


def title_from_markdown(path: Path) -> str:
  lines = read_markdown(path).splitlines()
  for line in lines:
    if line.startswith("# "):
      return line[2:].strip().replace("#", "")
  return path.stem.replace("_", " ").replace("-", " ").title()


def document_group(relative: str) -> str:
    if relative.startswith("docs/"):
        return "Документація"
    if relative.startswith("templates/"):
        return "Шаблони"
    if relative.startswith("memories/"):
        return "Проєкт memories"
    if relative.startswith("chats/"):
        return "Платформи"
    if relative.startswith("skills/"):
        return "Навички"
    if relative.startswith("knowledge-base/"):
        return "База знань"
    if relative.startswith("memories_agent/"):
        return "Внутрішня пам'ять"
    if relative.startswith("agents/"):
        return "Інструкції агента"
    if "/" not in relative:
        return "Файли кореня"
    return "Документація"


def collect_documents() -> list[dict[str, str]]:
    documents = []
    sources = (
      (AGENT_DIR, ""),
      (ROOT / "memories", "memories/"),
      (ROOT / "docs", "docs/"),
      (ROOT / "templates", "templates/"),
    )
    root_files = sorted(ROOT.glob("*.md"))
    for path in root_files:
      documents.append(
        {
          "path": path.name,
          "title": title_from_markdown(path),
          "group": document_group(path.name),
          "content": read_markdown(path),
        }
      )
    for base_dir, path_prefix in sources:
        if not base_dir.exists():
            continue
        for path in sorted(base_dir.rglob("*.md")):
            relative = path_prefix + path.relative_to(base_dir).as_posix()
            documents.append(
                {
                    "path": relative,
                    "title": title_from_markdown(path),
                    "group": document_group(relative),
                    "content": read_markdown(path),
                }
            )
    return documents


def build_html(documents: list[dict[str, str]]) -> str:
    payload = json.dumps(documents, ensure_ascii=False).replace("</", "<\\/")
    generated = "2026-08-22"
    return f'''<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Comfy-smart-lady | Каталог агента</title>
  <style>
    :root {{
      --ink: #17211b; --muted: #657268; --paper: #f4f1e8; --panel: #fffdf7;
      --line: #d9d4c7; --accent: #cc4b2c; --accent-dark: #96341f; --sage: #315c4b;
      --shadow: 0 18px 45px rgba(43, 42, 31, .10);
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; color: var(--ink); background: var(--paper); font-family: Georgia, 'Times New Roman', serif; }}
    button, input {{ font: inherit; }}
    .shell {{ display: grid; grid-template-columns: 310px minmax(0, 1fr); min-height: 100vh; }}
    aside {{ padding: 28px 20px; background: #21382f; color: #f6f0df; position: sticky; top: 0; height: 100vh; overflow: auto; }}
    .eyebrow {{ color: #f2a27f; font: 700 11px/1.2 'Trebuchet MS', sans-serif; letter-spacing: .12em; text-transform: uppercase; }}
    .brand {{ margin: 8px 0 6px; font-size: 29px; line-height: 1; }}
    .tagline {{ margin: 0 0 22px; color: #c5d4c6; font: 14px/1.45 'Trebuchet MS', sans-serif; }}
    .search {{ width: 100%; border: 1px solid #557260; border-radius: 5px; padding: 11px 12px; color: #f6f0df; background: #29473a; outline: none; }}
    .search:focus {{ border-color: #f2a27f; box-shadow: 0 0 0 3px rgba(242,162,127,.18); }}
    .rescan {{ width: 100%; margin-top: 8px; border: 1px solid #f2a27f; border-radius: 3px; padding: 9px 12px; color: #fff; background: transparent; cursor: pointer; font: 700 12px 'Trebuchet MS', sans-serif; }}
    .rescan:hover {{ color: #21382f; background: #f2a27f; }}
    .rescan-status {{ min-height: 16px; margin: 7px 0 0; color: #b7c8b9; font: 11px/1.3 'Trebuchet MS', sans-serif; }}
    .stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 18px 0 26px; }}
    .stat {{ padding: 10px; border-top: 1px solid #557260; }}
    .stat strong {{ display: block; font-size: 23px; }} .stat span {{ color: #b7c8b9; font: 11px 'Trebuchet MS', sans-serif; }}
    nav h2 {{ margin: 20px 0 7px; color: #f2a27f; font: 700 11px 'Trebuchet MS', sans-serif; letter-spacing: .1em; text-transform: uppercase; }}
    nav button {{ display: block; width: 100%; border: 0; border-left: 2px solid transparent; padding: 7px 9px; text-align: left; color: #d5e0d5; background: transparent; cursor: pointer; font: 13px/1.25 'Trebuchet MS', sans-serif; }}
    nav button:hover, nav button.active {{ border-left-color: #f2a27f; color: #fff; background: rgba(255,255,255,.08); }}
    main {{ min-width: 0; padding: 46px clamp(24px, 6vw, 92px) 70px; }}
    .hero {{ max-width: 920px; margin-bottom: 34px; }}
    .hero h1 {{ max-width: 800px; margin: 10px 0 12px; font-size: clamp(38px, 6vw, 72px); line-height: .98; font-weight: 400; }}
    .hero p {{ max-width: 680px; margin: 0; color: var(--muted); font: 16px/1.55 'Trebuchet MS', sans-serif; }}
    .toolbar {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 25px 0 30px; }}
    .filter {{ border: 1px solid var(--line); border-radius: 3px; padding: 8px 12px; color: var(--sage); background: var(--panel); cursor: pointer; font: 12px 'Trebuchet MS', sans-serif; }}
    .filter.active, .filter:hover {{ border-color: var(--accent); color: white; background: var(--accent); }}
    .catalog {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; max-width: 1080px; }}
    .card {{ min-height: 146px; padding: 19px; border: 1px solid var(--line); border-top: 4px solid var(--sage); background: var(--panel); box-shadow: 0 7px 20px rgba(43,42,31,.04); cursor: pointer; transition: transform .18s ease, box-shadow .18s ease; }}
    .card:hover {{ transform: translateY(-3px); box-shadow: var(--shadow); }}
    .card.platform {{ border-top-color: var(--accent); }}
    .card small {{ color: var(--muted); font: 11px 'Trebuchet MS', sans-serif; }}
    .card h2 {{ margin: 12px 0 8px; font-size: 22px; font-weight: 400; }}
    .card p {{ margin: 0; color: var(--muted); font: 12px/1.4 'Trebuchet MS', sans-serif; word-break: break-word; }}
    .reader {{ display: none; max-width: 900px; }}
    .reader.visible {{ display: block; animation: appear .28s ease both; }}
    .back {{ border: 0; padding: 0; color: var(--accent-dark); background: transparent; cursor: pointer; font: 700 12px 'Trebuchet MS', sans-serif; }}
    .reader-meta {{ margin: 22px 0 30px; color: var(--muted); font: 12px 'Trebuchet MS', sans-serif; }}
    .markdown {{ padding: clamp(22px, 4vw, 52px); border: 1px solid var(--line); background: var(--panel); box-shadow: var(--shadow); overflow-wrap: anywhere; }}
    .markdown h1, .markdown h2, .markdown h3, .markdown h4 {{ color: var(--sage); line-height: 1.1; }}
    .markdown h1 {{ margin-top: 0; font-size: clamp(30px, 5vw, 52px); font-weight: 400; }}
    .markdown h2 {{ margin-top: 32px; font-size: 30px; font-weight: 400; border-bottom: 1px solid var(--line); padding-bottom: 8px; }}
    .markdown h3 {{ margin-top: 25px; font-size: 22px; }}
    .markdown p, .markdown li {{ font-size: 16px; line-height: 1.65; }}
    .markdown blockquote {{ margin: 20px 0; padding: 12px 18px; border-left: 4px solid var(--accent); background: #f8eadf; color: #5a4035; }}
    .markdown code {{ padding: 2px 5px; color: #8e321e; background: #f1e9dc; font: 13px Consolas, monospace; }}
    .markdown pre {{ overflow: auto; padding: 17px; background: #1c2923; color: #e7efe2; }}
    .markdown pre code {{ padding: 0; color: inherit; background: transparent; }}
    .markdown table {{ width: 100%; border-collapse: collapse; display: block; overflow-x: auto; }}
    .markdown th, .markdown td {{ min-width: 110px; padding: 9px 11px; border: 1px solid var(--line); text-align: left; vertical-align: top; }}
    .markdown th {{ color: var(--sage); background: #edf0e8; }}
    .markdown a {{ color: var(--accent-dark); }}
    .empty {{ color: var(--muted); font: 15px 'Trebuchet MS', sans-serif; }}
    @keyframes appear {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}
    @media (max-width: 760px) {{ .shell {{ display: block; }} aside {{ position: relative; height: auto; }} main {{ padding: 32px 18px 50px; }} .stats {{ max-width: 330px; }} }}
  </style>
</head>
<body>
  <div class="shell">
    <aside>
      <div class="eyebrow">Agent registry / {generated}</div>
      <div class="brand">Comfy-smart-lady</div>
      <p class="tagline">Візуальний каталог інтеграцій, навичок і внутрішньої документації агента.</p>
      <input id="search" class="search" type="search" placeholder="Пошук у каталозі..." aria-label="Пошук у каталозі">
      <button id="rescan" class="rescan" type="button">↻ Пересканувати матеріали</button>
      <p id="rescan-status" class="rescan-status" aria-live="polite"></p>
      <div class="stats"><div class="stat"><strong id="doc-count">0</strong><span>MD-файлів</span></div><div class="stat"><strong id="platform-count">0</strong><span>платформ</span></div></div>
      <nav id="nav"></nav>
    </aside>
    <main>
      <section id="overview">
        <div class="hero"><div class="eyebrow">Єдине джерело істини: AGENT/</div><h1>Усе, що знає й уміє агент.</h1><p>Натисніть на картку, щоб відкрити відформатований Markdown. Пошук працює по назвах, шляхах і вмісту документів.</p></div>
        <div id="filters" class="toolbar"></div>
        <div id="catalog" class="catalog"></div>
      </section>
      <section id="reader" class="reader"><button id="back" class="back">← До каталогу</button><div id="reader-meta" class="reader-meta"></div><article id="markdown" class="markdown"></article></section>
    </main>
  </div>
  <script>
    let documents = {payload};
    const state = {{ query: '', group: 'Усі', selected: null }};
    let groups = ['Усі', ...new Set(documents.map(doc => doc.group))];
    const nav = document.querySelector('#nav');
    const catalog = document.querySelector('#catalog');
    const filters = document.querySelector('#filters');
    const search = document.querySelector('#search');
    const overview = document.querySelector('#overview');
    const reader = document.querySelector('#reader');
    const markdown = document.querySelector('#markdown');
    const readerMeta = document.querySelector('#reader-meta');
    const rescanStatus = document.querySelector('#rescan-status');
    const rootHandleKey = 'project-root-v2';

    function escapeHtml(value) {{ return value.replace(/[&<>"']/g, char => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[char])); }}
    function inline(value) {{
      let safe = escapeHtml(value);
      safe = safe.replace(/`([^`]+)`/g, '<code>$1</code>');
      safe = safe.replace(/!\\[([^]]*)\\]\\(([^)]+)\\)/g, '<img alt="$1" src="$2">');
      safe = safe.replace(/\\[([^]]+)\\]\\((https?:\\/\\/[^)]+)\\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>');
      safe = safe.replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>').replace(/__([^_]+)__/g, '<strong>$1</strong>');
      safe = safe.replace(/\\*([^*]+)\\*/g, '<em>$1</em>');
      return safe;
    }}
    function titleFromContent(content, path) {{ const heading = content.split(/\\r?\\n/).find(line => line.startsWith('# ')); return heading ? heading.slice(2).replace(/#/g, '').trim() : path.split('/').pop().replace(/[-_]/g, ' '); }}
    function groupFromPath(path) {{ if (path.startsWith('docs/')) return 'Документація'; if (path.startsWith('templates/')) return 'Шаблони'; if (path.startsWith('memories/')) return 'Проєкт memories'; if (path.startsWith('chats/')) return 'Платформи'; if (path.startsWith('skills/')) return 'Навички'; if (path.startsWith('knowledge-base/')) return 'База знань'; if (path.startsWith('memories_agent/')) return "Внутрішня пам'ять"; if (path.startsWith('agents/')) return 'Інструкції агента'; if (!path.includes('/')) return 'Файли кореня'; return 'Документація'; }}
    function openHandleStore() {{ return new Promise((resolve, reject) => {{ const request = indexedDB.open('comfy-smart-lady-catalog', 1); request.onupgradeneeded = () => request.result.createObjectStore('settings'); request.onsuccess = () => resolve(request.result); request.onerror = () => reject(request.error); }}); }}
    async function loadRootHandle() {{ try {{ const db = await openHandleStore(); return await new Promise((resolve, reject) => {{ const request = db.transaction('settings').objectStore('settings').get(rootHandleKey); request.onsuccess = () => resolve(request.result || null); request.onerror = () => reject(request.error); }}); }} catch (error) {{ return null; }} }}
    async function saveRootHandle(handle) {{ try {{ const db = await openHandleStore(); db.transaction('settings', 'readwrite').objectStore('settings').put(handle, rootHandleKey); }} catch (error) {{ void error; }} }}
    async function scanDirectory(handle, prefix, result) {{ for await (const [name, entry] of handle.entries()) {{ const path = prefix + name; if (entry.kind === 'directory') await scanDirectory(entry, path + '/', result); else if (entry.kind === 'file' && name.toLowerCase().endsWith('.md')) {{ const content = await (await entry.getFile()).text(); result.push({{ path, title: titleFromContent(content, path), group: groupFromPath(path), content }}); }} }} }}
    async function scanProjectRoot(handle, result) {{
      let foundSource = false;
      for (const name of ['AGENT', 'memories', 'docs', 'templates']) {{
        try {{ const directory = await handle.getDirectoryHandle(name); await scanDirectory(directory, name === 'AGENT' ? '' : name + '/', result); foundSource = true; }} catch (error) {{ void error; }}
      }}
      for await (const [name, entry] of handle.entries()) {{ if (entry.kind === 'file' && name.toLowerCase().endsWith('.md')) {{ const content = await (await entry.getFile()).text(); result.push({{ path: name, title: titleFromContent(content, name), group: groupFromPath(name), content }}); }} }}
      if (!foundSource && !result.length) await scanDirectory(handle, '', result);
    }}
    async function rescanMaterials() {{
      if (!window.showDirectoryPicker) {{ rescanStatus.textContent = 'Цей браузер не підтримує ресканування. Запустіть open-agent-catalog.bat.'; return; }}
      try {{
        let root = await loadRootHandle();
        if (root && (await root.queryPermission({{ mode: 'read' }})) !== 'granted' && (await root.requestPermission({{ mode: 'read' }})) !== 'granted') root = null;
        if (!root) {{ rescanStatus.textContent = 'Виберіть кореневу папку проєкту...'; root = await window.showDirectoryPicker({{ mode: 'read' }}); await saveRootHandle(root); }}
        rescanStatus.textContent = 'Сканування AGENT і memories...'; const scanned = []; await scanProjectRoot(root, scanned);
        if (!scanned.length) {{ rescanStatus.textContent = 'У вибраній папці не знайдено MD-файлів.'; return; }}
        documents = scanned.sort((left, right) => left.path.localeCompare(right.path)); groups = ['Усі', ...new Set(documents.map(doc => doc.group))]; state.group = 'Усі'; state.selected = null; rescanStatus.textContent = 'Оновлено з кореня проєкту: ' + documents.length + ' MD-файлів'; renderNav(); render(); closeDocument();
      }} catch (error) {{ if (error.name !== 'AbortError') rescanStatus.textContent = 'Не вдалося прочитати вибрану папку.'; }}
    }}
    function renderMarkdown(source) {{
      const lines = source.replace(/\\r/g, '').split('\\n'); let out = '', inCode = false, code = '', list = false, quote = false, table = false;
      const closeList = () => {{ if (list) {{ out += '</ul>'; list = false; }} }};
      const closeQuote = () => {{ if (quote) {{ out += '</blockquote>'; quote = false; }} }};
      const closeTable = () => {{ if (table) {{ out += '</tbody></table>'; table = false; }} }};
      for (const line of lines) {{
        if (line.startsWith('```')) {{ if (inCode) {{ out += '<pre><code>' + escapeHtml(code.slice(0, -1)) + '</code></pre>'; code = ''; inCode = false; }} else {{ closeList(); closeQuote(); closeTable(); inCode = true; }} continue; }}
        if (inCode) {{ code += line + '\\n'; continue; }}
        if (/^\\|.*\\|$/.test(line)) {{
          const cells = line.split('|').slice(1, -1).map(cell => cell.trim());
          if (/^[-: ]+$/.test(cells[0] || '')) continue;
          if (!table) {{ closeList(); closeQuote(); table = true; out += '<table><thead><tr>' + cells.map(cell => '<th>' + inline(cell) + '</th>').join('') + '</tr></thead><tbody>'; }} else out += '<tr>' + cells.map(cell => '<td>' + inline(cell) + '</td>').join('') + '</tr>';
          continue;
        }} else closeTable();
        const heading = line.match(/^(#{1,4})\\s+(.+)/); if (heading) {{ closeList(); closeQuote(); out += '<h' + heading[1].length + '>' + inline(heading[2]) + '</h' + heading[1].length + '>'; continue; }}
        if (/^>\\s?/.test(line)) {{ closeList(); if (!quote) {{ out += '<blockquote>'; quote = true; }} out += '<p>' + inline(line.replace(/^>\\s?/, '')) + '</p>'; continue; }} else closeQuote();
        const item = line.match(/^\\s*[-*+]\\s+(.+)/); if (item) {{ if (!list) {{ closeQuote(); out += '<ul>'; list = true; }} out += '<li>' + inline(item[1]) + '</li>'; continue; }} else closeList();
        if (/^---+$/.test(line.trim())) {{ out += '<hr>'; continue; }}
        if (line.trim()) out += '<p>' + inline(line) + '</p>';
      }}
      closeList(); closeQuote(); closeTable(); if (inCode) out += '<pre><code>' + escapeHtml(code) + '</code></pre>'; return out;
    }}
    function matches(doc) {{ const haystack = (doc.title + ' ' + doc.path + ' ' + doc.content).toLowerCase(); return (state.group === 'Усі' || doc.group === state.group) && haystack.includes(state.query.toLowerCase()); }}
    function renderNav() {{ nav.innerHTML = groups.slice(1).map(group => '<h2>' + group + '</h2>' + documents.filter(doc => doc.group === group).map(doc => '<button data-path="' + escapeHtml(doc.path) + '">' + escapeHtml(doc.title) + '</button>').join('')).join(''); nav.querySelectorAll('button').forEach(button => button.onclick = () => openDocument(button.dataset.path)); }}
    function renderFilters() {{ filters.innerHTML = groups.map(group => '<button class="filter ' + (group === state.group ? 'active' : '') + '" data-group="' + escapeHtml(group) + '">' + escapeHtml(group) + '</button>').join(''); filters.querySelectorAll('button').forEach(button => button.onclick = () => {{ state.group = button.dataset.group; render(); }}); }}
    function render() {{ const visible = documents.filter(matches); document.querySelector('#doc-count').textContent = documents.length; document.querySelector('#platform-count').textContent = documents.filter(doc => doc.group === 'Платформи').length; catalog.innerHTML = visible.length ? visible.map(doc => '<div class="card ' + (doc.group === 'Платформи' ? 'platform' : '') + '" data-path="' + escapeHtml(doc.path) + '"><small>' + escapeHtml(doc.group) + '</small><h2>' + escapeHtml(doc.title) + '</h2><p>' + escapeHtml(doc.path) + '</p></div>').join('') : '<p class="empty">Нічого не знайдено.</p>'; catalog.querySelectorAll('.card').forEach(card => card.onclick = () => openDocument(card.dataset.path)); renderFilters(); }}
    function openDocument(path) {{ const doc = documents.find(item => item.path === path); if (!doc) return; state.selected = path; overview.style.display = 'none'; reader.classList.add('visible'); readerMeta.textContent = doc.group + ' / ' + doc.path; markdown.innerHTML = renderMarkdown(doc.content); history.replaceState(null, '', '#' + encodeURIComponent(path)); window.scrollTo({{ top: 0, behavior: 'smooth' }}); }}
    function closeDocument() {{ state.selected = null; reader.classList.remove('visible'); overview.style.display = ''; history.replaceState(null, '', location.pathname); }}
    search.oninput = event => {{ state.query = event.target.value; render(); }}; document.querySelector('#rescan').onclick = rescanMaterials; document.querySelector('#back').onclick = closeDocument; window.onpopstate = closeDocument;
    renderNav(); render(); const initial = decodeURIComponent(location.hash.slice(1)); if (initial) openDocument(initial);
  </script>
</body>
</html>'''


def main() -> None:
    documents = collect_documents()
    OUTPUT.write_text(build_html(documents), encoding="utf-8")
    print(f"Згенеровано {OUTPUT} ({len(documents)} Markdown-файлів)")


if __name__ == "__main__":
    main()
