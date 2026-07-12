#!/usr/bin/env python3
"""Regenerate index.html from .html runbooks across the repo.

Reads <title> and <meta name="description"> from each runbook,
groups by top-level folder, sub-tag from the second-level folder.
Pure stdlib — runs on macOS-default Python 3 and ubuntu-latest.
"""
from __future__ import annotations

import html
import re
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CATEGORIES: dict[str, dict] = {
    "aix":       {"name": "AIX",       "accent": "aix",      "order": 1},
    "linux":     {"name": "Linux",     "accent": "linux",    "order": 2},
    "backup":    {"name": "Backup",    "accent": "backup",   "order": 3},
    "cohesity":  {"name": "Cohesity",  "accent": "cohesity", "order": 4},
    "reference": {"name": "Reference", "accent": "ref",      "order": 5},
    "vtl":       {"name": "VTL",       "accent": "vtl",      "order": 6},
    "security":  {"name": "Security",  "accent": "sec",      "order": 7},
}

# Categories with no real runbooks yet render a "coming soon" placeholder
# section instead. Placeholders are all-or-nothing per category: as soon as a
# category gains its first real page, build_section() takes over and the whole
# placeholder entry is ignored. Drop a category's entry once it has real
# content. Currently empty — every category has at least one runbook.
PLACEHOLDERS: dict[str, list[tuple[str, str, str]]] = {}

SKIP_DIRS  = {".git", ".github", "node_modules", "scripts", "docs", "_sandbox", "assets"}
SKIP_FILES = {"index.html"}

TITLE_RE = re.compile(r"<title>([\s\S]*?)</title>", re.IGNORECASE)
DESC_RE  = re.compile(
    r'<meta\s+name=["\']description["\']\s+content=["\']([\s\S]*?)["\']\s*/?>',
    re.IGNORECASE,
)
KW_RE = re.compile(
    r'<meta\s+name=["\']keywords["\']\s+content=["\']([\s\S]*?)["\']\s*/?>',
    re.IGNORECASE,
)


def walk_html_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.html"):
        if path.name in SKIP_FILES:
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts[:-1]):
            continue
        files.append(path)
    return files


def extract_meta(text: str) -> tuple[str | None, str | None, str]:
    t = TITLE_RE.search(text)
    d = DESC_RE.search(text)
    k = KW_RE.search(text)
    return (
        html.unescape(t.group(1).strip()) if t else None,
        html.unescape(d.group(1).strip()) if d else None,
        html.unescape(k.group(1).strip()) if k else "",
    )


def url_encode_path(rel: str) -> str:
    return "/".join(urllib.parse.quote(seg) for seg in rel.split("/"))


def fallback_title(rel: str) -> str:
    stem = Path(rel).stem
    return re.sub(r"\s+", " ", stem.replace("-", " ").replace("_", " ")).strip()


def build_card(entry: dict) -> str:
    accent = CATEGORIES.get(entry["category"], {}).get("accent", "sec")
    tag    = f'{entry["category"]} · {entry["sub_tag"]}' if entry["sub_tag"] else entry["category"]
    search = f'{entry["title"]} {tag} {entry["keywords"]} {Path(entry["rel_path"]).stem}'.lower()
    desc_html = f'\n        <p>{html.escape(entry["description"])}</p>' if entry["description"] else ""
    return (
        f'      <a class="card card-{accent}" href="{url_encode_path(entry["rel_path"])}" '
        f'data-search="{html.escape(search, quote=True)}">\n'
        f'        <div class="card-tag">{html.escape(tag)}</div>\n'
        f'        <h4>{html.escape(entry["title"])}</h4>{desc_html}\n'
        f'        <div class="card-foot"><span>{html.escape(Path(entry["rel_path"]).name)}</span>'
        f'<span class="arrow">→</span></div>\n'
        f'      </a>'
    )


def build_placeholder_card(cat_key: str, subdir: str, title: str, desc: str) -> str:
    accent = CATEGORIES.get(cat_key, {}).get("accent", "sec")
    tag    = f'{cat_key} · {subdir}'
    search = f'{title} {tag} {desc}'.lower()
    return (
        f'      <div class="card card-{accent} card-placeholder" '
        f'data-search="{html.escape(search, quote=True)}">\n'
        f'        <div class="card-tag">{html.escape(tag)}</div>\n'
        f'        <h4>{html.escape(title)}</h4>\n'
        f'        <p>{html.escape(desc)}</p>\n'
        f'        <div class="card-foot"><span>{html.escape(subdir)}/</span>'
        f'<span class="arrow">·</span></div>\n'
        f'      </div>'
    )


def build_placeholder_section(cat_key: str, cards_data: list[tuple[str, str, str]]) -> str:
    cat   = CATEGORIES.get(cat_key, {"name": cat_key.capitalize(), "accent": "sec"})
    cards = "\n".join(build_placeholder_card(cat_key, sub, title, desc) for sub, title, desc in cards_data)
    return (
        f'  <section class="section" data-cat="{cat_key}">\n'
        f'    <div class="section-head">\n'
        f'      <span class="accent accent-{cat["accent"]}"></span>\n'
        f'      <h3>{html.escape(cat["name"])}</h3>\n'
        f'      <span class="count">coming soon</span>\n'
        f'    </div>\n'
        f'    <div class="grid">\n'
        f'{cards}\n'
        f'    </div>\n'
        f'  </section>'
    )


def build_section(cat_key: str, entries: list[dict]) -> str:
    cat   = CATEGORIES.get(cat_key, {"name": cat_key.capitalize(), "accent": "sec"})
    count = f"{len(entries):02d}"
    noun  = "runbook" if len(entries) == 1 else "runbooks"
    cards = "\n".join(build_card(e) for e in entries)
    return (
        f'  <section class="section" data-cat="{cat_key}">\n'
        f'    <div class="section-head">\n'
        f'      <span class="accent accent-{cat["accent"]}"></span>\n'
        f'      <h3>{html.escape(cat["name"])}</h3>\n'
        f'      <span class="count">{count} {noun}</span>\n'
        f'    </div>\n'
        f'    <div class="grid">\n'
        f'{cards}\n'
        f'    </div>\n'
        f'  </section>'
    )


def main() -> None:
    files = walk_html_files(ROOT)
    entries: list[dict] = []
    for abs_path in files:
        rel = abs_path.relative_to(ROOT).as_posix()
        parts = rel.split("/")
        text = abs_path.read_text(encoding="utf-8", errors="replace")
        title, desc, kw = extract_meta(text)
        entries.append({
            "rel_path":    rel,
            "category":    parts[0],
            "sub_tag":     parts[1] if len(parts) > 2 else None,
            "title":       title or fallback_title(rel),
            "description": desc,
            "keywords":    kw,
        })

    grouped: dict[str, list[dict]] = {}
    for e in entries:
        grouped.setdefault(e["category"], []).append(e)
    for cat in grouped:
        grouped[cat].sort(key=lambda e: e["title"].lower())

    all_cat_keys = set(grouped.keys()) | set(PLACEHOLDERS.keys())
    sorted_cats = sorted(
        all_cat_keys,
        key=lambda c: (CATEGORIES.get(c, {}).get("order", 99), c),
    )

    section_blocks: list[str] = []
    for c in sorted_cats:
        if c in grouped:
            section_blocks.append(build_section(c, grouped[c]))
        else:
            section_blocks.append(build_placeholder_section(c, PLACEHOLDERS[c]))

    sections_html = "\n\n".join(section_blocks)
    total = len(entries)
    runbook_word = "RUNBOOK" if total == 1 else "RUNBOOKS"

    page = TEMPLATE.format(
        styles=STYLES,
        script=SCRIPT,
        sections=sections_html,
        total=total,
        runbook_word=runbook_word,
    )

    (ROOT / "index.html").write_text(page, encoding="utf-8")
    print(f"Wrote index.html — {total} runbooks across {len(sorted_cats)} categories: {', '.join(sorted_cats)}")


STYLES = """  :root {
    --paper:      #FAF6EE;
    --sidebar:    #F0E9DB;
    --surface:    #F6F0E4;
    --border:     #E0D7C6;
    --ink:        #2B2620;
    --ink-2:      #4A4234;
    --muted:      #6B6253;
    --faint:      #A09684;
    --ochre:      #9C7420;
    --ochre-tint: #F3EAD6;
    --ochre-bd:   #E6D8B8;
    --rust:       #A35A35;
    --sage:       #5F7038;
    --shadow:     0 2px 10px rgba(43, 38, 32, .07);
    --header-h:   56px;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--paper);
    color: var(--ink-2);
    font-family: 'Public Sans', system-ui, sans-serif;
    font-size: 13px;
    line-height: 1.55;
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
  }

  a { color: inherit; text-decoration: none; }

  header {
    height: var(--header-h);
    background: rgba(250, 246, 238, .85);
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    padding: 0 32px;
    gap: 12px;
    position: sticky;
    top: 0;
    z-index: 100;
    backdrop-filter: blur(8px);
  }

  .logo-dot {
    width: 7px; height: 7px;
    border-radius: 2px;
    background: var(--ochre);
    flex-shrink: 0;
  }

  header h1 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    font-weight: 600;
    color: var(--ink);
    letter-spacing: .12em;
    text-transform: uppercase;
  }

  .header-meta {
    margin-left: auto;
    display: flex;
    gap: 16px;
    align-items: center;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    font-weight: 600;
    color: var(--faint);
    letter-spacing: .1em;
  }

  .header-meta a:hover { color: var(--ochre); }

  .hero {
    max-width: 1180px;
    margin: 0 auto;
    padding: 64px 32px 28px;
  }

  .hero-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 8.5px;
    font-weight: 600;
    color: var(--faint);
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-bottom: 18px;
  }

  .hero h2 {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 38px;
    font-weight: 600;
    color: var(--ink);
    line-height: 1.15;
    letter-spacing: -.008em;
    margin-bottom: 16px;
  }

  .hero h2 strong { font-weight: 600; color: var(--ochre); }

  .hero p {
    color: var(--muted);
    max-width: 62ch;
    font-size: 14px;
    line-height: 1.6;
  }

  .search-wrap {
    max-width: 1180px;
    margin: 0 auto;
    padding: 0 32px 28px;
  }

  .search {
    display: flex;
    align-items: center;
    gap: 12px;
    background: var(--paper);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 11px 14px;
    box-shadow: var(--shadow);
    transition: border-color .15s, box-shadow .15s;
  }

  .search:focus-within {
    border-color: var(--ochre-bd);
    box-shadow: 0 0 0 3px var(--ochre-tint);
  }

  .search-icon { color: var(--faint); flex-shrink: 0; }

  .search input {
    flex: 1;
    background: transparent;
    border: 0;
    color: var(--ink);
    font-family: 'Public Sans', system-ui, sans-serif;
    font-size: 13.5px;
    outline: 0;
  }

  .search input::placeholder { color: var(--faint); }

  .search-kbd {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: var(--faint);
    background: var(--sidebar);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 2px 6px;
  }

  main {
    max-width: 1180px;
    margin: 0 auto;
    padding: 0 32px 80px;
  }

  .section { margin-bottom: 46px; }
  .section.hidden { display: none; }

  .section-head {
    display: flex;
    align-items: baseline;
    gap: 10px;
    padding-bottom: 10px;
    margin-bottom: 20px;
    border-bottom: 2px solid var(--ink);
  }

  .section-head h3 {
    font-family: 'Spectral', Georgia, serif;
    font-size: 19px;
    font-weight: 600;
    line-height: 1.2;
    color: var(--ink);
    letter-spacing: 0;
    text-transform: none;
  }

  .section-head .count {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    font-weight: 600;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--faint);
  }

  /* category accent dots — restrained warm set, no glow */
  .section-head .accent {
    width: 6px; height: 6px;
    border-radius: 2px;
    margin-right: 2px;
    align-self: center;
  }
  .accent-aix      { background: var(--ochre); }
  .accent-linux    { background: var(--sage);  }
  .accent-backup   { background: var(--rust);  }
  .accent-ref      { background: var(--muted); }
  .accent-vtl      { background: var(--ink);   }
  .accent-cohesity { background: var(--faint); }
  .accent-sec      { background: var(--border); }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 14px;
  }

  .card {
    display: block;
    background: var(--paper);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 18px;
    box-shadow: var(--shadow);
    transition: border-color .15s, transform .15s, box-shadow .15s;
    position: relative;
    overflow: hidden;
  }
  .card.hidden { display: none; }

  .card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 0; height: 100%;
    background: var(--ochre);
    transition: width .15s;
  }

  .card:hover {
    border-color: var(--ochre-bd);
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(43, 38, 32, .10);
  }
  .card:hover::before { width: 2px; }

  .card-placeholder { cursor: default; opacity: .55; }
  .card-placeholder:hover { transform: none; border-color: var(--border); box-shadow: var(--shadow); }
  .card-placeholder:hover::before { width: 0; }

  .card-tag {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 8.5px;
    font-weight: 600;
    color: var(--faint);
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-bottom: 10px;
  }

  .card h4 {
    font-family: 'Public Sans', system-ui, sans-serif;
    font-size: 15px;
    font-weight: 600;
    color: var(--ink);
    margin-bottom: 7px;
    line-height: 1.3;
  }

  .card p {
    font-size: 12.5px;
    color: var(--muted);
    line-height: 1.55;
  }

  .card-foot {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 14px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: var(--faint);
  }

  .card-foot .arrow {
    margin-left: auto;
    transition: transform .15s, color .15s;
  }

  .card:hover .arrow {
    transform: translateX(3px);
    color: var(--ochre);
  }

  .empty {
    display: none;
    text-align: center;
    padding: 64px 32px;
    color: var(--faint);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: .08em;
    text-transform: uppercase;
  }
  .empty.show { display: block; }

  footer {
    border-top: 1px solid var(--border);
    padding: 24px 32px;
    text-align: center;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: var(--faint);
    letter-spacing: .08em;
  }
  footer a:hover { color: var(--ochre); }

  @media (max-width: 640px) {
    header { padding: 0 20px; }
    .hero { padding: 48px 20px 24px; }
    .hero h2 { font-size: 28px; }
    .search-wrap, main { padding-left: 20px; padding-right: 20px; }
    .header-meta { display: none; }
  }"""


SCRIPT = """  const input    = document.getElementById('filter');
  const cards    = document.querySelectorAll('.card');
  const sections = document.querySelectorAll('.section');
  const empty    = document.getElementById('empty-state');

  function applyFilter(q) {
    q = q.trim().toLowerCase();
    let totalVisible = 0;
    sections.forEach(sec => {
      const secCards = sec.querySelectorAll('.card');
      let secVisible = 0;
      secCards.forEach(c => {
        const haystack = (c.dataset.search + ' ' + c.textContent).toLowerCase();
        const match = q === '' || haystack.includes(q);
        c.classList.toggle('hidden', !match);
        if (match) secVisible++;
      });
      sec.classList.toggle('hidden', secVisible === 0);
      totalVisible += secVisible;
    });
    empty.classList.toggle('show', totalVisible === 0);
  }

  input.addEventListener('input', e => applyFilter(e.target.value));

  document.addEventListener('keydown', e => {
    if (e.key === '/' && document.activeElement.tagName !== 'INPUT') {
      e.preventDefault();
      input.focus();
    }
    if (e.key === 'Escape' && document.activeElement === input) {
      input.value = '';
      applyFilter('');
      input.blur();
    }
  });"""


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Knowledge Base — AIX / Linux / Backup Runbooks</title>
<meta name="description" content="A curated collection of AIX, Linux, and backup operations runbooks built from production experience.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Public+Sans:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,600&family=Spectral:wght@600&display=swap" rel="stylesheet">
<style>
{styles}
</style>
</head>
<body>

<header>
  <span class="logo-dot"></span>
  <h1>WIKI &nbsp;/&nbsp; KNOWLEDGE BASE</h1>
  <div class="header-meta">
    <span id="total-count">{total} {runbook_word}</span>
    <a href="https://github.com/triippiing/Wiki" target="_blank" rel="noopener">GITHUB ↗</a>
  </div>
</header>

<section class="hero">
  <div class="hero-eyebrow">Operational Runbooks · Cheatsheets · Reference</div>
  <h2>AIX, Linux, and backup procedures<br>built from <strong>real-world ops work</strong>.</h2>
  <p>A curated knowledge base of step-by-step runbooks for IBM Power/AIX administration, Linux operations, TSM/Spectrum Protect backup workflows, and infrastructure hardening — written from production experience.</p>
</section>

<div class="search-wrap">
  <label class="search">
    <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
    <input id="filter" type="text" placeholder="Filter runbooks by name, category, or keyword…" autocomplete="off" autofocus>
    <span class="search-kbd">/</span>
  </label>
</div>

<main>

{sections}

  <div class="empty" id="empty-state">
    <p>No runbooks match your filter.</p>
  </div>

</main>

<footer>
  <span>BUILT FROM PRODUCTION OPS · </span>
  <a href="https://github.com/triippiing/Wiki" target="_blank" rel="noopener">github.com/triippiing/Wiki</a>
</footer>

<script>
{script}
</script>

</body>
</html>
"""


if __name__ == "__main__":
    main()
