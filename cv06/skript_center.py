import cv2
import numpy as np
import os

# Cesta k hlavní složce
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Vstupní a výstupní složky
FOLDERS = {
    "training": "training_center",
    "validation": "validation_center"
}

# Funkce pro centrování obrázků
def center_images(input_folder, output_folder):

    INPUT_DIR = os.path.join(BASE_DIR, input_folder)
    OUTPUT_DIR = os.path.join(BASE_DIR, output_folder)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for filename in os.listdir(INPUT_DIR):

        if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        path = os.path.join(INPUT_DIR, filename)
        img = cv2.imread(path)

        if img is None:
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detekce objektu (čísla) oproti pozadí
        _, thresh = cv2.threshold(
            gray, 0, 255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )

        points = cv2.findNonZero(thresh)

        if points is None:
            continue

        x, y, w, h = cv2.boundingRect(points)

        # Výpočet středu čísla
        center_x = x + w / 2
        center_y = y + h / 2

        # Cílový střed obrázku
        target_x = 128
        target_y = 128

        shift_x = round(target_x - center_x)
        shift_y = round(target_y - center_y)

        matrix = np.float32([
            [1, 0, shift_x],
            [0, 1, shift_y]
        ])

        result = cv2.warpAffine(
            img,
            matrix,
            (256, 256),
            borderValue=(255, 255, 255)
        )

        cv2.imwrite(
            os.path.join(OUTPUT_DIR, filename),
            result
        )

    print(f"Hotovo! Složka {input_folder} byla vycentrována.")


# Samostatné zpracování obou složek
for input_folder, output_folder in FOLDERS.items():
    center_images(input_folder, output_folder)

print("Všechny obrázky byly úspěšně vycentrovány!")