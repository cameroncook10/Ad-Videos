#!/usr/bin/env python3
"""
Scan Peptide AI - Creative Ad Reel Generator
Generates a visually stunning 9:16 vertical video ad with:
- Attention-grabbing hook
- Animated particles and glow effects
- App feature showcases
- Dynamic text animations
- Professional dark green aesthetic
"""

import math
import os
import random
import subprocess
import struct
import zlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ─── CONFIG ───────────────────────────────────────────────────────────────────
W, H = 1080, 1920
FPS = 30
OUTPUT_DIR = "/home/user/Ad-Videos/output"
FRAMES_DIR = os.path.join(OUTPUT_DIR, "frames")

# Colors (matching the app's dark green aesthetic)
BLACK = (0, 0, 0)
DARK_BG = (8, 12, 8)
DARK_GREEN = (10, 20, 10)
GREEN = (0, 220, 100)
BRIGHT_GREEN = (0, 255, 120)
NEON_GREEN = (57, 255, 20)
DIM_GREEN = (0, 80, 40)
DARK_ACCENT = (15, 40, 25)
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
MID_GRAY = (140, 140, 140)
DARK_GRAY = (60, 60, 60)

# Font paths
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

# ─── HELPERS ─────────────────────────────────────────────────────────────────

def ease_out_cubic(t):
    return 1 - (1 - t) ** 3

def ease_in_out_cubic(t):
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - (-2 * t + 2) ** 3 / 2

def ease_out_elastic(t):
    if t == 0 or t == 1:
        return t
    return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi) / 3) + 1

def ease_out_back(t):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)

def lerp(a, b, t):
    t = max(0, min(1, t))
    return a + (b - a) * t

def color_lerp(c1, c2, t):
    t = max(0, min(1, t))
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()


class Particle:
    def __init__(self, x=None, y=None, vx=None, vy=None, size=None, alpha=None, life=None):
        self.x = x if x is not None else random.randint(0, W)
        self.y = y if y is not None else random.randint(0, H)
        self.vx = vx if vx is not None else random.uniform(-1, 1)
        self.vy = vy if vy is not None else random.uniform(-2, -0.5)
        self.size = size if size is not None else random.uniform(1, 4)
        self.alpha = alpha if alpha is not None else random.randint(80, 255)
        self.life = life if life is not None else random.uniform(0.5, 3.0)
        self.max_life = self.life

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.life -= dt
        return self.life > 0

    def draw(self, draw):
        if self.life <= 0:
            return
        fade = self.life / self.max_life
        a = int(self.alpha * fade)
        r = max(1, int(self.size * (0.5 + 0.5 * fade)))
        color = (0, int(220 * fade), int(100 * fade), a)
        draw.ellipse([self.x - r, self.y - r, self.x + r, self.y + r], fill=color)
        # Glow
        if r > 2:
            gr = r * 3
            glow_color = (0, int(180 * fade), int(80 * fade), int(a * 0.2))
            draw.ellipse([self.x - gr, self.y - gr, self.x + gr, self.y + gr], fill=glow_color)


class ParticleSystem:
    def __init__(self, max_particles=80):
        self.particles = []
        self.max_particles = max_particles

    def emit(self, count=3, **kwargs):
        for _ in range(count):
            if len(self.particles) < self.max_particles:
                self.particles.append(Particle(**kwargs))

    def update(self, dt=1/30):
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, base_img):
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        for p in self.particles:
            p.draw(d)
        return Image.alpha_composite(base_img.convert("RGBA"), overlay)


def draw_rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    x1, y1, x2, y2 = xy
    r = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)
    # Main rectangles
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


def draw_glow_text(draw, pos, text, font, color, glow_color=None, glow_radius=8):
    """Draw text with a glow effect behind it."""
    if glow_color is None:
        glow_color = (color[0], color[1], color[2], 60)
    x, y = pos
    # Draw glow layers
    for offset in range(glow_radius, 0, -2):
        alpha = int(40 * (1 - offset / glow_radius))
        gc = (*glow_color[:3], alpha) if len(glow_color) == 4 else (*glow_color, alpha)
        for dx in range(-offset, offset + 1, max(1, offset)):
            for dy in range(-offset, offset + 1, max(1, offset)):
                draw.text((x + dx, y + dy), text, font=font, fill=gc)
    draw.text((x, y), text, font=font, fill=color)


def draw_diagonal_stripes(draw, opacity=40):
    """Draw the diagonal green stripes like in the app screenshots."""
    stripe_color = (0, int(220 * opacity / 255), int(100 * opacity / 255), opacity)
    stripe_w = 120
    gap = 300
    for offset in range(-H, W + H, gap):
        points = [
            (offset, 0),
            (offset + stripe_w, 0),
            (offset + stripe_w + H, H),
            (offset + H, H),
        ]
        draw.polygon(points, fill=stripe_color)


def draw_scan_line(draw, y, alpha=30):
    """Draw a horizontal scanning line effect."""
    for i in range(6):
        a = int(alpha * (1 - abs(i - 3) / 3))
        draw.line([(0, y + i), (W, y + i)], fill=(0, 220, 100, a), width=1)


def draw_grid_bg(draw, offset_y=0, alpha=15):
    """Draw subtle grid background."""
    grid_color = (0, 220, 100, alpha)
    spacing = 60
    for x in range(0, W, spacing):
        draw.line([(x, 0), (x, H)], fill=grid_color, width=1)
    for y in range(int(offset_y) % spacing, H, spacing):
        draw.line([(0, y), (W, y)], fill=grid_color, width=1)


def draw_dna_helix(draw, cx, cy, frame, scale=1.0, alpha=100):
    """Draw an animated DNA helix."""
    for i in range(40):
        t = i / 40 * math.pi * 4 + frame * 0.05
        y_pos = cy - 200 * scale + i * 10 * scale
        x1 = cx + math.sin(t) * 60 * scale
        x2 = cx - math.sin(t) * 60 * scale
        depth1 = (math.cos(t) + 1) / 2
        depth2 = 1 - depth1
        r1 = int(4 * scale * (0.5 + 0.5 * depth1))
        r2 = int(4 * scale * (0.5 + 0.5 * depth2))
        a1 = int(alpha * (0.3 + 0.7 * depth1))
        a2 = int(alpha * (0.3 + 0.7 * depth2))
        c1 = (0, int(220 * depth1), int(100 * depth1), a1)
        c2 = (0, int(180 * depth2), int(80 * depth2), a2)
        if depth1 > 0.5:
            draw.ellipse([x1 - r1, y_pos - r1, x1 + r1, y_pos + r1], fill=c1)
        if depth2 > 0.5:
            draw.ellipse([x2 - r2, y_pos - r2, x2 + r2, y_pos + r2], fill=c2)
        # Connecting bars every few points
        if i % 5 == 0:
            bar_alpha = int(alpha * 0.3)
            draw.line([(x1, y_pos), (x2, y_pos)], fill=(0, 150, 70, bar_alpha), width=1)


def draw_phone_mockup(draw, x, y, w, h, screen_content_fn=None):
    """Draw a phone frame outline."""
    r = 40
    # Phone body
    draw_rounded_rect(draw, [x, y, x + w, y + h], r, fill=(20, 25, 20), outline=(60, 70, 60), width=3)
    # Notch
    nw, nh = 160, 28
    nx = x + w // 2 - nw // 2
    draw_rounded_rect(draw, [nx, y, nx + nw, y + nh], 14, fill=(0, 0, 0))
    # Screen area
    sx, sy, sw, sh = x + 8, y + 8, w - 16, h - 16
    return sx, sy, sw, sh


def text_width(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def text_height(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[3] - bbox[1]


# ─── SCENE GENERATORS ────────────────────────────────────────────────────────

def scene_hook(frame, total_frames):
    """Scene 1: Attention-grabbing hook with dramatic reveal."""
    img = Image.new("RGBA", (W, H), DARK_BG + (255,))
    draw = ImageDraw.Draw(img)
    t = frame / total_frames

    # Animated grid background
    draw_grid_bg(draw, offset_y=frame * 2, alpha=10)

    # DNA helices on sides
    draw_dna_helix(draw, 100, H // 2, frame, scale=0.8, alpha=50)
    draw_dna_helix(draw, W - 100, H // 2, frame, scale=0.8, alpha=50)

    # Scanning line sweeping down
    scan_y = int((frame * 8) % (H + 200)) - 100
    draw_scan_line(draw, scan_y, alpha=50)

    # Particles
    particles = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(particles)
    random.seed(42)
    for i in range(30):
        px = random.randint(50, W - 50)
        base_py = random.randint(100, H - 100)
        py = base_py + int(math.sin(frame * 0.1 + i) * 30)
        ps = random.uniform(1, 3)
        pa = int(random.randint(40, 120) * (0.5 + 0.5 * math.sin(frame * 0.15 + i * 0.5)))
        pd.ellipse([px - ps, py - ps, px + ps, py + ps], fill=(0, 220, 100, max(0, pa)))
        # Glow
        gr = ps * 4
        pd.ellipse([px - gr, py - gr, px + gr, py + gr], fill=(0, 200, 90, max(0, pa // 4)))
    img = Image.alpha_composite(img, particles)
    draw = ImageDraw.Draw(img)

    # Hook text animation
    font_hook = get_font(FONT_BOLD, 72)
    font_hook_sm = get_font(FONT_BOLD, 52)

    # Phase 1: "Still tracking peptides..." slides in
    if t < 0.35:
        tt = ease_out_cubic(min(1, t / 0.25))
        x_off = int(lerp(-W, 0, tt))
        alpha_val = int(255 * min(1, t / 0.15))
        line1 = "Still tracking"
        line2 = "peptides on paper?"
        tw1 = text_width(draw, line1, font_hook)
        tw2 = text_width(draw, line2, font_hook)
        y_base = H // 2 - 120
        draw.text(((W - tw1) // 2 + x_off, y_base), line1, font=font_hook, fill=(*WHITE[:3], alpha_val))
        draw.text(((W - tw2) // 2 + x_off, y_base + 90), line2, font=font_hook, fill=(*WHITE[:3], alpha_val))

    # Phase 2: Text shakes and dissolves, red X appears
    elif t < 0.55:
        tt = (t - 0.35) / 0.2
        shake = int(math.sin(tt * 30) * 8 * (1 - tt))
        alpha_val = int(255 * (1 - ease_out_cubic(tt)))
        line1 = "Still tracking"
        line2 = "peptides on paper?"
        tw1 = text_width(draw, line1, font_hook)
        tw2 = text_width(draw, line2, font_hook)
        y_base = H // 2 - 120
        draw.text(((W - tw1) // 2 + shake, y_base), line1, font=font_hook, fill=(*WHITE[:3], alpha_val))
        draw.text(((W - tw2) // 2 + shake, y_base + 90), line2, font=font_hook, fill=(*WHITE[:3], alpha_val))

    # Phase 3: New text appears - "There's a smarter way."
    elif t < 0.75:
        tt = ease_out_back(min(1, (t - 0.55) / 0.15))
        scale_factor = lerp(0.5, 1.0, tt)
        alpha_val = int(255 * min(1, (t - 0.55) / 0.1))
        text1 = "There's a"
        text2 = "smarter way."
        font_big = get_font(FONT_BOLD, int(78 * scale_factor))
        tw1 = text_width(draw, text1, font_big)
        tw2 = text_width(draw, text2, font_big)
        y_base = H // 2 - 100
        draw.text(((W - tw1) // 2, y_base), text1, font=font_big, fill=(*LIGHT_GRAY[:3], alpha_val))
        draw_glow_text(draw, ((W - tw2) // 2, y_base + int(90 * scale_factor)),
                       text2, font_big, (*GREEN[:3], alpha_val))

    # Phase 4: Hold
    else:
        text1 = "There's a"
        text2 = "smarter way."
        font_big = get_font(FONT_BOLD, 78)
        tw1 = text_width(draw, text1, font_big)
        tw2 = text_width(draw, text2, font_big)
        y_base = H // 2 - 100
        pulse = 0.9 + 0.1 * math.sin(frame * 0.2)
        draw.text(((W - tw1) // 2, y_base), text1, font=font_big, fill=WHITE)
        glow_g = tuple(int(c * pulse) for c in GREEN)
        draw_glow_text(draw, ((W - tw2) // 2, y_base + 90), text2, font_big, glow_g)

    return img.convert("RGB")


def scene_intro_logo(frame, total_frames):
    """Scene 2: Brand intro - Scan logo with dramatic entrance."""
    img = Image.new("RGBA", (W, H), DARK_BG + (255,))
    draw = ImageDraw.Draw(img)
    t = frame / total_frames

    # Background diagonal stripes fading in
    stripe_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stripe_overlay)
    stripe_alpha = int(30 * min(1, t / 0.3))
    draw_diagonal_stripes(sd, opacity=stripe_alpha)
    img = Image.alpha_composite(img, stripe_overlay)
    draw = ImageDraw.Draw(img)

    # Animated grid
    draw_grid_bg(draw, offset_y=frame * 1.5, alpha=8)

    # Particles floating up
    random.seed(123)
    particle_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(particle_overlay)
    for i in range(40):
        px = random.randint(30, W - 30)
        py = (random.randint(0, H) - frame * 3 + i * 50) % H
        ps = random.uniform(1.5, 4)
        pa = int(random.randint(30, 100) * (0.5 + 0.5 * math.sin(frame * 0.1 + i)))
        pd.ellipse([px - ps, py - ps, px + ps, py + ps], fill=(0, 220, 100, max(0, pa)))
    img = Image.alpha_composite(img, particle_overlay)
    draw = ImageDraw.Draw(img)

    # Logo / Brand name animation
    if t < 0.4:
        tt = ease_out_elastic(min(1, t / 0.35))
        scale = lerp(3.0, 1.0, tt)
        alpha_val = int(255 * min(1, t / 0.15))
    else:
        scale = 1.0
        alpha_val = 255

    font_logo = get_font(FONT_SERIF_BOLD, int(120 * max(1, scale)))
    logo_text = "Scan"
    tw = text_width(draw, logo_text, font_logo)

    # Glow ring behind logo
    cx, cy = W // 2, H // 2 - 180
    ring_r = int(200 * (1 if t > 0.3 else ease_out_cubic(t / 0.3)))
    pulse = 0.7 + 0.3 * math.sin(frame * 0.15)
    ring_alpha = int(40 * pulse)
    ring_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring_overlay)
    for r_off in range(0, 30, 3):
        a = int(ring_alpha * (1 - r_off / 30))
        rd.ellipse([cx - ring_r - r_off, cy - ring_r - r_off,
                     cx + ring_r + r_off, cy + ring_r + r_off],
                    outline=(0, 220, 100, a), width=2)
    img = Image.alpha_composite(img, ring_overlay)
    draw = ImageDraw.Draw(img)

    draw_glow_text(draw, ((W - tw) // 2, cy - 50), logo_text, font_logo,
                   (*WHITE[:3], alpha_val), glow_radius=12)

    # Tagline appears after logo
    if t > 0.3:
        tt2 = ease_out_cubic(min(1, (t - 0.3) / 0.25))
        alpha2 = int(255 * tt2)
        y_off = int(lerp(30, 0, tt2))

        font_tag = get_font(FONT_REGULAR, 38)
        tag1 = "AI-Powered Peptide Research"
        tw_tag = text_width(draw, tag1, font_tag)
        draw.text(((W - tw_tag) // 2, cy + 100 + y_off), tag1, font=font_tag, fill=(*GREEN[:3], alpha2))

        font_tag2 = get_font(FONT_REGULAR, 32)
        tag2 = "Track  •  Scan  •  Optimize"
        tw_tag2 = text_width(draw, tag2, font_tag2)
        draw.text(((W - tw_tag2) // 2, cy + 160 + y_off), tag2, font=font_tag2, fill=(*LIGHT_GRAY[:3], alpha2))

    # Feature bullets appear with stagger
    if t > 0.5:
        features = [
            ("Body Scanning", "AI-powered health analysis"),
            ("Protocol Tracking", "BPC-157, TB-500, Semax & more"),
            ("Smart Dosing", "Titration schedules built in"),
            ("Research Logging", "Keep every data point organized"),
        ]
        font_feat = get_font(FONT_BOLD, 32)
        font_desc = get_font(FONT_REGULAR, 24)
        y_start = H // 2 + 100

        for i, (title, desc) in enumerate(features):
            feat_t = max(0, min(1, (t - 0.5 - i * 0.08) / 0.12))
            if feat_t <= 0:
                continue
            et = ease_out_cubic(feat_t)
            alpha_f = int(255 * et)
            x_off = int(lerp(100, 0, et))

            fy = y_start + i * 110
            # Green dot indicator
            dot_r = 8
            draw.ellipse([100 + x_off - dot_r, fy + 8 - dot_r, 100 + x_off + dot_r, fy + 8 + dot_r],
                        fill=(*GREEN[:3], alpha_f))
            # Title
            draw.text((125 + x_off, fy - 8), title, font=font_feat, fill=(*WHITE[:3], alpha_f))
            # Description
            draw.text((125 + x_off, fy + 30), desc, font=font_desc, fill=(*MID_GRAY[:3], alpha_f))

    return img.convert("RGB")


def scene_app_home(frame, total_frames):
    """Scene 3: App home screen showcase with phone mockup."""
    img = Image.new("RGBA", (W, H), DARK_BG + (255,))
    draw = ImageDraw.Draw(img)
    t = frame / total_frames

    # Diagonal stripe background
    stripe_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stripe_overlay)
    draw_diagonal_stripes(sd, opacity=25)
    img = Image.alpha_composite(img, stripe_overlay)
    draw = ImageDraw.Draw(img)

    # Phone mockup sliding in from bottom
    phone_w, phone_h = 420, 780
    phone_x = W // 2 - phone_w // 2
    if t < 0.25:
        et = ease_out_cubic(t / 0.25)
        phone_y = int(lerp(H, H // 2 - phone_h // 2 + 80, et))
    else:
        phone_y = H // 2 - phone_h // 2 + 80

    # Phone shadow
    shadow_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shd = ImageDraw.Draw(shadow_overlay)
    for s in range(20, 0, -2):
        sa = int(15 * (1 - s / 20))
        draw_rounded_rect(shd, [phone_x - s, phone_y - s, phone_x + phone_w + s, phone_y + phone_h + s],
                         45, fill=(0, 40, 20, sa))
    img = Image.alpha_composite(img, shadow_overlay)
    draw = ImageDraw.Draw(img)

    # Phone frame
    sx, sy, sw, sh = draw_phone_mockup(draw, phone_x, phone_y, phone_w, phone_h)

    # Screen content
    # Header
    font_greeting = get_font(FONT_REGULAR, 16)
    font_name = get_font(FONT_BOLD, 28)
    draw.text((sx + 20, sy + 35), "GOOD AFTERNOON", font=font_greeting, fill=MID_GRAY)
    draw.text((sx + 20, sy + 55), "User", font=font_name, fill=WHITE)

    # Green card - Body Scan
    card_y = sy + 110
    card_h = 180
    draw_rounded_rect(draw, [sx + 15, card_y, sx + sw - 15, card_y + card_h], 20, fill=(0, 180, 80))

    font_card_title = get_font(FONT_BOLD, 26)
    font_card_desc = get_font(FONT_REGULAR, 16)
    draw.text((sx + 35, card_y + 20), "Run Body Scan", font=font_card_title, fill=WHITE)
    draw.text((sx + 35, card_y + 55), "Start your research access", font=font_card_desc, fill=(220, 255, 230))
    draw.text((sx + 35, card_y + 75), "run you have at the time.", font=font_card_desc, fill=(220, 255, 230))

    # Play button
    play_cx = sx + 65
    play_cy = card_y + 140
    draw.ellipse([play_cx - 22, play_cy - 22, play_cx + 22, play_cy + 22], fill=(0, 100, 50))
    # Triangle
    draw.polygon([(play_cx - 8, play_cy - 12), (play_cx - 8, play_cy + 12), (play_cx + 14, play_cy)],
                fill=WHITE)

    # Stats circles
    stats_y = card_y + card_h + 25
    stats = [("ACTIVE", "3"), ("LOGGED", "3"), ("STREAK", "3")]
    for i, (label, val) in enumerate(stats):
        cx = sx + 80 + i * 130
        cy = stats_y + 35
        r = 32

        # Animated counter
        if t > 0.3:
            count_t = min(1, (t - 0.3 - i * 0.05) / 0.15)
            count_val = int(float(val) * ease_out_cubic(count_t))
        else:
            count_val = 0

        # Circle outline
        draw.arc([cx - r, cy - r, cx + r, cy + r], 0, 360, fill=DARK_GRAY, width=3)
        # Green arc (animated)
        if t > 0.3:
            arc_t = min(1, (t - 0.3 - i * 0.05) / 0.2)
            arc_end = int(360 * ease_out_cubic(arc_t))
            draw.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + arc_end, fill=GREEN, width=3)

        font_label = get_font(FONT_REGULAR, 12)
        font_val = get_font(FONT_BOLD, 28)
        lw = text_width(draw, label, font_label)
        vw = text_width(draw, str(count_val), font_val)
        draw.text((cx - lw // 2, cy - r - 20), label, font=font_label, fill=MID_GRAY)
        draw.text((cx - vw // 2, cy - 14), str(count_val), font=font_val, fill=WHITE)

    # Today's Stack section
    stack_y = stats_y + 100
    font_section = get_font(FONT_BOLD, 20)
    font_see_all = get_font(FONT_REGULAR, 16)
    draw.text((sx + 20, stack_y), "TODAY'S STACK", font=font_section, fill=WHITE)
    draw.text((sx + sw - 80, stack_y + 2), "See All", font=font_see_all, fill=GREEN)

    # Protocol card
    proto_y = stack_y + 35
    draw_rounded_rect(draw, [sx + 15, proto_y, sx + sw - 15, proto_y + 85], 12,
                     fill=(20, 30, 22), outline=(40, 60, 45), width=1)
    font_proto_label = get_font(FONT_REGULAR, 12)
    font_proto_name = get_font(FONT_BOLD, 20)
    font_proto_date = get_font(FONT_REGULAR, 14)
    draw.text((sx + 30, proto_y + 10), "ACTIVE PROTOCOL", font=font_proto_label, fill=MID_GRAY)
    draw.text((sx + 30, proto_y + 28), "Peptide Research", font=font_proto_name, fill=WHITE)
    draw.text((sx + 30, proto_y + 55), "Started March 3, 2025", font=font_proto_date, fill=DIM_GREEN)

    # Bottom nav
    nav_y = sy + sh - 60
    draw.line([(sx, nav_y), (sx + sw, nav_y)], fill=DARK_GRAY, width=1)
    nav_items = ["Home", "Fitness", "+", "Stack", "Track"]
    for i, item in enumerate(nav_items):
        nx = sx + 40 + i * (sw - 80) // 4
        font_nav = get_font(FONT_REGULAR, 14)
        nw = text_width(draw, item, font_nav)
        color = GREEN if item == "Home" else MID_GRAY
        if item == "+":
            draw.ellipse([nx - 18, nav_y + 12, nx + 18, nav_y + 48], fill=DARK_GRAY)
            draw.text((nx - 8, nav_y + 15), "+", font=get_font(FONT_BOLD, 24), fill=WHITE)
        else:
            draw.text((nx - nw // 2, nav_y + 22), item, font=font_nav, fill=color)

    # Title text above phone
    if t > 0.15:
        tt = ease_out_cubic(min(1, (t - 0.15) / 0.2))
        alpha_t = int(255 * tt)
        font_title = get_font(FONT_BOLD, 48)
        title = "Your Command Center"
        tw = text_width(draw, title, font_title)
        draw.text(((W - tw) // 2, phone_y - 100), title, font=font_title, fill=(*WHITE[:3], alpha_t))

        font_sub = get_font(FONT_REGULAR, 28)
        sub = "Everything in one place"
        sw_t = text_width(draw, sub, font_sub)
        draw.text(((W - sw_t) // 2, phone_y - 50), sub, font=font_sub, fill=(*GREEN[:3], alpha_t))

    return img.convert("RGB")


def scene_stack_tracking(frame, total_frames):
    """Scene 4: Stack/protocol tracking details."""
    img = Image.new("RGBA", (W, H), DARK_BG + (255,))
    draw = ImageDraw.Draw(img)
    t = frame / total_frames

    # Grid background
    draw_grid_bg(draw, offset_y=frame * 1, alpha=8)

    # Title
    if t > 0.05:
        tt = ease_out_cubic(min(1, (t - 0.05) / 0.15))
        font_title = get_font(FONT_BOLD, 52)
        title = "Track Every Dose"
        tw = text_width(draw, title, font_title)
        y_off = int(lerp(-50, 0, tt))
        draw.text(((W - tw) // 2, 120 + y_off), title, font=font_title, fill=(*WHITE[:3], int(255 * tt)))

        font_sub = get_font(FONT_REGULAR, 30)
        sub = "Smart protocols, zero guesswork"
        sw_t = text_width(draw, sub, font_sub)
        draw.text(((W - sw_t) // 2, 185 + y_off), sub, font=font_sub, fill=(*GREEN[:3], int(255 * tt)))

    # Peptide cards appearing with stagger
    peptides = [
        {"name": "BPC-157", "type": "PRIMARY COMPOUND", "dose": "250 mcg", "route": "SubQ", "freq": "Daily",
         "status": "ON CYCLE", "week": "Week 1 of 13", "progress": 0.08,
         "titration": "Start at 250 mcg/day SubQ. Titrate to 500 mcg after week 2 if well tolerated."},
        {"name": "TB-500", "type": "SUPPORTING COMPOUND", "dose": "2 mg", "route": "SubQ", "freq": "Twice weekly",
         "status": "ON CYCLE", "week": "Week 1 of 10", "progress": 0.1,
         "titration": "Standard dosing protocol. Maintain consistent schedule for optimal results."},
        {"name": "Semax", "type": "NOOTROPIC", "dose": "300 mcg", "route": "Nasal", "freq": "Daily",
         "status": "ON CYCLE", "week": "Week 3 of 8", "progress": 0.375,
         "titration": "Nasal spray 300mcg AM. Can increase to 600mcg if well tolerated."},
    ]

    card_w = W - 120
    card_x = 60
    card_start_y = 280

    for i, pep in enumerate(peptides):
        enter_t = max(0, min(1, (t - 0.15 - i * 0.12) / 0.18))
        if enter_t <= 0:
            continue
        et = ease_out_cubic(enter_t)
        alpha = int(255 * et)
        x_off = int(lerp(W, 0, et))

        card_h = 280
        cy = card_start_y + i * (card_h + 25)

        # Card background
        card_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card_overlay)
        draw_rounded_rect(cd, [card_x + x_off, cy, card_x + card_w + x_off, cy + card_h], 16,
                         fill=(18, 28, 20, alpha), outline=(40, 70, 45, alpha), width=2)
        img = Image.alpha_composite(img, card_overlay)
        draw = ImageDraw.Draw(img)

        bx = card_x + 25 + x_off

        # Type label
        font_type = get_font(FONT_REGULAR, 14)
        draw.text((bx, cy + 18), pep["type"], font=font_type, fill=(*MID_GRAY[:3], alpha))

        # Name
        font_name = get_font(FONT_BOLD, 36)
        draw.text((bx, cy + 38), pep["name"], font=font_name, fill=(*WHITE[:3], alpha))

        # Status badge
        font_badge = get_font(FONT_BOLD, 14)
        badge_text = pep["status"]
        bw = text_width(draw, badge_text, font_badge) + 20
        badge_x = card_x + card_w - bw - 25 + x_off
        draw_rounded_rect(draw, [badge_x, cy + 18, badge_x + bw, cy + 42], 8,
                         fill=(*DIM_GREEN[:3], alpha), outline=(*GREEN[:3], alpha), width=1)
        draw.text((badge_x + 10, cy + 22), badge_text, font=font_badge, fill=(*GREEN[:3], alpha))

        # Dose info
        font_info_label = get_font(FONT_REGULAR, 13)
        font_info_val = get_font(FONT_BOLD, 18)
        info_y = cy + 90
        infos = [("DOSE", pep["dose"]), ("ROUTE", pep["route"]), ("FREQUENCY", pep["freq"])]
        for j, (label, val) in enumerate(infos):
            ix = bx + j * 200
            draw.text((ix, info_y), label, font=font_info_label, fill=(*MID_GRAY[:3], alpha))
            draw.text((ix, info_y + 18), val, font=font_info_val, fill=(*WHITE[:3], alpha))

        # Progress bar
        prog_y = info_y + 55
        draw.text((bx, prog_y), pep["week"], font=font_info_label, fill=(*MID_GRAY[:3], alpha))
        prog_bar_y = prog_y + 20
        prog_w = card_w - 50
        # Background bar
        draw_rounded_rect(draw, [bx, prog_bar_y, bx + prog_w, prog_bar_y + 8], 4,
                         fill=(*DARK_GRAY[:3], alpha))
        # Fill bar (animated)
        if enter_t > 0.5:
            fill_t = min(1, (enter_t - 0.5) / 0.5)
            fill_w = int(prog_w * pep["progress"] * ease_out_cubic(fill_t))
            if fill_w > 4:
                draw_rounded_rect(draw, [bx, prog_bar_y, bx + fill_w, prog_bar_y + 8], 4,
                                 fill=(*GREEN[:3], alpha))

        # Titration note
        tit_y = prog_bar_y + 22
        draw_rounded_rect(draw, [bx, tit_y, bx + prog_w, tit_y + 55], 8,
                         fill=(15, 35, 20, int(alpha * 0.7)))
        font_tit_label = get_font(FONT_BOLD, 13)
        font_tit = get_font(FONT_REGULAR, 14)
        draw.text((bx + 12, tit_y + 8), "TITRATION", font=font_tit_label, fill=(*GREEN[:3], alpha))
        # Wrap text
        tit_text = pep["titration"]
        if len(tit_text) > 60:
            tit_text = tit_text[:60] + "..."
        draw.text((bx + 12, tit_y + 28), tit_text, font=font_tit, fill=(*LIGHT_GRAY[:3], alpha))

    return img.convert("RGB")


def scene_body_scan(frame, total_frames):
    """Scene 5: AI Body Scan feature showcase."""
    img = Image.new("RGBA", (W, H), DARK_BG + (255,))
    draw = ImageDraw.Draw(img)
    t = frame / total_frames

    # Animated scanning grid
    grid_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid_overlay)
    draw_grid_bg(gd, offset_y=frame * 3, alpha=12)
    img = Image.alpha_composite(img, grid_overlay)
    draw = ImageDraw.Draw(img)

    # Central DNA helix
    helix_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(helix_overlay)
    draw_dna_helix(hd, W // 2, H // 2, frame, scale=1.2, alpha=60)
    img = Image.alpha_composite(img, helix_overlay)
    draw = ImageDraw.Draw(img)

    # Scanning line
    scan_y = int(H * 0.2 + (H * 0.6) * ((frame * 4 / total_frames) % 1.0))
    scan_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    scd = ImageDraw.Draw(scan_overlay)
    for i in range(20):
        a = int(60 * (1 - abs(i - 10) / 10))
        scd.line([(100, scan_y + i - 10), (W - 100, scan_y + i - 10)],
                fill=(0, 220, 100, a), width=1)
    img = Image.alpha_composite(img, scan_overlay)
    draw = ImageDraw.Draw(img)

    # Title
    title_t = ease_out_cubic(min(1, t / 0.2))
    font_title = get_font(FONT_BOLD, 56)
    title = "AI Body Scan"
    tw = text_width(draw, title, font_title)
    draw.text(((W - tw) // 2, 130), title, font=font_title, fill=(*WHITE[:3], int(255 * title_t)))

    font_sub = get_font(FONT_REGULAR, 30)
    sub = "Powered by machine learning"
    sw_t = text_width(draw, sub, font_sub)
    draw.text(((W - sw_t) // 2, 200), sub, font=font_sub, fill=(*GREEN[:3], int(255 * title_t)))

    # Feature boxes around the helix
    features = [
        ("Real-Time Analysis", "Track changes as they happen", 150, H // 2 - 250),
        ("Smart Insights", "AI detects patterns in your data", W - 550, H // 2 - 100),
        ("Progress Tracking", "Visual health score over time", 150, H // 2 + 50),
        ("Research Grade", "Lab-quality data analysis", W - 550, H // 2 + 200),
    ]

    for i, (title_f, desc_f, fx, fy) in enumerate(features):
        feat_t = max(0, min(1, (t - 0.2 - i * 0.1) / 0.15))
        if feat_t <= 0:
            continue
        et = ease_out_cubic(feat_t)
        alpha = int(255 * et)
        scale = lerp(0.8, 1.0, et)

        box_w, box_h = 400, 90
        box_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bd = ImageDraw.Draw(box_overlay)
        draw_rounded_rect(bd, [fx, fy, fx + box_w, fy + box_h], 12,
                         fill=(12, 25, 15, int(200 * et)), outline=(0, 180, 80, alpha), width=2)
        img = Image.alpha_composite(img, box_overlay)
        draw = ImageDraw.Draw(img)

        # Green indicator bar on left
        draw_rounded_rect(draw, [fx + 2, fy + 15, fx + 6, fy + box_h - 15], 3,
                         fill=(*GREEN[:3], alpha))

        font_ft = get_font(FONT_BOLD, 22)
        font_fd = get_font(FONT_REGULAR, 16)
        draw.text((fx + 20, fy + 18), title_f, font=font_ft, fill=(*WHITE[:3], alpha))
        draw.text((fx + 20, fy + 48), desc_f, font=font_fd, fill=(*MID_GRAY[:3], alpha))

    # Bottom stats
    if t > 0.6:
        stat_t = ease_out_cubic(min(1, (t - 0.6) / 0.2))
        alpha_s = int(255 * stat_t)
        stats = [("98%", "Accuracy"), ("< 30s", "Scan Time"), ("24/7", "Monitoring")]
        for i, (val, label) in enumerate(stats):
            sx = 140 + i * 300
            sy = H - 350
            font_sv = get_font(FONT_BOLD, 52)
            font_sl = get_font(FONT_REGULAR, 20)
            vw = text_width(draw, val, font_sv)
            lw = text_width(draw, label, font_sl)
            draw.text((sx - vw // 2, sy), val, font=font_sv, fill=(*GREEN[:3], alpha_s))
            draw.text((sx - lw // 2, sy + 60), label, font=font_sl, fill=(*LIGHT_GRAY[:3], alpha_s))

    return img.convert("RGB")


def scene_features_grid(frame, total_frames):
    """Scene 6: Features overview in a dynamic grid."""
    img = Image.new("RGBA", (W, H), DARK_BG + (255,))
    draw = ImageDraw.Draw(img)
    t = frame / total_frames

    # Background
    stripe_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stripe_overlay)
    draw_diagonal_stripes(sd, opacity=15)
    img = Image.alpha_composite(img, stripe_overlay)
    draw = ImageDraw.Draw(img)

    # Title
    if t > 0.02:
        tt = ease_out_cubic(min(1, t / 0.15))
        font_title = get_font(FONT_BOLD, 50)
        title = "Everything You Need"
        tw = text_width(draw, title, font_title)
        draw.text(((W - tw) // 2, 120), title, font=font_title, fill=(*WHITE[:3], int(255 * tt)))

    # Feature cards in 2-column grid
    features = [
        ("Protocol Builder", "Create custom peptide\nprotocols from scratch", "BUILD"),
        ("Dose Calculator", "Auto-calculate based\non body weight", "CALC"),
        ("Progress Journal", "Log symptoms, mood,\nand recovery daily", "LOG"),
        ("Stack Optimizer", "AI recommends optimal\npeptide combinations", "AI"),
        ("Community", "Connect with other\nresearchers worldwide", "SOCIAL"),
        ("Data Export", "Export your research\ndata anytime", "CSV"),
    ]

    cols = 2
    card_w = (W - 120 - 30) // cols
    card_h = 220
    start_y = 240
    gap = 25

    for i, (title_f, desc_f, icon_text) in enumerate(features):
        col = i % cols
        row = i // cols
        feat_t = max(0, min(1, (t - 0.1 - i * 0.06) / 0.15))
        if feat_t <= 0:
            continue
        et = ease_out_back(feat_t)
        alpha = int(255 * min(1, feat_t / 0.5))

        cx = 60 + col * (card_w + gap)
        cy = start_y + row * (card_h + gap)
        y_off = int(lerp(40, 0, et))

        # Card
        card_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card_overlay)
        draw_rounded_rect(cd, [cx, cy + y_off, cx + card_w, cy + card_h + y_off], 16,
                         fill=(15, 28, 18, alpha), outline=(35, 65, 40, alpha), width=2)
        img = Image.alpha_composite(img, card_overlay)
        draw = ImageDraw.Draw(img)

        # Icon circle
        icon_cx = cx + 45
        icon_cy = cy + 50 + y_off
        draw.ellipse([icon_cx - 25, icon_cy - 25, icon_cx + 25, icon_cy + 25],
                    fill=(*DIM_GREEN[:3], alpha), outline=(*GREEN[:3], alpha), width=2)
        font_icon = get_font(FONT_BOLD, 14)
        iw = text_width(draw, icon_text, font_icon)
        draw.text((icon_cx - iw // 2, icon_cy - 8), icon_text, font=font_icon, fill=(*GREEN[:3], alpha))

        # Title and desc
        font_ct = get_font(FONT_BOLD, 24)
        font_cd = get_font(FONT_REGULAR, 16)
        draw.text((cx + 20, cy + 90 + y_off), title_f, font=font_ct, fill=(*WHITE[:3], alpha))
        for j, line in enumerate(desc_f.split("\n")):
            draw.text((cx + 20, cy + 125 + j * 22 + y_off), line, font=font_cd, fill=(*MID_GRAY[:3], alpha))

    return img.convert("RGB")


def scene_social_proof(frame, total_frames):
    """Scene 7: Social proof / stats."""
    img = Image.new("RGBA", (W, H), DARK_BG + (255,))
    draw = ImageDraw.Draw(img)
    t = frame / total_frames

    # Background particles
    random.seed(999)
    p_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(p_overlay)
    for i in range(50):
        px = random.randint(20, W - 20)
        py = (random.randint(0, H) - frame * 2 + i * 40) % H
        ps = random.uniform(1, 3)
        pa = int(random.randint(20, 80) * (0.5 + 0.5 * math.sin(frame * 0.08 + i * 0.3)))
        pd.ellipse([px - ps, py - ps, px + ps, py + ps], fill=(0, 220, 100, max(0, pa)))
    img = Image.alpha_composite(img, p_overlay)
    draw = ImageDraw.Draw(img)

    # Big stat numbers
    stats = [
        ("10K+", "Active Researchers"),
        ("50+", "Peptides Tracked"),
        ("1M+", "Doses Logged"),
        ("4.9★", "App Store Rating"),
    ]

    center_y = H // 2 - 250
    for i, (val, label) in enumerate(stats):
        stat_t = max(0, min(1, (t - 0.05 - i * 0.1) / 0.2))
        if stat_t <= 0:
            continue
        et = ease_out_cubic(stat_t)
        alpha = int(255 * et)
        y_off = int(lerp(60, 0, et))

        sy = center_y + i * 170

        font_val = get_font(FONT_BOLD, 72)
        font_label = get_font(FONT_REGULAR, 28)

        vw = text_width(draw, val, font_val)
        lw = text_width(draw, label, font_label)

        # Green glow behind number
        glow_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gld = ImageDraw.Draw(glow_overlay)
        for g in range(15, 0, -3):
            ga = int(15 * (1 - g / 15) * et)
            gld.text(((W - vw) // 2 - g, sy + y_off - g), val, font=font_val, fill=(0, 220, 100, ga))
            gld.text(((W - vw) // 2 + g, sy + y_off + g), val, font=font_val, fill=(0, 220, 100, ga))
        img = Image.alpha_composite(img, glow_overlay)
        draw = ImageDraw.Draw(img)

        draw.text(((W - vw) // 2, sy + y_off), val, font=font_val, fill=(*GREEN[:3], alpha))
        draw.text(((W - lw) // 2, sy + 75 + y_off), label, font=font_label, fill=(*LIGHT_GRAY[:3], alpha))

        # Divider line
        if i < len(stats) - 1:
            line_w = 300
            line_alpha = int(40 * et)
            draw.line([(W // 2 - line_w // 2, sy + 130 + y_off), (W // 2 + line_w // 2, sy + 130 + y_off)],
                     fill=(*DIM_GREEN[:3], line_alpha), width=1)

    return img.convert("RGB")


def scene_cta(frame, total_frames):
    """Scene 8: Call to action - download now."""
    img = Image.new("RGBA", (W, H), DARK_BG + (255,))
    draw = ImageDraw.Draw(img)
    t = frame / total_frames

    # Animated diagonal stripes
    stripe_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stripe_overlay)
    stripe_alpha = int(35 * (0.7 + 0.3 * math.sin(frame * 0.1)))
    draw_diagonal_stripes(sd, opacity=stripe_alpha)
    img = Image.alpha_composite(img, stripe_overlay)
    draw = ImageDraw.Draw(img)

    # Particles
    random.seed(777)
    p_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(p_overlay)
    for i in range(60):
        angle = (frame * 0.02 + i * 0.157)
        dist = 200 + i * 8 + math.sin(frame * 0.05 + i) * 50
        px = W // 2 + math.cos(angle) * dist
        py = H // 2 + math.sin(angle) * dist
        ps = random.uniform(1, 4)
        pa = int(random.randint(30, 100) * (0.5 + 0.5 * math.sin(frame * 0.1 + i * 0.2)))
        pd.ellipse([px - ps, py - ps, px + ps, py + ps], fill=(0, 220, 100, max(0, pa)))
    img = Image.alpha_composite(img, p_overlay)
    draw = ImageDraw.Draw(img)

    # Logo
    logo_t = ease_out_elastic(min(1, t / 0.3))
    font_logo = get_font(FONT_SERIF_BOLD, int(130 * logo_t))
    logo = "Scan"
    lw = text_width(draw, logo, font_logo)
    logo_y = H // 2 - 280
    draw_glow_text(draw, ((W - lw) // 2, logo_y), logo, font_logo, WHITE, glow_radius=15)

    # Tagline
    if t > 0.15:
        tag_t = ease_out_cubic(min(1, (t - 0.15) / 0.15))
        alpha_tag = int(255 * tag_t)
        font_tag = get_font(FONT_REGULAR, 32)
        tag = "The Future of Peptide Research"
        tw_tag = text_width(draw, tag, font_tag)
        draw.text(((W - tw_tag) // 2, logo_y + 140), tag, font=font_tag, fill=(*GREEN[:3], alpha_tag))

    # CTA Button
    if t > 0.3:
        btn_t = ease_out_back(min(1, (t - 0.3) / 0.2))
        alpha_btn = int(255 * btn_t)
        btn_w, btn_h = 500, 80
        btn_x = W // 2 - btn_w // 2
        btn_y = H // 2 + 20
        pulse = 1.0 + 0.03 * math.sin(frame * 0.15)

        # Button glow
        glow_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow_overlay)
        for g in range(20, 0, -2):
            ga = int(20 * (1 - g / 20) * btn_t)
            draw_rounded_rect(gd, [btn_x - g, btn_y - g, btn_x + btn_w + g, btn_y + btn_h + g],
                            45, fill=(0, 200, 90, ga))
        img = Image.alpha_composite(img, glow_overlay)
        draw = ImageDraw.Draw(img)

        # Button
        draw_rounded_rect(draw, [btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], 40,
                         fill=(*GREEN[:3], alpha_btn))
        font_btn = get_font(FONT_BOLD, 34)
        btn_text = "Download Now — It's Free"
        btw = text_width(draw, btn_text, font_btn)
        draw.text((W // 2 - btw // 2, btn_y + 20), btn_text, font=font_btn, fill=(*BLACK[:3], alpha_btn))

    # Additional info
    if t > 0.45:
        info_t = ease_out_cubic(min(1, (t - 0.45) / 0.15))
        alpha_info = int(255 * info_t)

        font_info = get_font(FONT_REGULAR, 24)
        infos = [
            "✦ Track 50+ peptides & compounds",
            "✦ AI-powered body scanning",
            "✦ Custom protocol builder",
            "✦ Research-grade data logging",
            "✦ Community of 10K+ researchers",
        ]
        info_y = H // 2 + 150
        for i, info in enumerate(infos):
            i_t = max(0, min(1, (t - 0.45 - i * 0.04) / 0.1))
            if i_t <= 0:
                continue
            iet = ease_out_cubic(i_t)
            ia = int(255 * iet)
            x_off = int(lerp(50, 0, iet))
            draw.text((160 + x_off, info_y + i * 45), info, font=font_info, fill=(*LIGHT_GRAY[:3], ia))

    # Bottom branding
    if t > 0.6:
        brand_t = min(1, (t - 0.6) / 0.15)
        ba = int(255 * brand_t)
        font_brand = get_font(FONT_BOLD, 22)
        font_url = get_font(FONT_REGULAR, 20)
        brand = "SCAN PEPTIDE AI"
        bw = text_width(draw, brand, font_brand)
        draw.text(((W - bw) // 2, H - 220), brand, font=font_brand, fill=(*GREEN[:3], ba))
        url = "Available on iOS & Android"
        uw = text_width(draw, url, font_url)
        draw.text(((W - uw) // 2, H - 185), url, font=font_url, fill=(*MID_GRAY[:3], ba))

    return img.convert("RGB")


# ─── MAIN GENERATION ─────────────────────────────────────────────────────────

def generate_video():
    # Create directories
    os.makedirs(FRAMES_DIR, exist_ok=True)

    # Scene definitions: (generator_fn, duration_seconds)
    scenes = [
        (scene_hook, 4.0),           # Hook - attention grabber
        (scene_intro_logo, 4.5),     # Brand intro with features
        (scene_app_home, 4.0),       # App home screen
        (scene_stack_tracking, 5.0), # Protocol/stack details
        (scene_body_scan, 4.5),      # AI body scan
        (scene_features_grid, 4.0),  # Features grid
        (scene_social_proof, 4.0),   # Social proof stats
        (scene_cta, 5.0),           # Call to action
    ]

    total_duration = sum(d for _, d in scenes)
    total_frames_all = int(total_duration * FPS)
    print(f"Generating {total_frames_all} frames ({total_duration}s at {FPS}fps)")

    frame_idx = 0
    for scene_idx, (scene_fn, duration) in enumerate(scenes):
        scene_frames = int(duration * FPS)
        print(f"  Scene {scene_idx + 1}/{len(scenes)}: {scene_fn.__name__} ({scene_frames} frames)")
        for f in range(scene_frames):
            img = scene_fn(f, scene_frames)
            img = img.convert("RGB")
            img.save(os.path.join(FRAMES_DIR, f"frame_{frame_idx:05d}.png"))
            frame_idx += 1
            if f % 30 == 0:
                print(f"    Frame {f}/{scene_frames}")

    print(f"Total frames generated: {frame_idx}")

    # Cross-fade transitions between scenes using ffmpeg complex filter
    output_path = os.path.join(OUTPUT_DIR, "scan-peptide-ai-reel.mp4")

    # Encode frames to video
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(FRAMES_DIR, "frame_%05d.png"),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-r", str(FPS),
        output_path
    ]
    print(f"Encoding video: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"Video saved to: {output_path}")

    # Clean up frames
    print("Cleaning up frames...")
    for f in os.listdir(FRAMES_DIR):
        os.remove(os.path.join(FRAMES_DIR, f))
    os.rmdir(FRAMES_DIR)
    print("Done!")

    return output_path


if __name__ == "__main__":
    generate_video()
