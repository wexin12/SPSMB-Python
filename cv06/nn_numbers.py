from matrix import (
    plus, apply, multiply, multiply_elementwise,
    minus, multiply_const, zeros, gen_random_matrix, T
)
import math
import random
from PIL import Image
from tqdm import tqdm
import glob
import pickle


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def sigmoid_derivative_matrix(A):
    return apply(A, lambda x: x * (1 - x))


def forward(X, W1, B1, W2, B2):

    Z1 = plus(multiply(W1, X), B1)
    A1 = apply(Z1, sigmoid)

    Z2 = plus(multiply(W2, A1), B2)
    A2 = apply(Z2, sigmoid)

    return Z1, A1, Z2, A2


def backward(X, Y, A1, A2, W1, B1, W2, B2, learning_rate):

    # Výstupní vrstva
    dZ2 = multiply_elementwise(
        minus(A2, Y),
        sigmoid_derivative_matrix(A2)
    )

    dW2 = multiply(dZ2, T(A1))
    dB2 = dZ2

    # Skrytá vrstva
    dA1 = multiply(T(W2), dZ2)

    dZ1 = multiply_elementwise(
        dA1,
        sigmoid_derivative_matrix(A1)
    )

    dW1 = multiply(dZ1, T(X))
    dB1 = dZ1

    # Aktualizace parametrů
    W1 = minus(W1, multiply_const(dW1, learning_rate))
    B1 = minus(B1, multiply_const(dB1, learning_rate))

    W2 = minus(W2, multiply_const(dW2, learning_rate))
    B2 = minus(B2, multiply_const(dB2, learning_rate))

    return W1, B1, W2, B2


def train_step(X, Y, W1, B1, W2, B2, learning_rate):

    # FORWARD
    Z1, A1, Z2, A2 = forward(X, W1, B1, W2, B2)

    # BACKWARD
    W1, B1, W2, B2 = backward(
        X, Y, A1, A2,
        W1, B1, W2, B2,
        learning_rate
    )

    return W1, B1, W2, B2


def train(training_data, epochs, learning_rate,
          W1, B1, W2, B2):

    for epoch in range(epochs):
        print(f"\nEpoch {epoch + 1}/{epochs}")

        random.shuffle(training_data)

        total_loss = 0

        for path, label in tqdm(
            training_data,
            desc=f"Training {epoch + 1}/{epochs}",
            unit="image"
        ):
            X = load_image(path)

            Y = zeros(10, 1)
            Y[label][0] = 1

            # FORWARD
            Z1, A1, Z2, A2 = forward(
                X, W1, B1, W2, B2
            )

            # LOSS
            for i in range(10):
                error = A2[i][0] - Y[i][0]
                total_loss += 0.5 * error ** 2

            # BACKWARD
            W1, B1, W2, B2 = backward(
                X, Y, A1, A2,
                W1, B1, W2, B2,
                learning_rate
            )

        print(
            f"Epoch {epoch + 1}/{epochs}, "
            f"Loss: {total_loss / len(training_data):.6f}"
        )

    return W1, B1, W2, B2


def load_image(path):

    img = Image.open(path).convert("L")
    img = img.resize((256, 256))

    pixels = list(img.getdata())

    # Normalizace pixelů 0–1
    pixels = [pixel / 255.0 for pixel in pixels]

    # Sloupcový vektor 65536 × 1
    X = [[pixel] for pixel in pixels]

    return X


def load_training_data():

    training_data = []

    paths = glob.glob("training_center/*.png")

    for path in paths:

        filename = path.replace("\\", "/").split("/")[-1]

        # Label je číslo před podtržítkem
        label = int(filename.split("_")[0])

        training_data.append((path, label))

    return training_data

def save_model(W1, B1, W2, B2):

    with open("model.pkl", "wb") as file:
        pickle.dump((W1, B1, W2, B2), file)

    print("Model byl uložen!")

def predict_image(path):

    # Načtení již natrénovaného modelu
    W1, B1, W2, B2 = load_model()

    # Načtení obrázku
    X = load_image(path)

    # Průchod neuronovou sítí
    Z1, A1, Z2, A2 = forward(X, W1, B1, W2, B2)

    # Hledání neuronu s nejvyšší hodnotou
    results = [A2[i][0] for i in range(10)]

    prediction = results.index(max(results))

    print(f"Rozpoznané číslo: {prediction}")
    print(f"Jistota sítě (aktivace): {max(results):.4f}")

    return prediction

def load_model():

    with open("model.pkl", "rb") as file:
        W1, B1, W2, B2 = pickle.load(file)

    print("Model byl načten!")

    return W1, B1, W2, B2

def evaluate_model():

    # Načtení natrénovaného modelu
    W1, B1, W2, B2 = load_model()

    # Načtení všech validačních obrázků
    paths = glob.glob("training_center/8_*.png")

    correct = 0
    incorrect = 0

    print("\n--- TESTOVÁNÍ NEURONOVÉ SÍTĚ ---\n")

    for path in paths:

        # Zjištění správné číslice z názvu souboru
        filename = path.replace("\\", "/").split("/")[-1]
        actual_label = int(filename.split("_")[0])

        # Načtení obrázku
        X = load_image(path)

        # Dopředný průchod neuronovou sítí
        Z1, A1, Z2, A2 = forward(
            X, W1, B1, W2, B2
        )

        # Výběr nejaktivnějšího výstupního neuronu
        results = [A2[i][0] for i in range(10)]
        prediction = results.index(max(results))

        # Porovnání výsledku
        if prediction == actual_label:
            correct += 1
        else:
            incorrect += 1

            print(
                f"CHYBA: {filename} | "
                f"Správně: {actual_label} | "
                f"Rozpoznáno: {prediction}"
            )

    # Výpočet úspěšnosti
    total = correct + incorrect

    if total == 0:
        print("Nebyly nalezeny žádné testovací obrázky!")
        return

    accuracy = (correct / total) * 100

    print("\n--- VÝSLEDKY ---")
    print(f"Počet testovacích obrázků: {total}")
    print(f"Správně rozpoznáno: {correct}")
    print(f"Špatně rozpoznáno: {incorrect}")
    print(f"\nÚspěšnost neuronové sítě: {accuracy:.2f} %")


if __name__ == "__main__":
        evaluate_model()
