import os
import math
import random
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

# ==============================================================================
# CONFIGURATION — IMAGE FILE NAMES
# ==============================================================================
PHOTO_FILE        = 'cropped_test-removebg-preview.png'  # Transparent BG-Removed Photo
BRAND_LOGO_FILE   = 'Personal Brand Logo.png'             # Personal brand logo
STARTUP_LOGO_FILE = 'Secniti Logo Startup.png'            # Secnity startup logo
# ==============================================================================

random.seed(42)
np.random.seed(42)


def process_photo_dither(img_path, target_w=220, target_h=260):
    """Process transparent background-removed photo into 1-bit Floyd-Steinberg dither dots."""
    raw_img = Image.open(img_path).convert('RGBA')

    # 1. Trim transparent margins around subject
    arr_raw = np.array(raw_img)
    alpha_raw = arr_raw[:, :, 3]
    non_bg_y, non_bg_x = np.where(alpha_raw > 30)

    if len(non_bg_y) > 0:
        min_y, max_y = np.min(non_bg_y), np.max(non_bg_y)
        min_x, max_x = np.min(non_bg_x), np.max(non_bg_x)
        cropped_subject = raw_img.crop((min_x, min_y, max_x, max_y))
    else:
        cropped_subject = raw_img

    # 2. Resize and Center Subject inside target canvas
    sub_w, sub_h = cropped_subject.size
    scale = min(target_w / sub_w, target_h / sub_h)
    fit_w = int(sub_w * scale)
    fit_h = int(sub_h * scale)

    resized_sub = cropped_subject.resize((fit_w, fit_h), Image.Resampling.LANCZOS)
    canvas = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 0))
    canvas.paste(resized_sub, ((target_w - fit_w) // 2, (target_h - fit_h) // 2))

    arr_c = np.array(canvas)
    fg_mask = arr_c[:, :, 3] > 40

    # Enhance Contrast & Perform Serpentine Dither
    gray_img = canvas.convert('L')
    gray_img = ImageEnhance.Contrast(gray_img).enhance(1.35)
    gray_img = ImageOps.autocontrast(gray_img, cutoff=1)
    gray_img = gray_img.filter(ImageFilter.UnsharpMask(radius=2, percent=130))
    gray_arr = np.array(gray_img, dtype=float)

    H, W = gray_arr.shape
    buf = gray_arr.copy()
    dots = []

    for y in range(H):
        left_to_right = (y % 2 == 0)
        x_range = range(W) if left_to_right else range(W - 1, -1, -1)
        dx_dir = 1 if left_to_right else -1

        for x in x_range:
            if not fg_mask[y, x]:
                buf[y, x] = 0
                continue

            old_val = buf[y, x]
            new_val = 255.0 if old_val > 115 else 0.0
            err = old_val - new_val

            if new_val == 255.0:
                dots.append((x, y))

            targets = [
                (x + dx_dir, y,     7.0 / 16.0),
                (x - dx_dir, y + 1, 3.0 / 16.0),
                (x,          y + 1, 5.0 / 16.0),
                (x + dx_dir, y + 1, 1.0 / 16.0),
            ]
            for tx, ty, weight in targets:
                if 0 <= tx < W and 0 <= ty < H and fg_mask[ty, tx]:
                    buf[ty, tx] += err * weight

    return dots


def dither_logo(img_rgba):
    """Convert logo graphic into crisp dithered dot coordinates."""
    alpha = np.array(img_rgba)[:, :, 3]
    gray = img_rgba.convert('L')
    arr = np.array(gray, dtype=float)
    H, W = arr.shape
    buf = arr.copy()
    fg_mask = alpha > 40

    dots = []
    for y in range(H):
        left_to_right = (y % 2 == 0)
        x_range = range(W) if left_to_right else range(W - 1, -1, -1)
        dx_dir = 1 if left_to_right else -1

        for x in x_range:
            if not fg_mask[y, x]:
                buf[y, x] = 0
                continue

            old_val = buf[y, x]
            new_val = 255.0 if old_val > 125 else 0.0
            err = old_val - new_val

            if new_val == 255.0 or (alpha[y, x] > 120 and old_val < 190):
                dots.append((x, y))

            targets = [
                (x + dx_dir, y,     7.0 / 16.0),
                (x - dx_dir, y + 1, 3.0 / 16.0),
                (x,          y + 1, 5.0 / 16.0),
                (x + dx_dir, y + 1, 1.0 / 16.0),
            ]
            for tx, ty, weight in targets:
                if 0 <= tx < W and 0 <= ty < H and fg_mask[ty, tx]:
                    buf[ty, tx] += err * weight

    return dots


def main():
    print("Generating Professional Cyber Banner...")
    dir_path = os.path.dirname(os.path.abspath(__file__))

    grid_w, grid_h = 220, 260
    box_x, box_y = 45, 105
    box_w, box_h = 360, 440
    dx_step = box_w / grid_w
    dy_step = box_h / grid_h

    # 1. Process Photo
    p1 = os.path.join(dir_path, PHOTO_FILE)
    raw_dots1 = process_photo_dither(p1, grid_w, grid_h)

    # 2. Load Personal Brand Logo
    p2 = os.path.join(dir_path, BRAND_LOGO_FILE)
    img2 = Image.open(p2).convert('RGBA')
    img2.thumbnail((grid_w - 20, grid_h - 20), Image.Resampling.LANCZOS)
    c2 = Image.new('RGBA', (grid_w, grid_h), (0, 0, 0, 0))
    c2.paste(img2, ((grid_w - img2.width) // 2, (grid_h - img2.height) // 2))
    raw_dots2 = dither_logo(c2)

    # 3. Load Secnity Startup Logo
    p3 = os.path.join(dir_path, STARTUP_LOGO_FILE)
    img3 = Image.open(p3).convert('RGBA')
    img3.thumbnail((grid_w - 20, grid_h - 20), Image.Resampling.LANCZOS)
    c3 = Image.new('RGBA', (grid_w, grid_h), (0, 0, 0, 0))
    c3.paste(img3, ((grid_w - img3.width) // 2, (grid_h - img3.height) // 2))
    raw_dots3 = dither_logo(c3)

    print(f"Asset 1 ({PHOTO_FILE}) dots: {len(raw_dots1)}")
    print(f"Asset 2 ({BRAND_LOGO_FILE}) dots: {len(raw_dots2)}")
    print(f"Asset 3 ({STARTUP_LOGO_FILE}) dots: {len(raw_dots3)}")

    def map_dots(raw):
        mapped = []
        for x, y in raw:
            px = round(box_x + x * dx_step, 1)
            py = round(box_y + y * dy_step, 1)
            mapped.append((px, py))
        return mapped

    dots1 = map_dots(raw_dots1)
    dots2 = map_dots(raw_dots2)
    dots3 = map_dots(raw_dots3)

    def build_path_string(dots):
        runs = [f'M{px},{py}h2.2v2.2h-2.2z' for px, py in dots]
        return "".join(runs)

    d_str1 = build_path_string(dots1)
    d_str2 = build_path_string(dots2)
    d_str3 = build_path_string(dots3)

    def build_svg(is_dark=True):
        bg_color         = "#090D16" if is_dark else "#F8FAFC"
        chrome_color     = "#38BDF8" if is_dark else "#0284C7"
        accent_color     = "#00E5A0" if is_dark else "#059669"
        text_color       = "#F1F5F9" if is_dark else "#0F172A"
        dot_leader_color = "#1E293B" if is_dark else "#E2E8F0"

        svg = []
        svg.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 610" width="1180" height="610">')
        svg.append('<style>')
        svg.append(f'  .bg     {{ fill: {bg_color}; }}')
        svg.append(f'  .chrome {{ stroke: {chrome_color}; stroke-width: 1.5; fill: none; }}')
        svg.append(f'  .title  {{ font-family: "Courier New", monospace; font-size: 14px; font-weight: bold; fill: {chrome_color}; }}')
        svg.append(f'  .label  {{ font-family: "Courier New", monospace; font-size: 13px; fill: {chrome_color}; font-weight: bold; }}')
        svg.append(f'  .text   {{ font-family: "Courier New", monospace; font-size: 14px; fill: {text_color}; }}')
        svg.append(f'  .leader {{ stroke: {dot_leader_color}; stroke-width: 1; stroke-dasharray: 2,4; }}')
        svg.append(f'  @keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} 100% {{ opacity: 1; }} }}')
        svg.append(f'  .live-dot {{ fill: #FF4D4D; animation: pulse 1.8s infinite ease-in-out; }}')
        svg.append('</style>')

        # Background & Window Frame
        svg.append(f'<rect width="1180" height="610" class="bg" rx="10"/>')
        svg.append(f'<rect x="15" y="15" width="1150" height="580" rx="8" class="chrome"/>')
        svg.append(f'<line x1="15" y1="50" x2="1165" y2="50" class="chrome"/>')

        # Traffic-lights
        svg.append(f'<circle cx="35" cy="32" r="6" fill="#FF4D4D"/>')
        svg.append(f'<circle cx="55" cy="32" r="6" fill="{chrome_color}"/>')
        svg.append(f'<circle cx="75" cy="32" r="6" fill="{accent_color}"/>')
        svg.append(f'<text x="105" y="37" class="title">profile.sh --live</text>')

        # Left Panel (No text label)
        svg.append(f'<rect x="30" y="65" width="390" height="515" rx="6" class="chrome"/>')

        # Corner crosshairs
        svg.append(f'<path d="M45,115 v15 M45,115 h15 M405,115 v15 M405,115 h-15 M45,535 v-15 M45,535 h15 M405,535 v-15 M405,535 h-15" stroke="{chrome_color}" stroke-width="1" fill="none" opacity="0.6"/>')

        # Right Panel (SHAMEEM.INFO)
        svg.append(f'<rect x="440" y="65" width="710" height="515" rx="6" class="chrome"/>')
        svg.append(f'<text x="455" y="90" class="label">SHAMEEM.INFO</text>')

        # LIVE dot + label
        svg.append(f'<circle cx="1090" cy="90" r="5" class="live-dot"/>')
        svg.append(f'<text x="1102" y="94" font-family="Courier New, monospace" font-size="12" font-weight="bold" fill="#FF4D4D">LIVE</text>')

        # Handle pill
        pill_bg = accent_color
        pill_fg = bg_color
        svg.append(f'<rect x="910" y="78" width="150" height="24" rx="12" fill="{pill_bg}"/>')
        svg.append(f'<text x="985" y="94" text-anchor="middle" font-family="Courier New, monospace" font-size="13" font-weight="bold" fill="{pill_fg}">@shameemkabeer</text>')

        # ── 3-Asset Smooth Dissolve Rotation ────────────────────────────────
        kt_all = "0; 0.286; 0.333; 0.620; 0.666; 0.953; 1.0"

        # Asset 1 (Photo)
        svg.append(f'<g id="asset-photo">')
        svg.append(f'  <animate attributeName="opacity" values="1; 1; 0; 0; 0; 0; 0" keyTimes="{kt_all}" dur="15.0s" repeatCount="indefinite"/>')
        svg.append(f'  <path d="{d_str1}" fill="{accent_color}" shape-rendering="crispEdges"/>')
        svg.append(f'</g>')

        # Asset 2 (Personal Brand Logo)
        svg.append(f'<g id="asset-brand-logo">')
        svg.append(f'  <animate attributeName="opacity" values="0; 0; 1; 1; 0; 0; 0" keyTimes="{kt_all}" dur="15.0s" repeatCount="indefinite"/>')
        svg.append(f'  <path d="{d_str2}" fill="{accent_color}" shape-rendering="crispEdges"/>')
        svg.append(f'</g>')

        # Asset 3 (Secnity Startup Logo)
        svg.append(f'<g id="asset-startup-logo">')
        svg.append(f'  <animate attributeName="opacity" values="0; 0; 0; 0; 1; 1; 0" keyTimes="{kt_all}" dur="15.0s" repeatCount="indefinite"/>')
        svg.append(f'  <path d="{d_str3}" fill="{accent_color}" shape-rendering="crispEdges"/>')
        svg.append(f'</g>')

        # ── SHAMEEM.INFO Readout ─────────────────────────────────────────────
        info_rows = [
            ("Subject",      "Mohamed Shameem PA"),
            ("Role",         "Cybersecurity Analyst | Security Researcher | Co-Founder, Secnity"),
            ("Credentials",  "CEH v13 | ADCD | BCA Graduate"),
            ("Focus",        "VAPT, Offensive Security & Web App Security — Responsible Disclosure"),
            ("Status",       "India Book of Records Achiever | Building Secnity"),
            ("Recognized",   "NASA | Apple | WHO | LG | US Dept. of Education | Zepto"),
            ("Signature",    "RecHunter & ReconXplorer — Custom Recon Tooling"),
            ("Research",     "How I Hacked a Solar Inverter | NETGEAR WNAP320 Firmware Exploit"),
            ("Network.Arch", "Network Design for NEXGEN Software Co."),
        ]

        start_y      = 130
        row_spacing  = 38
        left_label_x = 465
        right_val_x  = 1125

        svg.append(f'<g id="system-info">')
        for idx, (label_txt, val_txt) in enumerate(info_rows):
            curr_y = start_y + idx * row_spacing

            # Natural width per row — no flat 460 cap so long rows aren't compressed
            val_w        = len(val_txt) * 8.4
            leader_start = left_label_x + len(label_txt) * 9.5 + 8
            leader_end   = right_val_x - val_w - 10
            if leader_end > leader_start:
                svg.append(f'  <line x1="{leader_start:.1f}" y1="{curr_y - 4}" x2="{leader_end:.1f}" y2="{curr_y - 4}" class="leader"/>')

            # XML-escape special characters in text content
            val_escaped = val_txt.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            label_escaped = label_txt.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

            svg.append(f'  <text x="{left_label_x}" y="{curr_y}" class="label">{label_escaped}</text>')
            svg.append(f'  <text x="{right_val_x}" y="{curr_y}" text-anchor="end" class="text" textLength="{val_w:.1f}" lengthAdjust="spacingAndGlyphs">{val_escaped}</text>')

        svg.append(f'</g>')
        svg.append('</svg>')
        return "\n".join(svg)

    dark_svg  = build_svg(is_dark=True)
    light_svg = build_svg(is_dark=False)

    dark_path  = os.path.join(dir_path, 'dark.svg')
    light_path = os.path.join(dir_path, 'light.svg')

    with open(dark_path, 'w', encoding='utf-8') as f:
        f.write(dark_svg)
    with open(light_path, 'w', encoding='utf-8') as f:
        f.write(light_svg)

    print(f"Generated dark.svg  ({os.path.getsize(dark_path)  / 1024:.1f} KB)")
    print(f"Generated light.svg ({os.path.getsize(light_path) / 1024:.1f} KB)")


if __name__ == '__main__':
    main()
