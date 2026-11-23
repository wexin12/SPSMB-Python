
import csv
import time
import hashlib
from pathlib import Path
from io import BytesIO

import requests
from PIL import Image
from tqdm import tqdm

# CONFIG
TARGET_IMAGES = 1000
OUTPUT_DIR = Path("dataset/fish")
CSV_FILE = OUTPUT_DIR / "metadata.csv"

API_URL = "https://api.inaturalist.org/v1/observations"

# Povolené licence
ALLOWED_LICENSES = {"cc0", "cc-by"}

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

session = requests.Session()
session.headers.update({
    "User-Agent": "FishDatasetDownloader/1.0"
})

downloaded = set()
rows = []
page = 1

print("Starting fish dataset download...")

with tqdm(total=TARGET_IMAGES) as progress:

    while len(downloaded) < TARGET_IMAGES:

        params = {
            "iconic_taxa[]": "Actinopterygii",
            "has[]": "photos",
            "photo_license": "any",
            "quality_grade": "research",
            "per_page": 200,
            "page": page
        }

        try:
            response = session.get(
                API_URL,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            observations = response.json()["results"]

        except Exception as error:
            print("API error:", error)
            time.sleep(5)
            continue

        if not observations:
            print("No more observations available.")
            break

        for observation in observations:
            if len(downloaded) >= TARGET_IMAGES:
                break

            for photo in observation.get("photos", []):

                if len(downloaded) >= TARGET_IMAGES:
                    break

                license_code = photo.get("license_code")

                if license_code not in ALLOWED_LICENSES:
                    continue

                url = photo.get("url", "")

                if not url:
                    continue

                # Request larger image variant
                url = url.replace("/square.", "/large.")

                try:
                    image_response = session.get(
                        url,
                        timeout=30
                    )
                    image_response.raise_for_status()

                    image = Image.open(
                        BytesIO(image_response.content)
                    ).convert("RGB")

                    # Reject tiny images
                    if image.width < 224 or image.height < 224:
                        continue

                    # Detect duplicate image content
                    digest = hashlib.sha256(
                        image_response.content
                    ).hexdigest()

                    if digest in downloaded:
                        continue

                    filename = f"fish_{len(downloaded)+1:04d}.jpg"
                    image.save(OUTPUT_DIR / filename, quality=95)

                    downloaded.add(digest)

                    rows.append({
                        "filename": filename,
                        "license": license_code,
                        "attribution": photo.get("attribution", ""),
                        "observation_id": observation.get("id"),
                        "image_url": url
                    })

                    progress.update(1)

                except Exception:
                    continue

        page += 1
        time.sleep(1)

# Save metadata
with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "filename",
            "license",
            "attribution",
            "observation_id",
            "image_url"
        ]
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"\nDownloaded {len(downloaded)} fish images.")
print(f"Saved to: {OUTPUT_DIR}")

# moc pomale to bylo, tak jsme pouzili stranku - kagle. Ale alternativa funkcni a dost validni :)
