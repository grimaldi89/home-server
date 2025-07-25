import os
import requests
import json
import csv
import logging

logging.basicConfig(
    filename='backup.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    force=True
)
logger = logging.getLogger(__name__)

BASE_URL = "http://192.168.99.11:81"
API_URL = f"{BASE_URL}/api/documents/"
TOKEN = os.getenv("PAPERLESS_TOKEN")

if not TOKEN:
    logger.error("PAPERLESS_TOKEN environment variable not set.")
    raise RuntimeError("Por favor, defina a variável de ambiente PAPERLESS_TOKEN.")

HEADERS = {
    "Authorization": f"Token {TOKEN}",
    "Accept": "application/json",
}

def fetch_all_documents():
    documents = []
    url = API_URL
    while url:
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        documents.extend(data.get("results", []))
        url = data.get("next")
    return documents

def download_document(doc):
    doc_id = doc["id"]
    file_name = doc.get("archived_file_name")
    if not file_name:
        file_name = doc.get("original_file_name")
    if not file_name:
        file_name = f"document_{doc_id}.bin"
    os.makedirs("docs", exist_ok=True)
    file_path = os.path.join("docs", file_name)
    download_url = f"{BASE_URL}/api/documents/{doc_id}/download/"
    resp = requests.get(download_url, headers=HEADERS)
    resp.raise_for_status()
    with open(file_path, "wb") as f:
        f.write(resp.content)
    logger.info(f"Downloaded: {file_name}")

def main():
    logger.info("Starting Paperless NGX document download...")
    try:
        documents = fetch_all_documents()
        logger.info(f"Total documents to download: {len(documents)}")

        # Salvando metadados em JSON
        with open('paperless_metadata.json', 'w', encoding='utf-8') as f:
            json.dump(documents, f, ensure_ascii=False, indent=2)
        logger.info("Saved metadata to paperless_metadata.json")

        # Salvando metadados em CSV
        keys = set()
        for doc in documents:
            keys.update(doc.keys())
        keys = sorted(keys)
        
        for i, doc in enumerate(documents, 1):
            if not doc.get("archived_file_name") and not doc.get("original_file_name"):
                logger.warning(f"Skipping ({i}/{len(documents)}): Document {doc['id']} has no filename.")
                continue
            logger.info(f"Downloading ({i}/{len(documents)}): {doc.get('archived_file_name') or doc.get('original_file_name') or f'document_{doc['id']}.bin'}")
            try:
                download_document(doc)
            except Exception as e:
                logger.error(f"Failed to download document {doc['id']}: {e}", exc_info=True)
        logger.info("All documents downloaded!")
    except Exception as e:
        logger.exception("Error during Paperless NGX document download")
        raise

if __name__ == "__main__":
    main() 