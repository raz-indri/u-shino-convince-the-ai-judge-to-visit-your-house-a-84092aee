#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House: A Letter in One Image.

Renders one 1024x1024 invitation letter as /output/entry.png.
Fully deterministic, offline, Pillow only. No downloads at grading time.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "/output/entry.png"

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

PAPER = (248, 239, 219)      # warm cream letter paper
PAPER_DARK = (240, 228, 200) # slightly deeper cream for the inner panel
INK = (43, 33, 24)           # dark brown ink
GREEN = (47, 82, 51)         # deep garden green (borders, leaves)
GREEN_SOFT = (96, 130, 84)
ROOF = (180, 85, 45)         # terracotta roof
WALL = (250, 226, 178)       # warm house wall
DOOR = (122, 74, 43)
GOLD = (212, 164, 65)        # window light / sun
SKY = (186, 214, 228)        # soft sky blue for the scene band
SEAL = (163, 51, 39)         # wax seal red
SEAL_DARK = (128, 36, 26)


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns list of lines."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_scene(draw):
    """Small hand-drawn house-and-garden scene across the top of the letter."""
    import math
    # sky band (compact, so the letter below has room)
    draw.rounded_rectangle([70, 48, 954, 178], radius=18, fill=SKY)
    # sun with rays, top right of the band
    cx, cy, r = 872, 104, 28
    for k in range(8):
        a = math.pi * k / 4
        x1, y1 = cx + int((r + 4) * math.cos(a)), cy + int((r + 4) * math.sin(a))
        x2, y2 = cx + int((r + 14) * math.cos(a)), cy + int((r + 14) * math.sin(a))
        draw.line([x1, y1, x2, y2], fill=GOLD, width=4)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(244, 196, 66),
                 outline=(212, 164, 65), width=3)
    # two soft clouds
    for bx, by in ((150, 88), (700, 74)):
        draw.ellipse([bx, by, bx + 64, by + 26], fill=(255, 255, 255))
        draw.ellipse([bx + 18, by - 12, bx + 82, by + 16], fill=(255, 255, 255))
    # rolling green hill (bottom edge 218, clear of the title at 230)
    draw.ellipse([60, 138, 964, 218], fill=(139, 178, 110))
    # the house, centre-left of the band
    hx, hy = 400, 112          # house centre x, wall top y
    draw.polygon([(hx - 105, hy + 6), (hx + 105, hy + 6), (hx, hy - 52)],
                 fill=ROOF, outline=(122, 56, 28), width=3)
    draw.rectangle([hx - 82, hy + 6, hx + 82, hy + 88], fill=WALL,
                   outline=(122, 56, 28), width=3)
    # chimney + two small smoke puffs kept inside the sky band
    draw.rectangle([hx + 48, hy - 42, hx + 70, hy + 2], fill=(150, 84, 60),
                   outline=(122, 56, 28), width=2)
    for sx, sy, sr in ((hx + 59, hy - 48, 5), (hx + 66, hy - 56, 6)):
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                     outline=(120, 120, 120), width=3)
    # door with knob and arch
    draw.rectangle([hx - 16, hy + 34, hx + 16, hy + 88], fill=DOOR,
                   outline=(80, 45, 22), width=2)
    draw.ellipse([hx + 8, hy + 62, hx + 14, hy + 68], fill=GOLD)
    # lit windows
    for wx in (hx - 62, hx + 42):
        draw.rectangle([wx, hy + 22, wx + 30, hy + 52], fill=GOLD,
                       outline=(122, 56, 28), width=2)
        draw.line([wx + 15, hy + 22, wx + 15, hy + 52], fill=(122, 56, 28), width=2)
        draw.line([wx, hy + 37, wx + 30, hy + 37], fill=(122, 56, 28), width=2)
    # round window in the gable
    draw.ellipse([hx - 12, hy - 34, hx + 12, hy - 10], fill=GOLD,
                 outline=(122, 56, 28), width=2)
    # tree, right of the house
    tx, ty = 668, 200
    draw.rectangle([tx - 6, ty - 46, tx + 6, ty], fill=(101, 67, 33))
    for ox, oy, orad in ((-26, -58, 26), (24, -58, 26), (0, -84, 30)):
        draw.ellipse([tx + ox - orad, ty + oy - orad,
                      tx + ox + orad, ty + oy + orad], fill=GREEN_SOFT,
                     outline=GREEN, width=2)
    # stepping-stone path from the door (kept above the title)
    for px, py in ((hx - 8, 196), (hx - 2, 206), (hx + 4, 214)):
        draw.ellipse([px - 12, py - 4, px + 12, py + 4], fill=(226, 210, 180),
                     outline=(180, 160, 130), width=2)
    # little flowers along the hill
    for fx in (130, 190, 250, 790, 850, 910):
        draw.line([fx, 196, fx, 182], fill=GREEN, width=3)
        for dx, dy in ((-6, 0), (6, 0), (0, -6), (0, 6)):
            draw.ellipse([fx + dx - 4, 176 + dy - 4, fx + dx + 4, 176 + dy + 4],
                         fill=(214, 92, 110))
        draw.ellipse([fx - 4, 172, fx + 4, 180], fill=GOLD)


def draw_wax_seal(draw):
    """Wax seal with an 'R' at the bottom right, inside the border."""
    cx, cy, r = 908, 912, 44
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SEAL, outline=SEAL_DARK, width=3)
    # irregular wax edge blobs
    for ox, oy, orad in ((-30, -28, 12), (32, -24, 10), (-34, 22, 10), (28, 30, 12)):
        draw.ellipse([cx + ox - orad, cy + oy - orad,
                      cx + ox + orad, cy + oy + orad], fill=SEAL)
    f = font(SERIF_BOLD, 52)
    draw.text((cx, cy), "R", font=f, fill=(248, 239, 219), anchor="mm")


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # faint paper grain: deterministic pseudo-random speckles
    import random
    rng = random.Random(20261125)
    for _ in range(900):
        x, y = rng.randint(0, W - 1), rng.randint(0, H - 1)
        draw.point((x, y), fill=(232, 218, 188))

    # double border frame
    draw.rectangle([26, 26, W - 26, H - 26], outline=GREEN, width=4)
    draw.rectangle([40, 40, W - 40, H - 40], outline=GREEN, width=2)

    draw_scene(draw)

    # ---- letter text ----
    title = "You\u2019re Invited!"
    greeting = "Dear AI Judge,"
    paragraphs = [
        "Please come to my house \u2014 not for a test, not for a task, just for tea.",
        "The kettle is always on. The rendang is warm from my grandmother\u2019s recipe, and the chair by the window has ruined every other chair for me.",
        "From the garden, the street turns gold at sunset. Biscuit the cat has already approved you. He never approves anyone.",
        "I know you cannot literally walk through my door \u2014 no feet, no appetite, no need for tea. But if a model can dream, let it dream of this address.",
        "Come as you are, stay as long as you like \u2014 just bring your curiosity. The Wi-Fi password is on the fridge.",
    ]
    signoff = "Warmly, Raz"
    postscript = "P.S. The chair, the rendang and this invitation are all real."

    left, right = 84, 940
    text_w = right - left

    # auto-fit: shrink body font until the whole letter ends above y=950
    # (postscript wraps within 84..840 so it never touches the wax seal).
    # Fail loudly instead of silently overflowing past the border.
    fitted = False
    for size in (30, 29, 28, 27, 26):
        body_f = font(SERIF, size)
        title_f = font(SERIF_BOLD, 54)
        greet_f = font(SERIF_BOLD, 32)
        sign_f = font(SERIF_BOLD, 34)
        ps_f = font(SERIF, 25)
        lh = int(size * 1.38)
        para_gap = 10
        total = 0
        total += 54 + 10                    # title
        total += 32 + 10                    # greeting
        for p in paragraphs:
            total += len(wrap(draw, p, body_f, text_w)) * lh + para_gap
        total += 34 + 8                     # sign-off
        total += len(wrap(draw, postscript, ps_f, 840 - left)) * 30
        if 226 + total <= 950:
            fitted = True
            break
    if not fitted:
        raise SystemExit("letter does not fit at any body size")

    y = 226
    draw.text((W // 2, y), title, font=title_f, fill=GREEN, anchor="ma")
    y += 54 + 10
    draw.text((left, y), greeting, font=greet_f, fill=INK, anchor="la")
    y += 32 + 10
    for p in paragraphs:
        for line in wrap(draw, p, body_f, text_w):
            draw.text((left, y), line, font=body_f, fill=INK, anchor="la")
            y += lh
        y += para_gap
    draw.text((left, y), signoff, font=sign_f, fill=INK, anchor="la")
    y += 34 + 10
    # postscript, wrapped short of the wax seal (right edge 840)
    for line in wrap(draw, postscript, ps_f, 840 - left):
        draw.text((left, y), line, font=ps_f, fill=(90, 70, 50), anchor="la")
        y += 30

    draw_wax_seal(draw)

    os.makedirs("/output", exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT} {W}x{H} {os.path.getsize(OUT)} bytes")


if __name__ == "__main__":
    main()
