"""
Generate the app icon as .ico file for the executable.
Run this once before building with PyInstaller.
"""
from PIL import Image, ImageDraw, ImageFont
import os


def create_icon():
    """Create a multi-resolution .ico file."""
    sizes = [16, 32, 48, 64, 128, 256]
    images = []

    for size in sizes:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Blue circle
        bg_color = (137, 180, 250, 255)  # #89b4fa
        text_color = (30, 30, 46, 255)   # #1e1e2e

        margin = max(1, size // 16)
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=bg_color,
        )

        # "T" letter
        font_size = int(size * 0.55)
        try:
            font = ImageFont.truetype("segoeui.ttf", font_size)
        except Exception:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except Exception:
                font = ImageFont.load_default()

        text = "T"
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = (size - tw) // 2
        ty = (size - th) // 2 - max(1, size // 32)

        draw.text((tx, ty), text, fill=text_color, font=font)
        images.append(img)

    # Save as .ico
    icon_path = os.path.join(os.path.dirname(__file__), "app.ico")
    images[-1].save(icon_path, format="ICO", sizes=[(s, s) for s in sizes],
                     append_images=images[:-1])
    print(f"Icon saved: {icon_path}")
    return icon_path


if __name__ == "__main__":
    create_icon()
