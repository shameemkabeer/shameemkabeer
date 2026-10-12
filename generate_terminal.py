#!/usr/bin/env python3
"""Profile README art in the HackerPro terminal theme.

  terminal.svg              hero: terminal window with the ASCII-tile portrait + whoami panel
  assets/headers/*.svg      section headers drawn as shell prompts (╰─❯ cat credentials)
  assets/headers/ibr-callout.svg

The portrait is the background-removed photo turned into ASCII glyphs on tiles tinted with the
photo's colour at each spot (same look as the shxim-welcome terminal screen).

Usage: python3 generate_terminal.py [photo.png] [cols]
"""
import base64, os, sys
from html import escape
from PIL import Image, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
PHOTO = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.local/share/shxim/portrait.png")
COLS = int(sys.argv[2]) if len(sys.argv) > 2 else 48

# HackerPro palette
BG, BG_BAR, BORDER = "#0A0D12", "#161B22", "#30363D"
GREEN, GREEN_HI = "#3FB950", "#7EE787"
TEXT, DIM, MUTE = "#C9D1D9", "#8B949E", "#6E7681"
RED, AMBER, BLUE, PURPLE, CYAN = "#F85149", "#D29922", "#79C0FF", "#BC8CFF", "#39C5CF"
FONT = "'Hack','JetBrains Mono','DejaVu Sans Mono','SFMono-Regular',Menlo,Consolas,monospace"

USER, HOST = "shameem", "kabeer"
NAME = "Mohamed Shameem PA"
LOGO = os.path.join(HERE, "assets/logos/brand.png")      # personal >_S mark, green on transparent
INFO = [
    ("Role",           [(TEXT, "Cybersecurity Analyst · Security Researcher")]),
    ("Certifications", [(RED, "CEH v13"), (MUTE, " · "), (GREEN_HI, "ADCD"), (MUTE, " · "), (BLUE, "BCA")]),
    ("Expertise",      [(TEXT, "VAPT · Attack Surface · Web App Security")]),
    ("Recognition",    [(AMBER, "India Book of Records"), (MUTE, " · "), (TEXT, "Youngest Researcher")]),
    ("Acknowledged",   [(TEXT, "NASA · Apple · WHO · LG · US DoE · Zepto")]),
    ("Tools",          [(GREEN_HI, "RecHunter"), (MUTE, " · "), (GREEN_HI, "ReconXplorer")]),
    ("Research",       [(TEXT, "Solar Inverter Security · NETGEAR WNAP320")]),
    ("Hardware",       [(TEXT, "Raspberry Pi 5 · LilyGO T-Embed CC1101")]),
    ("Website",        [(BLUE, "mohamedshameem.com")]),
]

# ---------------------------------------------------------------- portrait tiles
RAMP = ".:-=+*#%@"
BG_DIM, FG_LIFT = 0.52, 1.35
CELL_W, CELL_H, GLYPH = 9.6, 19, 14


def portrait_cells():
    im = Image.open(PHOTO).convert("RGBA")
    im = im.crop(im.split()[-1].point(lambda a: 255 if a > 24 else 0).getbbox())
    rows = max(1, round(COLS * im.height / im.width * CELL_W / CELL_H))
    small = im.resize((COLS, rows), Image.LANCZOS)
    rgb = ImageEnhance.Contrast(small.convert("RGB")).enhance(1.12).filter(
        ImageFilter.UnsharpMask(radius=1, percent=60, threshold=2))
    alpha, lum = small.split()[-1], rgb.convert("L")
    vals = [lum.getpixel((x, y)) for y in range(rows) for x in range(COLS) if alpha.getpixel((x, y)) > 90]
    lo, hi = min(vals), max(vals)
    scale = lambda c, k: tuple(max(0, min(255, int(v * k))) for v in c)
    cells = []
    for y in range(rows):
        row = []
        for x in range(COLS):
            if alpha.getpixel((x, y)) <= 90:
                row.append(None); continue
            c = rgb.getpixel((x, y))
            L = (lum.getpixel((x, y)) - lo) / max(1, hi - lo)
            ch = RAMP[min(len(RAMP) - 1, int((0.15 + 0.85 * L) * len(RAMP)))]
            bg, fg = scale(c, BG_DIM), scale(c, FG_LIFT)
            if max(fg) < 95:                       # very dark hair/jacket: lift the glyph so it shows
                m = max(fg) or 1
                fg = tuple(int(v / m * 95) for v in fg)
            row.append((ch, bg, fg))
        cells.append(row)
    return cells


hexc = lambda c: "#%02X%02X%02X" % c


def spans(parts):
    return "".join(f'<tspan fill="{c}">{escape(t)}</tspan>' for c, t in parts)


# ---------------------------------------------------------------- hero terminal
def terminal_svg():
    cells = portrait_cells()
    rows = len(cells)
    W, PAD, BAR = 1180, 28, 38
    px, py = PAD + 8, BAR + 92                     # portrait origin
    pw, ph = COLS * CELL_W, rows * CELL_H
    ix = px + pw + 64                               # info column
    LINE = 27
    info_h = (len(INFO) + 4) * LINE
    iy = py + max(0, (ph - info_h) / 2) + 18
    H = int(py + ph + 78)

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'xmlns:xlink="http://www.w3.org/1999/xlink" role="img" aria-label="{USER}@{HOST} terminal: {NAME}, cybersecurity analyst">',
         f"""<style>
  text {{ font-family: {FONT}; white-space: pre; }}
  .p   {{ font-size: {GLYPH}px; text-anchor: middle; }}
  .t   {{ font-size: 15px; fill: {TEXT}; }}
  .k   {{ fill: {DIM}; }}
  .row {{ animation: in .35s ease-out both; }}
  .cur {{ animation: blink 1.1s steps(1) infinite; }}
  @keyframes in    {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @media (prefers-reduced-motion: reduce) {{ .row, .cur {{ animation: none; }} }}
</style>""",
         f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>',
         f'<path d="M1 {BAR} V13 a12 12 0 0 1 12 -12 H{W-13} a12 12 0 0 1 12 12 V{BAR} Z" fill="{BG_BAR}"/>',
         f'<line x1="1" y1="{BAR}" x2="{W-1}" y2="{BAR}" stroke="{BORDER}"/>']
    for i, c in enumerate((RED, AMBER, GREEN)):
        o.append(f'<circle cx="{24 + i * 20}" cy="{BAR/2+0.5}" r="6" fill="{c}"/>')
    o.append(f'<text x="{W/2}" y="{BAR/2+5}" text-anchor="middle" class="t" style="font-size:13px" fill="{DIM}">'
             f'<tspan fill="{DIM}">{USER}@{HOST}: ~</tspan></text>')

    # prompt
    y0 = BAR + 34
    o.append(f'<text x="{PAD}" y="{y0}" class="t">{spans([(MUTE, "╭─ "), (GREEN, USER), (MUTE, "@"), (TEXT, HOST), (MUTE, "  "), (BLUE, "~"), (MUTE, "  "), (PURPLE, "⎇ main")])}</text>')
    o.append(f'<text x="{PAD}" y="{y0 + 22}" class="t">{spans([(MUTE, "╰─"), (GREEN, "❯ "), (TEXT, "whoami")])}</text>')

    # portrait: tiles then glyphs, revealed top-down
    for y, row in enumerate(cells):
        o.append(f'<g class="row" style="animation-delay:{0.25 + y * 0.035:.3f}s">')
        x = 0
        while x < COLS:                               # merge runs of equal tile colour
            if row[x] is None:
                x += 1; continue
            x2 = x
            while x2 + 1 < COLS and row[x2 + 1] is not None and row[x2 + 1][1] == row[x][1]:
                x2 += 1
            o.append(f'<rect x="{px + x * CELL_W:.1f}" y="{py + y * CELL_H}" width="{(x2 - x + 1) * CELL_W + 0.6:.1f}" '
                     f'height="{CELL_H + 0.6}" fill="{hexc(row[x][1])}"/>')
            x = x2 + 1
        for x, cell in enumerate(row):
            if cell:
                o.append(f'<text x="{px + (x + 0.5) * CELL_W:.1f}" y="{py + y * CELL_H + 14}" class="p" '
                         f'fill="{hexc(cell[2])}">{escape(cell[0])}</text>')
        o.append("</g>")

    # info panel
    t0 = 0.25 + rows * 0.035 * 0.4
    logo = base64.b64encode(open(LOGO, "rb").read()).decode()
    ls = 2 * LINE + 6                                  # logo spans the two header lines
    lines = [f'<image x="{ix}" y="{{top}}" width="{ls:.0f}" height="{ls * 250 / 240:.0f}" '
             f'xlink:href="data:image/png;base64,{logo}" href="data:image/png;base64,{logo}"/>'
             f'<text x="{ix + ls + 16}" y="{{y}}" class="t" style="font-weight:700">{spans([(GREEN, USER), (MUTE, "@"), (TEXT, HOST)])}</text>',
             f'<text x="{ix + ls + 16}" y="{{y}}" class="t" fill="{DIM}">{NAME}</text>',
             f'<text x="{ix}" y="{{y}}" class="t" fill="{MUTE}">{"─" * 44}</text>']
    for k, v in INFO:
        lines.append(f'<text x="{ix}" y="{{y}}" class="t"><tspan class="k">{k:<15}</tspan>{spans(v)}</text>')
    lines.append("")
    bar = "".join(f'<rect x="{ix + i * 30}" y="{{bar}}" width="28" height="5" rx="1" fill="{c}"/>'
                  for i, c in enumerate((RED, AMBER, GREEN, CYAN, BLUE, PURPLE, TEXT)))
    lines.append(bar)
    for i, line in enumerate(lines):
        if not line:
            continue
        y = iy + i * LINE
        o.append(f'<g class="row" style="animation-delay:{t0 + i * 0.09:.2f}s">'
                 + line.replace("{y}", f"{y:.0f}").replace("{bar}", f"{y - 12:.0f}").replace("{top}", f"{y - 22:.0f}") + "</g>")

    # closing prompt with blinking cursor
    yb = H - 30
    o.append(f'<text x="{PAD}" y="{yb}" class="t">{spans([(MUTE, "╰─"), (GREEN, "❯ ")])}'
             f'<tspan class="cur" fill="{GREEN_HI}">█</tspan></text>')
    o.append("</svg>")
    return "\n".join(o)


# ---------------------------------------------------------------- section headers
def header_svg(cmd, arg, accent=GREEN):
    W, H = 800, 46
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(arg)}">
<style>text {{ font-family: {FONT}; font-size: 15px; white-space: pre; }}</style>
<rect x="0.75" y="0.75" width="{W-1.5}" height="{H-1.5}" rx="8" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>
<rect x="0.75" y="10" width="3" height="{H-20}" rx="1.5" fill="{accent}"/>
<text x="22" y="{H/2+5}">{spans([(MUTE, "╰─"), (accent, "❯ "), (TEXT, cmd + " "), (GREEN_HI if accent == GREEN else accent, arg)])}</text>
</svg>
"""


HEADERS = {
    "connect": ("ls", "~/connect", GREEN),
    "credentials": ("cat", "credentials.txt", GREEN),
    "recognized-by": ("grep -r", '"acknowledged" ./hall-of-fame', GREEN),
    "offensive-security-toolkit": ("ls", "/opt/offsec-toolkit", RED),
    "hardware": ("lsusb", "--hardware", GREEN),
    "development-stack": ("cat", "stack.json", GREEN),
    "support": ("./support.sh", "--coffee", AMBER),
    "github-stats": ("gh", "stats --user ShameemKabeer", GREEN),
}


def ibr_svg():
    W, H = 800, 64
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="India Book of Records — Youngest Indian Cybersecurity Researcher">
<style>text {{ font-family: {FONT}; white-space: pre; }}</style>
<rect x="0.75" y="0.75" width="{W-1.5}" height="{H-1.5}" rx="8" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>
<rect x="0.75" y="12" width="3" height="{H-24}" rx="1.5" fill="{AMBER}"/>
<text x="22" y="25" style="font-size:12px">{spans([(AMBER, "[ACHIEVEMENT]"), (MUTE, " india book of records")])}</text>
<text x="22" y="47" style="font-size:15px">{spans([(AMBER, "★ "), (TEXT, "Youngest Indian Cybersecurity Researcher"), (MUTE, " — "), (GREEN_HI, "global recognition in 37 days")])}</text>
</svg>
"""


def write(rel, data):
    path = os.path.join(HERE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(data)
    print(f"{rel:45} {len(data) / 1024:7.1f} KB")


if __name__ == "__main__":
    write("terminal.svg", terminal_svg())
    for name, (cmd, arg, accent) in HEADERS.items():
        write(f"assets/headers/{name}.svg", header_svg(cmd, arg, accent))
    write("assets/headers/ibr-callout.svg", ibr_svg())
