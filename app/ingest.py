import json
from pathlib import Path
from pypdf import PdfReader


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_FILE = BASE_DIR / "data" / "records.json"


def extract_records():
    records = []

    for pdf_file in RAW_DIR.glob("*.pdf"):
        try:
            reader = PdfReader(pdf_file)

            if "hbp" in pdf_file.name.lower():
                title = "National Health Benefit Package 2.2 - User Guidelines"
                url = "https://nha.gov.in/img/resources/HBP-2.2-manual.pdf"
                applies_to = "Hospitals and PM-JAY implementation teams"

            else:
                title = "Guidelines on Process of Beneficiary Identification"
                url = "https://ayushmanbharat.haryana.gov.in/policy-guidelines/"
                applies_to = "Beneficiary identification operators and State teams"

            for page_number, page in enumerate(reader.pages, start=1):
                try:
                    text = page.extract_text()

                    if not text or len(text.strip()) < 30:
                        continue

                    record = {
                        "rule_topic": f"{title} - Page {page_number}",
                        "rule_text": " ".join(text.split()),
                        "applies_to": applies_to,
                        "document_title": title,
                        "page_or_section": f"PDF page {page_number}",
                        "source_url": url
                    }

                    records.append(record)

                except Exception as error:
                    print("Page error:", error)

        except Exception as error:
            print("File error:", pdf_file.name, error)

    return records


def save_records(records):
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            json.dump(records, file, indent=4, ensure_ascii=False)

        print("Records saved successfully!")
        print("Total records:", len(records))

    except Exception as error:
        print("Saving error:", error)


if __name__ == "__main__":
    records = extract_records()
    save_records(records)
