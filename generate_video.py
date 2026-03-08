#!/usr/bin/env python3
"""
Scan Peptide AI - Premium Ad Reel Generator v3
Featuring:
- Particle-based DNA double helix (hundreds of glowing dots)
- Atmospheric green haze/fog
- Depth-of-field effects
- Smooth cross-fade transitions
- Tailwind CSS-inspired dark UI
- Futuristic biotech aesthetic
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

# ─── COLORS ──────────────────────────────────────────────────────────────────
BG = (4, 8, 6)
BG_CARD = (12, 18, 15)
BG_CARD_BORDER = (28, 42, 35)
BG_CARD_INNER = (16, 24, 19)

GREEN = (0, 220, 100)
GREEN_BRIGHT = (20, 255, 140)
GREEN_TEAL = (0, 200, 150)
GREEN_DIM = (0, 100, 50)
GREEN_SUBTLE = (0, 60, 30)
GREEN_DARK = (0, 40, 20)

WHITE = (255, 255, 255)
GRAY_100 = (240, 240, 240)
GRAY_200 = (200, 205, 210)
GRAY_400 = (140, 148, 155)
GRAY_500 = (100, 108, 115)
GRAY_600 = (70, 78, 85)
GRAY_700 = (40, 48, 44)
BLACK = (0, 0, 0)

# ─── FONTS ───────────────────────────────────────────────────────────────────
FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

# ─── EASING ──────────────────────────────────────────────────────────────────
def ease_out(t):
    return 1 - (1 - max(0, min(1, t))) ** 3

def ease_out_back(t):
    t = max(0, min(1, t))
    c = 1.70158
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2

def ease_out_elastic(t):
    t = max(0, min(1, t))
    if t == 0 or t == 1:
        return t
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * 2 * math.pi / 3) + 1

def lerp(a, b, t):
    return a + (b - a) * max(0, min(1, t))


# ─── DRAWING HELPERS ─────────────────────────────────────────────────────────

def tw(draw, text, f):
    bb = draw.textbbox((0, 0), text, font=f)
    return bb[2] - bb[0]

def draw_text_centered(draw, y, text, f, color):
    w = tw(draw, text, f)
    draw.text(((W - w) // 2, y), text, font=f, fill=color)

def rounded_rect(draw, box, r, fill=None, outline=None, width=1):
    x1, y1, x2, y2 = box
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
        draw.pieslice([x1, y1, x1 + 2 * r, y1 + 2 * r], 180, 270, fill=fill)
        draw.pieslice([x2 - 2 * r, y1, x2, y1 + 2 * r], 270, 360, fill=fill)
        draw.pieslice([x1, y2 - 2 * r, x1 + 2 * r, y2], 90, 180, fill=fill)
        draw.pieslice([x2 - 2 * r, y2 - 2 * r, x2, y2], 0, 90, fill=fill)
    if outline:
        draw.arc([x1, y1, x1 + 2 * r, y1 + 2 * r], 180, 270, fill=outline, width=width)
        draw.arc([x2 - 2 * r, y1, x2, y1 + 2 * r], 270, 360, fill=outline, width=width)
        draw.arc([x1, y2 - 2 * r, x1 + 2 * r, y2], 90, 180, fill=outline, width=width)
        draw.arc([x2 - 2 * r, y2 - 2 * r, x2, y2], 0, 90, fill=outline, width=width)
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


# ─── ATMOSPHERIC BACKGROUND ─────────────────────────────────────────────────

def make_atmosphere(center_x=None, center_y=None, intensity=1.0):
    """Rich atmospheric background with green fog/haze."""
    img = Image.new("RGB", (W, H), BG)
    cx = center_x or W // 2
    cy = center_y or H // 2

    # Multiple layered fog sources
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)

    # Main center glow
    max_r = 800
    for r in range(max_r, 0, -6):
        ratio = r / max_r
        a = int(18 * ratio * intensity)
        g_val = int(lerp(30, 80, ratio))
        fd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0, g_val, int(g_val * 0.5), a))

    # Secondary glow (offset)
    for r in range(500, 0, -8):
        ratio = r / 500
        a = int(10 * ratio * intensity)
        fd.ellipse([cx + 200 - r, cy - 300 - r, cx + 200 + r, cy - 300 + r],
                   fill=(0, 60, 40, a))

    # Bottom ambient
    for r in range(600, 0, -10):
        ratio = r / 600
        a = int(8 * ratio * intensity)
        fd.ellipse([cx - 100 - r, H - 200 - r, cx - 100 + r, H - 200 + r],
                   fill=(0, 50, 30, a))

    img = Image.alpha_composite(img.convert("RGBA"), fog).convert("RGB")
    return img


# ─── PARTICLE DNA HELIX ─────────────────────────────────────────────────────

def draw_dna_helix(base_img, frame, cx=None, y_start=None, y_end=None,
                   amplitude=180, num_points=300, particle_count=8,
                   speed=0.04, alpha_mult=1.0, draw_rungs=True,
                   blur_radius=2, size_mult=1.0):
    """
    Draw a stunning particle-based DNA double helix.
    Each strand is made of hundreds of tiny glowing particles.
    Rungs connect the two strands with thin green lines.
    Depth-of-field: front particles are bigger/brighter.
    """
    cx = cx or W // 2
    y_start = y_start if y_start is not None else -100
    y_end = y_end if y_end is not None else H + 100

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)

    # Pre-compute helix positions
    y_range = y_end - y_start
    phase_offset = frame * speed

    for i in range(num_points):
        t = i / num_points
        y = y_start + t * y_range
        angle = t * math.pi * 8 + phase_offset

        # Two strand positions
        x1 = cx + math.sin(angle) * amplitude
        x2 = cx + math.sin(angle + math.pi) * amplitude

        # Depth: cos gives us front/back. 1 = front, 0 = back
        depth1 = (math.cos(angle) + 1) / 2
        depth2 = (math.cos(angle + math.pi) + 1) / 2

        # Draw rungs (connecting bars) every N points
        if draw_rungs and i % 12 == 0:
            rung_depth = min(depth1, depth2)
            rung_a = int(35 * rung_depth * alpha_mult)
            if rung_a > 0:
                ld.line([(int(x1), int(y)), (int(x2), int(y))],
                        fill=(0, 160, 80, rung_a), width=1)

        # Draw particles for each strand
        for strand_x, depth in [(x1, depth1), (x2, depth2)]:
            # Multiple particles per point for density
            random.seed(int(i * 1000 + depth * 100 + frame * 0.01))
            for p in range(particle_count):
                # Jitter position slightly for organic feel
                jx = strand_x + random.gauss(0, 3 * size_mult)
                jy = y + random.gauss(0, 3 * size_mult)

                # Size based on depth (front = larger)
                base_size = lerp(1.5, 4.5, depth) * size_mult
                size = base_size * random.uniform(0.5, 1.3)

                # Alpha based on depth
                base_alpha = lerp(15, 100, depth) * alpha_mult
                alpha = int(base_alpha * random.uniform(0.4, 1.0))
                alpha = max(0, min(255, alpha))

                if alpha < 3:
                    continue

                # Color: deeper particles are more teal, front ones are bright green
                g = int(lerp(140, 240, depth))
                b = int(lerp(100, 120, depth))
                r = int(lerp(0, 20, depth))

                s = max(1, int(size))
                ld.ellipse([int(jx) - s, int(jy) - s, int(jx) + s, int(jy) + s],
                           fill=(r, g, b, alpha))

                # Extra bright core for front particles
                if depth > 0.7 and size > 2.5:
                    core_s = max(1, s // 2)
                    core_a = min(255, int(alpha * 1.5))
                    ld.ellipse([int(jx) - core_s, int(jy) - core_s,
                                int(jx) + core_s, int(jy) + core_s],
                               fill=(r + 30, min(255, g + 30), b + 20, core_a))

    # Soft blur for glow effect
    if blur_radius > 0:
        layer = layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    return Image.alpha_composite(base_img.convert("RGBA"), layer)


# ─── FLOATING PARTICLES ─────────────────────────────────────────────────────

def draw_particles(base_img, frame, seed=42, count=30, speed=1.0):
    """Soft floating bokeh particles."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    random.seed(seed)

    for i in range(count):
        base_x = random.randint(-80, W + 80)
        base_y = random.randint(-80, H + 80)
        x = base_x + int(math.cos(frame * 0.018 * speed + i * 2.3) * 30)
        y = base_y + int(math.sin(frame * 0.025 * speed + i * 1.7) * 45)
        size = random.randint(12, 55)
        pulse = 0.5 + 0.5 * math.sin(frame * 0.04 + i * 0.9)
        base_a = random.randint(8, 35)
        alpha = int(base_a * pulse)

        for r in range(size, 0, -2):
            ring_a = int(alpha * (r / size) ** 0.6)
            g = int(lerp(80, 220, r / size))
            od.ellipse([x - r, y - r, x + r, y + r],
                       fill=(0, g, int(g * 0.5), ring_a))

    return Image.alpha_composite(base_img.convert("RGBA"), overlay)


def draw_diagonal_stripes(base_img, alpha=15, offset=0):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    stripe_w = 80
    gap = 320
    for start in range(-H + int(offset), W + H, gap):
        pts = [(start, 0), (start + stripe_w, 0),
               (start + stripe_w + int(H * 0.7), H), (start + int(H * 0.7), H)]
        od.polygon(pts, fill=(0, 180, 80, alpha))
        pts2 = [(start + stripe_w + 20, 0), (start + stripe_w + 32, 0),
                (start + stripe_w + 32 + int(H * 0.7), H),
                (start + stripe_w + 20 + int(H * 0.7), H)]
        od.polygon(pts2, fill=(0, 180, 80, alpha // 3))
    return Image.alpha_composite(base_img.convert("RGBA"), overlay)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCENE 1: HOOK - DNA helix behind text (like reference image 3)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def scene_hook(frame, total):
    t = frame / total
    img = make_atmosphere(W // 2, H // 2 - 100, intensity=1.2)

    # DNA helix running through center - vertical, behind text
    dna_alpha = min(1.0, t / 0.15) * 0.8
    img = draw_dna_helix(img, frame, cx=W // 2, y_start=-200, y_end=H + 200,
                         amplitude=160, num_points=350, particle_count=6,
                         speed=0.035, alpha_mult=dna_alpha, draw_rungs=True,
                         blur_radius=3, size_mult=1.1)

    img = draw_particles(img, frame, seed=42, count=20, speed=1.0)

    # Phase 1: Hook text
    if t < 0.45:
        tt = ease_out(min(1, t / 0.2))
        alpha = int(255 * min(1, t / 0.1))
        y_off = int(lerp(60, 0, tt))

        f1 = font(FONT_BOLD, 72)
        f2 = font(FONT_BOLD, 72)

        img = glow_text_centered(img, H // 2 - 100 + y_off, "Your peptides",
                                 f1, (*WHITE, alpha), radius=20, glow_alpha=50)
        img = glow_text_centered(img, H // 2 + 0 + y_off, "deserve better.",
                                 f2, (*GREEN, alpha), radius=25, glow_alpha=70)

    # Phase 2: Transition to "Meet Scan."
    else:
        fade_out = max(0, 1 - (t - 0.45) / 0.1)
        if fade_out > 0:
            a = int(255 * fade_out)
            f1 = font(FONT_BOLD, 72)
            img = glow_text_centered(img, H // 2 - 100, "Your peptides",
                                     f1, (*WHITE, a), radius=20, glow_alpha=int(50 * fade_out))
            img = glow_text_centered(img, H // 2, "deserve better.",
                                     f1, (*GREEN, a), radius=25, glow_alpha=int(70 * fade_out))

        fade_in = ease_out(max(0, (t - 0.5) / 0.18))
        if fade_in > 0:
            a = int(255 * fade_in)
            y_off = int(lerp(30, 0, fade_in))

            # "AI-POWERED PEPTIDE TRACKING" badge
            f_badge = font(FONT_BOLD, 18)
            badge_text = "AI-POWERED PEPTIDE TRACKING"
            bw = tw(ImageDraw.Draw(img), badge_text, f_badge) + 40
            bx = W // 2 - bw // 2
            by = H // 2 - 180 + y_off

            badge_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            bd = ImageDraw.Draw(badge_layer)
            rounded_rect(bd, [bx, by, bx + bw, by + 36], 18,
                         fill=(0, 40, 25, int(180 * fade_in)),
                         outline=(0, 180, 90, int(150 * fade_in)), width=1)
            img = Image.alpha_composite(img.convert("RGBA"), badge_layer)
            draw = ImageDraw.Draw(img)
            draw_text_centered(draw, by + 8, badge_text, f_badge, (*GREEN, a))

            # Big "Scan" text
            f_scan = font(FONT_BOLD, 120)
            img = glow_text_centered(img, H // 2 - 120 + y_off, "Scan",
                                     f_scan, (*WHITE, a), radius=35, glow_alpha=int(90 * fade_in))

            # Subtitle
            if t > 0.62:
                sub_t = ease_out((t - 0.62) / 0.12)
                sub_a = int(255 * sub_t)
                f_sub = font(FONT_REG, 32)
                img = glow_text_centered(img, H // 2 + 30 + int(lerp(15, 0, sub_t)),
                                         "AI-Powered Peptide Intelligence",
                                         f_sub, (*GREEN_TEAL, sub_a), radius=15, glow_alpha=int(50 * sub_t))

    return img.convert("RGB")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCENE 2: APP HOME SCREEN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def scene_app_home(frame, total):
    t = frame / total
    img = make_atmosphere(W // 2, H // 2, intensity=0.8)
    img = draw_diagonal_stripes(img, alpha=10, offset=frame * 0.4)

    # Subtle DNA in background (faded)
    img = draw_dna_helix(img, frame, cx=W // 2 + 300, y_start=-100, y_end=H + 100,
                         amplitude=100, num_points=150, particle_count=3,
                         speed=0.02, alpha_mult=0.25, draw_rungs=False,
                         blur_radius=4, size_mult=0.8)

    img = draw_particles(img, frame, seed=100, count=12, speed=0.8)
    draw = ImageDraw.Draw(img)

    # Title
    if t > 0.03:
        tt = ease_out(min(1, (t - 0.03) / 0.15))
        a = int(255 * tt)
        y_off = int(lerp(-25, 0, tt))
        f_t = font(FONT_BOLD, 46)
        f_s = font(FONT_REG, 26)
        draw_text_centered(draw, 95 + y_off, "Your Command Center", f_t, (*WHITE, a))
        draw_text_centered(draw, 150 + y_off, "Everything in one place", f_s, (*GREEN, a))

    # Phone mockup
    pw, ph = 440, 820
    px = W // 2 - pw // 2
    py = int(lerp(H, 250, ease_out(min(1, t / 0.18)))) if t < 0.18 else 250

    # Phone shadow
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for s in range(35, 0, -2):
        sa = int(10 * (1 - s / 35))
        rounded_rect(sd, [px - s + 6, py - s + 10, px + pw + s + 6, py + ph + s + 10],
                     50, fill=(0, 0, 0, sa))
    img = Image.alpha_composite(img.convert("RGBA"), shadow)
    draw = ImageDraw.Draw(img)

    # Phone body + border glow
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    for g in range(12, 0, -1):
        ga = int(5 * (1 - g / 12))
        rounded_rect(gd, [px - g, py - g, px + pw + g, py + ph + g], 46,
                     fill=(0, 150, 70, ga))
    img = Image.alpha_composite(img.convert("RGBA"), glow_layer)
    draw = ImageDraw.Draw(img)

    rounded_rect(draw, [px, py, px + pw, py + ph], 44, fill=(10, 14, 11, 255))
    rounded_rect(draw, [px, py, px + pw, py + ph], 44, outline=(40, 55, 45, 255), width=2)

    # Notch
    nw, nh = 140, 28
    nx = px + pw // 2 - nw // 2
    rounded_rect(draw, [nx, py, nx + nw, py + nh], 14, fill=(0, 0, 0, 255))

    # Screen content
    sx, sy = px + 16, py + 40
    sw = pw - 32

    f_greet = font(FONT_REG, 14)
    f_name = font(FONT_BOLD, 28)
    draw.text((sx + 20, sy + 12), "GOOD AFTERNOON", font=f_greet, fill=GRAY_500)
    draw.text((sx + 20, sy + 30), "User", font=f_name, fill=WHITE)

    # Profile icon
    ix = sx + sw - 50
    draw.ellipse([ix, sy + 15, ix + 36, sy + 51], fill=GRAY_700, outline=GRAY_600, width=1)

    # Green "Run Body Scan" card
    cy = sy + 80
    ch = 180
    for row in range(ch):
        ratio = row / ch
        g = int(lerp(190, 130, ratio))
        draw.line([(sx + 15, cy + row), (sx + sw - 15, cy + row)],
                  fill=(0, g, int(g * 0.45), 255))

    f_card = font(FONT_BOLD, 26)
    f_csub = font(FONT_REG, 15)
    draw.text((sx + 32, cy + 22), "Run Body Scan", font=f_card, fill=WHITE)
    draw.text((sx + 32, cy + 55), "Start your research access", font=f_csub, fill=(220, 255, 235))
    draw.text((sx + 32, cy + 75), "anywhere, at any time.", font=f_csub, fill=(220, 255, 235))

    # Play button
    pbx, pby = sx + 50, cy + 125
    draw.ellipse([pbx - 18, pby - 18, pbx + 18, pby + 18], fill=(0, 70, 35, 255))
    draw.polygon([(pbx - 6, pby - 9), (pbx - 6, pby + 9), (pbx + 10, pby)], fill=WHITE)

    f_logo_sm = font(FONT_BOLD, 48)
    draw.text((sx + sw - 125, cy + 105), "Scan", font=f_logo_sm, fill=(0, 110, 50, 80))

    # Stats row
    stats_y = cy + ch + 20
    stats = [("ACTIVE", "3"), ("LOGGED", "3"), ("STREAK", "3")]
    anim_base = max(0, (t - 0.25)) / 0.18

    for i, (label, val) in enumerate(stats):
        cx_s = sx + 55 + i * (sw - 110) // 2
        cy_s = stats_y + 38
        r = 28
        draw.arc([cx_s - r, cy_s - r, cx_s + r, cy_s + r], 0, 360, fill=GRAY_700, width=3)
        prog = min(1, max(0, anim_base - i * 0.12))
        if prog > 0:
            angle = int(360 * ease_out(prog))
            draw.arc([cx_s - r, cy_s - r, cx_s + r, cy_s + r], -90, -90 + angle,
                     fill=GREEN, width=3)
        count_v = int(int(val) * ease_out(prog)) if prog > 0 else 0
        f_lab = font(FONT_REG, 10)
        f_val = font(FONT_BOLD, 24)
        lw_ = tw(draw, label, f_lab)
        vw_ = tw(draw, str(count_v), f_val)
        draw.text((cx_s - lw_ // 2, cy_s - r - 16), label, font=f_lab, fill=GRAY_500)
        draw.text((cx_s - vw_ // 2, cy_s - 12), str(count_v), font=f_val, fill=WHITE)

    # Today's Stack
    sty = stats_y + 92
    f_sec = font(FONT_BOLD, 17)
    f_see = font(FONT_REG, 14)
    draw.text((sx + 18, sty), "TODAY'S STACK", font=f_sec, fill=WHITE)
    draw.text((sx + sw - 65, sty + 2), "See All", font=f_see, fill=GREEN)

    items = [("BPC-157", "250mcg · SubQ · 08:00 AM"), ("Semax", "300mcg · Nasal · 12:00 PM")]
    for i, (name, detail) in enumerate(items):
        iy = sty + 30 + i * 66
        rounded_rect(draw, [sx + 14, iy, sx + sw - 14, iy + 55], 11,
                     fill=BG_CARD_INNER, outline=BG_CARD_BORDER, width=1)
        draw.text((sx + 28, iy + 8), name, font=font(FONT_BOLD, 17), fill=WHITE)
        draw.text((sx + 28, iy + 30), detail, font=font(FONT_REG, 12), fill=GRAY_400)
        draw.ellipse([sx + sw - 46, iy + 16, sx + sw - 24, iy + 38], outline=GRAY_600, width=2)

    # Nav bar
    sh = ph - 56
    nav_y = sy + sh - 50
    draw.line([(sx, nav_y), (sx + sw, nav_y)], fill=GRAY_700, width=1)
    for i, item in enumerate(["Home", "Fitness", "Log", "Stack", "Track"]):
        nx_ = sx + 32 + i * (sw - 64) // 4
        color = GREEN if item == "Home" else GRAY_500
        iw = tw(draw, item, font(FONT_REG, 11))
        draw.text((nx_ - iw // 2, nav_y + 22), item, font=font(FONT_REG, 11), fill=color)
        if item == "Home":
            draw.ellipse([nx_ - 2, nav_y + 8, nx_ + 2, nav_y + 12], fill=GREEN)

    return img.convert("RGB")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCENE 3: STACK TRACKING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def scene_stack_tracking(frame, total):
    t = frame / total
    img = make_atmosphere(W // 2, 400, intensity=0.7)

    # DNA on the right side, faded
    img = draw_dna_helix(img, frame, cx=W - 80, y_start=0, y_end=H,
                         amplitude=90, num_points=180, particle_count=4,
                         speed=0.03, alpha_mult=0.3, draw_rungs=True,
                         blur_radius=3, size_mult=0.7)

    img = draw_particles(img, frame, seed=200, count=15, speed=0.7)
    draw = ImageDraw.Draw(img)

    # Title
    tt = ease_out(min(1, t / 0.12))
    a = int(255 * tt)
    y_off = int(lerp(-25, 0, tt))
    draw_text_centered(draw, 95 + y_off, "Track Every Dose", font(FONT_BOLD, 50), (*WHITE, a))
    draw_text_centered(draw, 155 + y_off, "Smart protocols, zero guesswork",
                       font(FONT_REG, 28), (*GREEN, a))

    peptides = [
        {"name": "BPC-157", "type": "PRIMARY COMPOUND", "dose": "250 mcg",
         "route": "SubQ", "freq": "Daily", "status": "ON CYCLE",
         "week": "Week 1 of 13", "progress": 0.08,
         "note": "Start 250mcg/day SubQ. Titrate to 500mcg after week 2."},
        {"name": "TB-500", "type": "SUPPORTING COMPOUND", "dose": "2 mg",
         "route": "SubQ", "freq": "2x Weekly", "status": "ON CYCLE",
         "week": "Week 1 of 10", "progress": 0.1,
         "note": "Standard dosing. Maintain consistent schedule."},
        {"name": "Semax", "type": "NOOTROPIC", "dose": "300 mcg",
         "route": "Nasal", "freq": "Daily", "status": "ON CYCLE",
         "week": "Week 3 of 8", "progress": 0.375,
         "note": "Nasal spray 300mcg AM. Can increase to 600mcg."},
    ]

    card_w = W - 100
    card_x = 50
    start_y = 230

    for i, pep in enumerate(peptides):
        et_raw = max(0, min(1, (t - 0.04 - i * 0.06) / 0.14))
        if et_raw <= 0:
            continue
        et = ease_out(et_raw)
        a = int(255 * et)
        x_sl = int(lerp(120, 0, et))

        card_h = 295
        cy = start_y + i * (card_h + 16)

        # Card layer
        cl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(cl)

        # Green glow at top
        for g in range(10, 0, -1):
            ga = int(7 * (1 - g / 10) * et)
            rounded_rect(cd, [card_x + x_sl - g, cy - g,
                              card_x + card_w + x_sl + g, cy + 3], 4,
                         fill=(0, 200, 90, ga))

        rounded_rect(cd, [card_x + x_sl, cy, card_x + card_w + x_sl, cy + card_h],
                     16, fill=(*BG_CARD, a))
        rounded_rect(cd, [card_x + x_sl, cy, card_x + card_w + x_sl, cy + card_h],
                     16, outline=(*BG_CARD_BORDER, int(a * 0.5)), width=1)
        cd.line([(card_x + 16 + x_sl, cy + 1), (card_x + card_w - 16 + x_sl, cy + 1)],
                fill=(*GREEN, int(a * 0.4)), width=2)

        img = Image.alpha_composite(img.convert("RGBA"), cl)
        draw = ImageDraw.Draw(img)
        bx = card_x + 22 + x_sl

        # Type + name + badge
        draw.text((bx, cy + 16), pep["type"], font=font(FONT_REG, 11), fill=(*GRAY_500, a))
        draw.text((bx, cy + 32), pep["name"], font=font(FONT_BOLD, 34), fill=(*WHITE, a))

        f_badge = font(FONT_BOLD, 11)
        bw = tw(draw, pep["status"], f_badge) + 16
        badge_x = card_x + card_w - bw - 22 + x_sl
        rounded_rect(draw, [badge_x, cy + 18, badge_x + bw, cy + 36], 5,
                     fill=(*GREEN_DARK, a), outline=(*GREEN, int(a * 0.5)), width=1)
        draw.text((badge_x + 8, cy + 20), pep["status"], font=f_badge, fill=(*GREEN, a))

        # Info row
        iy = cy + 82
        infos = [("DOSE", pep["dose"]), ("ROUTE", pep["route"]), ("FREQ", pep["freq"])]
        for j, (lb, vl) in enumerate(infos):
            ix = bx + j * int((card_w - 55) / 3)
            draw.text((ix, iy), lb, font=font(FONT_REG, 10), fill=(*GRAY_500, a))
            draw.text((ix, iy + 14), vl, font=font(FONT_BOLD, 17), fill=(*WHITE, a))

        # Progress bar
        py_ = iy + 50
        draw.text((bx, py_), pep["week"], font=font(FONT_REG, 11), fill=(*GRAY_400, a))
        bar_y = py_ + 20
        bar_w = card_w - 44
        rounded_rect(draw, [bx, bar_y, bx + bar_w, bar_y + 7], 3, fill=(*GRAY_700, a))
        if et_raw > 0.3:
            fw = max(6, int(bar_w * pep["progress"] * ease_out((et_raw - 0.3) / 0.7)))
            rounded_rect(draw, [bx, bar_y, bx + fw, bar_y + 7], 3, fill=(*GREEN, a))

        # Titration note
        ny = bar_y + 18
        rounded_rect(draw, [bx, ny, bx + bar_w, ny + 50], 8,
                     fill=(*BG_CARD_INNER, int(a * 0.8)))
        draw.line([(bx + 4, ny + 8), (bx + 4, ny + 42)], fill=(*GREEN, int(a * 0.5)), width=3)
        draw.text((bx + 14, ny + 8), "TITRATION", font=font(FONT_BOLD, 10), fill=(*GREEN, a))
        draw.text((bx + 14, ny + 24), pep["note"], font=font(FONT_REG, 12), fill=(*GRAY_200, a))

    return img.convert("RGB")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCENE 4: AI BODY SCAN - Full DNA showcase
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def scene_body_scan(frame, total):
    t = frame / total
    img = make_atmosphere(W // 2, H // 2 - 100, intensity=1.5)

    # PROMINENT DNA helix - center stage
    img = draw_dna_helix(img, frame, cx=W // 2, y_start=-150, y_end=H + 150,
                         amplitude=200, num_points=400, particle_count=10,
                         speed=0.045, alpha_mult=1.0, draw_rungs=True,
                         blur_radius=2, size_mult=1.3)

    # Second smaller helix (background depth)
    img = draw_dna_helix(img, frame + 50, cx=W // 2 - 250, y_start=200, y_end=H - 100,
                         amplitude=80, num_points=100, particle_count=3,
                         speed=0.03, alpha_mult=0.2, draw_rungs=False,
                         blur_radius=5, size_mult=0.6)

    # Scanning line sweeping across the DNA
    scan_y = int(200 + (H - 400) * ((t * 2.0) % 1.0))
    scan = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    for dy in range(-35, 35):
        sa = int(60 * (1 - abs(dy) / 35))
        sd.line([(80, scan_y + dy), (W - 80, scan_y + dy)],
                fill=(0, 220, 110, sa), width=1)
    sd.line([(80, scan_y), (W - 80, scan_y)], fill=(0, 255, 130, 100), width=2)
    img = Image.alpha_composite(img.convert("RGBA"), scan)

    img = draw_particles(img, frame, seed=300, count=20, speed=1.2)

    # Title
    tt = ease_out(min(1, t / 0.12))
    a = int(255 * tt)
    f_t = font(FONT_BOLD, 54)
    f_s = font(FONT_REG, 28)
    img = glow_text_centered(img, 100, "AI Body Scan", f_t, (*WHITE, a),
                             radius=22, glow_alpha=int(60 * tt))
    draw = ImageDraw.Draw(img)
    draw_text_centered(draw, 168, "Powered by machine learning", f_s, (*GREEN, a))

    # Feature boxes - positioned to avoid DNA center
    features = [
        ("Real-Time Analysis", "Track changes as\nthey happen"),
        ("Smart Insights", "AI detects patterns\nin your data"),
        ("Progress Tracking", "Visual health scores\nover time"),
        ("Research Grade", "Lab-quality data\nanalysis"),
    ]

    box_w = 380
    positions = [
        (40, H // 2 - 200),
        (W - box_w - 40, H // 2 - 200),
        (40, H // 2 + 30),
        (W - box_w - 40, H // 2 + 30),
    ]

    for i, ((fx, fy), (title, desc)) in enumerate(zip(positions, features)):
        ft = max(0, min(1, (t - 0.12 - i * 0.06) / 0.12))
        if ft <= 0:
            continue
        et = ease_out_back(ft)
        fa = int(255 * min(1, ft / 0.4))
        y_off = int(lerp(25, 0, et))

        box_h = 130
        bl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bl)
        rounded_rect(bd, [fx, fy + y_off, fx + box_w, fy + box_h + y_off], 14,
                     fill=(10, 16, 13, int(200 * min(1, ft / 0.3))))
        rounded_rect(bd, [fx, fy + y_off, fx + box_w, fy + box_h + y_off], 14,
                     outline=(*GREEN_SUBTLE, fa), width=1)
        bd.line([(fx + 14, fy + y_off + 1), (fx + box_w - 14, fy + y_off + 1)],
                fill=(*GREEN, int(fa * 0.3)), width=2)
        img = Image.alpha_composite(img.convert("RGBA"), bl)
        draw = ImageDraw.Draw(img)

        draw.ellipse([fx + 18, fy + 20 + y_off, fx + 30, fy + 32 + y_off], fill=(*GREEN, fa))
        draw.text((fx + 40, fy + 18 + y_off), title, font=font(FONT_BOLD, 22), fill=(*WHITE, fa))
        for li, line in enumerate(desc.split("\n")):
            draw.text((fx + 18, fy + 50 + li * 22 + y_off), line,
                      font=font(FONT_REG, 16), fill=(*GRAY_400, fa))

    # Bottom stats
    if t > 0.5:
        st = ease_out(min(1, (t - 0.5) / 0.12))
        sa = int(255 * st)
        stats = [("98%", "Accuracy"), ("<30s", "Scan Time"), ("24/7", "Monitoring")]
        for i, (val, label) in enumerate(stats):
            sx_ = 140 + i * 300
            sy_ = H - 320
            f_sv = font(FONT_BOLD, 48)
            f_sl = font(FONT_REG, 18)
            vw = tw(draw, val, f_sv)
            lw = tw(draw, label, f_sl)
            img = glow_text(img, (sx_ - vw // 2, sy_), val, f_sv,
                            (*GREEN, sa), radius=12, glow_alpha=int(40 * st))
            draw = ImageDraw.Draw(img)
            draw.text((sx_ - lw // 2, sy_ + 55), label, font=f_sl, fill=(*GRAY_200, sa))

    return img.convert("RGB")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCENE 5: FEATURES OVERVIEW
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def scene_features(frame, total):
    t = frame / total
    img = make_atmosphere(W // 2, 600, intensity=0.8)
    img = draw_diagonal_stripes(img, alpha=8, offset=frame * 0.3)
    img = draw_particles(img, frame, seed=400, count=15, speed=0.6)
    draw = ImageDraw.Draw(img)

    tt = ease_out(min(1, t / 0.12))
    a = int(255 * tt)
    draw_text_centered(draw, 110, "Everything You Need", font(FONT_BOLD, 48), (*WHITE, a))

    features = [
        ("Protocol Builder", "Create custom peptide protocols"),
        ("Dose Calculator", "Auto-calculate based on weight"),
        ("Progress Journal", "Log symptoms & recovery daily"),
        ("Stack Optimizer", "AI-optimized peptide combos"),
        ("Community", "10K+ researchers worldwide"),
        ("Data Export", "Export research data anytime"),
    ]

    card_w = (W - 110 - 20) // 2
    card_h = 190
    gap = 20
    start_y = 230

    for i, (title, desc) in enumerate(features):
        col, row = i % 2, i // 2
        ft = max(0, min(1, (t - 0.06 - i * 0.04) / 0.12))
        if ft <= 0:
            continue
        et = ease_out_back(ft)
        fa = int(255 * min(1, ft / 0.3))
        y_off = int(lerp(40, 0, et))

        cx_ = 55 + col * (card_w + gap)
        cy_ = start_y + row * (card_h + gap)

        cl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(cl)
        rounded_rect(cd, [cx_, cy_ + y_off, cx_ + card_w, cy_ + card_h + y_off], 16,
                     fill=(*BG_CARD, int(220 * min(1, ft / 0.25))))
        rounded_rect(cd, [cx_, cy_ + y_off, cx_ + card_w, cy_ + card_h + y_off], 16,
                     outline=(*BG_CARD_BORDER, fa), width=1)
        img = Image.alpha_composite(img.convert("RGBA"), cl)
        draw = ImageDraw.Draw(img)

        # Number circle
        draw.ellipse([cx_ + 22, cy_ + 28 + y_off, cx_ + 44, cy_ + 50 + y_off],
                     fill=(*GREEN_DARK, fa), outline=(*GREEN, fa), width=2)
        f_num = font(FONT_BOLD, 14)
        ns = str(i + 1)
        nw = tw(draw, ns, f_num)
        draw.text((cx_ + 33 - nw // 2, cy_ + 31 + y_off), ns, font=f_num, fill=(*GREEN, fa))

        draw.text((cx_ + 20, cy_ + 65 + y_off), title,
                  font=font(FONT_BOLD, 22), fill=(*WHITE, fa))
        draw.text((cx_ + 20, cy_ + 95 + y_off), desc,
                  font=font(FONT_REG, 15), fill=(*GRAY_400, fa))

    return img.convert("RGB")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCENE 6: SOCIAL PROOF
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def scene_social_proof(frame, total):
    t = frame / total
    img = make_atmosphere(W // 2, H // 2, intensity=1.0)

    # Subtle DNA in background
    img = draw_dna_helix(img, frame, cx=W // 2, y_start=-50, y_end=H + 50,
                         amplitude=250, num_points=200, particle_count=3,
                         speed=0.025, alpha_mult=0.2, draw_rungs=False,
                         blur_radius=5, size_mult=0.7)

    img = draw_particles(img, frame, seed=500, count=25, speed=0.9)
    draw = ImageDraw.Draw(img)

    tt = ease_out(min(1, t / 0.1))
    a = int(255 * tt)
    draw_text_centered(draw, 220, "Trusted by Researchers", font(FONT_BOLD, 46), (*WHITE, a))
    draw_text_centered(draw, 278, "Join thousands already optimizing",
                       font(FONT_REG, 24), (*GRAY_400, a))

    stats = [("10K+", "Active Researchers"), ("50+", "Peptides Tracked"),
             ("1M+", "Doses Logged"), ("4.9/5", "App Store Rating")]

    center_y = H // 2 - 150
    for i, (val, label) in enumerate(stats):
        st = max(0, min(1, (t - 0.06 - i * 0.07) / 0.15))
        if st <= 0:
            continue
        et = ease_out(st)
        sa = int(255 * et)
        y_off = int(lerp(30, 0, et))
        sy = center_y + i * 160

        f_v = font(FONT_BOLD, 72)
        f_l = font(FONT_REG, 26)
        vw = tw(draw, val, f_v)
        lw = tw(draw, label, f_l)

        img = glow_text(img, ((W - vw) // 2, sy + y_off), val, f_v,
                        (*GREEN, sa), radius=18, glow_alpha=int(55 * et))
        draw = ImageDraw.Draw(img)
        draw.text(((W - lw) // 2, sy + 72 + y_off), label, font=f_l, fill=(*GRAY_200, sa))

        if i < 3:
            div_a = int(25 * et)
            draw.line([(W // 2 - 100, sy + 125 + y_off), (W // 2 + 100, sy + 125 + y_off)],
                      fill=(*GRAY_700, div_a), width=1)

    return img.convert("RGB")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCENE 7: CTA - DNA + Call to Action
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def scene_cta(frame, total):
    t = frame / total
    img = make_atmosphere(W // 2, H // 2, intensity=1.3)
    img = draw_diagonal_stripes(img, alpha=14, offset=frame * 0.6)

    # DNA helix behind CTA
    img = draw_dna_helix(img, frame, cx=W // 2, y_start=-100, y_end=H + 100,
                         amplitude=220, num_points=300, particle_count=7,
                         speed=0.04, alpha_mult=0.5, draw_rungs=True,
                         blur_radius=3, size_mult=1.0)

    img = draw_particles(img, frame, seed=700, count=30, speed=1.1)
    draw = ImageDraw.Draw(img)

    # Logo with elastic bounce
    logo_t = ease_out_elastic(min(1, t / 0.25))
    logo_a = int(255 * min(1, t / 0.1))
    f_logo = font(FONT_BOLD, int(120 * lerp(0.7, 1.0, logo_t)))
    img = glow_text_centered(img, H // 2 - 320, "Scan", f_logo,
                             (*WHITE, logo_a), radius=35, glow_alpha=int(90 * logo_t))
    draw = ImageDraw.Draw(img)

    # Tagline
    if t > 0.12:
        tag_t = ease_out(min(1, (t - 0.12) / 0.1))
        ta = int(255 * tag_t)
        draw_text_centered(draw, H // 2 - 175, "The Future of Peptide Research",
                           font(FONT_REG, 30), (*GREEN_TEAL, ta))

    # CTA Button
    if t > 0.22:
        btn_t = ease_out_back(min(1, (t - 0.22) / 0.12))
        ba = int(255 * btn_t)
        btn_w, btn_h = 640, 74
        btn_x = W // 2 - btn_w // 2
        btn_y = H // 2 - 80

        # Button glow
        bg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bgd = ImageDraw.Draw(bg)
        for g in range(30, 0, -2):
            ga = int(12 * (1 - g / 30) * btn_t)
            rounded_rect(bgd, [btn_x - g, btn_y - g, btn_x + btn_w + g, btn_y + btn_h + g],
                         42, fill=(0, 200, 90, ga))
        img = Image.alpha_composite(img.convert("RGBA"), bg)
        draw = ImageDraw.Draw(img)

        rounded_rect(draw, [btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], 37, fill=(*GREEN, ba))
        f_btn = font(FONT_BOLD, 28)
        btn_text = "Join the Waitlist — It's Free"
        btw = tw(draw, btn_text, f_btn)
        draw.text((W // 2 - btw // 2, btn_y + 21), btn_text, font=f_btn, fill=(*BLACK, ba))

    # URL
    if t > 0.32:
        ut = ease_out(min(1, (t - 0.32) / 0.08))
        ua = int(255 * ut)
        f_url = font(FONT_MONO, 24)
        url = "waitlist.peptideai.co"
        uw = tw(draw, url, f_url)
        draw.text(((W - uw) // 2, H // 2 + 20), url, font=f_url, fill=(*GREEN_BRIGHT, ua))

    # Feature bullets
    if t > 0.38:
        bullets = [
            "Track 50+ peptides & compounds",
            "AI-powered body scanning",
            "Custom protocol builder",
            "Research-grade data logging",
            "Community of 10K+ researchers",
        ]
        f_b = font(FONT_REG, 23)
        by_start = H // 2 + 90
        for i, b in enumerate(bullets):
            bt = max(0, min(1, (t - 0.38 - i * 0.035) / 0.08))
            if bt <= 0:
                continue
            bet = ease_out(bt)
            ba_ = int(255 * bet)
            x_off = int(lerp(35, 0, bet))

            bx_ = 155 + x_off
            by_ = by_start + i * 50
            draw.ellipse([bx_, by_ + 9, bx_ + 8, by_ + 17], fill=(*GREEN, ba_))
            draw.text((bx_ + 22, by_), b, font=f_b, fill=(*GRAY_100, ba_))

    # Bottom brand
    if t > 0.55:
        br = min(1, (t - 0.55) / 0.1)
        bra = int(255 * br)
        draw_text_centered(draw, H - 210, "SCAN PEPTIDE AI",
                           font(FONT_BOLD, 18), (*GREEN, bra))
        draw_text_centered(draw, H - 180, "Coming soon to iOS & Android",
                           font(FONT_REG, 18), (*GRAY_400, bra))

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
        (scene_app_home, 5.0),
        (scene_stack_tracking, 6.0),
        (scene_body_scan, 5.5),
        (scene_features, 4.5),
        (scene_social_proof, 4.5),
        (scene_cta, 6.0),
    ]

    total_duration = sum(d for _, d in scenes)
    print(f"Total duration: {total_duration}s at {FPS}fps")
    cf = CROSSFADE_FRAMES

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

    # Previews
    for ts in [1, 3, 5, 8, 12, 16, 20, 24, 28, 32]:
        subprocess.run(["ffmpeg", "-y", "-i", output_path, "-ss", str(ts),
                        "-frames:v", "1",
                        os.path.join(OUTPUT_DIR, f"preview_{ts}s.jpg")],
                       capture_output=True)
    print("All done!")
    return output_path


if __name__ == "__main__":
    generate_video()
