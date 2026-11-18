import math
import os
import pickle
import sys
from pathlib import Path

from PIL import Image

from matrix import plus, apply, multiply

# ---------------------------------------------------------------
# NASTAVENÍ
# ---------------------------------------------------------------
IMG_SIZE = 256
INPUT_SIZE = IMG_SIZE * IMG_SIZE
OUTPUT_SIZE = 10
INVERT = True

DATA_DIR = "cislice"

EXTENSIONS = (".png", ".jpg", ".jpeg")
MODEL_FILES = ["model_best.pkl", "model.pkl"]


# ---------------------------------------------------------------
# MATEMATIKA
# ---------------------------------------------------------------
def sigmoid(x):
    x = max(-500.0, min(500.0, x))
    return 1 / (1 + math.exp(-x))


def forward(X, W1, B1, W2, B2):
    A1 = apply(plus(multiply(W1, X), B1), sigmoid)
    A2 = apply(plus(multiply(W2, A1), B2), sigmoid)
    return A2


# ---------------------------------------------------------------
# DATA
# ---------------------------------------------------------------
if INVERT:
    _LUT = [1.0 - b / 255.0 for b in range(256)]
else:
    _LUT = [b / 255.0 for b in range(256)]


def load_image(path):
    img = Image.open(path).convert("L").resize((IMG_SIZE, IMG_SIZE))
    return [[_LUT[b]] for b in img.tobytes()]


def find_images(folder):
    folder = Path(folder)

    if not folder.exists():
        raise SystemExit(f"Složka '{folder}' neexistuje.")

    if not folder.is_dir():
        raise SystemExit(f"'{folder}' není složka.")

    # Projde všechny podsložky včetně jejich podsložek
    images = [
        path
        for path in folder.rglob("*")
        if path.is_file() and path.suffix.lower() in EXTENSIONS
    ]

    images = sorted(images)

    if not images:
        raise SystemExit(
            f"Ve složce '{folder}' ani jejích podsložkách "
            f"nejsou žádné obrázky."
        )

    return images


def get_label(path):
    """
    Zkusí zjistit správnou číslici:
    1. z názvu souboru, např. 7_obrazek.png
    2. z názvu složky, např. cislice/7/obrazek.png
    """

    filename = Path(path).stem

    # Číslice z názvu souboru (např. 7_obrazek.png)
    prefix = filename.split("_")[0]

    if prefix.isdigit() and 0 <= int(prefix) < OUTPUT_SIZE:
        return int(prefix)

    # Číslice z názvu rodičovské složky (např. složka "7")
    parent = Path(path).parent.name

    if parent.isdigit() and 0 <= int(parent) < OUTPUT_SIZE:
        return int(parent)

    return None


# ---------------------------------------------------------------
# MODEL
# ---------------------------------------------------------------
def load_model():
    for model_file in MODEL_FILES:

        if os.path.exists(model_file):

            with open(model_file, "rb") as f:
                model = pickle.load(f)

            if len(model["W1"][0]) != INPUT_SIZE:
                raise SystemExit(
                    f"Model '{model_file}' má jiný vstup "
                    f"({len(model['W1'][0])}) než IMG_SIZE={IMG_SIZE} "
                    f"({INPUT_SIZE})."
                )

            print(
                f"Načten model: {model_file} "
                f"(skrytá vrstva {len(model['W1'])}, "
                f"natrénováno {model.get('epochs', '?')} epoch)"
            )

            return model

    raise SystemExit(
        "Nenalezen žádný model ("
        + ", ".join(MODEL_FILES)
        + ")."
    )


# ---------------------------------------------------------------
# ROZPOZNÁVÁNÍ
# ---------------------------------------------------------------
def predict(model, path):
    """Vrátí rozpoznanou číslici a jistotu."""

    X = load_image(path)

    A2 = forward(
        X,
        model["W1"],
        model["B1"],
        model["W2"],
        model["B2"]
    )

    results = [A2[i][0] for i in range(OUTPUT_SIZE)]

    digit = results.index(max(results))
    confidence = results[digit]

    return digit, confidence


# ---------------------------------------------------------------
# HLAVNÍ PROGRAM
# ---------------------------------------------------------------
if __name__ == "__main__":

    # Možnost zadat složku přes příkazovou řádku
    # Pokud není zadána, použije se složka cislice
    folder = sys.argv[1] if len(sys.argv) > 1 else DATA_DIR

    model = load_model()

    images = find_images(folder)

    print(f"\nNalezeno obrázků: {len(images)}")
    print(f"Prohledávaná složka: {folder}")
    print("-" * 60)

    labeled = 0
    correct = 0

    for path in images:

        digit, confidence = predict(model, path)

        name = path.name
        label = get_label(path)

        if label is None:

            print(
                f"{path}: {digit} "
                f"(jistota {confidence:.2f})"
            )

        else:

            labeled += 1

            if digit == label:

                correct += 1

                print(
                    f"{path}: {digit} "
                    f"(jistota {confidence:.2f}) OK"
                )

            else:

                print(
                    f"{path}: {digit} "
                    f"(jistota {confidence:.2f}) "
                    f"CHYBA, správně: {label}"
                )

    # -----------------------------------------------------------
    # STATISTIKY
    # -----------------------------------------------------------
    print("\n" + "=" * 60)
    print("VÝSLEDKY")

    print(f"Celkem rozpoznaných obrázků: {len(images)}")

    if labeled:

        print(f"Označených obrázků: {labeled}")
        print(f"Správně: {correct}")
        print(f"Špatně: {labeled - correct}")

        accuracy = correct / labeled * 100

        print(f"Úspěšnost: {accuracy:.2f} %")

    else:

        print("Obrázky nemají označení správné číslice.")
        print("Úspěšnost proto nelze vypočítat.")

    print("=" * 60)