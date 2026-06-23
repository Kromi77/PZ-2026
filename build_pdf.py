# -*- coding: utf-8 -*-
"""Konwersja DOCUMENTATION.md -> DOCUMENTATION.pdf (Markdown -> HTML -> PDF przez Edge headless)."""
import subprocess, sys, pathlib, markdown

ROOT = pathlib.Path(__file__).parent
md_path = ROOT / "DOCUMENTATION.md"
html_path = ROOT / "DOCUMENTATION.html"
pdf_path = ROOT / "DOCUMENTATION.pdf"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

text = md_path.read_text(encoding="utf-8")
body = markdown.markdown(
    text,
    extensions=["tables", "fenced_code", "toc", "sane_lists"],
)

def font_uri(name):
    return pathlib.Path(r"C:\Windows\Fonts", name).as_uri()

# Osadzone czcionki z Windows o pełnym pokryciu polskich znaków -> brak fallbacku per-glyph.
FONT_FACES = f"""
@font-face {{ font-family:'DocSans'; font-weight:400; font-style:normal; src:url('{font_uri("segoeui.ttf")}'); }}
@font-face {{ font-family:'DocSans'; font-weight:700; font-style:normal; src:url('{font_uri("segoeuib.ttf")}'); }}
@font-face {{ font-family:'DocSans'; font-weight:400; font-style:italic; src:url('{font_uri("segoeuii.ttf")}'); }}
@font-face {{ font-family:'DocMono'; font-weight:400; font-style:normal; src:url('{font_uri("consola.ttf")}'); }}
@font-face {{ font-family:'DocMono'; font-weight:700; font-style:normal; src:url('{font_uri("consolab.ttf")}'); }}
"""

CSS = FONT_FACES + """
@page { size: A4; margin: 18mm 16mm; }
* { box-sizing: border-box; }
body { font-family: 'DocSans', sans-serif; font-size: 10.5pt; line-height: 1.5;
       color: #1a1a1a; max-width: 100%; }
h1 { font-size: 22pt; color: #0b3d91; border-bottom: 3px solid #0b3d91; padding-bottom: 6px; }
h2 { font-size: 15pt; color: #0b3d91; margin-top: 26px; border-bottom: 1px solid #c9d6ea; padding-bottom: 4px; }
h3 { font-size: 12.5pt; color: #244; margin-top: 18px; }
h2, h3 { page-break-after: avoid; }
p, li { orphans: 2; widows: 2; }
code { font-family: 'DocMono', monospace; font-size: 9pt;
       background: #f1f3f6; padding: 1px 4px; border-radius: 3px; }
pre { background: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 6px; padding: 10px 12px;
      overflow-x: auto; page-break-inside: avoid; }
pre code { background: none; padding: 0; font-size: 8.6pt; line-height: 1.35; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 9.3pt;
        page-break-inside: avoid; }
th, td { border: 1px solid #cbd5e1; padding: 5px 8px; text-align: left; vertical-align: top; }
th { background: #eaf0fb; color: #0b3d91; }
tr:nth-child(even) td { background: #f8fafc; }
blockquote { border-left: 4px solid #ffb300; background: #fff8e6; margin: 12px 0;
             padding: 6px 14px; color: #5a4a00; }
blockquote p { margin: 4px 0; }
a { color: #0b57d0; text-decoration: none; }
hr { border: none; border-top: 1px solid #d0d7de; margin: 22px 0; }
"""

html = f"""<!DOCTYPE html>
<html lang="pl"><head><meta charset="utf-8">
<title>Dokumentacja PZ-2026</title>
<style>{CSS}</style></head>
<body>{body}</body></html>"""

html_path.write_text(html, encoding="utf-8")

import tempfile
profile = tempfile.mkdtemp(prefix="edge_pdf_")

if pdf_path.exists():
    pdf_path.unlink()

subprocess.run([
    EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
    f"--user-data-dir={profile}",
    f"--print-to-pdf={pdf_path}", html_path.as_uri(),
], check=True)

print("PDF:", pdf_path, pdf_path.stat().st_size, "bytes")
