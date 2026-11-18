import glob
import math
import os
import pickle
import random
import time

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
INVERT = True

TIME_LIMIT_H = 0.5                 # celkový čas běhu v hodinách (rezerva do 7 h)
START_LR = 0.02                   # počáteční learning rate
MIN_LR = 0.0002
PATIENCE = 3                       # po kolika epochách bez zlepšení se LR půlí
DIVERGENCE_FACTOR = 1.5            # loss > 1.5x předchozí => rollback
VALIDATION_SPLIT = 0.1

MODEL_FILE = "model.pkl"
BEST_FILE = "model_best.pkl"
DATA_PATTERN = "training_center/*.png"

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
# Lookup tabulka bajt -> hodnota pixelu (rychlejší než dělení)
if INVERT:
    _LUT = [1.0 - b / 255.0 for b in range(256)]
else:
    _LUT = [b / 255.0 for b in range(256)]

_cache = {}   # path -> bytes (65 kB na obrázek)


def load_image(path):
    raw = _cache.get(path)
    if raw is None:
        img = Image.open(path).convert("L").resize((IMG_SIZE, IMG_SIZE))
        raw = img.tobytes()
        _cache[path] = raw
    return [[_LUT[b]] for b in raw]


def load_data():
    """Vrátí (trénovací, validační) data. Rozdělení je pokaždé stejné."""
    data = []
    for path in sorted(glob.glob(DATA_PATTERN)):
        filename = path.replace("\\", "/").split("/")[-1]
        label = int(filename.split("_")[0])
        data.append((path, label))

    random.Random(42).shuffle(data)
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


def load_model(verbose=True):
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

    if verbose:
        print(f"Načten model: skrytá vrstva {len(model['W1'])}, "
              f"dosud natrénováno {model['epochs']} epoch")
    return model


def save_model(model, path=MODEL_FILE):
    tmp = path + ".tmp"

    try:
        with open(tmp, "wb") as f:
            pickle.dump(model, f)
            f.flush()
            os.fsync(f.fileno())

        os.replace(tmp, path)

        print(f"Model úspěšně uložen: {path}")

    except PermissionError as e:
        print(f"\nCHYBA: Nelze uložit model '{path}'.")
        print("Soubor pravděpodobně používá jiný program.")
        print("Zavři ostatní instance programu a zkus to znovu.")
        print(f"Podrobnosti: {e}")

        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass

        raise


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


def train(model, train_data, val_data):

    lr = model.get("lr", START_LR)
    best_acc = model.get("best_acc", 0.0)
    best_loss = model.get("best_loss", float("inf"))
    prev_loss = None
    stale = 0

    W1, B1, W2, B2 = model["W1"], model["B1"], model["W2"], model["B2"]

    print("\nTrénink běží až do ručního zastavení (Ctrl+C).")

    try:
        while True:

            total_epoch = model["epochs"] + 1
            random.shuffle(train_data)
            total_loss = 0.0

            bar = tqdm(
                train_data,
                desc=f"Epocha {total_epoch} (lr {lr:.5f})",
                unit="img"
            )

            for n, (path, label) in enumerate(bar, start=1):

                X = load_image(path)

                Y = zeros(OUTPUT_SIZE, 1)
                Y[label][0] = 1

                _, A1, _, A2 = forward(X, W1, B1, W2, B2)

                current_loss = 0.0

                for i in range(OUTPUT_SIZE):
                    current_loss += 0.5 * (A2[i][0] - Y[i][0]) ** 2

                total_loss += current_loss

                bar.set_postfix(
                    loss=f"{current_loss:.4f}",
                    avg=f"{total_loss / n:.4f}"
                )

                W1, B1, W2, B2 = backward(
                    X, Y, A1, A2,
                    W1, B1, W2, B2,
                    lr
                )

            # ---------------------------------------------------
            # KONEC EPOCHY
            # ---------------------------------------------------

            avg_loss = total_loss / len(train_data)

            print(
                f"\nEpocha {total_epoch} | lr {lr:.5f} | "
                f"Loss: {total_loss:.4f} | "
                f"Průměrný loss: {avg_loss:.6f}"
            )

            # ---------------------------------------------------
            # OCHRANA PROTI DIVERGENCI
            # ---------------------------------------------------

            if prev_loss is not None and avg_loss > prev_loss * DIVERGENCE_FACTOR:

                lr = max(MIN_LR, lr * 0.5)

                print(
                    f"!! Loss vyskočil, rollback "
                    f"a nové lr = {lr:.5f}"
                )

                good = load_model(verbose=False)

                if good is not None:
                    W1 = good["W1"]
                    B1 = good["B1"]
                    W2 = good["W2"]
                    B2 = good["B2"]

                model.update(
                    W1=W1,
                    B1=B1,
                    W2=W2,
                    B2=B2,
                    lr=lr
                )

                save_model(model)

                stale = 0
                continue

            prev_loss = avg_loss

            # ---------------------------------------------------
            # SNIŽOVÁNÍ LEARNING RATE PŘI STAGNACI
            # ---------------------------------------------------

            if avg_loss < best_loss * 0.998:

                best_loss = avg_loss
                stale = 0

            else:

                stale += 1

                if stale >= PATIENCE and lr > MIN_LR:

                    lr = max(MIN_LR, lr * 0.5)
                    stale = 0

                    print(
                        f"Stagnace, snižuji lr na {lr:.5f}"
                    )

            # ---------------------------------------------------
            # ULOŽENÍ MODELU PO CELÉ EPOCHĚ
            # ---------------------------------------------------

            model.update(
                W1=W1,
                B1=B1,
                W2=W2,
                B2=B2,
                epochs=total_epoch,
                lr=lr,
                best_acc=best_acc,
                best_loss=best_loss
            )

            save_model(model)

            print("Model uložen.")

            # ---------------------------------------------------
            # VALIDACE
            # ---------------------------------------------------

            acc = evaluate(model, val_data)

            if acc >= best_acc:

                best_acc = acc
                model["best_acc"] = best_acc

                save_model(model, BEST_FILE)

                print(
                    f"** Nový nejlepší model "
                    f"({best_acc:.2f} %) uložen do {BEST_FILE}"
                )

    except KeyboardInterrupt:

        print("\n\nTrénink ručně přerušen.")

        model.update(
            W1=W1,
            B1=B1,
            W2=W2,
            B2=B2,
            lr=lr,
            best_acc=best_acc,
            best_loss=best_loss
        )

        save_model(model)

        print("Aktuální model byl uložen do model.pkl.")

    return model


if __name__ == "__main__":
    train_data, val_data = load_data()
    print(f"Trénovacích obrázků: {len(train_data)}, validačních: {len(val_data)}")

    model = load_model()
    if model is None:
        model = create_model()
        save_model(model)

    model = train(model, train_data, val_data)

    print("\n--- ZÁVĚREČNÝ TEST (poslední model) ---")
    evaluate(model, val_data, show_errors=True)

    if os.path.exists(BEST_FILE):
        with open(BEST_FILE, "rb") as f:
            best = pickle.load(f)

        print("\n--- ZÁVĚREČNÝ TEST (nejlepší model) ---")
        evaluate(best, val_data, show_errors=True)