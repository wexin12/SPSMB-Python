
from pathlib import Path
from PIL import Image

# -------------------------------------------------
# NASTAVENÍ
# -------------------------------------------------

SOURCE_DIR = Path("training_center")
OUTPUT_DIR = Path("training_center_rotated")

ROTATION_ANGLE = 10

EXTENSIONS = (".png", ".jpg", ".jpeg")

IMAGE_SIZE = 256

# -------------------------------------------------
# ZPRACOVÁNÍ OBRÁZKU
# -------------------------------------------------

def process_image(path):

    img = Image.open(path).convert("L")

    img = img.resize((IMAGE_SIZE, IMAGE_SIZE))

    rotated = img.rotate(
        ROTATION_ANGLE,
        resample=Image.Resampling.BILINEAR,
        expand=False,
        fillcolor=255
    )

    output_name = path.stem + ".png"

    rotated.save(OUTPUT_DIR / output_name)


# -------------------------------------------------
# HLAVNÍ PROGRAM
# -------------------------------------------------

def main():

    if not SOURCE_DIR.exists():
        print(f"Zdrojová složka neexistuje: {SOURCE_DIR}")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    images = sorted(
        path for path in SOURCE_DIR.rglob("*")
        if path.is_file()
        and path.suffix.lower() in EXTENSIONS
    )

    print(f"Nalezeno obrázků: {len(images)}")
    print(f"Rotace: +{ROTATION_ANGLE} stupně")

    for i, path in enumerate(images, start=1):

        process_image(path)

        print(f"[{i}/{len(images)}] {path.name}")

    print("\nHotovo!")
    print(f"Výsledky jsou ve složce: {OUTPUT_DIR}")
    print(f"Celkem otočeno: {len(images)} obrázků")


if __name__ == "__main__":
    main()