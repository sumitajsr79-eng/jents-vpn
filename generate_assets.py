"""
Jents VPN — Asset Generator
============================
Creates glowing minimalist shield/orb icons in .ico and .png formats.
"""

import os
import math
from PIL import Image, ImageDraw

def create_jents_icon():
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center = size / 2.0
    radius = 100.0

    # Draw Outer Glowing Halo
    for r in range(int(radius + 18), int(radius), -1):
        alpha = int(60 * (1 - (r - radius) / 18.0))
        draw.ellipse(
            [center - r, center - r, center + r, center + r],
            outline=(6, 182, 212, alpha),
            width=2
        )

    # Main Inner Gradient Disc
    draw.ellipse(
        [center - radius, center - radius, center + radius, center + radius],
        fill=(10, 15, 30, 255),
        outline=(6, 182, 212, 255),
        width=4
    )

    # Stylized Shield / 'J' Emblem
    # Draw Shield outline
    shield_pts = [
        (center - 45, center - 45),
        (center + 45, center - 45),
        (center + 45, center + 10),
        (center, center + 55),
        (center - 45, center + 10),
    ]
    draw.polygon(shield_pts, fill=(14, 116, 144, 180), outline=(56, 189, 248, 255))

    # Inner Lightning / Core Dot
    draw.ellipse(
        [center - 15, center - 15, center + 15, center + 15],
        fill=(34, 197, 94, 255),
        outline=(255, 255, 255, 220),
        width=2
    )

    icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
    os.makedirs(icons_dir, exist_ok=True)

    png_path = os.path.join(icons_dir, "jents_icon.png")
    ico_path = os.path.join(icons_dir, "jents_icon.ico")

    img.save(png_path, format="PNG")
    img.save(ico_path, format="ICO", sizes=[(256, 256), (64, 64), (32, 32), (16, 16)])
    print(f"Icons saved to {png_path} and {ico_path}")

if __name__ == "__main__":
    create_jents_icon()
