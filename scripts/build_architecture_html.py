"""將 docs/architecture.md 轉為獨立 HTML 檔案（含 Mermaid 支援）。"""
import markdown
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "docs" / "architecture.md"
OUT_PATH = ROOT / "ai-team-agent.html"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Team Agent — 系統架構</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<style>
:root { --bg: #0d1117; --fg: #e6edf3; --accent: #58a6ff; --card: #161b22; --border: #30363d; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: var(--bg); color: var(--fg); line-height: 1.7; padding: 2rem; max-width: 960px; margin: 0 auto; }
h1 { color: var(--accent); border-bottom: 2px solid var(--border); padding-bottom: 0.5rem; margin: 2rem 0 1rem; font-size: 2rem; }
h2 { color: var(--accent); margin: 2rem 0 0.8rem; font-size: 1.5rem; border-bottom: 1px solid var(--border); padding-bottom: 0.3rem; }
h3 { color: #79c0ff; margin: 1.5rem 0 0.5rem; font-size: 1.2rem; }
h4 { color: #a5d6ff; margin: 1rem 0 0.4rem; }
p { margin: 0.6rem 0; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
code { background: var(--card); padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.9em; color: #f0883e; }
pre { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; overflow-x: auto; margin: 1rem 0; }
pre code { background: none; padding: 0; color: var(--fg); }
table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
th, td { border: 1px solid var(--border); padding: 0.5rem 0.8rem; text-align: left; }
th { background: var(--card); color: var(--accent); }
tr:nth-child(even) { background: rgba(22, 27, 34, 0.5); }
blockquote { border-left: 3px solid var(--accent); padding-left: 1rem; color: #8b949e; margin: 1rem 0; }
ul, ol { padding-left: 1.5rem; margin: 0.5rem 0; }
li { margin: 0.3rem 0; }
hr { border: none; border-top: 1px solid var(--border); margin: 2rem 0; }
.mermaid { background: var(--card); border-radius: 8px; padding: 1rem; margin: 1rem 0; text-align: center; }
</style>
</head>
<body>
{content}
<script>
mermaid.initialize({ startOnLoad: true, theme: 'dark' });
// Convert fenced mermaid code blocks to mermaid divs
document.querySelectorAll('code.language-mermaid').forEach(el => {
  const pre = el.parentElement;
  const div = document.createElement('pre');
  div.className = 'mermaid';
  div.textContent = el.textContent;
  pre.replaceWith(div);
});
</script>
</body>
</html>"""


def build():
    md_text = MD_PATH.read_text(encoding="utf-8")
    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "codehilite", "toc"],
        extension_configs={"codehilite": {"css_class": "highlight", "guess_lang": False}},
    )
    html = HTML_TEMPLATE.replace("{content}", html_body)
    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"✅ 產出: {OUT_PATH}")


if __name__ == "__main__":
    build()
