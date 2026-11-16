import glob
import math
import os
import pickle
import random

from PIL import Image
from tqdm import tqdm

from matrix import (
    plus, apply, multiply, multiply_elementwise,
    minus, multiply_const, zeros, T
)

# ---------------------------------------------------------------
# NASTAVENÍ
# ---------------------------------------------------------------
IMG_SIZE = 256                      
INPUT_SIZE = IMG_SIZE * IMG_SIZE
OUTPUT_SIZE = 10
INVERT = False                     # True, pokud máš číslice tmavé na bílém pozadí
                                   # (síť funguje líp, když číslice je světlá na tmavém)

EPOCHS_PER_RUN = 10                # kolik epoch proběhne při jednom spuštění
LEARNING_RATE = 0.01
VALIDATION_SPLIT = 0.1             # 10 % obrázků se nikdy netrénuje a slouží k testu

MODEL_FILE = "model.pkl"
DATA_PATTERN = "training_center/*.png"

# Velikost skryté vrstvy se použije JEN při úplně prvním spuštění.
# Jakmile existuje model.pkl, velikost se zjistí z uložených vah.
FIRST_RUN_HIDDEN = 64


# ---------------------------------------------------------------
# MATEMATIKA
# ---------------------------------------------------------------
def sigmoid(x):
    x = max(-500.0, min(500.0, x))
    return 1 / (1 + math.exp(-x))


def sigmoid_derivative_matrix(A):
    return apply(A, lambda x: x * (1 - x))


def random_matrix(rows, cols):
    # malé náhodné váhy škálované podle počtu vstupů
    limit = 1 / math.sqrt(cols)
    return [[random.uniform(-limit, limit) for _ in range(cols)]
            for _ in range(rows)]


def forward(X, W1, B1, W2, B2):
    Z1 = plus(multiply(W1, X), B1)
    A1 = apply(Z1, sigmoid)

    Z2 = plus(multiply(W2, A1), B2)
    A2 = apply(Z2, sigmoid)

    return Z1, A1, Z2, A2


def backward(X, Y, A1, A2, W1, B1, W2, B2, learning_rate):
    dZ2 = multiply_elementwise(
        minus(A2, Y),
        sigmoid_derivative_matrix(A2)
    )
    dW2 = multiply(dZ2, T(A1))
    dB2 = dZ2

    dA1 = multiply(T(W2), dZ2)
    dZ1 = multiply_elementwise(dA1, sigmoid_derivative_matrix(A1))
    dW1 = multiply(dZ1, T(X))
    dB1 = dZ1

    W1 = minus(W1, multiply_const(dW1, learning_rate))
    B1 = minus(B1, multiply_const(dB1, learning_rate))
    W2 = minus(W2, multiply_const(dW2, learning_rate))
    B2 = minus(B2, multiply_const(dB2, learning_rate))

    return W1, B1, W2, B2


# ---------------------------------------------------------------
# DATA
# ---------------------------------------------------------------
def load_image(path):
    img = Image.open(path).convert("L")
    img = img.resize((IMG_SIZE, IMG_SIZE))

    pixels = [p / 255.0 for p in img.getdata()]
    if INVERT:
        pixels = [1.0 - p for p in pixels]

    return [[p] for p in pixels]


def load_data():
    """Vrátí (trénovací, validační) data. Rozdělení je pokaždé stejné."""
    data = []
    for path in sorted(glob.glob(DATA_PATTERN)):
        filename = path.replace("\\", "/").split("/")[-1]
        label = int(filename.split("_")[0])
        data.append((path, label))

    random.Random(42).shuffle(data)          # pevný seed = stále stejné rozdělení
    split = int(len(data) * (1 - VALIDATION_SPLIT))
    return data[:split], data[split:]


# ---------------------------------------------------------------
# MODEL (ukládání / načítání)
# ---------------------------------------------------------------
def create_model():
    print(f"Vytvářím nový model (skrytá vrstva: {FIRST_RUN_HIDDEN})")
    W1 = random_matrix(FIRST_RUN_HIDDEN, INPUT_SIZE)
    B1 = zeros(FIRST_RUN_HIDDEN, 1)
    W2 = random_matrix(OUTPUT_SIZE, FIRST_RUN_HIDDEN)
    B2 = zeros(OUTPUT_SIZE, 1)
    return {"W1": W1, "B1": B1, "W2": W2, "B2": B2, "epochs": 0}


def load_model():
    if not os.path.exists(MODEL_FILE):
        return None

    with open(MODEL_FILE, "rb") as f:
        model = pickle.load(f)

    if len(model["W1"][0]) != INPUT_SIZE:
        raise SystemExit(
            f"Uložený model má jiný vstup ({len(model['W1'][0])}) než "
            f"IMG_SIZE={IMG_SIZE} ({INPUT_SIZE}). Smaž {MODEL_FILE} "
            f"nebo vrať původní IMG_SIZE."
        )

    print(f"Načten model: skrytá vrstva {len(model['W1'])}, "
          f"dosud natrénováno {model['epochs']} epoch")
    return model


def save_model(model):
    tmp = MODEL_FILE + ".tmp"
    with open(tmp, "wb") as f:
        pickle.dump(model, f)
    os.replace(tmp, MODEL_FILE)              # bezpečné přepsání


# ---------------------------------------------------------------
# TRÉNINK A TESTOVÁNÍ
# ---------------------------------------------------------------
def evaluate(model, data, show_errors=False):
    if not data:
        print("Žádná validační data.")
        return 0.0

    correct = 0
    for path, label in data:
        X = load_image(path)
        _, _, _, A2 = forward(X, model["W1"], model["B1"],
                              model["W2"], model["B2"])
        results = [A2[i][0] for i in range(OUTPUT_SIZE)]
        prediction = results.index(max(results))

        if prediction == label:
            correct += 1
        elif show_errors:
            print(f"CHYBA: {path} | správně: {label} | rozpoznáno: {prediction}")

    accuracy = correct / len(data) * 100
    print(f"Validační úspěšnost: {accuracy:.2f} % ({correct}/{len(data)})")
    return accuracy


def train(model, train_data, val_data, epochs, learning_rate):
    W1, B1, W2, B2 = model["W1"], model["B1"], model["W2"], model["B2"]

    for epoch in range(1, epochs + 1):
        total_epoch = model["epochs"] + 1
        random.shuffle(train_data)
        total_loss = 0.0

        bar = tqdm(train_data,
                   desc=f"Epocha {epoch}/{epochs}",
                   unit="img")

        for n, (path, label) in enumerate(bar, start=1):
            X = load_image(path)
            Y = zeros(OUTPUT_SIZE, 1)
            Y[label][0] = 1

            _, A1, _, A2 = forward(X, W1, B1, W2, B2)

            # loss aktuálního obrázku
            current_loss = 0.0
            for i in range(OUTPUT_SIZE):
                current_loss += 0.5 * (A2[i][0] - Y[i][0]) ** 2

            total_loss += current_loss

            # živý výpis do progress baru
            bar.set_postfix(
                loss=f"{current_loss:.4f}",
                avg=f"{total_loss / n:.4f}"
            )

            W1, B1, W2, B2 = backward(X, Y, A1, A2, W1, B1, W2, B2,
                                      learning_rate)

        avg_loss = total_loss / len(train_data)
        print(f"Epocha {epoch}/{epochs} (celkem {total_epoch}) | "
              f"Loss: {total_loss:.4f} | Průměrný loss: {avg_loss:.6f}")

        model.update(W1=W1, B1=B1, W2=W2, B2=B2, epochs=total_epoch)
        save_model(model)
        evaluate(model, val_data)

    return model


if __name__ == "__main__":
    train_data, val_data = load_data()
    print(f"Trénovacích obrázků: {len(train_data)}, validačních: {len(val_data)}")

    model = load_model() or create_model()

    model = train(model, train_data, val_data,
                  epochs=EPOCHS_PER_RUN,
                  learning_rate=LEARNING_RATE)

    print("\n--- ZÁVĚREČNÝ TEST ---")
    evaluate(model, val_data, show_errors=True)