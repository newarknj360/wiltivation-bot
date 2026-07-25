"""
Wiltivation Carousel Generator
Turns a quote/thought into an on-brand Instagram carousel (4:5 slides).
"""
from PIL import Image, ImageDraw, ImageFont
import textwrap, os, json

# ---------- BRAND CONFIG (real Wiltivation identity: black/gold/silver, Georgia serif) ----------
BG_COLOR      = (10, 10, 10)        # #0a0a0a — true brand black
TEXT_COLOR    = (232, 230, 224)     # #e8e6e0 — off-white
ACCENT_COLOR  = (201, 162, 75)      # #c9a24b — brand gold
SILVER_COLOR  = (185, 188, 196)     # #b9bcc4 — brand silver, secondary accent
MUTED_COLOR   = (138, 114, 55)      # #8a7237 — gold-dim, for de-emphasized text

W, H = 1080, 1350  # 4:5 portrait, IG's max-real-estate ratio

def _find_font(filename):
    """Look in common locations so this works both in the dev sandbox
    (google-fonts apt package) and on the GitHub Actions runner (~/.fonts)."""
    candidates = [
        os.path.expanduser(f"~/.fonts/{filename}"),
        f"/usr/share/fonts/truetype/google-fonts/{filename}",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    raise FileNotFoundError(f"Font {filename} not found in {candidates}")

FONT_QUOTE  = _find_font("Lora-Italic-Variable.ttf")
FONT_BOLD   = _find_font("Poppins-Bold.ttf")
FONT_LIGHT  = _find_font("Poppins-Light.ttf")
FONT_MEDIUM = _find_font("Poppins-Medium.ttf")

HANDLE = "@wiltivation"

def wrap_and_fit(draw, text, font_path, max_width, start_size, min_size=40):
    """Shrink font size until the wrapped text fits within max_width, return font + lines."""
    size = start_size
    while size >= min_size:
        font = ImageFont.truetype(font_path, size)
        avg_char_w = font.getlength("x") or 1
        wrap_chars = max(10, int(max_width / avg_char_w * 1.8))
        lines = textwrap.wrap(text, width=wrap_chars)
        widths = [draw.textlength(l, font=font) for l in lines]
        if max(widths, default=0) <= max_width:
            return font, lines
        size -= 4
    return ImageFont.truetype(font_path, min_size), textwrap.wrap(text, width=30)

def draw_centered_lines(draw, lines, font, y_start, fill, line_spacing=1.35):
    y = y_start
    for line in lines:
        w = draw.textlength(line, font=font)
        draw.text(((W - w) / 2, y), line, font=font, fill=fill)
        y += font.size * line_spacing
    return y

def make_quote_slide(quote, index, total, tag=None):
    img = Image.new("RGB", (W, H), BG_COLOR)
    d = ImageDraw.Draw(img)

    # top accent line + slide counter
    d.line([(80, 90), (140, 90)], fill=ACCENT_COLOR, width=4)
    counter_font = ImageFont.truetype(FONT_MEDIUM, 28)
    d.text((W - 80 - d.textlength(f"{index:02d}/{total:02d}", font=counter_font), 76),
            f"{index:02d}/{total:02d}", font=counter_font, fill=MUTED_COLOR)

    # quote mark
    mark_font = ImageFont.truetype(FONT_BOLD, 110)
    d.text((72, 140), "\u201C", font=mark_font, fill=ACCENT_COLOR)

    # main quote text, vertically centered-ish
    font, lines = wrap_and_fit(d, quote, FONT_QUOTE, W - 160, start_size=76)
    total_h = len(lines) * font.size * 1.35
    y_start = (H - total_h) / 2
    draw_centered_lines(d, lines, font, y_start, TEXT_COLOR)

    # optional tag / theme label bottom-left
    if tag:
        tag_font = ImageFont.truetype(FONT_MEDIUM, 26)
        d.text((72, H - 100), tag.upper(), font=tag_font, fill=ACCENT_COLOR)

    # handle bottom-right
    handle_font = ImageFont.truetype(FONT_LIGHT, 26)
    hw = d.textlength(HANDLE, font=handle_font)
    d.text((W - 72 - hw, H - 100), HANDLE, font=handle_font, fill=MUTED_COLOR)

    return img

def make_cta_slide(headline="Solitude builds what\ncrowds destroy.", sub="Follow for daily discipline."):
    img = Image.new("RGB", (W, H), BG_COLOR)
    d = ImageDraw.Draw(img)
    d.line([(W/2 - 40, 110), (W/2 + 40, 110)], fill=ACCENT_COLOR, width=4)

    font = ImageFont.truetype(FONT_BOLD, 66)
    lines = headline.split("\n")
    total_h = len(lines) * font.size * 1.3
    y = (H - total_h) / 2 - 60
    draw_centered_lines(d, lines, font, y, TEXT_COLOR, line_spacing=1.3)

    sub_font = ImageFont.truetype(FONT_MEDIUM, 30)
    sw = d.textlength(sub, font=sub_font)
    d.text(((W - sw) / 2, y + total_h + 40), sub, font=sub_font, fill=ACCENT_COLOR)

    handle_font = ImageFont.truetype(FONT_LIGHT, 28)
    hw = d.textlength(HANDLE, font=handle_font)
    d.text(((W - hw) / 2, H - 110), HANDLE, font=handle_font, fill=MUTED_COLOR)
    return img

def build_carousel(slides_text, tag, out_dir, slug):
    # Instagram's Content Publishing API only officially supports JPEG for
    # photo/carousel items -- PNG uploads "succeed" at the raw-file level but
    # get rejected by Instagram's media fetcher with a vague "doesn't meet our
    # requirements" error. Always save as .jpg (RGB, no alpha) for this reason.
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    total = len(slides_text) + 1  # + CTA slide
    for i, q in enumerate(slides_text, start=1):
        img = make_quote_slide(q, i, total, tag=tag)
        p = f"{out_dir}/{slug}_{i:02d}.jpg"
        img.convert("RGB").save(p, "JPEG", quality=92)
        paths.append(p)
    cta = make_cta_slide()
    p = f"{out_dir}/{slug}_{total:02d}.jpg"
    cta.convert("RGB").save(p, "JPEG", quality=92)
    paths.append(p)
    return paths

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from quote_generator import get_batch
    batch = get_batch(n=3)
    slides = [q["text"] for q in batch]
    tag = batch[0]["tag"]
    paths = build_carousel(slides, tag=tag, out_dir="posts_test", slug="test")
    print(json.dumps(paths, indent=2))
