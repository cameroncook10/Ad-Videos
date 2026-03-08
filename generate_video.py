#!/usr/bin/env python3
"""
Scan Peptide AI - Premium Ad Reel Generator v4
Matching app screenshots and waitlist page exactly.
Featuring:
- Particle-based DNA double helix
- Atmospheric teal haze/fog
- Smooth cross-fade transitions
- Exact app UI replication
- Waitlist page CTA replication
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
BG_CARD = (12, 18, 15)
BG_CARD_BORDER = (28, 45, 38)
BG_CARD_INNER = (16, 24, 19)

GREEN = (0, 230, 160)          # Primary teal/mint accent
GREEN_BRIGHT = (0, 255, 170)   # Brighter for buttons/CTA
GREEN_TEAL = (0, 210, 155)     # Subtitle teal
GREEN_DIM = (0, 110, 70)
GREEN_SUBTLE = (0, 65, 42)
GREEN_DARK = (0, 42, 28)
GREEN_GLOW = (0, 200, 130)     # For card border glows

WHITE = (255, 255, 255)
GRAY_100 = (240, 240, 240)
GRAY_200 = (200, 205, 210)
GRAY_400 = (140, 148, 155)
GRAY_500 = (100, 108, 115)
GRAY_600 = (70, 78, 85)
GRAY_700 = (40, 48, 44)
BLACK = (0, 0, 0)

# Stat card icon colors
BLUE_ACCENT = (60, 140, 255)
ORANGE_ACCENT = (255, 160, 50)
RED_ACCENT = (255, 80, 80)

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

def th(draw, text, f):
    bb = draw.textbbox((0, 0), text, font=f)
    return bb[3] - bb[1]

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
    """Rich atmospheric background with teal fog/haze."""
    img = Image.new("RGB", (W, H), BG)
    cx = center_x or W // 2
    cy = center_y or H // 2

    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)

    # Main center glow - teal tinted
    max_r = 800
    for r in range(max_r, 0, -6):
        ratio = r / max_r
        a = int(18 * ratio * intensity)
        g_val = int(lerp(30, 80, ratio))
        b_val = int(g_val * 0.7)  # More teal
        fd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0, g_val, b_val, a))

    # Secondary glow (offset)
    for r in range(500, 0, -8):
        ratio = r / 500
        a = int(10 * ratio * intensity)
        fd.ellipse([cx + 200 - r, cy - 300 - r, cx + 200 + r, cy - 300 + r],
                   fill=(0, 60, 50, a))

    # Bottom ambient
    for r in range(600, 0, -10):
        ratio = r / 600
        a = int(8 * ratio * intensity)
        fd.ellipse([cx - 100 - r, H - 200 - r, cx - 100 + r, H - 200 + r],
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

        if draw_rungs and i % 12 == 0:
            rung_depth = min(depth1, depth2)
            rung_a = int(35 * rung_depth * alpha_mult)
            if rung_a > 0:
                ld.line([(int(x1), int(y)), (int(x2), int(y))],
                        fill=(0, 180, 120, rung_a), width=1)

        for strand_x, depth in [(x1, depth1), (x2, depth2)]:
            random.seed(int(i * 1000 + depth * 100 + frame * 0.01))
            for p in range(particle_count):
                jx = strand_x + random.gauss(0, 3 * size_mult)
                jy = y + random.gauss(0, 3 * size_mult)

                base_size = lerp(1.5, 4.5, depth) * size_mult
                size = base_size * random.uniform(0.5, 1.3)

                base_alpha = lerp(15, 100, depth) * alpha_mult
                alpha = int(base_alpha * random.uniform(0.4, 1.0))
                alpha = max(0, min(255, alpha))

                if alpha < 3:
                    continue

                # Teal-shifted particle colors
                g = int(lerp(150, 240, depth))
                b = int(lerp(110, 160, depth))
                r = int(lerp(0, 15, depth))

                s = max(1, int(size))
                ld.ellipse([int(jx) - s, int(jy) - s, int(jx) + s, int(jy) + s],
                           fill=(r, g, b, alpha))

                if depth > 0.7 and size > 2.5:
                    core_s = max(1, s // 2)
                    core_a = min(255, int(alpha * 1.5))
                    ld.ellipse([int(jx) - core_s, int(jy) - core_s,
                                int(jx) + core_s, int(jy) + core_s],
                               fill=(r + 20, min(255, g + 20), min(255, b + 20), core_a))

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
        x = base_x + int(math.cos(frame * 0.018 * speed + i * 2.3) * 30)
        y = base_y + int(math.sin(frame * 0.025 * speed + i * 1.7) * 45)
        size = random.randint(12, 55)
        pulse = 0.5 + 0.5 * math.sin(frame * 0.04 + i * 0.9)
        base_a = random.randint(8, 35)
        alpha = int(base_a * pulse)

        for r in range(size, 0, -2):
            ring_a = int(alpha * (r / size) ** 0.6)
            g = int(lerp(80, 220, r / size))
            b_val = int(g * 0.7)
            od.ellipse([x - r, y - r, x + r, y + r],
                       fill=(0, g, b_val, ring_a))

    return Image.alpha_composite(base_img.convert("RGBA"), overlay)


def draw_diagonal_stripes(base_img, alpha=15, offset=0):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    stripe_w = 80
    gap = 320
    for start in range(-H + int(offset), W + H, gap):
        pts = [(start, 0), (start + stripe_w, 0),
               (start + stripe_w + int(H * 0.7), H), (start + int(H * 0.7), H)]
        od.polygon(pts, fill=(0, 180, 120, alpha))
        pts2 = [(start + stripe_w + 20, 0), (start + stripe_w + 32, 0),
                (start + stripe_w + 32 + int(H * 0.7), H),
                (start + stripe_w + 20 + int(H * 0.7), H)]
        od.polygon(pts2, fill=(0, 180, 120, alpha // 3))
    return Image.alpha_composite(base_img.convert("RGBA"), overlay)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCENE 1: HOOK - Hero text from app + DNA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def scene_hook(frame, total):
    t = frame / total
    img = make_atmosphere(W // 2, H // 2 - 100, intensity=1.2)

    # DNA helix running through center
    dna_alpha = min(1.0, t / 0.15) * 0.8
    img = draw_dna_helix(img, frame, cx=W // 2, y_start=-200, y_end=H + 200,
                         amplitude=160, num_points=350, particle_count=6,
                         speed=0.035, alpha_mult=dna_alpha, draw_rungs=True,
                         blur_radius=3, size_mult=1.1)

    img = draw_particles(img, frame, seed=42, count=20, speed=1.0)

    # Phase 1: Hook text from hero
    if t < 0.45:
        tt = ease_out(min(1, t / 0.2))
        alpha = int(255 * min(1, t / 0.1))
        y_off = int(lerp(60, 0, tt))

        f1 = font(FONT_BOLD, 68)

        # "Optimize Your" in white, "Peptide Stack" in teal
        img = glow_text_centered(img, H // 2 - 120 + y_off, "Optimize Your",
                                 f1, (*WHITE, alpha), radius=20, glow_alpha=50)
        img = glow_text_centered(img, H // 2 - 40 + y_off, "Peptide Stack",
                                 f1, (*GREEN, alpha), radius=25, glow_alpha=70)

        # Subtitle from waitlist
        if t > 0.12:
            sub_t = ease_out((t - 0.12) / 0.12)
            sub_a = int(200 * sub_t)
            f_sub = font(FONT_REG, 28)
            img = glow_text_centered(img, H // 2 + 60 + y_off,
                                     "The smarter way to run your protocol.",
                                     f_sub, (*GREEN_TEAL, sub_a), radius=12, glow_alpha=40)

    # Phase 2: Transition to "Scan" brand reveal
    else:
        fade_out = max(0, 1 - (t - 0.45) / 0.1)
        if fade_out > 0:
            a = int(255 * fade_out)
            f1 = font(FONT_BOLD, 68)
            img = glow_text_centered(img, H // 2 - 120, "Optimize Your",
                                     f1, (*WHITE, a), radius=20, glow_alpha=int(50 * fade_out))
            img = glow_text_centered(img, H // 2 - 40, "Peptide Stack",
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
                         fill=(0, 42, 28, int(180 * fade_in)),
                         outline=(0, 200, 130, int(150 * fade_in)), width=1)
            img = Image.alpha_composite(img.convert("RGBA"), badge_layer)
            draw = ImageDraw.Draw(img)
            draw_text_centered(draw, by + 8, badge_text, f_badge, (*GREEN, a))

            # Big "Scan" text
            f_scan = font(FONT_BOLD, 120)
            img = glow_text_centered(img, H // 2 - 120 + y_off, "Scan",
                                     f_scan, (*WHITE, a), radius=35, glow_alpha=int(90 * fade_in))
            draw = ImageDraw.Draw(img)

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
# SCENE 2: APP HOME SCREEN (exact match to screenshot)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def scene_app_home(frame, total):
    t = frame / total
    img = make_atmosphere(W // 2, H // 2, intensity=0.6)
    img = draw_diagonal_stripes(img, alpha=8, offset=frame * 0.4)
    img = draw_particles(img, frame, seed=100, count=10, speed=0.8)
    draw = ImageDraw.Draw(img)

    # Phone mockup dimensions
    pw, ph = 480, 880
    px = W // 2 - pw // 2
    py_target = 520
    py = int(lerp(H + 100, py_target, ease_out(min(1, t / 0.2))))

    # Title above phone
    if t > 0.03:
        tt = ease_out(min(1, (t - 0.03) / 0.15))
        a = int(255 * tt)
        y_off = int(lerp(-25, 0, tt))
        draw_text_centered(draw, 140 + y_off, "Your Command Center",
                           font(FONT_BOLD, 50), (*WHITE, a))
        draw_text_centered(draw, 205 + y_off, "Everything in one place",
                           font(FONT_REG, 28), (*GREEN, a))

    # Phone shadow
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for s in range(30, 0, -2):
        sa = int(8 * (1 - s / 30))
        rounded_rect(sd, [px - s + 5, py - s + 8, px + pw + s + 5, py + ph + s + 8],
                     48, fill=(0, 0, 0, sa))
    img = Image.alpha_composite(img.convert("RGBA"), shadow)
    draw = ImageDraw.Draw(img)

    # Phone body with green border glow
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    for g in range(14, 0, -1):
        ga = int(6 * (1 - g / 14))
        rounded_rect(gd, [px - g, py - g, px + pw + g, py + ph + g], 48,
                     fill=(0, 180, 120, ga))
    img = Image.alpha_composite(img.convert("RGBA"), glow_layer)
    draw = ImageDraw.Draw(img)

    # Phone body
    rounded_rect(draw, [px, py, px + pw, py + ph], 44, fill=(8, 12, 10, 255))
    rounded_rect(draw, [px, py, px + pw, py + ph], 44,
                 outline=(35, 55, 45, 255), width=2)

    # Notch
    nw, nh = 140, 28
    nx = px + pw // 2 - nw // 2
    rounded_rect(draw, [nx, py, nx + nw, py + nh], 14, fill=(0, 0, 0, 255))

    # ── Screen content area ──
    sx, sy = px + 20, py + 48
    sw = pw - 40

    # Greeting: "GOOD EVENING" in green, "Cameron" in white
    anim_t = max(0, (t - 0.15)) / 0.15
    if anim_t > 0:
        et = ease_out(min(1, anim_t))
        a = int(255 * et)

        f_greet = font(FONT_BOLD, 13)
        f_name = font(FONT_BOLD, 30)
        f_date = font(FONT_REG, 14)

        draw.text((sx + 14, sy + 8), "GOOD EVENING", font=f_greet, fill=(*GREEN, a))
        draw.text((sx + 14, sy + 26), "Cameron", font=f_name, fill=(*WHITE, a))
        draw.text((sx + 14, sy + 62), "Tuesday, Mar 3", font=f_date, fill=(*GRAY_400, a))

        # App icon (green rounded square, top right)
        icon_x = sx + sw - 52
        icon_y = sy + 12
        icon_s = 42
        rounded_rect(draw, [icon_x, icon_y, icon_x + icon_s, icon_y + icon_s], 12,
                     fill=(*GREEN, a))
        # "S" letter inside icon
        f_icon = font(FONT_BOLD, 24)
        siw = tw(draw, "S", f_icon)
        draw.text((icon_x + icon_s // 2 - siw // 2, icon_y + 8), "S",
                  font=f_icon, fill=(*BLACK, a))

    # "Run Body Scan" card - single row with green dot and chevron
    card_y = sy + 95
    card_h = 56
    if t > 0.22:
        ct = ease_out(min(1, (t - 0.22) / 0.12))
        ca = int(255 * ct)
        x_sl = int(lerp(40, 0, ct))

        # Dark card with subtle green border
        cl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(cl)
        rounded_rect(cd, [sx + 10 + x_sl, card_y, sx + sw - 10 + x_sl, card_y + card_h], 14,
                     fill=(14, 22, 18, ca))
        rounded_rect(cd, [sx + 10 + x_sl, card_y, sx + sw - 10 + x_sl, card_y + card_h], 14,
                     outline=(*BG_CARD_BORDER, ca), width=1)
        img = Image.alpha_composite(img.convert("RGBA"), cl)
        draw = ImageDraw.Draw(img)

        # Green dot
        dot_x = sx + 30 + x_sl
        dot_y = card_y + card_h // 2
        draw.ellipse([dot_x - 5, dot_y - 5, dot_x + 5, dot_y + 5], fill=(*GREEN, ca))

        # "Run Body Scan" text
        draw.text((dot_x + 16, card_y + 16), "Run Body Scan",
                  font=font(FONT_BOLD, 20), fill=(*WHITE, ca))

        # Chevron ">"
        chev_x = sx + sw - 38 + x_sl
        draw.text((chev_x, card_y + 14), ">", font=font(FONT_BOLD, 22), fill=(*GRAY_500, ca))

    # 3 Square stat cards: ACTIVE, LOGGED, STREAK
    stat_y = card_y + card_h + 18
    stat_card_w = (sw - 48) // 3
    stat_card_h = stat_card_w  # Square

    stat_items = [
        ("ACTIVE", "3", GREEN, (0, 180, 120)),
        ("LOGGED", "12", BLUE_ACCENT, (50, 100, 200)),
        ("STREAK", "5d", ORANGE_ACCENT, (200, 120, 30)),
    ]

    for i, (label, val, icon_color, icon_bg) in enumerate(stat_items):
        anim_delay = 0.28 + i * 0.05
        if t <= anim_delay:
            continue
        st = ease_out_back(min(1, (t - anim_delay) / 0.14))
        sa = int(255 * st)
        y_off = int(lerp(25, 0, st))

        cx_ = sx + 14 + i * (stat_card_w + 10)
        cy_ = stat_y + y_off

        # Card background
        cl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(cl)
        rounded_rect(cd, [cx_, cy_, cx_ + stat_card_w, cy_ + stat_card_h], 16,
                     fill=(14, 22, 18, sa))
        rounded_rect(cd, [cx_, cy_, cx_ + stat_card_w, cy_ + stat_card_h], 16,
                     outline=(*BG_CARD_BORDER, int(sa * 0.6)), width=1)
        img = Image.alpha_composite(img.convert("RGBA"), cl)
        draw = ImageDraw.Draw(img)

        # Colored icon circle at top-left of card
        ic_x = cx_ + 14
        ic_y = cy_ + 14
        ic_r = 16
        draw.ellipse([ic_x, ic_y, ic_x + ic_r * 2, ic_y + ic_r * 2],
                     fill=(*icon_bg, int(sa * 0.3)))
        draw.ellipse([ic_x + 3, ic_y + 3, ic_x + ic_r * 2 - 3, ic_y + ic_r * 2 - 3],
                     fill=(*icon_color, sa))

        # Value - large
        f_val = font(FONT_BOLD, 32)
        draw.text((cx_ + 14, cy_ + stat_card_h - 60), val,
                  font=f_val, fill=(*WHITE, sa))

        # Label - small
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

    # Stack items: BPC-157 (green accent, checkmark), Semax (gray circle)
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
        x_sl = int(lerp(30, 0, it))

        iy = stack_y + 28 + i * 62

        # Card with green left accent for BPC-157
        cl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(cl)
        rounded_rect(cd, [sx + 10 + x_sl, iy, sx + sw - 10 + x_sl, iy + 52], 12,
                     fill=(14, 22, 18, ia))
        # Green left accent bar for checked items
        if checked:
            cd.rectangle([sx + 10 + x_sl, iy + 6, sx + 14 + x_sl, iy + 46],
                         fill=(*GREEN, ia))
        img = Image.alpha_composite(img.convert("RGBA"), cl)
        draw = ImageDraw.Draw(img)

        # Text
        tx = sx + 24 + x_sl
        draw.text((tx, iy + 8), name, font=font(FONT_BOLD, 17), fill=(*WHITE, ia))
        draw.text((tx, iy + 30), detail, font=font(FONT_REG, 12), fill=(*GRAY_400, ia))

        # Checkmark or circle on right
        ck_x = sx + sw - 38 + x_sl
        ck_y = iy + 16
        if checked:
            draw.ellipse([ck_x, ck_y, ck_x + 20, ck_y + 20], fill=(*GREEN, ia))
            # Simple checkmark
            draw.line([(ck_x + 5, ck_y + 10), (ck_x + 9, ck_y + 14)],
                      fill=(*BLACK, ia), width=2)
            draw.line([(ck_x + 9, ck_y + 14), (ck_x + 15, ck_y + 6)],
                      fill=(*BLACK, ia), width=2)
        else:
            draw.ellipse([ck_x, ck_y, ck_x + 20, ck_y + 20],
                         outline=(*GRAY_600, ia), width=2)

    # Bottom navigation bar
    nav_y = py + ph - 60
    draw.line([(sx, nav_y), (sx + sw, nav_y)], fill=(*GRAY_700, 200), width=1)

    nav_items = ["Home", "Scan", "Log", "Stack", "Profile"]
    for i, item in enumerate(nav_items):
        nx_ = sx + 28 + i * (sw - 56) // 4
        color = GREEN if item == "Home" else GRAY_500
        f_nav = font(FONT_REG, 11)
        iw = tw(draw, item, f_nav)

        # Simple icon representations
        ic_y = nav_y + 10
        ic_x = nx_
        if item == "Home":
            # Filled dot for active
            draw.ellipse([ic_x - 3, ic_y, ic_x + 3, ic_y + 6], fill=GREEN)
        else:
            draw.ellipse([ic_x - 2, ic_y + 1, ic_x + 2, ic_y + 5],
                         outline=GRAY_600, width=1)

        draw.text((nx_ - iw // 2, nav_y + 22), item, font=f_nav, fill=color)

    return img.convert("RGB")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCENE 3: STACK TRACKING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def scene_stack_tracking(frame, total):
    t = frame / total
    img = make_atmosphere(W // 2, 400, intensity=0.7)

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
         "note": "Start at 250mcg/day SubQ. Titrate to 500 mcg after week 2 i..."},
        {"name": "TB-500", "type": "SUPPORTING COMPOUND", "dose": "2 mg",
         "route": "SubQ", "freq": "Twice weekly", "status": "ON CYCLE",
         "week": "Week 1 of 10", "progress": 0.1,
         "note": "Standard dosing protocol. Maintain consistent schedule for u..."},
        {"name": "Semax", "type": "NOOTROPIC", "dose": "300 mcg",
         "route": "Nasal", "freq": "Daily", "status": "ON CYCLE",
         "week": "Week 3 of 8", "progress": 0.375,
         "note": "Nasal spray 300mcg AM. Can increase to 600mcg if well toler..."},
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

        cl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(cl)

        # Green glow at top
        for g in range(10, 0, -1):
            ga = int(7 * (1 - g / 10) * et)
            rounded_rect(cd, [card_x + x_sl - g, cy - g,
                              card_x + card_w + x_sl + g, cy + 3], 4,
                         fill=(0, 200, 130, ga))

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
        infos = [("DOSE", pep["dose"]), ("ROUTE", pep["route"]), ("FREQUENCY", pep["freq"])]
        for j, (lb, vl) in enumerate(infos):
            ix = bx + j * int((card_w - 55) / 3)
            draw.text((ix, iy), lb, font=font(FONT_REG, 10), fill=(*GRAY_500, a))
            draw.text((ix, iy + 14), vl, font=font(FONT_BOLD, 17), fill=(*GREEN, a))

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

    # Prominent DNA helix
    img = draw_dna_helix(img, frame, cx=W // 2, y_start=-150, y_end=H + 150,
                         amplitude=200, num_points=400, particle_count=10,
                         speed=0.045, alpha_mult=1.0, draw_rungs=True,
                         blur_radius=2, size_mult=1.3)

    # Second smaller helix (background)
    img = draw_dna_helix(img, frame + 50, cx=W // 2 - 250, y_start=200, y_end=H - 100,
                         amplitude=80, num_points=100, particle_count=3,
                         speed=0.03, alpha_mult=0.2, draw_rungs=False,
                         blur_radius=5, size_mult=0.6)

    # Scanning line
    scan_y = int(200 + (H - 400) * ((t * 2.0) % 1.0))
    scan = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    for dy in range(-35, 35):
        sa = int(60 * (1 - abs(dy) / 35))
        sd.line([(80, scan_y + dy), (W - 80, scan_y + dy)],
                fill=(0, 220, 150, sa), width=1)
    sd.line([(80, scan_y), (W - 80, scan_y)], fill=(0, 255, 170, 100), width=2)
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

    # Feature boxes
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

        # Green icon circle
        draw.ellipse([cx_ + 22, cy_ + 28 + y_off, cx_ + 48, cy_ + 54 + y_off],
                     fill=(*GREEN_DARK, fa), outline=(*GREEN, fa), width=2)
        f_num = font(FONT_BOLD, 16)
        ns = str(i + 1)
        nw = tw(draw, ns, f_num)
        draw.text((cx_ + 35 - nw // 2, cy_ + 33 + y_off), ns, font=f_num, fill=(*GREEN, fa))

        draw.text((cx_ + 20, cy_ + 70 + y_off), title,
                  font=font(FONT_BOLD, 22), fill=(*WHITE, fa))
        draw.text((cx_ + 20, cy_ + 100 + y_off), desc,
                  font=font(FONT_REG, 15), fill=(*GRAY_400, fa))

    return img.convert("RGB")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCENE 6: SOCIAL PROOF
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def scene_social_proof(frame, total):
    t = frame / total
    img = make_atmosphere(W // 2, H // 2, intensity=1.0)

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
# SCENE 7: CTA - Waitlist page replication
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def scene_cta(frame, total):
    t = frame / total
    img = make_atmosphere(W // 2, H // 2, intensity=1.3)
    img = draw_diagonal_stripes(img, alpha=14, offset=frame * 0.6)

    # DNA helix behind CTA
    img = draw_dna_helix(img, frame, cx=W // 2, y_start=-100, y_end=H + 100,
                         amplitude=220, num_points=300, particle_count=7,
                         speed=0.04, alpha_mult=0.4, draw_rungs=True,
                         blur_radius=3, size_mult=1.0)

    img = draw_particles(img, frame, seed=700, count=30, speed=1.1)
    draw = ImageDraw.Draw(img)

    # ── "LAUNCHING SOON" badge ──
    if t > 0.02:
        badge_t = ease_out(min(1, (t - 0.02) / 0.1))
        ba = int(255 * badge_t)
        f_badge = font(FONT_BOLD, 16)
        badge_text = "LAUNCHING SOON"
        bw = tw(draw, badge_text, f_badge) + 36
        bx = W // 2 - bw // 2
        by = H // 2 - 380

        badge_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bd = ImageDraw.Draw(badge_layer)
        rounded_rect(bd, [bx, by, bx + bw, by + 34], 17,
                     fill=(0, 42, 28, int(200 * badge_t)),
                     outline=(0, 200, 130, int(160 * badge_t)), width=1)
        img = Image.alpha_composite(img.convert("RGBA"), badge_layer)
        draw = ImageDraw.Draw(img)
        draw_text_centered(draw, by + 8, badge_text, f_badge, (*GREEN, ba))

    # ── Big "Scan" logo ──
    logo_t = ease_out_elastic(min(1, t / 0.2))
    logo_a = int(255 * min(1, t / 0.08))
    f_logo = font(FONT_BOLD, int(110 * lerp(0.7, 1.0, logo_t)))
    img = glow_text_centered(img, H // 2 - 330, "Scan", f_logo,
                             (*WHITE, logo_a), radius=35, glow_alpha=int(90 * logo_t))
    draw = ImageDraw.Draw(img)

    # ── Tagline: "The smarter way to run your protocol." ──
    if t > 0.1:
        tag_t = ease_out(min(1, (t - 0.1) / 0.1))
        ta = int(255 * tag_t)
        f_tag = font(FONT_BOLD, 36)

        # "The smarter way to" in white
        line1 = "The smarter way to"
        # "run your protocol." in teal
        line2 = "run your protocol."

        img = glow_text_centered(img, H // 2 - 195, line1, f_tag,
                                 (*WHITE, ta), radius=12, glow_alpha=30)
        img = glow_text_centered(img, H // 2 - 148, line2, f_tag,
                                 (*GREEN, ta), radius=15, glow_alpha=50)
        draw = ImageDraw.Draw(img)

    # ── Description text ──
    if t > 0.16:
        desc_t = ease_out(min(1, (t - 0.16) / 0.08))
        da = int(200 * desc_t)
        f_desc = font(FONT_REG, 22)
        draw_text_centered(draw, H // 2 - 90, "Track, optimize, and manage your",
                           f_desc, (*GRAY_400, da))
        draw_text_centered(draw, H // 2 - 62, "peptide research in one place.",
                           f_desc, (*GRAY_400, da))

    # ── Email input field mockup ──
    if t > 0.22:
        inp_t = ease_out(min(1, (t - 0.22) / 0.1))
        inp_a = int(255 * inp_t)

        inp_w = 620
        inp_h = 56
        inp_x = W // 2 - inp_w // 2
        inp_y = H // 2 - 10

        cl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(cl)
        rounded_rect(cd, [inp_x, inp_y, inp_x + inp_w, inp_y + inp_h], 12,
                     fill=(10, 16, 13, int(220 * inp_t)),
                     outline=(*GRAY_700, inp_a), width=1)
        img = Image.alpha_composite(img.convert("RGBA"), cl)
        draw = ImageDraw.Draw(img)
        draw.text((inp_x + 20, inp_y + 16), "Enter your email",
                  font=font(FONT_REG, 20), fill=(*GRAY_500, inp_a))

    # ── Phone input field mockup ──
    if t > 0.25:
        ph_t = ease_out(min(1, (t - 0.25) / 0.1))
        ph_a = int(255 * ph_t)

        ph_w = 620
        ph_h = 56
        ph_x = W // 2 - ph_w // 2
        ph_y = H // 2 + 58

        cl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(cl)
        rounded_rect(cd, [ph_x, ph_y, ph_x + ph_w, ph_y + ph_h], 12,
                     fill=(10, 16, 13, int(220 * ph_t)),
                     outline=(*GRAY_700, ph_a), width=1)
        img = Image.alpha_composite(img.convert("RGBA"), cl)
        draw = ImageDraw.Draw(img)
        draw.text((ph_x + 20, ph_y + 16), "Phone number (optional)",
                  font=font(FONT_REG, 20), fill=(*GRAY_500, ph_a))

    # ── "Join the Waitlist" button - bright teal ──
    if t > 0.3:
        btn_t = ease_out_back(min(1, (t - 0.3) / 0.12))
        ba = int(255 * btn_t)
        btn_w, btn_h = 620, 64
        btn_x = W // 2 - btn_w // 2
        btn_y = H // 2 + 138

        # Button glow
        bg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bgd = ImageDraw.Draw(bg)
        for g in range(25, 0, -2):
            ga = int(10 * (1 - g / 25) * btn_t)
            rounded_rect(bgd, [btn_x - g, btn_y - g, btn_x + btn_w + g, btn_y + btn_h + g],
                         38, fill=(0, 230, 160, ga))
        img = Image.alpha_composite(img.convert("RGBA"), bg)
        draw = ImageDraw.Draw(img)

        rounded_rect(draw, [btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], 32,
                     fill=(*GREEN_BRIGHT, ba))
        f_btn = font(FONT_BOLD, 24)
        btn_text = "Join the Waitlist"
        btw = tw(draw, btn_text, f_btn)
        draw.text((W // 2 - btw // 2, btn_y + 18), btn_text, font=f_btn, fill=(*BLACK, ba))

    # ── "Join 500+ on the waitlist" social proof ──
    if t > 0.38:
        sp_t = ease_out(min(1, (t - 0.38) / 0.08))
        sp_a = int(200 * sp_t)
        f_sp = font(FONT_REG, 20)
        draw_text_centered(draw, H // 2 + 222, "Join 500+ on the waitlist",
                           f_sp, (*GRAY_400, sp_a))

    # ── URL ──
    if t > 0.42:
        ut = ease_out(min(1, (t - 0.42) / 0.08))
        ua = int(255 * ut)
        f_url = font(FONT_MONO, 22)
        url = "waitlist.peptideai.co"
        uw = tw(draw, url, f_url)
        draw.text(((W - uw) // 2, H // 2 + 280), url, font=f_url, fill=(*GREEN, ua))

    # ── Bottom brand ──
    if t > 0.55:
        br = min(1, (t - 0.55) / 0.1)
        bra = int(255 * br)
        draw_text_centered(draw, H - 180, "SCAN PEPTIDE AI",
                           font(FONT_BOLD, 18), (*GREEN, bra))
        draw_text_centered(draw, H - 150, "Coming soon to iOS & Android",
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
    for ts in [1, 3, 5, 8, 10, 14, 17, 20, 22, 25, 28, 32, 35]:
        subprocess.run(["ffmpeg", "-y", "-i", output_path, "-ss", str(ts),
                        "-frames:v", "1",
                        os.path.join(OUTPUT_DIR, f"preview_{ts}s.jpg")],
                       capture_output=True)
    print("All done!")
    return output_path


if __name__ == "__main__":
    generate_video()
