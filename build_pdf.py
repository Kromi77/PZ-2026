# -*- coding: utf-8 -*-
"""Konwersja DOCUMENTATION.md -> DOCUMENTATION.pdf (Markdown -> HTML -> PDF).

Działa na Windows, macOS i Linux:
- automatycznie wyszukuje przeglądarkę opartą o Chromium (Edge / Chrome / Chromium),
- osadza systemową czcionkę o pełnym pokryciu polskich znaków (z fallbackiem per-system),
  dzięki czemu PDF wygląda tak samo niezależnie od urządzenia.

Wymaga: pip install markdown
"""
import platform
import shutil
import subprocess
import sys
import tempfile
import pathlib

ROOT = pathlib.Path(__file__).parent
md_path = ROOT / "DOCUMENTATION.md"
html_path = ROOT / "DOCUMENTATION.html"
pdf_path = ROOT / "DOCUMENTATION.pdf"

SYSTEM = platform.system()  # 'Windows' | 'Darwin' | 'Linux'


# --------------------------------------------------------------------------- #
# 1. Wyszukanie przeglądarki Chromium (Edge / Chrome / Chromium)
# --------------------------------------------------------------------------- #
def find_browser() -> str:
    # najpierw szukamy w PATH (typowe dla Linuksa)
    for name in (
        "microsoft-edge", "microsoft-edge-stable",
        "google-chrome", "google-chrome-stable",
        "chromium", "chromium-browser", "chrome",
    ):
        found = shutil.which(name)
        if found:
            return found

    candidates = {
        "Windows": [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ],
        "Darwin": [
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ],
        "Linux": [
            "/usr/bin/microsoft-edge",
            "/usr/bin/google-chrome",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
        ],
    }.get(SYSTEM, [])

    for path in candidates:
        if pathlib.Path(path).exists():
            return path

    sys.exit(
        "Nie znaleziono przeglądarki opartej o Chromium (Edge/Chrome/Chromium).\n"
        "Zainstaluj jedną z nich lub dodaj ją do PATH."
    )


# --------------------------------------------------------------------------- #
# 2. Wyszukanie czcionek (regular / bold / italic / mono) per system
#    Wszystkie kandydatki mają pełne pokrycie polskiego alfabetu.
# --------------------------------------------------------------------------- #
FONT_CANDIDATES = {
    "Windows": {
        "sans":        [r"C:\Windows\Fonts\segoeui.ttf",  r"C:\Windows\Fonts\arial.ttf"],
        "sans_bold":   [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"],
        "sans_italic": [r"C:\Windows\Fonts\segoeuii.ttf", r"C:\Windows\Fonts\ariali.ttf"],
        "mono":        [r"C:\Windows\Fonts\consola.ttf",  r"C:\Windows\Fonts\cour.ttf"],
        "mono_bold":   [r"C:\Windows\Fonts\consolab.ttf", r"C:\Windows\Fonts\courbd.ttf"],
    },
    "Darwin": {
        "sans":        ["/System/Library/Fonts/Supplemental/Arial.ttf",
                        "/Library/Fonts/Arial.ttf",
                        "/System/Library/Fonts/Helvetica.ttc"],
        "sans_bold":   ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                        "/Library/Fonts/Arial Bold.ttf"],
        "sans_italic": ["/System/Library/Fonts/Supplemental/Arial Italic.ttf",
                        "/Library/Fonts/Arial Italic.ttf"],
        "mono":        ["/System/Library/Fonts/Menlo.ttc",
                        "/System/Library/Fonts/Supplemental/Courier New.ttf"],
        "mono_bold":   ["/System/Library/Fonts/Supplemental/Courier New Bold.ttf"],
    },
    "Linux": {
        "sans":        ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"],
        "sans_bold":   ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"],
        "sans_italic": ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
                        "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
                        "/usr/share/fonts/truetype/noto/NotoSans-Italic.ttf"],
        "mono":        ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
                        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"],
        "mono_bold":   ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
                        "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"],
    },
}


def first_existing(paths):
    for p in paths:
        if pathlib.Path(p).exists():
            return pathlib.Path(p)
    return None


def build_font_faces() -> str:
    roles = FONT_CANDIDATES.get(SYSTEM, {})
    faces = []
    # (rola, rodzina CSS, waga, styl)
    spec = [
        ("sans",        "DocSans", 400, "normal"),
        ("sans_bold",   "DocSans", 700, "normal"),
        ("sans_italic", "DocSans", 400, "italic"),
        ("mono",        "DocMono", 400, "normal"),
        ("mono_bold",   "DocMono", 700, "normal"),
    ]
    found_any = False
    for role, family, weight, style in spec:
        font = first_existing(roles.get(role, []))
        if font is None:
            continue  # brak pliku -> przeglądarka zsyntetyzuje wariant / użyje fallbacku
        found_any = True
        faces.append(
            f"@font-face {{ font-family:'{family}'; font-weight:{weight}; "
            f"font-style:{style}; src:url('{font.as_uri()}'); }}"
        )
    if not found_any:
        print("Uwaga: nie znaleziono żadnej systemowej czcionki do osadzenia; "
              "używam rodzin ogólnych (sans-serif / monospace).", file=sys.stderr)
    return "\n".join(faces)


# --------------------------------------------------------------------------- #
# 3. Markdown -> HTML
# --------------------------------------------------------------------------- #
try:
    import markdown
    from markdown.extensions.toc import slugify_unicode
except ImportError:
    sys.exit("Brak biblioteki 'markdown'. Zainstaluj: pip install markdown")

body = markdown.markdown(
    md_path.read_text(encoding="utf-8"),
    extensions=["tables", "fenced_code", "toc", "sane_lists"],
    # slugify_unicode zachowuje polskie znaki w id nagłówków -> linki spisu treści
    # (np. #4-przepływ-danych) trafiają w cel, tak samo jak na GitHubie.
    extension_configs={"toc": {"slugify": slugify_unicode}},
)

CSS = build_font_faces() + """
@page { size: A4; margin: 18mm 16mm; }
* { box-sizing: border-box; }
body { font-family: 'DocSans', Arial, Helvetica, sans-serif; font-size: 10.5pt; line-height: 1.5;
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


# --------------------------------------------------------------------------- #
# 4. HTML -> PDF (Chromium headless, świeża instancja by uniknąć kolizji)
# --------------------------------------------------------------------------- #
browser = find_browser()
profile = tempfile.mkdtemp(prefix="chromium_pdf_")

if pdf_path.exists():
    try:
        pdf_path.unlink()
    except PermissionError:
        sys.exit(f"Nie można nadpisać {pdf_path.name} - zamknij plik w podglądzie PDF i spróbuj ponownie.")

subprocess.run([
    browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
    f"--user-data-dir={profile}",
    f"--print-to-pdf={pdf_path}", html_path.as_uri(),
], check=True)

html_path.unlink(missing_ok=True)  # plik pośredni - sprzątamy

print(f"PDF: {pdf_path} ({pdf_path.stat().st_size} bytes) | system: {SYSTEM} | przeglądarka: {browser}")
