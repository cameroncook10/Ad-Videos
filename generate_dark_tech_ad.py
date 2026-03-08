#!/usr/bin/env python3
"""
Dark-Tech Cinematic Product Ad Generator
─────────────────────────────────────────
Cinematic dark-tech product ad. Black background, neon green (#00E5A0) accent.
Aesthetic: biohacker meets luxury tech — Apple meets clinical precision.
55 seconds total. 1080x1920 (9:16). 30fps.

Scenes:
  1. ECG pulse line on black (0-8s)
  2. Chaos flash cuts - scattered papers/screens (8-16s)
  3. Smartphone rises from darkness, UI reveal (16-28s)
  4. Quick-cut montage - wearable, body scan, testimonials (28-38s)
  5. Sonar pulse + "PROTOCOL. TRACKED." typography (38-48s)
  6. Logo reveal - PEPTIDE AI (48-55s)
"""

import math
import os
import random
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ─── CONFIG ───────────────────────────────────────────────────────────────────
W, H = 1080, 1920
FPS = 30
OUTPUT_DIR = "/home/user/Ad-Videos/output"
FRAMES_DIR = os.path.join(OUTPUT_DIR, "dark_tech_frames")
CROSSFADE_FRAMES = 12

# ─── COLORS ───────────────────────────────────────────────────────────────────
BG = (0, 0, 0)
GREEN = (0, 229, 160)        # #00E5A0
GREEN_BRIGHT = (0, 255, 180)
GREEN_DIM = (0, 110, 70)
GREEN_DARK = (0, 42, 28)
GREEN_GLOW = (0, 200, 130)
GREEN_SUBTLE = (0, 65, 42)

WHITE = (255, 255, 255)
GRAY_200 = (200, 200, 200)
GRAY_400 = (140, 140, 140)
GRAY_600 = (70, 70, 70)
BLACK = (0, 0, 0)

TEAL_SHADOW = (0, 20, 25)    # dark teal shadows for color grade

# ─── FONTS ────────────────────────────────────────────────────────────────────
FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FONT_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


# ─── EASING ───────────────────────────────────────────────────────────────────
def ease_out(t):
    t = max(0, min(1, t))
    return 1 - (1 - t) ** 3

def ease_in(t):
    t = max(0, min(1, t))
    return t * t * t

def ease_in_out(t):
    t = max(0, min(1, t))
    return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2

def ease_out_back(t):
    t = max(0, min(1, t))
    c = 1.70158
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2

def lerp(a, b, t):
    return a + (b - a) * max(0, min(1, t))

def color_lerp(c1, c2, t):
    t = max(0, min(1, t))
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


# ─── DRAWING HELPERS ──────────────────────────────────────────────────────────
def tw(draw, text, f):
    bb = draw.textbbox((0, 0), text, font=f)
    return bb[2] - bb[0]

def th(draw, text, f):
    bb = draw.textbbox((0, 0), text, font=f)
    return bb[3] - bb[1]

def draw_text_centered(draw, y, text, f, color):
    w = tw(draw, text, f)
    draw.text(((W - w) // 2, y), text, font=f, fill=color)

def rounded_rect(draw, box, r, fill=None, outline=None, width=1):
    x1, y1, x2, y2 = [int(v) for v in box]
    r = min(r, (x2 - x1) // 2, (y2 - y1) // 2)
    if r < 1:
        if fill:
            draw.rectangle([x1, y1, x2, y2], fill=fill)
        if outline:
            draw.rectangle([x1, y1, x2, y2], outline=outline, width=width)
        return
    if fill:
        draw.rectangle([x1 + r, y1, x2 - r, y2], fill=fill)
        draw.rectangle([x1, y1 + r, x2, y2 - r], fill=fill)
        draw.pieslice([x1, y1, x1 + 2*r, y1 + 2*r], 180, 270, fill=fill)
        draw.pieslice([x2 - 2*r, y1, x2, y1 + 2*r], 270, 360, fill=fill)
        draw.pieslice([x1, y2 - 2*r, x1 + 2*r, y2], 90, 180, fill=fill)
        draw.pieslice([x2 - 2*r, y2 - 2*r, x2, y2], 0, 90, fill=fill)
    if outline:
        draw.arc([x1, y1, x1 + 2*r, y1 + 2*r], 180, 270, fill=outline, width=width)
        draw.arc([x2 - 2*r, y1, x2, y1 + 2*r], 270, 360, fill=outline, width=width)
        draw.arc([x1, y2 - 2*r, x1 + 2*r, y2], 90, 180, fill=outline, width=width)
        draw.arc([x2 - 2*r, y2 - 2*r, x2, y2], 0, 90, fill=outline, width=width)
        draw.line([x1 + r, y1, x2 - r, y1], fill=outline, width=width)
        draw.line([x1 + r, y2, x2 - r, y2], fill=outline, width=width)
        draw.line([x1, y1 + r, x1, y2 - r], fill=outline, width=width)
        draw.line([x2, y1 + r, x2, y2 - r], fill=outline, width=width)


def glow_text(img, pos, text, f, color, radius=20, glow_alpha=80):
    x, y = pos
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    c = color if len(color) == 4 else (*color, 255)
    gd.text((x, y), text, font=f, fill=(c[0], c[1], c[2], glow_alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=radius))
    result = Image.alpha_composite(img.convert("RGBA"), glow)
    rd = ImageDraw.Draw(result)
    rd.text((x, y), text, font=f, fill=c)
    return result


def glow_text_centered(img, y, text, f, color, radius=20, glow_alpha=80):
    d = ImageDraw.Draw(img)
    w = tw(d, text, f)
    x = (W - w) // 2
    return glow_text(img, (x, y), text, f, color, radius, glow_alpha)


# ─── VIGNETTE ─────────────────────────────────────────────────────────────────
_vignette_cache = None
def get_vignette():
    global _vignette_cache
    if _vignette_cache is not None:
        return _vignette_cache
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    cx, cy = W // 2, H // 2
    max_r = int(math.sqrt(cx*cx + cy*cy))
    for r in range(max_r, int(max_r * 0.35), -3):
        ratio = (r - max_r * 0.35) / (max_r * 0.65)
        a = int(160 * ratio * ratio)
        vd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0, 0, 0, a))
    _vignette_cache = vig
    return vig

def apply_vignette(img):
    return Image.alpha_composite(img.convert("RGBA"), get_vignette())


# ─── ANAMORPHIC LENS FLARE ───────────────────────────────────────────────────
def draw_lens_flare(base_img, x, y, intensity=1.0, width=600):
    """Horizontal anamorphic lens flare streak — optimized."""
    flare = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(flare)
    hw = width // 2
    # Draw horizontal streak as line segments instead of per-pixel
    for dy in range(-3, 4):
        ya_factor = (1 - abs(dy) / 4)
        a = int(40 * ya_factor * intensity)
        if a > 0:
            fd.line([(x - hw, y + dy), (x + hw, y + dy)],
                    fill=(0, 180, 120, a), width=1)
    # Central bright spot
    for r in range(30, 0, -4):
        ratio = r / 30
        a = int(60 * (1 - ratio) * intensity)
        fd.ellipse([x - r, y - r, x + r, y + r],
                   fill=(200, 255, 230, a))
    return Image.alpha_composite(base_img.convert("RGBA"), flare)


# ─── NOISE TEXTURE ───────────────────────────────────────────────────────────
def apply_noise(img, amount=8, seed=None):
    """Subtle film grain — fast version using sparse dots."""
    if seed is not None:
        random.seed(seed)
    noise = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(noise)
    for _ in range(W * H // 300):
        x = random.randint(0, W - 1)
        y = random.randint(0, H - 1)
        v = random.randint(0, amount)
        nd.point((x, y), fill=(v, v, v, 30))
    return Image.alpha_composite(img.convert("RGBA"), noise)


# ─── CINEMATIC ATMOSPHERE ────────────────────────────────────────────────────
def make_dark_atmosphere(frame=0, intensity=0.5):
    """Pure black with subtle dark teal fog drift."""
    img = Image.new("RGB", (W, H), BG)
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)

    drift_x = int(math.sin(frame * 0.006) * 50)
    drift_y = int(math.cos(frame * 0.004) * 30)
    cx, cy = W // 2, H // 2

    # Very subtle teal center glow (coarser steps for speed)
    for r in range(700, 0, -30):
        ratio = r / 700
        a = int(10 * ratio * intensity)
        g = int(lerp(15, 40, ratio))
        fd.ellipse([cx + drift_x - r, cy + drift_y - r,
                     cx + drift_x + r, cy + drift_y + r],
                   fill=(0, g, int(g * 0.8), a))

    img = Image.alpha_composite(img.convert("RGBA"), fog).convert("RGB")
    return img


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCENE 1: ECG PULSE LINE (0-8s)
# Single glowing green ECG line pulses across pure black — slow, clinical, ominous
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def ecg_waveform(x, phase=0):
    """Generate ECG-like waveform value at position x with phase offset."""
    x = (x + phase) % 400
    if 140 < x < 155:
        return -15 * math.sin((x - 140) / 15 * math.pi)
    elif 155 <= x < 170:
        return 80 * math.sin((x - 155) / 15 * math.pi)
    elif 170 <= x < 185:
        return -25 * math.sin((x - 170) / 15 * math.pi)
    elif 185 <= x < 210:
        return 20 * math.sin((x - 185) / 25 * math.pi)
    elif 210 <= x < 230:
        return 8 * math.sin((x - 210) / 20 * math.pi)
    else:
        return random.gauss(0, 0.3)


def scene_ecg_pulse(frame, total):
    t = frame / total
    img = make_dark_atmosphere(frame, intensity=0.3)

    ecg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ed = ImageDraw.Draw(ecg)

    cy = H // 2
    # Line draws from left to right over time
    draw_width = int(W * min(1.0, t * 1.5))
    phase = frame * 3.5  # slow scroll

    # ECG glow trail
    random.seed(frame // 3)
    points = []
    for x in range(0, draw_width):
        y_val = ecg_waveform(x, phase)
        y = int(cy + y_val)
        points.append((x, y))

    if len(points) > 1:
        # Outer glow (simplified — 3 passes instead of 169)
        for w, a in [(9, 8), (6, 20), (4, 50)]:
            ed.line(points, fill=(0, 200, 140, a), width=w)

        # Inner glow
        ed.line(points, fill=(0, 229, 160, 120), width=3)
        # Core line
        ed.line(points, fill=(0, 255, 200, 220), width=2)

        # Bright leading dot
        if draw_width > 2:
            lx, ly = points[-1]
            pulse = 0.6 + 0.4 * math.sin(frame * 0.15)
            for r in range(25, 0, -1):
                da = int(50 * (1 - r / 25) * pulse)
                ed.ellipse([lx - r, ly - r, lx + r, ly + r],
                           fill=(0, 229, 160, da))
            ed.ellipse([lx - 3, ly - 3, lx + 3, ly + 3],
                       fill=(200, 255, 230, 220))

    img = Image.alpha_composite(img.convert("RGBA"), ecg)

    # Subtle horizontal scan lines for CRT feel
    scan = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    for y in range(0, H, 4):
        sd.line([(0, y), (W, y)], fill=(0, 0, 0, 15), width=1)
    img = Image.alpha_composite(img, scan)

    img = apply_vignette(img)
    img = apply_noise(img, amount=6, seed=frame)
    return img.convert("RGB")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCENE 2: CHAOS FLASH CUTS (8-16s)
# Rapid flash cuts of scattered papers/phone screens — desaturated, grainy
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def draw_scattered_papers(img, seed, alpha=255):
    """Draw abstract scattered paper/document shapes."""
    draw = ImageDraw.Draw(img)
    random.seed(seed)
    for _ in range(random.randint(6, 12)):
        x = random.randint(50, W - 200)
        y = random.randint(100, H - 300)
        pw = random.randint(120, 280)
        ph = random.randint(160, 350)
        angle_bias = random.uniform(-0.15, 0.15)
        # Paper background
        gray = random.randint(20, 40)
        draw.rectangle([x, y, x + pw, y + ph], fill=(gray, gray, gray, alpha))
        # Text lines on paper
        for ly in range(y + 20, y + ph - 15, random.randint(14, 22)):
            lw = random.randint(pw // 3, pw - 20)
            lx = x + random.randint(10, 20)
            g = random.randint(50, 80)
            draw.line([(lx, ly), (lx + lw, ly)], fill=(g, g, g, alpha), width=2)
    return img


def draw_phone_screen_chaos(img, seed, alpha=255):
    """Draw abstract phone screens with chaotic data."""
    draw = ImageDraw.Draw(img)
    random.seed(seed)
    for _ in range(random.randint(2, 4)):
        px = random.randint(100, W - 300)
        py = random.randint(200, H - 500)
        pw, ph = random.randint(160, 240), random.randint(280, 420)
        # Phone outline
        rounded_rect(draw, [px, py, px + pw, py + ph], 20,
                     fill=(15, 15, 18, alpha), outline=(50, 50, 55, alpha), width=2)
        # Screen content - random bars/graphs
        for _ in range(random.randint(4, 8)):
            bx = px + random.randint(15, pw - 60)
            by = py + random.randint(40, ph - 30)
            bw = random.randint(30, pw - 40)
            bh = random.randint(3, 8)
            g = random.randint(30, 60)
            draw.rectangle([bx, by, bx + bw, by + bh], fill=(g, g, g, alpha))
        # Red/orange warning indicators
        for _ in range(random.randint(1, 3)):
            cx = px + random.randint(20, pw - 20)
            cy = py + random.randint(30, ph - 30)
            draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4],
                         fill=(180, 60, 40, alpha))
    return img


def scene_chaos(frame, total):
    t = frame / total

    # Flash cut timing - each "cut" lasts 8-15 frames
    cut_lengths = [10, 8, 12, 9, 11, 8, 14, 10, 8, 12, 9, 11, 13, 8, 10, 12, 9, 8, 11, 10, 9, 8, 12, 10]
    cut_idx = 0
    acc = 0
    for i, cl in enumerate(cut_lengths):
        if acc + cl > frame:
            cut_idx = i
            break
        acc += cl
    else:
        cut_idx = len(cut_lengths) - 1

    local_frame = frame - acc
    cut_len = cut_lengths[min(cut_idx, len(cut_lengths) - 1)]

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))

    # Alternate between paper chaos and phone chaos
    seed = cut_idx * 137 + 42
    if cut_idx % 3 == 0:
        img = draw_scattered_papers(img, seed)
    elif cut_idx % 3 == 1:
        img = draw_phone_screen_chaos(img, seed)
    else:
        img = draw_scattered_papers(img, seed)
        img = draw_phone_screen_chaos(img, seed + 77)

    # Flash on cut transitions (bright flash at start of each cut)
    if local_frame < 2:
        flash_a = int(120 * (1 - local_frame / 2))
        flash = Image.new("RGBA", (W, H), (255, 255, 255, flash_a))
        img = Image.alpha_composite(img, flash)

    # Desaturation - make everything gray-ish (already gray, but darken)
    # Add grain heavily
    img = apply_noise(img, amount=25, seed=frame)

    # CRT scan lines (heavier for chaos feel)
    scan = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    for y in range(0, H, 3):
        sd.line([(0, y), (W, y)], fill=(0, 0, 0, 25), width=1)
    img = Image.alpha_composite(img, scan)

    # Occasional glitch - horizontal displacement
    if cut_idx % 4 == 2 and local_frame < 3:
        # Simple glitch: shift a band of pixels
        result = img.copy()
        band_y = random.randint(H // 4, 3 * H // 4)
        band_h = random.randint(20, 80)
        shift = random.randint(-50, 50)
        band = img.crop((max(0, -shift), band_y, min(W, W - shift), band_y + band_h))
        result.paste(band, (max(0, shift), band_y))
        img = result

    # Dark overlay for ominous feel
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 60))
    img = Image.alpha_composite(img, dark)

    img = apply_vignette(img)
    return img.convert("RGB")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCENE 3: SMARTPHONE RISES FROM DARKNESS (16-28s)
# Sleek black phone rises in slow motion, screen illuminates with dark UI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def draw_phone_ui(draw, img, px, py, pw, ph, t, frame):
    """Draw the clean dark UI with green labels on the phone screen."""
    sx = px + 22
    sy = py + 55
    sw = pw - 44

    # Status bar
    f_time = font(FONT_BOLD, 13)
    draw.text((sx + 10, py + 12), "9:41", font=f_time, fill=(*WHITE, 200))

    # Notch
    nw, nh = 120, 26
    nx = px + pw // 2 - nw // 2
    rounded_rect(draw, [nx, py, nx + nw, py + nh], 13, fill=(0, 0, 0, 255))

    # Header
    ui_t = max(0, (t - 0.25) / 0.15)
    if ui_t > 0:
        et = ease_out(min(1, ui_t))
        a = int(255 * et)

        f_label = font(FONT_BOLD, 11)
        f_title = font(FONT_BOLD, 28)

        draw.text((sx + 14, sy), "ACTIVE PROTOCOL", font=f_label, fill=(*GREEN, a))
        draw.text((sx + 14, sy + 18), "Daily Stack", font=f_title, fill=(*WHITE, a))

    # Protocol cards
    protocols = [
        ("BPC-157", "250mcg", "SubQ", "Daily"),
        ("Semax", "300mcg", "Nasal", "Daily"),
        ("GHK-Cu", "200mcg", "SubQ", "3x/week"),
    ]

    card_start_t = 0.35
    for i, (name, dose, route, freq) in enumerate(protocols):
        card_t = max(0, (t - card_start_t - i * 0.06) / 0.12)
        if card_t <= 0:
            continue
        et = ease_out(min(1, card_t))
        a = int(255 * et)
        y_off = int(lerp(20, 0, et))

        cy = sy + 70 + i * 105 + y_off
        # Card background
        rounded_rect(draw, [sx + 8, cy, sx + sw - 8, cy + 88], 14,
                     fill=(10, 18, 14, a), outline=(0, 60, 40, a), width=1)

        f_name = font(FONT_BOLD, 22)
        f_detail = font(FONT_MONO, 14)
        f_freq = font(FONT_REG, 13)

        draw.text((sx + 24, cy + 12), name, font=f_name, fill=(*GREEN, a))

        detail = f"{dose}  ·  {route}"
        draw.text((sx + 24, cy + 42), detail, font=f_detail, fill=(*GRAY_200, a))
        draw.text((sx + 24, cy + 62), freq, font=f_freq, fill=(*GREEN_DIM, a))

        # Progress bar
        bar_x = sx + sw - 80
        bar_y = cy + 35
        bar_w = 50
        draw.rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + 4],
                       fill=(*GREEN_DARK, a))
        # Fill animation
        fill_t = max(0, (t - card_start_t - i * 0.06 - 0.1) / 0.15)
        fill_w = int(bar_w * ease_out(min(1, fill_t)))
        if fill_w > 0:
            draw.rectangle([bar_x, bar_y, bar_x + fill_w, bar_y + 4],
                           fill=(*GREEN, a))

        # Green glow dot (status)
        dot_x = sx + sw - 28
        dot_y = cy + 20
        pulse = 0.6 + 0.4 * math.sin(frame * 0.08 + i)
        dot_a = int(a * pulse)
        draw.ellipse([dot_x - 5, dot_y - 5, dot_x + 5, dot_y + 5],
                     fill=(*GREEN, dot_a))

    # Bottom nav hint
    nav_t = max(0, (t - 0.7) / 0.1)
    if nav_t > 0:
        na = int(150 * ease_out(min(1, nav_t)))
        nav_y = py + ph - 40
        # Nav dots
        for i in range(5):
            nx = px + pw // 2 - 60 + i * 30
            c = GREEN if i == 0 else GRAY_600
            draw.ellipse([nx - 3, nav_y - 3, nx + 3, nav_y + 3],
                         fill=(*c, na))


def scene_phone_rise(frame, total):
    t = frame / total
    img = make_dark_atmosphere(frame, intensity=0.4)

    # Phone dimensions
    pw, ph = 440, 820
    px = W // 2 - pw // 2

    # Rise animation: starts below screen, rises to center
    py_start = H + 100
    py_end = (H - ph) // 2 + 50
    rise_t = ease_out(min(1, t / 0.3))
    py = int(lerp(py_start, py_end, rise_t))

    # Phone shadow (dramatic, deep)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for s in range(50, 0, -2):
        sa = int(12 * (1 - s / 50))
        rounded_rect(sd, [px - s + 8, py - s + 15, px + pw + s + 8, py + ph + s + 15],
                     50, fill=(0, 0, 0, sa))
    img = Image.alpha_composite(img.convert("RGBA"), shadow)

    # Screen illumination glow
    if t > 0.15:
        glow_t = ease_out(min(1, (t - 0.15) / 0.2))
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gcx, gcy = px + pw // 2, py + ph // 2
        for r in range(300, 0, -5):
            ratio = r / 300
            ga = int(15 * ratio * glow_t)
            gd.ellipse([gcx - r, gcy - r, gcx + r, gcy + r],
                       fill=(0, 100, 70, ga))
        img = Image.alpha_composite(img, glow)

    draw = ImageDraw.Draw(img)

    # Phone body
    # Green edge glow
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    for g in range(15, 0, -1):
        ga = int(5 * (1 - g / 15))
        rounded_rect(gd, [px - g, py - g, px + pw + g, py + ph + g], 46,
                     fill=(0, 200, 140, ga))
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img)

    # Phone body (pure black with subtle border)
    rounded_rect(draw, [px, py, px + pw, py + ph], 42, fill=(5, 8, 6, 255))
    rounded_rect(draw, [px, py, px + pw, py + ph], 42,
                 outline=(35, 50, 42, 255), width=2)

    # Draw UI content
    if t > 0.2:
        draw_phone_ui(draw, img, px, py, pw, ph, t, frame)

    # Lens flare when phone arrives
    if 0.25 < t < 0.45:
        flare_t = 1 - abs(t - 0.35) / 0.1
        flare_t = max(0, min(1, flare_t))
        img = draw_lens_flare(img, px + pw // 2, py + 100, intensity=flare_t * 0.8, width=800)

    img = apply_vignette(img)
    img = apply_noise(img, amount=5, seed=frame)
    return img.convert("RGB")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCENE 4: QUICK-CUT MONTAGE (28-38s)
# Wearable syncing, body scan outline, testimonial bubbles — each cut on beat
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def draw_wearable_sync(img, frame, t_local):
    """Wearable device with glowing data lines syncing."""
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2

    # Watch face outline (rounded square)
    ws = 220
    wx, wy = cx - ws // 2, cy - ws // 2 - 60
    rounded_rect(draw, [wx, wy, wx + ws, wy + ws], 40,
                 fill=(8, 12, 10, 255), outline=(*GREEN_DIM, 200), width=3)

    # Watch band hints
    draw.rectangle([cx - 50, wy - 60, cx + 50, wy], fill=(15, 20, 18, 255))
    draw.rectangle([cx - 50, wy + ws, cx + 50, wy + ws + 60], fill=(15, 20, 18, 255))

    # Heart rate display
    f_hr = font(FONT_MONO, 48)
    f_label = font(FONT_BOLD, 14)
    hr_val = str(int(72 + 3 * math.sin(frame * 0.1)))
    draw.text((wx + 30, wy + 30), "BPM", font=f_label, fill=(*GREEN, 200))
    draw.text((wx + 30, wy + 50), hr_val, font=f_hr, fill=(*GREEN_BRIGHT, 240))

    # Mini ECG on watch
    ecg_y = wy + 130
    points = []
    for x in range(ws - 40):
        val = ecg_waveform(x * 2, frame * 4) * 0.3
        points.append((wx + 20 + x, int(ecg_y + val)))
    if len(points) > 1:
        draw.line(points, fill=(*GREEN, 180), width=2)

    # Sync data lines radiating outward
    sync_t = ease_out(min(1, t_local / 0.5))
    num_lines = 8
    for i in range(num_lines):
        angle = (i / num_lines) * 2 * math.pi + frame * 0.02
        line_len = int(200 * sync_t + 30 * math.sin(frame * 0.05 + i))
        x1 = int(cx + (ws // 2 + 30) * math.cos(angle))
        y1 = int(cy - 60 + (ws // 2 + 30) * math.sin(angle))
        x2 = int(cx + (ws // 2 + 30 + line_len) * math.cos(angle))
        y2 = int(cy - 60 + (ws // 2 + 30 + line_len) * math.sin(angle))
        a = int(100 * (1 - i / num_lines) * sync_t)
        draw.line([(x1, y1), (x2, y2)], fill=(*GREEN, a), width=2)

        # Data dot at end
        if sync_t > 0.5:
            da = int(180 * (sync_t - 0.5) * 2)
            draw.ellipse([x2 - 4, y2 - 4, x2 + 4, y2 + 4], fill=(*GREEN, da))

    # "SYNCING..." text
    f_sync = font(FONT_MONO, 20)
    dots = "." * (1 + (frame // 8) % 3)
    draw_text_centered(draw, cy + ws // 2 + 40, f"SYNCING{dots}", f_sync, (*GREEN, 200))

    return img


def draw_body_scan(img, frame, t_local):
    """Human body outline with green dashed measurement lines."""
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2

    # Human figure outline (simplified)
    # Head
    head_r = 45
    head_y = cy - 320
    draw.ellipse([cx - head_r, head_y - head_r, cx + head_r, head_y + head_r],
                 outline=(*GREEN, 180), width=2)

    # Body outline points
    body_points = [
        # Shoulders
        (cx - 120, cy - 250), (cx + 120, cy - 250),
        # Torso
        (cx - 100, cy - 100), (cx + 100, cy - 100),
        # Hips
        (cx - 90, cy), (cx + 90, cy),
        # Legs
        (cx - 80, cy + 200), (cx + 80, cy + 200),
        # Feet
        (cx - 60, cy + 380), (cx + 60, cy + 380),
    ]

    # Draw body lines
    # Left side
    left = [(cx, head_y + head_r), (cx - 120, cy - 250), (cx - 100, cy - 100),
            (cx - 90, cy), (cx - 80, cy + 200), (cx - 60, cy + 380)]
    right = [(cx, head_y + head_r), (cx + 120, cy - 250), (cx + 100, cy - 100),
             (cx + 90, cy), (cx + 80, cy + 200), (cx + 60, cy + 380)]

    scan_progress = ease_out(min(1, t_local / 0.6))
    visible_points = max(2, int(len(left) * scan_progress))

    for side in [left[:visible_points], right[:visible_points]]:
        if len(side) > 1:
            draw.line(side, fill=(*GREEN, 160), width=2)

    # Arms
    if scan_progress > 0.3:
        arm_a = int(160 * min(1, (scan_progress - 0.3) / 0.3))
        draw.line([(cx - 120, cy - 250), (cx - 200, cy - 80), (cx - 220, cy + 30)],
                  fill=(*GREEN, arm_a), width=2)
        draw.line([(cx + 120, cy - 250), (cx + 200, cy - 80), (cx + 220, cy + 30)],
                  fill=(*GREEN, arm_a), width=2)

    # Dashed measurement lines with labels
    measurements = [
        (cy - 250, "Shoulders", "48.2 cm"),
        (cy - 100, "Chest", "102.5 cm"),
        (cy, "Waist", "82.1 cm"),
        (cy + 200, "Thigh", "56.8 cm"),
    ]

    for i, (my, label, value) in enumerate(measurements):
        m_t = max(0, (t_local - 0.2 - i * 0.08) / 0.15)
        if m_t <= 0:
            continue
        et = ease_out(min(1, m_t))
        ma = int(200 * et)

        # Dashed line extending to the right
        line_len = int(200 * et)
        for dx in range(0, line_len, 8):
            x1 = cx + 130 + dx
            x2 = min(cx + 130 + dx + 4, cx + 130 + line_len)
            draw.line([(x1, my), (x2, my)], fill=(*GREEN, ma), width=1)

        # Label and value
        f_label = font(FONT_BOLD, 14)
        f_val = font(FONT_MONO, 18)
        lx = cx + 140 + line_len + 10
        draw.text((lx, my - 20), label, font=f_label, fill=(*GREEN_DIM, ma))
        draw.text((lx, my - 2), value, font=f_val, fill=(*GREEN, ma))

    # Scanning line sweeping down
    scan_y = int(head_y - head_r + (cy + 400) * (t_local % 1.0))
    if scan_y < cy + 400:
        for dy in range(-15, 15):
            la = int(40 * (1 - abs(dy) / 15))
            draw.line([(cx - 250, scan_y + dy), (cx + 250, scan_y + dy)],
                      fill=(0, 229, 160, la), width=1)

    # "BODY SCAN" header
    f_title = font(FONT_BOLD, 36)
    draw_text_centered(draw, 160, "BODY SCAN", f_title, (*GREEN, 220))

    return img


def draw_testimonials(img, frame, t_local):
    """Testimonial speech bubbles floating upward."""
    draw = ImageDraw.Draw(img)
    cx = W // 2

    testimonials = [
        ("Recovery time cut in half", "Mike R.", 0.0),
        ("Sleep quality improved 40%", "Sarah K.", 0.15),
        ("Best tracking app I've used", "Dr. Chen", 0.3),
        ("Game changer for my protocol", "James L.", 0.45),
    ]

    f_quote = font(FONT_REG, 22)
    f_name = font(FONT_BOLD, 16)

    for i, (quote, name, delay) in enumerate(testimonials):
        bt = max(0, (t_local - delay) / 0.3)
        if bt <= 0:
            continue
        et = ease_out(min(1, bt))
        a = int(240 * et)

        # Float upward
        base_y = H // 2 - 200 + i * 160
        y = int(base_y - 30 * et)
        x_offset = (-1 if i % 2 == 0 else 1) * 80

        # Speech bubble
        bw = tw(draw, quote, f_quote) + 50
        bx = cx - bw // 2 + x_offset
        by = y

        # Bubble background
        rounded_rect(draw, [bx, by, bx + bw, by + 70], 18,
                     fill=(10, 18, 14, a), outline=(0, 80, 55, a), width=1)

        draw.text((bx + 25, by + 12), quote, font=f_quote, fill=(*WHITE, a))
        draw.text((bx + 25, by + 42), f"— {name}", font=f_name, fill=(*GREEN, a))

        # Upward arrow/icon
        arrow_x = bx + bw // 2
        arrow_y = by - 15
        if a > 100:
            draw.polygon([(arrow_x, arrow_y - 8), (arrow_x - 6, arrow_y),
                          (arrow_x + 6, arrow_y)], fill=(*GREEN, a // 2))

    return img


def scene_montage(frame, total):
    t = frame / total

    # 3 sub-scenes within the montage, quick-cut style
    # Each ~3.3s
    sub_duration = total // 3
    sub_idx = min(2, frame // sub_duration)
    sub_frame = frame - sub_idx * sub_duration
    sub_t = sub_frame / sub_duration

    img = make_dark_atmosphere(frame, intensity=0.35)

    # Flash on transitions
    if sub_frame < 3:
        flash_a = int(80 * (1 - sub_frame / 3))
        flash = Image.new("RGBA", (W, H), (255, 255, 255, flash_a))
        img = Image.alpha_composite(img.convert("RGBA"), flash)

    if sub_idx == 0:
        img = draw_wearable_sync(img.convert("RGBA"), frame, sub_t)
    elif sub_idx == 1:
        img = draw_body_scan(img.convert("RGBA"), frame, sub_t)
    else:
        img = draw_testimonials(img.convert("RGBA"), frame, sub_t)

    img = apply_vignette(img)
    img = apply_noise(img, amount=6, seed=frame)
    return img.convert("RGB")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCENE 5: SONAR PULSE + TYPOGRAPHY (38-48s)
# Close-up phone screen, green pulse rippling outward like sonar
# "PROTOCOL. TRACKED." appearing letter by letter
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def scene_sonar_typography(frame, total):
    t = frame / total
    img = Image.new("RGB", (W, H), BG)

    cx, cy = W // 2, H // 2

    # Sonar rings expanding outward
    sonar = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sonar)

    num_rings = 5
    for i in range(num_rings):
        ring_delay = i * 0.12
        ring_t = max(0, t - ring_delay)
        if ring_t <= 0:
            continue

        # Ring expands and fades
        ring_progress = (ring_t * 2) % 1.0
        ring_r = int(50 + 500 * ring_progress)
        ring_a = int(120 * (1 - ring_progress))

        if ring_a > 0:
            for dr in range(-3, 3):
                ra = int(ring_a * (1 - abs(dr) / 3))
                sd.ellipse([cx - ring_r + dr, cy - ring_r + dr,
                           cx + ring_r - dr, cy + ring_r - dr],
                          outline=(0, 229, 160, ra), width=2)

    # Center pulse dot
    pulse = 0.5 + 0.5 * math.sin(frame * 0.12)
    for r in range(40, 0, -1):
        ratio = r / 40
        pa = int(80 * (1 - ratio) * pulse)
        sd.ellipse([cx - r, cy - r, cx + r, cy + r],
                   fill=(0, 229, 160, pa))
    sd.ellipse([cx - 6, cy - 6, cx + 6, cy + 6],
               fill=(0, 255, 200, 200))

    img = Image.alpha_composite(img.convert("RGBA"), sonar)

    # Typography: "PROTOCOL. TRACKED." — letter by letter, white serif on black
    text1 = "PROTOCOL."
    text2 = "TRACKED."

    f_title = font(FONT_SERIF_BOLD, 80)

    # Text 1 appears after initial sonar
    if t > 0.25:
        char_t = (t - 0.25) / 0.25  # Time to type all chars
        visible_chars = int(len(text1) * min(1, char_t * 1.2))
        visible_text = text1[:visible_chars]

        if visible_text:
            fade = min(1, (t - 0.25) / 0.1)
            a = int(255 * fade)
            img = glow_text_centered(img, cy - 140, visible_text,
                                     f_title, (*WHITE, a),
                                     radius=15, glow_alpha=30)

            # Typing cursor
            if visible_chars < len(text1):
                d = ImageDraw.Draw(img)
                cursor_x = W // 2 + tw(d, visible_text, f_title) // 2 + 5
                if frame % 16 < 10:
                    d.rectangle([cursor_x, cy - 140, cursor_x + 3, cy - 65],
                                fill=(*GREEN, 200))

    # Text 2 appears later
    if t > 0.55:
        char_t = (t - 0.55) / 0.2
        visible_chars = int(len(text2) * min(1, char_t * 1.2))
        visible_text = text2[:visible_chars]

        if visible_text:
            fade = min(1, (t - 0.55) / 0.1)
            a = int(255 * fade)
            img = glow_text_centered(img, cy - 40, visible_text,
                                     f_title, (*WHITE, a),
                                     radius=15, glow_alpha=30)

            if visible_chars < len(text2):
                d = ImageDraw.Draw(img)
                cursor_x = W // 2 + tw(d, visible_text, f_title) // 2 + 5
                if frame % 16 < 10:
                    d.rectangle([cursor_x, cy - 40, cursor_x + 3, cy + 35],
                                fill=(*GREEN, 200))

    # Subtle underline reveal
    if t > 0.8:
        line_t = ease_out(min(1, (t - 0.8) / 0.15))
        line_w = int(500 * line_t)
        line_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(line_layer)
        lx = cx - line_w // 2
        for dx in range(line_w):
            dist = abs(dx - line_w // 2) / (line_w // 2 + 1)
            la = int(80 * (1 - dist) * line_t)
            ld.line([(lx + dx, cy + 60), (lx + dx, cy + 60)],
                    fill=(0, 229, 160, la), width=2)
        img = Image.alpha_composite(img.convert("RGBA"), line_layer)

    img = apply_vignette(img)
    img = apply_noise(img, amount=5, seed=frame)
    return img.convert("RGB")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCENE 6: LOGO REVEAL (48-55s)
# Circular heartbeat icon in green, "PEPTIDE AI" text, slow fade to black
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def draw_heartbeat_icon(img, cx, cy, size, alpha, frame):
    """Draw a circular heartbeat/pulse icon."""
    icon = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    id = ImageDraw.Draw(icon)

    r = size // 2

    # Outer circle glow
    for gr in range(r + 30, r, -1):
        ga = int(8 * (1 - (gr - r) / 30) * (alpha / 255))
        id.ellipse([cx - gr, cy - gr, cx + gr, cy + gr],
                   fill=(0, 229, 160, ga))

    # Main circle outline
    id.ellipse([cx - r, cy - r, cx + r, cy + r],
               outline=(0, 229, 160, alpha), width=3)

    # ECG line inside circle
    ecg_points = []
    for x in range(-r + 15, r - 15):
        val = ecg_waveform(x + r, frame * 2) * 0.35
        px = cx + x
        py = int(cy + val)
        ecg_points.append((px, py))

    if len(ecg_points) > 1:
        id.line(ecg_points, fill=(0, 229, 160, alpha), width=3)

    # Pulse effect on the circle (traveling dot)
    angle = (frame * 0.04) % (2 * math.pi)
    dot_x = int(cx + r * math.cos(angle))
    dot_y = int(cy + r * math.sin(angle))
    pulse_a = int(alpha * 0.8)
    for pr in range(12, 0, -1):
        pa = int(pulse_a * (1 - pr / 12) * 0.5)
        id.ellipse([dot_x - pr, dot_y - pr, dot_x + pr, dot_y + pr],
                   fill=(0, 255, 200, pa))

    return Image.alpha_composite(img.convert("RGBA"), icon)


def scene_logo_reveal(frame, total):
    t = frame / total
    img = Image.new("RGB", (W, H), BG)

    cx, cy = W // 2, H // 2 - 80

    # Icon scales up and fades in
    icon_t = ease_out_back(min(1, t / 0.3))
    if icon_t > 0:
        icon_size = int(160 * icon_t)
        icon_alpha = int(255 * min(1, t / 0.15))
        img = draw_heartbeat_icon(img, cx, cy, icon_size, icon_alpha, frame)

    # "PEPTIDE AI" text appears below
    if t > 0.2:
        text_t = ease_out(min(1, (t - 0.2) / 0.2))
        a = int(255 * text_t)
        y_off = int(lerp(20, 0, text_t))

        # Spaced caps
        f_brand = font(FONT_BOLD, 52)
        brand_text = "P E P T I D E   A I"
        img = glow_text_centered(img, cy + 130 + y_off, brand_text,
                                 f_brand, (*GREEN, a),
                                 radius=25, glow_alpha=60)

    # Tagline
    if t > 0.35:
        tag_t = ease_out(min(1, (t - 0.35) / 0.15))
        ta = int(200 * tag_t)
        f_tag = font(FONT_REG, 24)
        draw = ImageDraw.Draw(img)
        draw_text_centered(draw, cy + 200, "Intelligence for your protocol.",
                           f_tag, (*GRAY_400, ta))

    # Horizontal line under tagline
    if t > 0.4:
        line_t = ease_out(min(1, (t - 0.4) / 0.15))
        draw = ImageDraw.Draw(img)
        lw = int(250 * line_t)
        la = int(60 * line_t)
        draw.line([(cx - lw // 2, cy + 240), (cx + lw // 2, cy + 240)],
                  fill=(*GREEN_SUBTLE, la), width=1)

    # Fade to black at the end
    if t > 0.7:
        fade = ease_in(min(1, (t - 0.7) / 0.3))
        black_overlay = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * fade)))
        img = Image.alpha_composite(img.convert("RGBA"), black_overlay)

    img = apply_vignette(img)
    img = apply_noise(img, amount=4, seed=frame)
    return img.convert("RGB")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VIDEO GENERATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def crossfade(img1, img2, t):
    return Image.blend(img1, img2, t)


def generate_video():
    os.makedirs(FRAMES_DIR, exist_ok=True)

    scenes = [
        (scene_ecg_pulse,         8.0),   # ECG pulse on black
        (scene_chaos,             8.0),   # Chaos flash cuts
        (scene_phone_rise,       12.0),   # Smartphone rises, UI reveal
        (scene_montage,          10.0),   # Quick-cut montage
        (scene_sonar_typography, 10.0),   # Sonar + "PROTOCOL. TRACKED."
        (scene_logo_reveal,       7.0),   # Logo reveal + fade to black
    ]

    total_duration = sum(d for _, d in scenes)
    print(f"Total duration: {total_duration}s at {FPS}fps")
    cf = CROSSFADE_FRAMES

    # Pre-build vignette cache
    print("Building vignette cache...")
    get_vignette()

    # Render all scene frames
    all_scene_frames = []
    for idx, (fn, dur) in enumerate(scenes):
        n = int(dur * FPS)
        print(f"  Scene {idx + 1}/{len(scenes)}: {fn.__name__} ({n} frames, {dur}s)")
        frames = []
        for f in range(n):
            frames.append(fn(f, n))
            if f % 30 == 0:
                print(f"    {f}/{n}")
        all_scene_frames.append(frames)

    # Composite with crossfades
    print("Compositing crossfades...")
    frame_idx = 0

    for s_idx, frames in enumerate(all_scene_frames):
        n = len(frames)
        for f in range(n):
            if s_idx == 0 and f < cf:
                black = Image.new("RGB", (W, H), BG)
                img = crossfade(black, frames[f], f / cf)
            elif s_idx > 0 and f < cf:
                prev = all_scene_frames[s_idx - 1]
                pf = len(prev) - cf + f
                if 0 <= pf < len(prev):
                    img = crossfade(prev[pf], frames[f], f / cf)
                else:
                    img = frames[f]
            elif s_idx == len(all_scene_frames) - 1 and f >= n - cf:
                fade = (f - (n - cf)) / cf
                black = Image.new("RGB", (W, H), BG)
                img = crossfade(frames[f], black, fade)
            else:
                img = frames[f]
            img.save(os.path.join(FRAMES_DIR, f"frame_{frame_idx:05d}.png"))
            frame_idx += 1

    print(f"Total frames: {frame_idx}")

    output_path = os.path.join(OUTPUT_DIR, "dark-tech-product-ad.mp4")
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(FRAMES_DIR, "frame_%05d.png"),
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-r", str(FPS), output_path
    ]
    print(f"Encoding: {output_path}")
    subprocess.run(cmd, check=True)
    print("Video encoded successfully!")

    # Cleanup frames
    for f_name in os.listdir(FRAMES_DIR):
        os.remove(os.path.join(FRAMES_DIR, f_name))
    os.rmdir(FRAMES_DIR)

    # Generate preview frames at key timestamps
    for ts in [1, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 54]:
        subprocess.run(["ffmpeg", "-y", "-i", output_path, "-ss", str(ts),
                        "-frames:v", "1",
                        os.path.join(OUTPUT_DIR, f"dark_tech_preview_{ts}s.jpg")],
                       capture_output=True)

    print(f"Output: {output_path}")
    print("All done!")
    return output_path


if __name__ == "__main__":
    generate_video()
