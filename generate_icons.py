"""
Generate all required Tauri icon sizes from the original icon.
Run: .venv\Scripts\python generate_icons.py <source_image_path>
"""
import sys
import os
from PIL import Image

def generate_icons(source_path, tauri_icons_dir):
    """Generate all required Tauri icon sizes."""
    img = Image.open(source_path).convert("RGBA")
    print(f"Source: {source_path} ({img.size[0]}x{img.size[1]})")

    # Tauri required icons
    tauri_sizes = {
        "32x32.png": 32,
        "128x128.png": 128,
        "128x128@2x.png": 256,
        "icon.png": 512,
        # Windows Store logos
        "Square30x30Logo.png": 30,
        "Square44x44Logo.png": 44,
        "Square71x71Logo.png": 71,
        "Square89x89Logo.png": 89,
        "Square107x107Logo.png": 107,
        "Square142x142Logo.png": 142,
        "Square150x150Logo.png": 150,
        "Square284x284Logo.png": 284,
        "Square310x310Logo.png": 310,
        "StoreLogo.png": 50,
    }

    os.makedirs(tauri_icons_dir, exist_ok=True)

    for filename, size in tauri_sizes.items():
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        path = os.path.join(tauri_icons_dir, filename)
        resized.save(path, "PNG")
        print(f"  Created: {filename} ({size}x{size})")

    # Generate .ico (Windows) - multi-resolution
    ico_sizes = [16, 24, 32, 48, 64, 128, 256]
    ico_images = []
    for s in ico_sizes:
        ico_images.append(img.resize((s, s), Image.Resampling.LANCZOS))
    ico_path = os.path.join(tauri_icons_dir, "icon.ico")
    ico_images[-1].save(ico_path, format="ICO",
                         sizes=[(s, s) for s in ico_sizes],
                         append_images=ico_images[:-1])
    print(f"  Created: icon.ico (multi-res)")

    # Generate .icns (macOS) - use 512x512 PNG as base
    # PIL can save .icns on mac but on Windows we just save a 512x512 PNG and rename
    icns_path = os.path.join(tauri_icons_dir, "icon.icns")
    try:
        icon_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
        icon_512.save(icns_path, format="ICNS")
        print(f"  Created: icon.icns")
    except Exception as e:
        # If ICNS format not supported, copy the 512 PNG
        print(f"  Note: ICNS format not supported on Windows ({e})")
        icon_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
        icon_512.save(icns_path.replace('.icns', '_fallback.png'), "PNG")

    print("\nDone!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_icons.py <source_image>")
        sys.exit(1)

    source = sys.argv[1]
    tauri_dir = os.path.join(os.path.dirname(__file__), "tauri-app", "src-tauri", "icons")
    generate_icons(source, tauri_dir)
