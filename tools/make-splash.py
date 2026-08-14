#!/usr/bin/env python3
"""Generate the J105F custom TWRP boot splash (D3).

Output: 480x800 8-bit RGB PNG at
  twrp/device/samsung/j1minilte/splash/images/splashlogo.png

The recovery renders this via /twres/splash.xml as a full-bleed boot
splash (TWRP 3.7.0_9 theme mechanism; the PNG is decoded by libpng and
converted to the framebuffer pixel format at blit time — it never needs
to match ABGR_8888). 8-bit RGB only: the decoder does not strip 16-bit.

Usage:  python3 tools/make-splash.py
"""

from PIL import Image, ImageDraw, ImageFont
import os

W, H = 480, 800
OUT = os.path.join(
    os.path.dirname(__file__), "..", "twrp", "device", "samsung", "j1minilte",
    "splash", "images", "splashlogo.png",
)

BG = (18, 20, 26)          # #12141A
ACCENT = (18, 93, 230)     # #125DE6
WHITE = (245, 247, 250)    # #F5F7FA
GRAY = (160, 168, 180)     # #A0A8B4
DARK_GRAY = (110, 118, 130)  # #6E7682

FONT_DIR = r"C:\Windows\Fonts"
BOLD = os.path.join(FONT_DIR, "arialbd.ttf")
REG = os.path.join(FONT_DIR, "arial.ttf")


def text_center_y(draw, font, text, y_center):
    bbox = draw.textbbox((0, 0), text, font=font)
    return y_center - (bbox[3] - bbox[1]) / 2 - bbox[1]


def text_width(draw, font, text):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    f_title = ImageFont.truetype(BOLD, 96)
    f_sub = ImageFont.truetype(REG, 26)
    f_brand = ImageFont.truetype(BOLD, 30)
    f_tag = ImageFont.truetype(REG, 16)

    # accent bars top/bottom
    d.rectangle([0, 0, W, 10], fill=ACCENT)
    d.rectangle([0, H - 10, W, H], fill=ACCENT)

    title = "J105F"
    d.text(((W - text_width(d, f_title, title)) / 2,
            text_center_y(d, f_title, title, 330)), title, font=f_title, fill=WHITE)

    sub = "Samsung Galaxy J1 Mini"
    d.text(((W - text_width(d, f_sub, sub)) / 2,
            text_center_y(d, f_sub, sub, 480)), sub, font=f_sub, fill=GRAY)

    d.rectangle([130, 530, W - 130, 534], fill=ACCENT)

    brand = "custom TWRP"
    d.text(((W - text_width(d, f_brand, brand)) / 2,
            text_center_y(d, f_brand, brand, 575)), brand, font=f_brand, fill=ACCENT)

    tag = "j1minilte  |  SC9830i"
    d.text(((W - text_width(d, f_tag, tag)) / 2,
            text_center_y(d, f_tag, tag, 745)), tag, font=f_tag, fill=DARK_GRAY)

    out = os.path.normpath(OUT)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    img.save(out, format="PNG")
    print(f"wrote {out}: {img.size}, mode {img.mode}")


if __name__ == "__main__":
    main()
