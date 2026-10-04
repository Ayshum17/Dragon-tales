"""Generate all game assets (images, sounds, icon) using Pillow and wave module."""

import os
import math
import wave
import struct
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)


def save_png(img, name):
    path = os.path.join(ASSETS_DIR, name)
    img.save(path, "PNG")
    print(f"  Created {name}")


def save_ico(img, name):
    path = os.path.join(ASSETS_DIR, name)
    img.save(path, format="ICO", sizes=[(32, 32), (64, 64), (128, 128), (256, 256)])
    print(f"  Created {name}")


def make_dragon_frame(frame):
    size = 80
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2

    body_color = (40, 180, 60)
    belly_color = (180, 220, 100)
    eye_color = (255, 255, 0)
    wing_color = (30, 140, 50)

    draw.ellipse([cx - 22, cy - 18, cx + 22, cy + 18], fill=body_color, outline=(20, 100, 30), width=2)
    draw.ellipse([cx - 16, cy - 8, cx + 16, cy + 16], fill=belly_color)

    head_x = cx + 18
    head_y = cy - 10
    draw.ellipse([head_x - 14, head_y - 14, head_x + 14, head_y + 14], fill=body_color, outline=(20, 100, 30), width=2)

    draw.ellipse([head_x + 2, head_y - 6, head_x + 10, head_y + 2], fill=eye_color)
    draw.ellipse([head_x + 4, head_y - 5, head_x + 7, head_y - 2], fill=(0, 0, 0))

    if frame == 0:
        draw.polygon([(cx - 5, cy - 16), (cx + 5, cy - 16), (cx, cy - 28)], fill=(255, 240, 200))
    else:
        draw.polygon([(cx - 8, cy - 14), (cx + 2, cy - 14), (cx - 3, cy - 26)], fill=(255, 240, 200))

    if frame == 0:
        wing_pts = [(cx - 18, cy - 5), (cx - 35, cy - 25), (cx - 25, cy + 5)]
    else:
        wing_pts = [(cx - 18, cy - 5), (cx - 38, cy - 10), (cx - 25, cy + 8)]
    draw.polygon(wing_pts, fill=wing_color, outline=(20, 100, 30))

    if frame == 0:
        wing_pts2 = [(cx - 15, cy + 2), (cx - 32, cy + 18), (cx - 20, cy + 10)]
    else:
        wing_pts2 = [(cx - 15, cy + 2), (cx - 30, cy + 8), (cx - 20, cy + 12)]
    draw.polygon(wing_pts2, fill=wing_color, outline=(20, 100, 30))

    tail_pts = [(cx - 22, cy), (cx - 38, cy - 8), (cx - 34, cy), (cx - 38, cy + 8)]
    draw.polygon(tail_pts, fill=body_color, outline=(20, 100, 30))

    if frame == 0:
        flame_pts = [(head_x + 12, head_y - 2), (head_x + 24, head_y - 6), (head_x + 20, head_y), (head_x + 26, head_y + 4), (head_x + 14, head_y + 2)]
    else:
        flame_pts = [(head_x + 12, head_y - 2), (head_x + 28, head_y - 4), (head_x + 22, head_y), (head_x + 30, head_y + 6), (head_x + 14, head_y + 2)]
    draw.polygon(flame_pts, fill=(255, 100, 0))
    flame_pts2 = [(head_x + 12, head_y), (head_x + 20, head_y - 2), (head_x + 18, head_y + 2)]
    draw.polygon(flame_pts2, fill=(255, 200, 0))

    return img


def make_obstacle_top():
    w, h = 80, 200
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    rock_color = (120, 100, 90)
    rock_dark = (80, 65, 55)
    rock_light = (160, 140, 125)

    draw.rectangle([10, 0, w - 10, h - 30], fill=rock_color, outline=rock_dark, width=3)

    for i in range(5):
        x = 15 + i * 13
        draw.polygon([(x, h - 30), (x + 6, h - 10), (x + 13, h - 30)], fill=rock_dark, outline=(60, 50, 40))

    for i in range(3):
        y = 20 + i * 50
        draw.ellipse([15, y, 30, y + 15], fill=rock_light)
        draw.ellipse([w - 30, y + 25, w - 15, y + 40], fill=rock_light)

    return img


def make_obstacle_bottom():
    w, h = 80, 200
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    rock_color = (120, 100, 90)
    rock_dark = (80, 65, 55)
    rock_light = (160, 140, 125)

    draw.rectangle([10, 30, w - 10, h], fill=rock_color, outline=rock_dark, width=3)

    for i in range(5):
        x = 15 + i * 13
        draw.polygon([(x, 30), (x + 6, 10), (x + 13, 30)], fill=rock_dark, outline=(60, 50, 40))

    for i in range(3):
        y = 40 + i * 50
        draw.ellipse([15, y, 30, y + 15], fill=rock_light)
        draw.ellipse([w - 30, y + 25, w - 15, y + 40], fill=rock_light)

    return img


def make_flame_obstacle():
    size = 60
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2

    draw.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(255, 80, 0), outline=(200, 50, 0), width=2)
    draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=(255, 160, 0))
    draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(255, 230, 100))

    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        x1 = cx + 18 * math.cos(rad)
        y1 = cy + 18 * math.sin(rad)
        x2 = cx + 28 * math.cos(rad)
        y2 = cy + 28 * math.sin(rad)
        draw.ellipse([x2 - 4, y2 - 4, x2 + 4, y2 + 4], fill=(255, 200, 0))

    return img


def make_background():
    w, h = 480, 720
    img = Image.new("RGB", (w, h), (20, 30, 80))
    draw = ImageDraw.Draw(img)

    for y in range(0, h, 4):
        ratio = y / h
        r = int(20 + ratio * 80)
        g = int(30 + ratio * 100)
        b = int(80 + ratio * 120)
        draw.rectangle([0, y, w, y + 4], fill=(r, g, b))

    cloud_positions = [(80, 60), (350, 120), (150, 200), (380, 280),
                       (100, 350), (300, 420), (200, 500), (50, 580)]
    for cx, cy in cloud_positions:
        draw.ellipse([cx, cy, cx + 70, cy + 25], fill=(200, 200, 220))
        draw.ellipse([cx + 15, cy - 10, cx + 55, cy + 15], fill=(220, 220, 240))

    for i in range(5):
        x = 30 + i * 100
        peak_h = 80 + i * 20
        draw.polygon([(x, h), (x + 40, h - peak_h), (x + 80, h)], fill=(30, 25, 50))

    return img


def make_icon():
    size = 256
    img = Image.new("RGBA", (size, size), (20, 30, 80, 255))
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2

    draw.ellipse([cx - 60, cy - 50, cx + 60, cy + 50], fill=(40, 180, 60), outline=(20, 100, 30), width=4)

    hx, hy = cx + 50, cy - 30
    draw.ellipse([hx - 40, hy - 40, hx + 40, hy + 40], fill=(40, 180, 60), outline=(20, 100, 30), width=4)
    draw.ellipse([hx + 8, hy - 18, hx + 28, hy + 2], fill=(255, 255, 0))
    draw.ellipse([hx + 14, hy - 14, hx + 22, hy - 6], fill=(0, 0, 0))

    draw.polygon([(cx - 50, cy - 15), (cx - 110, cy - 70), (cx - 70, cy + 15)], fill=(30, 140, 50))
    draw.polygon([(cx - 60, cy + 20), (cx - 120, cy + 50), (cx - 70, cy + 30)], fill=(30, 140, 50))

    flame_pts = [(hx + 35, hy - 5), (hx + 75, hy - 20), (hx + 60, hy + 5), (hx + 80, hy + 15), (hx + 40, hy + 8)]
    draw.polygon(flame_pts, fill=(255, 100, 0))
    draw.polygon([(hx + 35, hy), (hx + 55, hy - 8), (hx + 50, hy + 5)], fill=(255, 220, 0))

    return img


def make_sound(name, freq, duration, volume=0.3, wave_type="sine"):
    path = os.path.join(ASSETS_DIR, name)
    sample_rate = 22050
    num_samples = int(duration * sample_rate)

    with wave.open(path, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)

        for i in range(num_samples):
            t = float(i) / sample_rate
            if wave_type == "sine":
                value = math.sin(2.0 * math.pi * freq * t)
            elif wave_type == "sweep":
                sweep_freq = freq + (freq * 2 * t / duration)
                value = math.sin(2.0 * math.pi * sweep_freq * t)
            elif wave_type == "noise":
                value = math.sin(2.0 * math.pi * freq * t) * 0.5 + math.sin(2.0 * math.pi * freq * 1.5 * t) * 0.3
            else:
                value = math.sin(2.0 * math.pi * freq * t)

            envelope = 1.0
            attack = 0.01
            release = 0.1
            if t < attack:
                envelope = t / attack
            elif t > duration - release:
                envelope = max(0, (duration - t) / release)

            sample = int(value * volume * envelope * 32767)
            wav.writeframesraw(struct.pack("<h", sample))

    print(f"  Created {name}")


def main():
    print("Generating Dragon Climb assets...")

    print("\nImages:")
    save_png(make_dragon_frame(0), "dragon_1.png")
    save_png(make_dragon_frame(1), "dragon_2.png")

    combined = Image.new("RGBA", (160, 80), (0, 0, 0, 0))
    combined.paste(make_dragon_frame(0), (0, 0))
    combined.paste(make_dragon_frame(1), (80, 0))
    save_png(combined, "dragon.png")

    save_png(make_obstacle_top(), "obstacle_top.png")
    save_png(make_obstacle_bottom(), "obstacle_bottom.png")
    save_png(make_flame_obstacle(), "obstacle.png")
    save_png(make_background(), "background.png")

    print("\nIcon:")
    icon_img = make_icon()
    save_png(icon_img, "dragon_climb_icon.png")
    save_ico(icon_img, "dragon_climb.ico")

    print("\nSounds:")
    make_sound("sound_jump.wav", 440, 0.15, volume=0.25, wave_type="sweep")
    make_sound("sound_crash.wav", 150, 0.4, volume=0.35, wave_type="noise")
    make_sound("sound_score.wav", 880, 0.1, volume=0.2, wave_type="sine")

    print("\nAll assets generated successfully!")


if __name__ == "__main__":
    main()