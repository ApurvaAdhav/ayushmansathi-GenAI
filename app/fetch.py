
import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"


documents = {
    "HBP-2.2-manual-download.pdf":
        "https://bsmedia.business-standard.com/_media/bs/data/general-file-upload/2025-04/Ayuhman%20Bharat%20Health%20Benefit%20Package%20HBP-2.2-manual.pdf",

    "Operation-Manual-PMJAY-download.pdf":
        "https://sha.kerala.gov.in/wp-content/uploads/2025/12/Operation-Manual-for-AB-PM-JAY-April-2022.pdf",

    "Grievance-Redressal-Guidelines-download.pdf":
        "https://cdnbbsr.s3waas.gov.in/s3169779d3852b32ce8b1a1724dbf5217d/uploads/2022/05/2022051099.pdf"
}

def download_documents():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for filename, url in documents.items():
        try:
            response = requests.get(
                url,
                timeout=30,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            response.raise_for_status()

            if not response.content.lstrip().startswith(b"%PDF"):
                print("Invalid PDF:", filename)
                continue

            with open(RAW_DIR / filename, "wb") as file:
                file.write(response.content)

            print("Downloaded:", filename)

        except (requests.exceptions.RequestException, OSError) as error:
            print("Download failed:", filename, error)


if __name__ == "__main__":
    download_documents()
