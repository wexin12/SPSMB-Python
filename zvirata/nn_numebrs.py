import os
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageFile
from tqdm import tqdm

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms


# ============================================================
# KONFIGURACE
# ============================================================

# Cesty se vždy počítají od umístění tohoto Python souboru.
BASE_DIR = Path(__file__).resolve().parent

# Trénovací obrázky a validační obrázky jsou v oddělených složkách.
TRAIN_DATASET_PATH = BASE_DIR / "test_set_animals"
VALIDATION_DATASET_PATH = BASE_DIR / "animals"

MODEL_PATH = BASE_DIR / "model_animals.pth"

IMAGE_SIZE = 256

# Názvy musí přesně odpovídat názvům podsložek.
# Pořadí tříd musí zůstat stejné při trénování i validaci.
CLASS_NAMES = [
    "elephant",
    "dog",
    "cat",
    "fish",
    "parrot",
]

OUTPUT_SIZE = len(CLASS_NAMES)

LEARNING_RATE = 0.001
BATCH_SIZE = 8
EPOCHS = 3
WEIGHT_DECAY = 0.0001
EARLY_STOPPING_PATIENCE = 10
SEED = 42

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print(f"Používané zařízení: {DEVICE}")
print(f"Trénovací složka: {TRAIN_DATASET_PATH}")
print(f"Validační složka: {VALIDATION_DATASET_PATH}")

ImageFile.LOAD_TRUNCATED_IMAGES = True


# ============================================================
# RANDOM SEED
# ============================================================

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)


# ============================================================
# DATA AUGMENTATION – POUZE PRO TRÉNOVÁNÍ
# ============================================================

train_transform = transforms.Compose([
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomAffine(
        degrees=4,
        translate=(0.05, 0.05),
        scale=(0.95, 1.05),
        shear=3,
        fill=1.0,
    ),
    transforms.ColorJitter(
        brightness=0.15,
        contrast=0.15,
        saturation=0.15,
    ),
])


# ============================================================
# CNN BLOCK
# ============================================================

class ConvBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()

        self.block = nn.Sequential(
            nn.Conv2d(
                in_channels,
                out_channels,
                kernel_size=5,
                padding=1,
            ),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
        )

    def forward(self, x):
        return self.block(x)


# ============================================================
# CNN MODEL
# ============================================================

class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv_layers = nn.Sequential(
            ConvBlock(3, 16),
            ConvBlock(16, 32),
            ConvBlock(32, 64),
            ConvBlock(64, 128),
        )

        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(128, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.15),
            nn.Linear(256, OUTPUT_SIZE),
        )

    def forward(self, x):
        x = self.conv_layers(x)
        return self.classifier(x)


# ============================================================
# NAČÍTÁNÍ JEDNOHO OBRÁZKU
# ============================================================

def load_image(path):
    with Image.open(path) as img:
        img = img.convert("RGB")
        img = img.resize(
            (IMAGE_SIZE, IMAGE_SIZE),
            Image.Resampling.LANCZOS,
        )
        pixels = np.array(img, dtype=np.float32)

    x = torch.from_numpy(pixels)
    x = x.permute(2, 0, 1)
    x.div_(255.0)

    return x


# ============================================================
# NAČTENÍ OBRÁZKŮ Z JEDNÉ SLOŽKY DATASETU
# ============================================================

def load_all_data(dataset_path, dataset_description="DATASET"):
    dataset_path = Path(dataset_path)

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Složka {dataset_description} nebyla nalezena: {dataset_path}"
        )

    data = []

    extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp",
    }

    print(f"\nNačítám {dataset_description}: {dataset_path}\n")

    for label, class_name in enumerate(CLASS_NAMES):
        folder = dataset_path / class_name

        if not folder.exists():
            raise FileNotFoundError(
                f"Chybí podsložka třídy: {folder}"
            )

        # Načte obrázky s podporovanými příponami bez ohledu na velikost písmen.
        class_paths = sorted(
            path for path in folder.iterdir()
            if path.is_file() and path.suffix.lower() in extensions
        )

        valid_paths = []

        for path in class_paths:
            try:
                with Image.open(path) as img:
                    img.verify()
                valid_paths.append(path)
            except Exception as error:
                print(f"Neplatný obrázek: {path} ({error})")

        if len(valid_paths) == 0:
            raise RuntimeError(
                f"Třída '{class_name}' neobsahuje žádné platné obrázky "
                f"ve složce {folder}"
            )

        for path in valid_paths:
            data.append((str(path), label))

        print(f"{class_name}: {len(valid_paths)} obrázků")

    if len(data) == 0:
        raise RuntimeError(
            f"Složka {dataset_description} neobsahuje žádné platné obrázky!"
        )

    print(f"\nCelkem {dataset_description}: {len(data)} obrázků\n")
    return data


# ============================================================
# DATASET CLASS
# ============================================================

class AnimalDataset(Dataset):
    def __init__(self, data, transform=None):
        self.data = data
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        path, label = self.data[index]

        x = load_image(path)

        if self.transform is not None:
            x = self.transform(x)

        y = torch.tensor(label, dtype=torch.long)
        return x, y


# ============================================================
# NAČTENÍ MODELU
# ============================================================

def load_model():
    model = NeuralNetwork().to(DEVICE)

    if not MODEL_PATH.exists():
        print("Vytvářím nový model – checkpoint nebyl nalezen!")
        return model, None

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE,
        weights_only=True,
    )

    if checkpoint.get("class_names") != CLASS_NAMES:
        print("Checkpoint má jiné názvy nebo pořadí tříd!")
        print("Vytvářím nový model.")
        return model, None

    try:
        model.load_state_dict(checkpoint["model_state_dict"])
        print("Předchozí model byl načten!")
        return model, checkpoint
    except (RuntimeError, KeyError):
        print("Checkpoint není kompatibilní s aktuální architekturou!")
        print("Vytvářím nový model.")
        return model, None


# ============================================================
# ULOŽENÍ CHECKPOINTU
# ============================================================

def save_model(model, optimizer, epoch, best_loss):
    torch.save({
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "epoch": epoch,
        "best_loss": best_loss,
        "class_names": CLASS_NAMES,
        "image_size": IMAGE_SIZE,
    }, MODEL_PATH)

    print(f"Model uložen do: {MODEL_PATH}")


# ============================================================
# TRAINING – JEDNA EPOCHA
# ============================================================

def train_epoch(model, loader, optimizer, criterion, epoch):
    model.train()

    total_loss = 0.0
    correct = 0
    incorrect = 0
    total = 0

    progress = tqdm(
        loader,
        desc=f"Training {epoch}",
        unit="batch",
    )

    for x, y in progress:
        x = x.to(DEVICE)
        y = y.to(DEVICE)

        optimizer.zero_grad(set_to_none=True)

        output = model(x)
        loss = criterion(output, y)

        loss.backward()
        optimizer.step()

        predictions = output.argmax(dim=1)

        correct += (predictions == y).sum().item()
        incorrect += (predictions != y).sum().item()
        total += y.size(0)
        total_loss += loss.item() * x.size(0)

        progress.set_postfix(
            loss=f"{loss.item():.5f}",
            accuracy=f"{correct / total * 100:.2f}%",
        )

    average_loss = total_loss / total
    accuracy = correct / total * 100

    return average_loss, accuracy, correct, incorrect


# ============================================================
# VALIDACE
# ============================================================

def validate(model, loader, criterion, description="VALIDATION"):
    model.eval()

    total_loss = 0.0
    correct = 0
    incorrect = 0
    total = 0

    class_correct = [0] * OUTPUT_SIZE
    class_total = [0] * OUTPUT_SIZE

    confusion_matrix = torch.zeros(
        OUTPUT_SIZE,
        OUTPUT_SIZE,
        dtype=torch.int64,
    )

    print("\n--- VALIDACE ---\n")

    with torch.inference_mode():
        for x, y in loader:
            x = x.to(DEVICE)
            y = y.to(DEVICE)

            output = model(x)
            loss = criterion(output, y)
            predictions = output.argmax(dim=1)

            for actual, prediction in zip(y.cpu(), predictions.cpu()):
                actual_index = actual.item()
                prediction_index = prediction.item()
                confusion_matrix[actual_index, prediction_index] += 1

            total_loss += loss.item() * x.size(0)

            for actual, prediction in zip(y.cpu(), predictions.cpu()):
                actual_index = actual.item()
                prediction_index = prediction.item()

                total += 1
                class_total[actual_index] += 1

                if prediction_index == actual_index:
                    correct += 1
                    class_correct[actual_index] += 1
                    status = "OK"
                else:
                    incorrect += 1
                    status = "CHYBA"

                accuracy = correct / total * 100

                tqdm.write(
                    f"[{status}] "
                    f"Skutečnost: {CLASS_NAMES[actual_index]} | "
                    f"Rozpoznáno: {CLASS_NAMES[prediction_index]} | "
                    f"Accuracy: {accuracy:.2f}%"
                )

    if total == 0:
        raise RuntimeError("Validační dataset je prázdný!")

    average_loss = total_loss / total
    accuracy = correct / total * 100

    print("\n--------------------------------")
    print(f"{description} Loss: {average_loss:.6f}")
    print(f"Správně: {correct}")
    print(f"Špatně: {incorrect}")
    print(f"Úspěšnost: {accuracy:.2f}%")
    print("--------------------------------")

    print("\nMATICE ZÁMĚN")
    print("Řádky = skutečnost, sloupce = predikce\n")

    print(
        " " * 12
        + " ".join(f"{name[:8]:>9}" for name in CLASS_NAMES)
    )

    for i, name in enumerate(CLASS_NAMES):
        print(
            f"{name:<12}"
            + " ".join(f"{int(value):9d}" for value in confusion_matrix[i])
        )

    return (
        average_loss,
        accuracy,
        correct,
        incorrect,
        class_correct,
        class_total,
    )


# ============================================================
# TRÉNOVÁNÍ
# ============================================================

def train():
    # Pro trénování se použijí VŠECHNY obrázky ze složky animals_train.
    training_data = load_all_data(
        TRAIN_DATASET_PATH,
        "TRÉNOVACÍ DATASET",
    )

    training_dataset = AnimalDataset(
        training_data,
        transform=train_transform,
    )

    training_loader = DataLoader(
        training_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
        pin_memory=(DEVICE.type == "cuda"),
    )

    model, checkpoint = load_model()
    criterion = nn.CrossEntropyLoss()

    optimizer = optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )

    start_epoch = 0
    best_loss = float("inf")
    patience_counter = 0

    # Pokračování v trénování z uloženého checkpointu.
    if checkpoint is not None:
        if "optimizer_state_dict" in checkpoint:
            try:
                optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
            except (ValueError, RuntimeError):
                print("Optimalizér se nepodařilo načíst, začíná s novým nastavením.")

        for param_group in optimizer.param_groups:
            param_group["lr"] = LEARNING_RATE

        start_epoch = checkpoint.get("epoch", 0)
        best_loss = checkpoint.get("best_loss", float("inf"))

        print(f"Pokračuji od epochy {start_epoch + 1}")
        print(f"Nejlepší Train Loss: {best_loss:.6f}")

    # ========================================================
    # EPOCHS
    # ========================================================

    for epoch in range(start_epoch, start_epoch + EPOCHS):
        print("\n========================================")
        print(f"EPOCH: {epoch + 1}")
        print("========================================")

        train_loss, train_accuracy, train_correct, train_incorrect = train_epoch(
            model,
            training_loader,
            optimizer,
            criterion,
            epoch + 1,
        )

        print("\n--- TRAINING VÝSLEDKY ---")
        print(f"Train Loss: {train_loss:.6f}")
        print(f"Správně: {train_correct}")
        print(f"Špatně: {train_incorrect}")
        print(f"Train Accuracy: {train_accuracy:.2f}%")

        # Uložení nejlepšího modelu podle Train Loss.
        if train_loss < best_loss:
            best_loss = train_loss
            patience_counter = 0

            save_model(
                model,
                optimizer,
                epoch + 1,
                best_loss,
            )
        else:
            patience_counter += 1
            print(
                f"Bez zlepšení: {patience_counter}/"
                f"{EARLY_STOPPING_PATIENCE}"
            )

        if patience_counter >= EARLY_STOPPING_PATIENCE:
            print("\nEARLY STOPPING!")
            print("Train Loss se nezlepšuje.")
            break

    print("\n========================================")
    print("TRÉNOVÁNÍ DOKONČENO")
    print(f"Nejlepší Train Loss: {best_loss:.6f}")
    print("========================================")


# ============================================================
# SAMOSTATNÁ VALIDACE
# ============================================================

def evaluate_model():
    if not MODEL_PATH.exists():
        print("Model nebyl nalezen! Nejdříve spusť trénování.")
        return

    # Pro validaci se použijí VŠECHNY obrázky ze složky animals.
    validation_data = load_all_data(
        VALIDATION_DATASET_PATH,
        "VALIDAČNÍ DATASET",
    )

    model = NeuralNetwork().to(DEVICE)

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE,
        weights_only=True,
    )

    if checkpoint.get("class_names") != CLASS_NAMES:
        print("Checkpoint má jiné názvy nebo pořadí tříd!")
        print("Zkontroluj CLASS_NAMES a případně model znovu natrénuj.")
        return

    try:
        model.load_state_dict(checkpoint["model_state_dict"])
    except (RuntimeError, KeyError) as error:
        print(f"Model se nepodařilo načíst: {error}")
        return

    dataset = AnimalDataset(
        validation_data,
        transform=None,
    )

    loader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
        pin_memory=(DEVICE.type == "cuda"),
    )

    criterion = nn.CrossEntropyLoss()

    (
        loss,
        accuracy,
        correct,
        incorrect,
        class_correct,
        class_total,
    ) = validate(
        model,
        loader,
        criterion,
        description="VALIDATION",
    )

    print("\n========================================")
    print("          CELKOVÉ VÝSLEDKY")
    print("========================================")
    print(f"Počet obrázků: {correct + incorrect}")
    print(f"Správně: {correct}")
    print(f"Špatně: {incorrect}")
    print(f"Average Loss: {loss:.6f}")
    print("----------------------------------------")
    print(f"CELKOVÁ ÚSPĚŠNOST: {accuracy:.2f}%")
    print("----------------------------------------")

    for label, name in enumerate(CLASS_NAMES):
        if class_total[label] > 0:
            class_accuracy = class_correct[label] / class_total[label] * 100
            print(
                f"{name}: {class_accuracy:.2f}% "
                f"({class_correct[label]}/{class_total[label]})"
            )

    print("========================================")


# ============================================================
# HLAVNÍ PROGRAM
# ============================================================

if __name__ == "__main__":
    # "train" = trénování na animals_train
    # "validate" = validace na všech obrázcích v animals

    MODE = "train"  # Změň na "validate", pokud chceš pouze validovat.

    if MODE == "train":
        train()
    elif MODE == "validate":
        evaluate_model()
    else:
        print("Neznámý režim! Použij 'train' nebo 'validate'.")
