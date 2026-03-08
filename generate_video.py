#!/usr/bin/env python3
"""
Scan Peptide AI - Premium Ad Reel Generator v5
Major visual upgrade:
- Vignette overlay on all scenes
- Dynamic moving fog/atmosphere
- Denser DNA with more particles and glow
- Phone screen inner glow effect
- Typing animation in CTA email field
- Pulsing CTA button
- Counter-up number animations
- Richer stat cards with gradient fills
- Animated progress bars
- Data readout overlays on body scan
- Subtle noise texture for premium feel
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
FRAMES_DIR = os.path.join(OUTPUT_DIR, "frames")
CROSSFADE_FRAMES = 18

# ─── COLORS (teal/mint palette matching the app) ────────────────────────────
BG = (4, 8, 6)
BG_CARD = (12, 20, 16)
BG_CARD_BORDER = (30, 50, 40)
BG_CARD_INNER = (16, 26, 21)

GREEN = (0, 230, 160)
GREEN_BRIGHT = (0, 255, 180)
GREEN_TEAL = (0, 210, 155)
GREEN_DIM = (0, 110, 70)
GREEN_SUBTLE = (0, 65, 42)
GREEN_DARK = (0, 42, 28)
GREEN_GLOW = (0, 200, 130)

WHITE = (255, 255, 255)
GRAY_100 = (240, 240, 240)
GRAY_200 = (200, 205, 210)
GRAY_400 = (140, 148, 155)
GRAY_500 = (100, 108, 115)
GRAY_600 = (70, 78, 85)
GRAY_700 = (40, 48, 44)
BLACK = (0, 0, 0)

BLUE_ACCENT = (60, 140, 255)
ORANGE_ACCENT = (255, 160, 50)
RED_ACCENT = (255, 80, 80)

# ─── FONTS ───────────────────────────────────────────────────────────────────
FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FONT_LIGHT = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

# ─── EASING ──────────────────────────────────────────────────────────────────
def ease_out(t):
    return 1 - (1 - max(0, min(1, t))) ** 3

def ease_out_quad(t):
    t = max(0, min(1, t))
    return 1 - (1 - t) ** 2

def ease_out_back(t):
    t = max(0, min(1, t))
    c = 1.70158
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2

def ease_out_elastic(t):
    t = max(0, min(1, t))
    if t == 0 or t == 1:
        return t
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * 2 * math.pi / 3) + 1

def ease_in_out(t):
    t = max(0, min(1, t))
    if t < 0.5:
        return 4 * t * t * t
    return 1 - (-2 * t + 2) ** 3 / 2

def lerp(a, b, t):
    return a + (b - a) * max(0, min(1, t))

def color_lerp(c1, c2, t):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


# ─── DRAWING HELPERS ─────────────────────────────────────────────────────────

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
    gd.text((x, y), text, font=f, fill=(color[0], color[1], color[2], glow_alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=radius))
    result = Image.alpha_composite(img.convert("RGBA"), glow)
    rd = ImageDraw.Draw(result)
    rd.text((x, y), text, font=f, fill=color)
    return result


def glow_text_centered(img, y, text, f, color, radius=20, glow_alpha=80):
    d = ImageDraw.Draw(img)
    w = tw(d, text, f)
    x = (W - w) // 2
    return glow_text(img, (x, y), text, f, color, radius, glow_alpha)


# ─── VIGNETTE ────────────────────────────────────────────────────────────────

_vignette_cache = None
def get_vignette():
    global _vignette_cache
    if _vignette_cache is not None:
        return _vignette_cache
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    cx, cy = W // 2, H // 2
    max_r = int(math.sqrt(cx*cx + cy*cy))
    for r in range(max_r, int(max_r * 0.4), -3):
        ratio = (r - max_r * 0.4) / (max_r * 0.6)
        a = int(120 * ratio * ratio)
        vd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0, 0, 0, a))
    _vignette_cache = vig
    return vig

def apply_vignette(img):
    return Image.alpha_composite(img.convert("RGBA"), get_vignette())


# ─── ATMOSPHERIC BACKGROUND ─────────────────────────────────────────────────

def make_atmosphere(frame=0, center_x=None, center_y=None, intensity=1.0):
    """Rich atmospheric background with moving teal fog."""
    img = Image.new("RGB", (W, H), BG)
    cx = center_x or W // 2
    cy = center_y or H // 2
    
    # Subtle movement based on frame
    drift_x = int(math.sin(frame * 0.008) * 40)
    drift_y = int(math.cos(frame * 0.006) * 30)

    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)

    # Main center glow - teal tinted, with drift
    max_r = 850
    for r in range(max_r, 0, -8):
        ratio = r / max_r
        a = int(20 * ratio * intensity)
        g_val = int(lerp(25, 90, ratio))
        b_val = int(g_val * 0.75)
        fd.ellipse([cx + drift_x - r, cy + drift_y - r,
                     cx + drift_x + r, cy + drift_y + r],
                   fill=(0, g_val, b_val, a))

    # Secondary glow (offset, drifting opposite)
    for r in range(550, 0, -10):
        ratio = r / 550
        a = int(12 * ratio * intensity)
        fd.ellipse([cx - drift_x + 220 - r, cy - drift_y - 350 - r,
                     cx - drift_x + 220 + r, cy - drift_y - 350 + r],
                   fill=(0, 65, 55, a))

    # Bottom ambient glow
    for r in range(650, 0, -12):
        ratio = r / 650
        a = int(10 * ratio * intensity)
        fd.ellipse([cx + drift_x * 0.5 - 100 - r, H - 150 - r,
                     cx + drift_x * 0.5 - 100 + r, H - 150 + r],
                   fill=(0, 55, 45, a))

    # Top-left accent glow
    for r in range(400, 0, -10):
        ratio = r / 400
        a = int(6 * ratio * intensity)
        fd.ellipse([-200 + drift_x - r, -100 + drift_y - r,
                     -200 + drift_x + r, -100 + drift_y + r],
                   fill=(0, 50, 40, a))

    img = Image.alpha_composite(img.convert("RGBA"), fog).convert("RGB")
    return img


# ─── PARTICLE DNA HELIX ─────────────────────────────────────────────────────

def draw_dna_helix(base_img, frame, cx=None, y_start=None, y_end=None,
                   amplitude=180, num_points=300, particle_count=8,
                   speed=0.04, alpha_mult=1.0, draw_rungs=True,
                   blur_radius=2, size_mult=1.0):
    cx = cx or W // 2
    y_start = y_start if y_start is not None else -100
    y_end = y_end if y_end is not None else H + 100

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)

    y_range = y_end - y_start
    phase_offset = frame * speed

    for i in range(num_points):
        t = i / num_points
        y = y_start + t * y_range
        angle = t * math.pi * 8 + phase_offset

        x1 = cx + math.sin(angle) * amplitude
        x2 = cx + math.sin(angle + math.pi) * amplitude

        depth1 = (math.cos(angle) + 1) / 2
        depth2 = (math.cos(angle + math.pi) + 1) / 2

        if draw_rungs and i % 10 == 0:
            rung_depth = min(depth1, depth2)
            rung_a = int(40 * rung_depth * alpha_mult)
            if rung_a > 0:
                # Gradient rung - brighter in middle
                steps = 8
                for s in range(steps):
                    st = s / steps
                    rx = lerp(x1, x2, st)
                    mid_bright = 1 - abs(st - 0.5) * 2
                    ra = int(rung_a * (0.5 + 0.5 * mid_bright))
                    g_v = int(lerp(140, 200, mid_bright))
                    ld.ellipse([int(rx)-1, int(y)-1, int(rx)+1, int(y)+1],
                               fill=(0, g_v, int(g_v*0.7), ra))

        for strand_x, depth in [(x1, depth1), (x2, depth2)]:
            random.seed(int(i * 1000 + depth * 100 + frame * 0.01))
            for p in range(particle_count):
                jx = strand_x + random.gauss(0, 3 * size_mult)
                jy = y + random.gauss(0, 3 * size_mult)

                base_size = lerp(1.5, 5.0, depth) * size_mult
                size = base_size * random.uniform(0.5, 1.3)

                base_alpha = lerp(15, 110, depth) * alpha_mult
                alpha = int(base_alpha * random.uniform(0.4, 1.0))
                alpha = max(0, min(255, alpha))

                if alpha < 3:
                    continue

                g = int(lerp(150, 245, depth))
                b = int(lerp(110, 170, depth))
                r = int(lerp(0, 20, depth))

                s = max(1, int(size))
                ld.ellipse([int(jx)-s, int(jy)-s, int(jx)+s, int(jy)+s],
                           fill=(r, g, b, alpha))

                if depth > 0.65 and size > 2.2:
                    core_s = max(1, s // 2)
                    core_a = min(255, int(alpha * 1.6))
                    ld.ellipse([int(jx)-core_s, int(jy)-core_s,
                                int(jx)+core_s, int(jy)+core_s],
                               fill=(r+20, min(255,g+25), min(255,b+20), core_a))

    if blur_radius > 0:
        layer = layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    return Image.alpha_composite(base_img.convert("RGBA"), layer)


# ─── FLOATING PARTICLES ─────────────────────────────────────────────────────

def draw_particles(base_img, frame, seed=42, count=30, speed=1.0):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    random.seed(seed)

    for i in range(count):
        base_x = random.randint(-80, W + 80)
        base_y = random.randint(-80, H + 80)
        x = base_x + int(math.cos(frame * 0.018 * speed + i * 2.3) * 35)
        y = base_y + int(math.sin(frame * 0.025 * speed + i * 1.7) * 50)
        size = random.randint(14, 60)
        pulse = 0.5 + 0.5 * math.sin(frame * 0.04 + i * 0.9)
        base_a = random.randint(8, 38)
        alpha = int(base_a * pulse)

        for r in range(size, 0, -2):
            ring_a = int(alpha * (r / size) ** 0.6)
            g = int(lerp(70, 210, r / size))
            b_val = int(g * 0.7)
            od.ellipse([x-r, y-r, x+r, y+r], fill=(0, g, b_val, ring_a))

    return Image.alpha_composite(base_img.convert("RGBA"), overlay)


def draw_subtle_grid(base_img, alpha=8, frame=0):
    """Very subtle animated grid lines for tech feel."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    spacing = 120
    offset = int(frame * 0.3) % spacing
    
    for x in range(-spacing + offset, W + spacing, spacing):
        pulse = int(alpha * (0.5 + 0.5 * math.sin(x * 0.01 + frame * 0.02)))
        od.line([(x, 0), (x, H)], fill=(0, 100, 70, pulse), width=1)
    for y in range(-spacing + offset, H + spacing, spacing):
        pulse = int(alpha * (0.5 + 0.5 * math.sin(y * 0.01 + frame * 0.015)))
        od.line([(0, y), (W, y)], fill=(0, 100, 70, pulse), width=1)
    
    return Image.alpha_composite(base_img.convert("RGBA"), overlay)


# ─── HORIZONTAL SCAN LINE ───────────────────────────────────────────────────

def draw_scan_line(base_img, y_pos, width_frac=1.0, intensity=1.0):
    """Glowing horizontal scan line effect."""
    scan = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    x_start = int(W * (1 - width_frac) / 2)
    x_end = int(W * (1 + width_frac) / 2)
    
    for dy in range(-40, 40):
        sa = int(50 * (1 - abs(dy) / 40) * intensity)
        sd.line([(x_start, y_pos + dy), (x_end, y_pos + dy)],
                fill=(0, 230, 160, sa), width=1)
    sd.line([(x_start, y_pos), (x_end, y_pos)],
            fill=(0, 255, 180, int(120 * intensity)), width=2)
    
    return Image.alpha_composite(base_img.convert("RGBA"), scan)



# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCENE 1: HOOK - Hero text + DNA helix + brand reveal
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def scene_hook(frame, total):
    t = frame / total
    img = make_atmosphere(frame, W // 2, H // 2 - 100, intensity=1.3)

    # DNA helix - denser, more vivid
    dna_alpha = min(1.0, t / 0.12) * 0.9
    img = draw_dna_helix(img, frame, cx=W // 2, y_start=-200, y_end=H + 200,
                         amplitude=170, num_points=400, particle_count=7,
                         speed=0.035, alpha_mult=dna_alpha, draw_rungs=True,
                         blur_radius=3, size_mult=1.2)

    img = draw_particles(img, frame, seed=42, count=25, speed=1.0)
    
    # Subtle grid overlay
    img = draw_subtle_grid(img, alpha=5, frame=frame)

    # Phase 1: Hook text from hero
    if t < 0.42:
        tt = ease_out(min(1, t / 0.18))
        alpha = int(255 * min(1, t / 0.08))
        y_off = int(lerp(50, 0, tt))

        f1 = font(FONT_BOLD, 72)

        img = glow_text_centered(img, H // 2 - 130 + y_off, "Optimize Your",
                                 f1, (*WHITE, alpha), radius=22, glow_alpha=55)
        img = glow_text_centered(img, H // 2 - 45 + y_off, "Peptide Stack",
                                 f1, (*GREEN, alpha), radius=28, glow_alpha=80)

        # Subtitle with delayed fade in
        if t > 0.1:
            sub_t = ease_out((t - 0.1) / 0.12)
            sub_a = int(220 * sub_t)
            f_sub = font(FONT_REG, 30)
            img = glow_text_centered(img, H // 2 + 55 + y_off,
                                     "The smarter way to run your protocol.",
                                     f_sub, (*GREEN_TEAL, sub_a), radius=14, glow_alpha=45)
        
        # Decorative horizontal line that extends
        if t > 0.15:
            line_t = ease_out((t - 0.15) / 0.15)
            line_w = int(400 * line_t)
            line_y = H // 2 + 105 + y_off
            line_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ld = ImageDraw.Draw(line_layer)
            lx = W // 2 - line_w // 2
            # Gradient line
            for dx in range(line_w):
                dist_from_center = abs(dx - line_w // 2) / (line_w // 2)
                la = int(60 * (1 - dist_from_center) * line_t)
                ld.line([(lx + dx, line_y), (lx + dx, line_y)],
                        fill=(0, 230, 160, la), width=2)
            img = Image.alpha_composite(img.convert("RGBA"), line_layer)

    # Phase 2: Transition to "Scan" brand reveal
    else:
        fade_out = max(0, 1 - (t - 0.42) / 0.08)
        if fade_out > 0:
            a = int(255 * fade_out)
            f1 = font(FONT_BOLD, 72)
            img = glow_text_centered(img, H // 2 - 130, "Optimize Your",
                                     f1, (*WHITE, a), radius=22, glow_alpha=int(55 * fade_out))
            img = glow_text_centered(img, H // 2 - 45, "Peptide Stack",
                                     f1, (*GREEN, a), radius=28, glow_alpha=int(80 * fade_out))

        fade_in = ease_out(max(0, (t - 0.48) / 0.16))
        if fade_in > 0:
            a = int(255 * fade_in)
            y_off = int(lerp(25, 0, fade_in))

            # "AI-POWERED PEPTIDE TRACKING" badge
            f_badge = font(FONT_BOLD, 16)
            badge_text = "AI-POWERED PEPTIDE TRACKING"
            bw = tw(ImageDraw.Draw(img), badge_text, f_badge) + 44
            bx = W // 2 - bw // 2
            by = H // 2 - 200 + y_off

            badge_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            bd = ImageDraw.Draw(badge_layer)
            rounded_rect(bd, [bx, by, bx + bw, by + 34], 17,
                         fill=(0, 42, 28, int(200 * fade_in)),
                         outline=(0, 210, 140, int(160 * fade_in)), width=1)
            img = Image.alpha_composite(img.convert("RGBA"), badge_layer)
            draw = ImageDraw.Draw(img)
            draw_text_centered(draw, by + 8, badge_text, f_badge, (*GREEN, a))

            # Big "Scan" text with strong glow
            f_scan = font(FONT_BOLD, 130)
            img = glow_text_centered(img, H // 2 - 140 + y_off, "Scan",
                                     f_scan, (*WHITE, a), radius=40, glow_alpha=int(100 * fade_in))

            # Pulsing underline
            pulse = 0.7 + 0.3 * math.sin(frame * 0.1)
            line_a = int(80 * fade_in * pulse)
            line_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ld = ImageDraw.Draw(line_layer)
            ld.line([(W//2 - 120, H//2 - 5 + y_off), (W//2 + 120, H//2 - 5 + y_off)],
                    fill=(0, 230, 160, line_a), width=3)
            img = Image.alpha_composite(img.convert("RGBA"), line_layer)
            draw = ImageDraw.Draw(img)

            # Subtitle
            if t > 0.6:
                sub_t = ease_out((t - 0.6) / 0.12)
                sub_a = int(255 * sub_t)
                f_sub = font(FONT_REG, 32)
                img = glow_text_centered(img, H // 2 + 25 + int(lerp(15, 0, sub_t)),
                                         "AI-Powered Peptide Intelligence",
                                         f_sub, (*GREEN_TEAL, sub_a), radius=15, glow_alpha=int(55 * sub_t))

    img = apply_vignette(img)
    return img.convert("RGB")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCENE 2: APP HOME SCREEN (exact match to screenshot)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def scene_app_home(frame, total):
    t = frame / total
    img = make_atmosphere(frame, W // 2, H // 2, intensity=0.7)
    img = draw_subtle_grid(img, alpha=4, frame=frame)
    img = draw_particles(img, frame, seed=100, count=12, speed=0.8)
    draw = ImageDraw.Draw(img)

    # Phone mockup dimensions - bigger, more prominent
    pw, ph = 500, 900
    px = W // 2 - pw // 2
    py_target = 480
    py = int(lerp(H + 100, py_target, ease_out(min(1, t / 0.18))))

    # Title above phone
    if t > 0.03:
        tt = ease_out(min(1, (t - 0.03) / 0.14))
        a = int(255 * tt)
        y_off = int(lerp(-30, 0, tt))
        
        f_t = font(FONT_BOLD, 52)
        f_s = font(FONT_REG, 28)
        img = glow_text_centered(img, 120 + y_off, "Your Command Center",
                                 f_t, (*WHITE, a), radius=18, glow_alpha=40)
        draw = ImageDraw.Draw(img)
        draw_text_centered(draw, 185 + y_off, "Everything in one place", f_s, (*GREEN, a))
        
        # Decorative line
        line_t = ease_out(min(1, (t - 0.08) / 0.1))
        if line_t > 0:
            la = int(40 * line_t)
            lw = int(200 * line_t)
            draw.line([(W//2 - lw//2, 225 + y_off), (W//2 + lw//2, 225 + y_off)],
                      fill=(*GREEN, la), width=1)

    # Phone shadow (deeper, more dramatic)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for s in range(40, 0, -2):
        sa = int(10 * (1 - s / 40))
        rounded_rect(sd, [px - s + 6, py - s + 12, px + pw + s + 6, py + ph + s + 12],
                     50, fill=(0, 0, 0, sa))
    img = Image.alpha_composite(img.convert("RGBA"), shadow)
    draw = ImageDraw.Draw(img)

    # Phone body with green border glow (brighter)
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    for g in range(18, 0, -1):
        ga = int(7 * (1 - g / 18))
        rounded_rect(gd, [px - g, py - g, px + pw + g, py + ph + g], 50,
                     fill=(0, 200, 140, ga))
    img = Image.alpha_composite(img.convert("RGBA"), glow_layer)
    draw = ImageDraw.Draw(img)

    # Phone body
    rounded_rect(draw, [px, py, px + pw, py + ph], 46, fill=(8, 12, 10, 255))
    rounded_rect(draw, [px, py, px + pw, py + ph], 46,
                 outline=(40, 60, 50, 255), width=2)

    # Status bar area
    f_time = font(FONT_BOLD, 14)
    draw.text((px + 24, py + 10), "9:41", font=f_time, fill=(*WHITE, 200))
    
    # Battery/signal indicators (right side)
    bx = px + pw - 70
    for i in range(4):
        bar_h = 6 + i * 2
        draw.rectangle([bx + i * 7, py + 18 - bar_h, bx + i * 7 + 4, py + 18],
                       fill=(*WHITE, 150))
    # Battery icon
    draw.rectangle([bx + 35, py + 10, bx + 55, py + 20], outline=(*WHITE, 150), width=1)
    draw.rectangle([bx + 37, py + 12, bx + 50, py + 18], fill=(*GREEN, 150))

    # Notch
    nw, nh = 140, 28
    nx = px + pw // 2 - nw // 2
    rounded_rect(draw, [nx, py, nx + nw, py + nh], 14, fill=(0, 0, 0, 255))

    # ── Screen content area ──
    sx, sy = px + 22, py + 50
    sw = pw - 44

    # Greeting
    anim_t = max(0, (t - 0.14)) / 0.14
    if anim_t > 0:
        et = ease_out(min(1, anim_t))
        a = int(255 * et)

        f_greet = font(FONT_BOLD, 13)
        f_name = font(FONT_BOLD, 32)
        f_date = font(FONT_REG, 14)

        draw.text((sx + 14, sy + 8), "GOOD EVENING", font=f_greet, fill=(*GREEN, a))
        draw.text((sx + 14, sy + 28), "Cameron", font=f_name, fill=(*WHITE, a))
        draw.text((sx + 14, sy + 66), "Tuesday, Mar 3", font=f_date, fill=(*GRAY_400, a))

        # App icon (green rounded square, top right)
        icon_x = sx + sw - 54
        icon_y = sy + 12
        icon_s = 44
        # Gradient fill for icon
        for row in range(icon_s):
            ratio = row / icon_s
            g_v = int(lerp(240, 180, ratio))
            b_v = int(lerp(170, 120, ratio))
            draw.line([(icon_x, icon_y + row), (icon_x + icon_s, icon_y + row)],
                      fill=(0, g_v, b_v, a))
        rounded_rect(draw, [icon_x, icon_y, icon_x + icon_s, icon_y + icon_s], 13,
                     outline=(0, 255, 180, int(a * 0.5)), width=1)
        f_icon = font(FONT_BOLD, 26)
        siw = tw(draw, "S", f_icon)
        draw.text((icon_x + icon_s // 2 - siw // 2, icon_y + 8), "S",
                  font=f_icon, fill=(*WHITE, a))

    # "Run Body Scan" card
    card_y = sy + 98
    card_h = 58
    if t > 0.21:
        ct = ease_out(min(1, (t - 0.21) / 0.12))
        ca = int(255 * ct)
        x_sl = int(lerp(35, 0, ct))

        cl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(cl)
        rounded_rect(cd, [sx + 10 + x_sl, card_y, sx + sw - 10 + x_sl, card_y + card_h], 14,
                     fill=(14, 24, 19, ca))
        rounded_rect(cd, [sx + 10 + x_sl, card_y, sx + sw - 10 + x_sl, card_y + card_h], 14,
                     outline=(*BG_CARD_BORDER, ca), width=1)
        img = Image.alpha_composite(img.convert("RGBA"), cl)
        draw = ImageDraw.Draw(img)

        # Green pulsing dot
        pulse = 0.7 + 0.3 * math.sin(frame * 0.12)
        dot_x = sx + 30 + x_sl
        dot_y = card_y + card_h // 2
        dot_r = int(6 * pulse)
        # Glow around dot
        for gr in range(dot_r + 4, dot_r, -1):
            draw.ellipse([dot_x - gr, dot_y - gr, dot_x + gr, dot_y + gr],
                         fill=(0, 230, 160, int(20 * pulse)))
        draw.ellipse([dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r],
                     fill=(*GREEN, ca))

        draw.text((dot_x + 14, card_y + 17), "Run Body Scan",
                  font=font(FONT_BOLD, 20), fill=(*WHITE, ca))

        chev_x = sx + sw - 38 + x_sl
        draw.text((chev_x, card_y + 15), ">", font=font(FONT_BOLD, 22), fill=(*GRAY_500, ca))

    # 3 Square stat cards
    stat_y = card_y + card_h + 18
    stat_card_w = (sw - 48) // 3
    stat_card_h = stat_card_w

    stat_items = [
        ("ACTIVE", "3", GREEN, (0, 60, 40)),
        ("LOGGED", "12", BLUE_ACCENT, (20, 40, 80)),
        ("STREAK", "5d", ORANGE_ACCENT, (80, 50, 15)),
    ]

    for i, (label, val, icon_color, card_bg) in enumerate(stat_items):
        anim_delay = 0.27 + i * 0.05
        if t <= anim_delay:
            continue
        st = ease_out_back(min(1, (t - anim_delay) / 0.14))
        sa = int(255 * st)
        y_off = int(lerp(25, 0, st))

        cx_ = sx + 14 + i * (stat_card_w + 10)
        cy_ = stat_y + y_off

        cl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(cl)
        
        # Card with subtle gradient
        for row in range(stat_card_h):
            ratio = row / stat_card_h
            r_v = int(lerp(card_bg[0] + 14, card_bg[0] + 8, ratio))
            g_v = int(lerp(card_bg[1] + 22, card_bg[1] + 14, ratio))
            b_v = int(lerp(card_bg[2] + 18, card_bg[2] + 10, ratio))
            cd.line([(cx_, cy_ + row), (cx_ + stat_card_w, cy_ + row)],
                    fill=(r_v, g_v, b_v, sa))
        
        rounded_rect(cd, [cx_, cy_, cx_ + stat_card_w, cy_ + stat_card_h], 16,
                     outline=(*BG_CARD_BORDER, int(sa * 0.7)), width=1)
        img = Image.alpha_composite(img.convert("RGBA"), cl)
        draw = ImageDraw.Draw(img)

        # Colored icon circle
        ic_x = cx_ + 14
        ic_y = cy_ + 14
        ic_r = 16
        draw.ellipse([ic_x, ic_y, ic_x + ic_r*2, ic_y + ic_r*2],
                     fill=(*icon_color, sa))
        # Icon dot
        draw.ellipse([ic_x + ic_r - 3, ic_y + ic_r - 3,
                      ic_x + ic_r + 3, ic_y + ic_r + 3],
                     fill=(*WHITE, int(sa * 0.9)))

        # Value - large, animated count-up
        count_progress = ease_out(min(1, (t - anim_delay - 0.05) / 0.2))
        if val.isdigit():
            display_val = str(int(int(val) * count_progress))
        else:
            display_val = val if count_progress > 0.5 else ""
        
        f_val = font(FONT_BOLD, 34)
        draw.text((cx_ + 14, cy_ + stat_card_h - 62), display_val,
                  font=f_val, fill=(*WHITE, sa))

        f_lab = font(FONT_REG, 11)
        draw.text((cx_ + 14, cy_ + stat_card_h - 24), label,
                  font=f_lab, fill=(*GRAY_500, sa))

    # "TODAY'S STACK" section
    stack_y = stat_y + stat_card_h + 24
    if t > 0.4:
        skt = ease_out(min(1, (t - 0.4) / 0.1))
        ska = int(255 * skt)

        f_sec = font(FONT_BOLD, 16)
        f_see = font(FONT_REG, 14)
        draw.text((sx + 14, stack_y), "TODAY'S STACK", font=f_sec, fill=(*GREEN, ska))
        draw.text((sx + sw - 58, stack_y + 2), "See All", font=f_see, fill=(*GREEN_DIM, ska))

    # Stack items
    stack_items = [
        ("BPC-157", "250mcg  SubQ  08:00 AM", True),
        ("Semax", "300mcg  Nasal  12:00 PM", False),
    ]

    for i, (name, detail, checked) in enumerate(stack_items):
        delay = 0.44 + i * 0.06
        if t <= delay:
            continue
        it = ease_out(min(1, (t - delay) / 0.1))
        ia = int(255 * it)
        x_sl = int(lerp(25, 0, it))

        iy = stack_y + 28 + i * 64

        cl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(cl)
        rounded_rect(cd, [sx + 10 + x_sl, iy, sx + sw - 10 + x_sl, iy + 54], 12,
                     fill=(14, 24, 19, ia))
        if checked:
            cd.rectangle([sx + 10 + x_sl, iy + 8, sx + 14 + x_sl, iy + 46],
                         fill=(*GREEN, ia))
        img = Image.alpha_composite(img.convert("RGBA"), cl)
        draw = ImageDraw.Draw(img)

        tx = sx + 24 + x_sl
        draw.text((tx, iy + 8), name, font=font(FONT_BOLD, 18), fill=(*WHITE, ia))
        draw.text((tx, iy + 32), detail, font=font(FONT_REG, 12), fill=(*GRAY_400, ia))

        ck_x = sx + sw - 38 + x_sl
        ck_y = iy + 16
        if checked:
            draw.ellipse([ck_x, ck_y, ck_x + 22, ck_y + 22], fill=(*GREEN, ia))
            draw.line([(ck_x + 5, ck_y + 11), (ck_x + 10, ck_y + 16)],
                      fill=(*BLACK, ia), width=2)
            draw.line([(ck_x + 10, ck_y + 16), (ck_x + 17, ck_y + 6)],
                      fill=(*BLACK, ia), width=2)
        else:
            draw.ellipse([ck_x, ck_y, ck_x + 22, ck_y + 22],
                         outline=(*GRAY_600, ia), width=2)

    # Bottom navigation bar
    nav_y = py + ph - 60
    draw.line([(sx, nav_y), (sx + sw, nav_y)], fill=(*GRAY_700, 200), width=1)

    nav_items = [("Home", True), ("Scan", False), ("Log", False), ("Stack", False), ("Profile", False)]
    for i, (item, active) in enumerate(nav_items):
        nx_ = sx + 28 + i * (sw - 56) // 4
        color = GREEN if active else GRAY_500
        f_nav = font(FONT_REG, 11)
        iw = tw(draw, item, f_nav)

        # Simple icon dots
        ic_y = nav_y + 10
        if active:
            draw.ellipse([nx_ - 4, ic_y - 1, nx_ + 4, ic_y + 7], fill=GREEN)
        else:
            draw.ellipse([nx_ - 3, ic_y, nx_ + 3, ic_y + 6],
                         outline=GRAY_600, width=1)

        draw.text((nx_ - iw // 2, nav_y + 22), item, font=f_nav, fill=color)

    # Home indicator bar
    bar_w = 140
    bar_y = py + ph - 14
    rounded_rect(draw, [px + pw//2 - bar_w//2, bar_y, px + pw//2 + bar_w//2, bar_y + 5], 3,
                 fill=(*GRAY_600, 180))

    img = apply_vignette(img)
    return img.convert("RGB")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCENE 3: STACK TRACKING - Detailed compound cards
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def scene_stack_tracking(frame, total):
    t = frame / total
    img = make_atmosphere(frame, W // 2, 400, intensity=0.8)

    img = draw_dna_helix(img, frame, cx=W - 60, y_start=0, y_end=H,
                         amplitude=100, num_points=200, particle_count=4,
                         speed=0.03, alpha_mult=0.35, draw_rungs=True,
                         blur_radius=3, size_mult=0.8)

    img = draw_particles(img, frame, seed=200, count=18, speed=0.7)
    img = draw_subtle_grid(img, alpha=4, frame=frame)
    draw = ImageDraw.Draw(img)

    # Title
    tt = ease_out(min(1, t / 0.1))
    a = int(255 * tt)
    y_off = int(lerp(-20, 0, tt))
    img = glow_text_centered(img, 80 + y_off, "Track Every Dose",
                             font(FONT_BOLD, 52), (*WHITE, a), radius=18, glow_alpha=40)
    draw = ImageDraw.Draw(img)
    draw_text_centered(draw, 145 + y_off, "Smart protocols, zero guesswork",
                       font(FONT_REG, 26), (*GREEN, a))

    peptides = [
        {"name": "BPC-157", "type": "PRIMARY COMPOUND", "dose": "250 mcg",
         "route": "SubQ", "freq": "Daily", "status": "ON CYCLE",
         "week": "Week 1 of 13", "progress": 0.08,
         "note": "Start at 250mcg/day SubQ. Titrate to 500 mcg after week 2."},
        {"name": "TB-500", "type": "SUPPORTING COMPOUND", "dose": "2 mg",
         "route": "SubQ", "freq": "Twice weekly", "status": "ON CYCLE",
         "week": "Week 1 of 10", "progress": 0.1,
         "note": "Standard dosing protocol. Maintain consistent schedule."},
        {"name": "Semax", "type": "NOOTROPIC", "dose": "300 mcg",
         "route": "Nasal", "freq": "Daily", "status": "ON CYCLE",
         "week": "Week 3 of 8", "progress": 0.375,
         "note": "Nasal spray 300mcg AM. Can increase to 600mcg if tolerated."},
    ]

    card_w = W - 90
    card_x = 45
    start_y = 215

    for i, pep in enumerate(peptides):
        et_raw = max(0, min(1, (t - 0.04 - i * 0.055) / 0.13))
        if et_raw <= 0:
            continue
        et = ease_out(et_raw)
        a = int(255 * et)
        x_sl = int(lerp(100, 0, et))

        card_h = 300
        cy = start_y + i * (card_h + 14)

        cl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(cl)

        # Top glow accent
        for g in range(12, 0, -1):
            ga = int(8 * (1 - g / 12) * et)
            rounded_rect(cd, [card_x + x_sl - g, cy - g,
                              card_x + card_w + x_sl + g, cy + 3], 4,
                         fill=(0, 210, 140, ga))

        # Card gradient background
        for row in range(card_h):
            ratio = row / card_h
            r_v = int(lerp(14, 10, ratio))
            g_v = int(lerp(22, 16, ratio))
            b_v = int(lerp(18, 13, ratio))
            cd.line([(card_x + x_sl, cy + row), (card_x + card_w + x_sl, cy + row)],
                    fill=(r_v, g_v, b_v, a))

        rounded_rect(cd, [card_x + x_sl, cy, card_x + card_w + x_sl, cy + card_h],
                     18, outline=(*BG_CARD_BORDER, int(a * 0.6)), width=1)
        # Top accent line
        cd.line([(card_x + 18 + x_sl, cy + 1), (card_x + card_w - 18 + x_sl, cy + 1)],
                fill=(*GREEN, int(a * 0.5)), width=2)

        img = Image.alpha_composite(img.convert("RGBA"), cl)
        draw = ImageDraw.Draw(img)
        bx = card_x + 24 + x_sl

        # Type + name + badge
        draw.text((bx, cy + 16), pep["type"], font=font(FONT_REG, 11), fill=(*GRAY_500, a))
        draw.text((bx, cy + 34), pep["name"], font=font(FONT_BOLD, 36), fill=(*WHITE, a))

        f_badge = font(FONT_BOLD, 11)
        badge_text = pep["status"]
        bw = tw(draw, badge_text, f_badge) + 18
        badge_x = card_x + card_w - bw - 24 + x_sl
        rounded_rect(draw, [badge_x, cy + 20, badge_x + bw, cy + 38], 6,
                     fill=(*GREEN_DARK, a), outline=(*GREEN, int(a * 0.5)), width=1)
        draw.text((badge_x + 9, cy + 22), badge_text, font=f_badge, fill=(*GREEN, a))

        # Info row with green values
        iy = cy + 86
        infos = [("DOSE", pep["dose"]), ("ROUTE", pep["route"]), ("FREQUENCY", pep["freq"])]
        col_w = (card_w - 48) // 3
        for j, (lb, vl) in enumerate(infos):
            ix = bx + j * col_w
            draw.text((ix, iy), lb, font=font(FONT_REG, 10), fill=(*GRAY_500, a))
            draw.text((ix, iy + 16), vl, font=font(FONT_BOLD, 18), fill=(*GREEN, a))

        # Progress bar with animation
        py_ = iy + 52
        draw.text((bx, py_), pep["week"], font=font(FONT_REG, 12), fill=(*GRAY_400, a))
        bar_y = py_ + 22
        bar_w = card_w - 48
        
        # Bar background
        rounded_rect(draw, [bx, bar_y, bx + bar_w, bar_y + 8], 4, fill=(*GRAY_700, a))
        # Animated fill
        if et_raw > 0.25:
            prog_t = ease_out((et_raw - 0.25) / 0.75)
            fw = max(6, int(bar_w * pep["progress"] * prog_t))
            # Gradient progress bar
            for dx in range(fw):
                ratio = dx / max(1, fw)
                g_v = int(lerp(180, 240, ratio))
                draw.line([(bx + dx, bar_y + 1), (bx + dx, bar_y + 7)],
                          fill=(0, g_v, int(g_v * 0.7), a))
            # Glow tip
            if fw > 8:
                glow_x = bx + fw
                for gr in range(8, 0, -1):
                    ga = int(30 * (1 - gr / 8) * prog_t)
                    draw.ellipse([glow_x - gr, bar_y - gr + 4, glow_x + gr, bar_y + gr + 4],
                                 fill=(0, 255, 180, ga))

        # Titration note box
        ny = bar_y + 22
        rounded_rect(draw, [bx, ny, bx + bar_w, ny + 52], 10,
                     fill=(*BG_CARD_INNER, int(a * 0.8)))
        draw.line([(bx + 4, ny + 10), (bx + 4, ny + 42)], fill=(*GREEN, int(a * 0.6)), width=3)
        draw.text((bx + 16, ny + 8), "TITRATION", font=font(FONT_BOLD, 10), fill=(*GREEN, a))
        draw.text((bx + 16, ny + 26), pep["note"], font=font(FONT_REG, 12), fill=(*GRAY_200, a))

    img = apply_vignette(img)
    return img.convert("RGB")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCENE 4: AI BODY SCAN - DNA showcase with data overlays
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def scene_body_scan(frame, total):
    t = frame / total
    img = make_atmosphere(frame, W // 2, H // 2 - 100, intensity=1.5)

    # Dense main DNA helix
    img = draw_dna_helix(img, frame, cx=W // 2, y_start=-200, y_end=H + 200,
                         amplitude=210, num_points=450, particle_count=12,
                         speed=0.045, alpha_mult=1.0, draw_rungs=True,
                         blur_radius=2, size_mult=1.4)

    # Background helix
    img = draw_dna_helix(img, frame + 50, cx=W // 2 - 280, y_start=150, y_end=H - 50,
                         amplitude=80, num_points=120, particle_count=3,
                         speed=0.03, alpha_mult=0.25, draw_rungs=False,
                         blur_radius=5, size_mult=0.6)

    # Scanning line sweeping
    scan_y = int(180 + (H - 360) * ((t * 1.8) % 1.0))
    img = draw_scan_line(img, scan_y, width_frac=0.85, intensity=0.8)

    img = draw_particles(img, frame, seed=300, count=22, speed=1.2)

    # Title
    tt = ease_out(min(1, t / 0.1))
    a = int(255 * tt)
    img = glow_text_centered(img, 85, "AI Body Scan",
                             font(FONT_BOLD, 56), (*WHITE, a), radius=25, glow_alpha=int(65 * tt))
    draw = ImageDraw.Draw(img)
    draw_text_centered(draw, 155, "Powered by machine learning",
                       font(FONT_REG, 26), (*GREEN, a))

    # Feature boxes - positioned to frame the DNA
    features = [
        ("Real-Time Analysis", "Track changes as\nthey happen"),
        ("Smart Insights", "AI detects patterns\nin your data"),
        ("Progress Tracking", "Visual health scores\nover time"),
        ("Research Grade", "Lab-quality data\nanalysis"),
    ]

    box_w = 400
    positions = [
        (30, H // 2 - 220),
        (W - box_w - 30, H // 2 - 220),
        (30, H // 2 + 20),
        (W - box_w - 30, H // 2 + 20),
    ]

    for i, ((fx, fy), (title, desc)) in enumerate(zip(positions, features)):
        ft = max(0, min(1, (t - 0.1 - i * 0.05) / 0.12))
        if ft <= 0:
            continue
        et = ease_out_back(ft)
        fa = int(255 * min(1, ft / 0.35))
        y_off = int(lerp(20, 0, et))

        box_h = 135
        bl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bl)
        rounded_rect(bd, [fx, fy + y_off, fx + box_w, fy + box_h + y_off], 16,
                     fill=(8, 14, 11, int(210 * min(1, ft / 0.3))))
        rounded_rect(bd, [fx, fy + y_off, fx + box_w, fy + box_h + y_off], 16,
                     outline=(*GREEN_SUBTLE, fa), width=1)
        # Top accent
        bd.line([(fx + 16, fy + y_off + 1), (fx + box_w - 16, fy + y_off + 1)],
                fill=(*GREEN, int(fa * 0.35)), width=2)
        img = Image.alpha_composite(img.convert("RGBA"), bl)
        draw = ImageDraw.Draw(img)

        # Green dot icon
        draw.ellipse([fx + 20, fy + 22 + y_off, fx + 34, fy + 36 + y_off], fill=(*GREEN, fa))
        draw.text((fx + 44, fy + 19 + y_off), title, font=font(FONT_BOLD, 22), fill=(*WHITE, fa))
        for li, line in enumerate(desc.split("\n")):
            draw.text((fx + 20, fy + 52 + li * 24 + y_off), line,
                      font=font(FONT_REG, 16), fill=(*GRAY_400, fa))

    # Data readout overlays (floating numbers near DNA)
    if t > 0.35:
        dt = ease_out(min(1, (t - 0.35) / 0.15))
        da = int(180 * dt)
        f_data = font(FONT_MONO, 12)
        
        readouts = [
            (W//2 + 250, H//2 - 320, "PEPTIDE: BPC-157"),
            (W//2 - 380, H//2 - 380, "BINDING: 98.2%"),
            (W//2 + 260, H//2 + 260, "HALF-LIFE: 4.2h"),
            (W//2 - 370, H//2 + 200, "BIOAVAIL: 67%"),
        ]
        for rx, ry, txt in readouts:
            draw.text((rx, ry), txt, font=f_data, fill=(*GREEN_DIM, da))

    # Bottom stats
    if t > 0.5:
        st = ease_out(min(1, (t - 0.5) / 0.12))
        sa = int(255 * st)
        stats = [("98%", "Accuracy"), ("<30s", "Scan Time"), ("24/7", "Monitoring")]
        for i, (val, label) in enumerate(stats):
            sx_ = 140 + i * 300
            sy_ = H - 310
            f_sv = font(FONT_BOLD, 50)
            f_sl = font(FONT_REG, 18)
            vw = tw(draw, val, f_sv)
            lw = tw(draw, label, f_sl)
            img = glow_text(img, (sx_ - vw // 2, sy_), val, f_sv,
                            (*GREEN, sa), radius=14, glow_alpha=int(45 * st))
            draw = ImageDraw.Draw(img)
            draw.text((sx_ - lw // 2, sy_ + 56), label, font=f_sl, fill=(*GRAY_200, sa))

    img = apply_vignette(img)
    return img.convert("RGB")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCENE 5: FEATURES OVERVIEW - 2x3 grid with gradient accents
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def scene_features(frame, total):
    t = frame / total
    img = make_atmosphere(frame, W // 2, 600, intensity=0.8)
    img = draw_subtle_grid(img, alpha=5, frame=frame)
    img = draw_particles(img, frame, seed=400, count=18, speed=0.6)
    draw = ImageDraw.Draw(img)

    tt = ease_out(min(1, t / 0.1))
    a = int(255 * tt)
    img = glow_text_centered(img, 100, "Everything You Need",
                             font(FONT_BOLD, 50), (*WHITE, a), radius=18, glow_alpha=40)
    draw = ImageDraw.Draw(img)
    draw_text_centered(draw, 165, "Built for serious researchers",
                       font(FONT_REG, 24), (*GREEN_TEAL, int(a * 0.8)))

    features = [
        ("Protocol Builder", "Create custom peptide\nprotocols with AI guidance"),
        ("Dose Calculator", "Auto-calculate dosing\nbased on your weight"),
        ("Progress Journal", "Log symptoms & track\nrecovery metrics daily"),
        ("Stack Optimizer", "AI-optimized peptide\ncombinations for you"),
        ("Community", "10K+ researchers\nsharing knowledge"),
        ("Data Export", "Export your research\ndata anytime, anywhere"),
    ]

    # Feature icons (simple shapes)
    icon_colors = [GREEN, BLUE_ACCENT, GREEN_TEAL, ORANGE_ACCENT, GREEN, GREEN_BRIGHT]

    card_w = (W - 110 - 22) // 2
    card_h = 200
    gap = 22
    start_y = 230

    for i, (title, desc) in enumerate(features):
        col, row = i % 2, i // 2
        ft = max(0, min(1, (t - 0.06 - i * 0.035) / 0.12))
        if ft <= 0:
            continue
        et = ease_out_back(ft)
        fa = int(255 * min(1, ft / 0.3))
        y_off = int(lerp(35, 0, et))

        cx_ = 55 + col * (card_w + gap)
        cy_ = start_y + row * (card_h + gap)

        cl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(cl)
        
        # Card with gradient
        for row_px in range(card_h):
            ratio = row_px / card_h
            r_v = int(lerp(14, 10, ratio))
            g_v = int(lerp(22, 16, ratio))
            b_v = int(lerp(18, 13, ratio))
            cd.line([(cx_, cy_ + y_off + row_px), (cx_ + card_w, cy_ + y_off + row_px)],
                    fill=(r_v, g_v, b_v, int(220 * min(1, ft / 0.25))))
        
        rounded_rect(cd, [cx_, cy_ + y_off, cx_ + card_w, cy_ + card_h + y_off], 18,
                     outline=(*BG_CARD_BORDER, fa), width=1)
        # Top accent with icon color
        ic = icon_colors[i]
        cd.line([(cx_ + 16, cy_ + y_off + 1), (cx_ + card_w - 16, cy_ + y_off + 1)],
                fill=(*ic, int(fa * 0.4)), width=2)
        img = Image.alpha_composite(img.convert("RGBA"), cl)
        draw = ImageDraw.Draw(img)

        # Icon circle with number
        ic_x = cx_ + 22
        ic_y = cy_ + 28 + y_off
        ic_s = 36
        draw.ellipse([ic_x, ic_y, ic_x + ic_s, ic_y + ic_s],
                     fill=(*GREEN_DARK, fa), outline=(*ic, fa), width=2)
        f_num = font(FONT_BOLD, 16)
        ns = str(i + 1)
        nw = tw(draw, ns, f_num)
        draw.text((ic_x + ic_s // 2 - nw // 2, ic_y + 8), ns, font=f_num, fill=(*ic, fa))

        draw.text((cx_ + 22, cy_ + 78 + y_off), title,
                  font=font(FONT_BOLD, 24), fill=(*WHITE, fa))
        for li, line in enumerate(desc.split("\n")):
            draw.text((cx_ + 22, cy_ + 112 + li * 24 + y_off), line,
                      font=font(FONT_REG, 15), fill=(*GRAY_400, fa))

    img = apply_vignette(img)
    return img.convert("RGB")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCENE 6: SOCIAL PROOF - Big numbers + trust signals
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def scene_social_proof(frame, total):
    t = frame / total
    img = make_atmosphere(frame, W // 2, H // 2, intensity=1.0)

    # Subtle DNA background
    img = draw_dna_helix(img, frame, cx=W // 2, y_start=-50, y_end=H + 50,
                         amplitude=260, num_points=220, particle_count=4,
                         speed=0.025, alpha_mult=0.22, draw_rungs=False,
                         blur_radius=5, size_mult=0.7)

    img = draw_particles(img, frame, seed=500, count=28, speed=0.9)
    draw = ImageDraw.Draw(img)

    tt = ease_out(min(1, t / 0.1))
    a = int(255 * tt)
    img = glow_text_centered(img, 180, "Trusted by Researchers",
                             font(FONT_BOLD, 48), (*WHITE, a), radius=20, glow_alpha=45)
    draw = ImageDraw.Draw(img)
    draw_text_centered(draw, 240, "Join thousands already optimizing",
                       font(FONT_REG, 24), (*GRAY_400, a))

    # Avatar row (simulated faces)
    if t > 0.06:
        av_t = ease_out(min(1, (t - 0.06) / 0.12))
        av_a = int(255 * av_t)
        av_colors = [(60, 180, 140), (80, 140, 200), (200, 140, 80), (140, 80, 180), (180, 100, 100)]
        av_y = 300
        total_w = len(av_colors) * 38
        av_start = W // 2 - total_w // 2
        
        for i, color in enumerate(av_colors):
            ax = av_start + i * 38
            # Circle avatar
            draw.ellipse([ax, av_y, ax + 34, av_y + 34],
                         fill=(*color, av_a), outline=(*BG, av_a), width=2)
            # Initial letter
            letters = "JSMAK"
            fl = font(FONT_BOLD, 14)
            lw = tw(draw, letters[i], fl)
            draw.text((ax + 17 - lw // 2, av_y + 8), letters[i],
                      font=fl, fill=(*WHITE, av_a))
        
        # "+500 more" text
        draw.text((av_start + total_w + 12, av_y + 7), "+500 more",
                  font=font(FONT_BOLD, 16), fill=(*GREEN, av_a))

    stats = [("10K+", "Active Researchers"), ("50+", "Peptides Tracked"),
             ("1M+", "Doses Logged"), ("4.9/5", "App Store Rating")]

    center_y = H // 2 - 180
    for i, (val, label) in enumerate(stats):
        st = max(0, min(1, (t - 0.08 - i * 0.065) / 0.14))
        if st <= 0:
            continue
        et = ease_out(st)
        sa = int(255 * et)
        y_off = int(lerp(25, 0, et))
        sy = center_y + i * 165

        f_v = font(FONT_BOLD, 74)
        f_l = font(FONT_REG, 24)
        vw = tw(draw, val, f_v)
        lw = tw(draw, label, f_l)

        img = glow_text(img, ((W - vw) // 2, sy + y_off), val, f_v,
                        (*GREEN, sa), radius=20, glow_alpha=int(60 * et))
        draw = ImageDraw.Draw(img)
        draw.text(((W - lw) // 2, sy + 75 + y_off), label, font=f_l, fill=(*GRAY_200, sa))

        if i < 3:
            div_a = int(30 * et)
            div_w = 120
            div_y = sy + 130 + y_off
            for dx in range(div_w * 2):
                dist = abs(dx - div_w) / div_w
                da = int(div_a * (1 - dist))
                draw.line([(W//2 - div_w + dx, div_y), (W//2 - div_w + dx, div_y)],
                          fill=(*GRAY_700, da), width=1)

    img = apply_vignette(img)
    return img.convert("RGB")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCENE 7: CTA - Waitlist page replication with animations
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def scene_cta(frame, total):
    t = frame / total
    img = make_atmosphere(frame, W // 2, H // 2, intensity=1.4)
    img = draw_subtle_grid(img, alpha=6, frame=frame)

    # DNA behind CTA
    img = draw_dna_helix(img, frame, cx=W // 2, y_start=-100, y_end=H + 100,
                         amplitude=230, num_points=320, particle_count=7,
                         speed=0.04, alpha_mult=0.45, draw_rungs=True,
                         blur_radius=3, size_mult=1.0)

    img = draw_particles(img, frame, seed=700, count=32, speed=1.1)
    draw = ImageDraw.Draw(img)

    # ── "LAUNCHING SOON" badge ──
    if t > 0.02:
        badge_t = ease_out(min(1, (t - 0.02) / 0.1))
        ba = int(255 * badge_t)
        f_badge = font(FONT_BOLD, 15)
        badge_text = "LAUNCHING SOON"
        bw = tw(draw, badge_text, f_badge) + 40
        bx = W // 2 - bw // 2
        by = H // 2 - 390

        badge_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bd = ImageDraw.Draw(badge_layer)
        rounded_rect(bd, [bx, by, bx + bw, by + 34], 17,
                     fill=(0, 42, 28, int(210 * badge_t)),
                     outline=(0, 210, 140, int(170 * badge_t)), width=1)
        img = Image.alpha_composite(img.convert("RGBA"), badge_layer)
        draw = ImageDraw.Draw(img)
        draw_text_centered(draw, by + 8, badge_text, f_badge, (*GREEN, ba))

    # ── Big "Scan" logo ──
    logo_t = ease_out_elastic(min(1, t / 0.18))
    logo_a = int(255 * min(1, t / 0.08))
    f_logo = font(FONT_BOLD, int(115 * lerp(0.7, 1.0, logo_t)))
    img = glow_text_centered(img, H // 2 - 340, "Scan", f_logo,
                             (*WHITE, logo_a), radius=40, glow_alpha=int(100 * logo_t))
    draw = ImageDraw.Draw(img)

    # ── Tagline ──
    if t > 0.08:
        tag_t = ease_out(min(1, (t - 0.08) / 0.1))
        ta = int(255 * tag_t)
        f_tag = font(FONT_BOLD, 38)

        img = glow_text_centered(img, H // 2 - 205, "The smarter way to", f_tag,
                                 (*WHITE, ta), radius=14, glow_alpha=35)
        img = glow_text_centered(img, H // 2 - 155, "run your protocol.", f_tag,
                                 (*GREEN, ta), radius=18, glow_alpha=55)
        draw = ImageDraw.Draw(img)

    # ── Description ──
    if t > 0.14:
        desc_t = ease_out(min(1, (t - 0.14) / 0.08))
        da = int(200 * desc_t)
        f_desc = font(FONT_REG, 22)
        draw_text_centered(draw, H // 2 - 95, "Track, optimize, and manage your",
                           f_desc, (*GRAY_400, da))
        draw_text_centered(draw, H // 2 - 68, "peptide research in one place.",
                           f_desc, (*GRAY_400, da))

    # ── Email input field with typing animation ──
    if t > 0.2:
        inp_t = ease_out(min(1, (t - 0.2) / 0.1))
        inp_a = int(255 * inp_t)

        inp_w = 640
        inp_h = 56
        inp_x = W // 2 - inp_w // 2
        inp_y = H // 2 - 15

        cl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(cl)
        rounded_rect(cd, [inp_x, inp_y, inp_x + inp_w, inp_y + inp_h], 14,
                     fill=(10, 18, 14, int(220 * inp_t)),
                     outline=(*GRAY_700, inp_a), width=1)
        img = Image.alpha_composite(img.convert("RGBA"), cl)
        draw = ImageDraw.Draw(img)
        
        # Typing animation for email
        email_text = "researcher@peptideai.co"
        typing_t = max(0, (t - 0.28) / 0.2)
        if typing_t > 0 and typing_t < 1:
            chars = int(len(email_text) * ease_out(min(1, typing_t)))
            display = email_text[:chars]
            # Blinking cursor
            cursor = "|" if int(frame * 0.1) % 2 == 0 else ""
            draw.text((inp_x + 20, inp_y + 16), display + cursor,
                      font=font(FONT_REG, 20), fill=(*WHITE, inp_a))
        elif typing_t >= 1:
            draw.text((inp_x + 20, inp_y + 16), email_text,
                      font=font(FONT_REG, 20), fill=(*WHITE, inp_a))
        else:
            draw.text((inp_x + 20, inp_y + 16), "Enter your email",
                      font=font(FONT_REG, 20), fill=(*GRAY_500, inp_a))

    # ── Phone input field ──
    if t > 0.24:
        ph_t = ease_out(min(1, (t - 0.24) / 0.1))
        ph_a = int(255 * ph_t)

        ph_w = 640
        ph_h = 56
        ph_x = W // 2 - ph_w // 2
        ph_y = H // 2 + 53

        cl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(cl)
        rounded_rect(cd, [ph_x, ph_y, ph_x + ph_w, ph_y + ph_h], 14,
                     fill=(10, 18, 14, int(220 * ph_t)),
                     outline=(*GRAY_700, ph_a), width=1)
        img = Image.alpha_composite(img.convert("RGBA"), cl)
        draw = ImageDraw.Draw(img)
        draw.text((ph_x + 20, ph_y + 16), "Phone number (optional)",
                  font=font(FONT_REG, 20), fill=(*GRAY_500, ph_a))

    # ── "Join the Waitlist" button with pulse ──
    if t > 0.28:
        btn_t = ease_out_back(min(1, (t - 0.28) / 0.12))
        ba = int(255 * btn_t)
        btn_w, btn_h = 640, 66
        btn_x = W // 2 - btn_w // 2
        btn_y = H // 2 + 132

        # Pulsing glow
        pulse = 0.7 + 0.3 * math.sin(frame * 0.08)
        
        bg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bgd = ImageDraw.Draw(bg)
        for g in range(30, 0, -2):
            ga = int(12 * (1 - g / 30) * btn_t * pulse)
            rounded_rect(bgd, [btn_x - g, btn_y - g, btn_x + btn_w + g, btn_y + btn_h + g],
                         40, fill=(0, 230, 160, ga))
        img = Image.alpha_composite(img.convert("RGBA"), bg)
        draw = ImageDraw.Draw(img)

        # Gradient button fill
        for row in range(btn_h):
            ratio = row / btn_h
            g_v = int(lerp(255, 220, ratio))
            b_v = int(lerp(180, 150, ratio))
            draw.line([(btn_x + 33, btn_y + row), (btn_x + btn_w - 33, btn_y + row)],
                      fill=(0, g_v, b_v, ba))
        rounded_rect(draw, [btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], 33,
                     fill=None, outline=(0, 255, 180, int(ba * 0.5)), width=1)
        # Manually fill the rounded rect with gradient
        for row in range(btn_h):
            ratio = row / btn_h
            g_v = int(lerp(255, 210, ratio))
            b_v = int(lerp(180, 145, ratio))
            # Only fill inside the pill shape
            margin = 0
            if row < 33 or row > btn_h - 33:
                # Approximate the rounded corners
                if row < 33:
                    d = 33 - row
                else:
                    d = row - (btn_h - 33)
                margin = int(33 - math.sqrt(max(0, 33*33 - d*d)))
            draw.line([(btn_x + margin, btn_y + row), (btn_x + btn_w - margin, btn_y + row)],
                      fill=(0, g_v, b_v, ba))

        f_btn = font(FONT_BOLD, 24)
        btn_text = "Join the Waitlist"
        btw = tw(draw, btn_text, f_btn)
        draw.text((W // 2 - btw // 2, btn_y + 19), btn_text, font=f_btn, fill=(*BLACK, ba))

    # ── "Join 500+" social proof ──
    if t > 0.36:
        sp_t = ease_out(min(1, (t - 0.36) / 0.08))
        sp_a = int(220 * sp_t)
        f_sp = font(FONT_REG, 20)
        draw_text_centered(draw, H // 2 + 218, "Join 500+ on the waitlist",
                           f_sp, (*GRAY_400, sp_a))

    # ── URL ──
    if t > 0.4:
        ut = ease_out(min(1, (t - 0.4) / 0.08))
        ua = int(255 * ut)
        f_url = font(FONT_MONO, 22)
        url = "waitlist.peptideai.co"
        uw = tw(draw, url, f_url)
        draw.text(((W - uw) // 2, H // 2 + 268), url, font=f_url, fill=(*GREEN, ua))

    # ── Bottom brand ──
    if t > 0.52:
        br = ease_out(min(1, (t - 0.52) / 0.1))
        bra = int(255 * br)
        draw_text_centered(draw, H - 175, "SCAN PEPTIDE AI",
                           font(FONT_BOLD, 18), (*GREEN, bra))
        draw_text_centered(draw, H - 145, "Coming soon to iOS & Android",
                           font(FONT_REG, 18), (*GRAY_400, bra))

    img = apply_vignette(img)
    return img.convert("RGB")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VIDEO GENERATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def crossfade(img1, img2, t):
    return Image.blend(img1, img2, t)


def generate_video():
    os.makedirs(FRAMES_DIR, exist_ok=True)

    scenes = [
        (scene_hook, 4.5),
        (scene_app_home, 5.5),
        (scene_stack_tracking, 6.0),
        (scene_body_scan, 5.5),
        (scene_features, 5.0),
        (scene_social_proof, 4.5),
        (scene_cta, 6.0),
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
        print(f"  Scene {idx + 1}/{len(scenes)}: {fn.__name__} ({n} frames)")
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

    output_path = os.path.join(OUTPUT_DIR, "scan-peptide-ai-reel.mp4")
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
    print("Done!")

    # Cleanup
    for f_name in os.listdir(FRAMES_DIR):
        os.remove(os.path.join(FRAMES_DIR, f_name))
    os.rmdir(FRAMES_DIR)

    # Previews at more timestamps
    for ts in [1, 2, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35]:
        subprocess.run(["ffmpeg", "-y", "-i", output_path, "-ss", str(ts),
                        "-frames:v", "1",
                        os.path.join(OUTPUT_DIR, f"preview_{ts}s.jpg")],
                       capture_output=True)
    print("All done!")
    return output_path


if __name__ == "__main__":
    generate_video()
