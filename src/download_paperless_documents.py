import os
import requests
from requests.auth import HTTPBasicAuth
import json
import csv

BASE_URL = "http://192.168.99.11:81"
API_URL = f"{BASE_URL}/api/documents/"
USERNAME = os.getenv("PAPERLESS_USERNAME")
PASSWORD = os.getenv("PAPERLESS_PASSWORD")

if not USERNAME or not PASSWORD:
    raise RuntimeError("Por favor, defina as variáveis de ambiente PAPERLESS_USERNAME e PAPERLESS_PASSWORD.")

def fetch_all_documents():
    documents = []
    url = API_URL
    while url:
        resp = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD))
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
    # Garante que a pasta 'docs' existe
    os.makedirs("docs", exist_ok=True)
    file_path = os.path.join("docs", file_name)
    download_url = f"{BASE_URL}/api/documents/{doc_id}/download/"
    resp = requests.get(download_url, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    resp.raise_for_status()
    with open(file_path, "wb") as f:
        f.write(resp.content)

def main():
    print("Buscando lista de documentos...")
    documents = fetch_all_documents()
    print(f"Total de documentos: {len(documents)}")

    # Salvando metadados em JSON
    with open('paperless_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)

    # Salvando metadados em CSV
    keys = set()
    for doc in documents:
        keys.update(doc.keys())
    keys = sorted(keys)


    for i, doc in enumerate(documents, 1):
        if not doc.get("archived_file_name") and not doc.get("original_file_name"):
            print(f"Pulando ({i}/{len(documents)}): Documento {doc['id']} sem nome de arquivo.")
            continue
        print(f"Baixando ({i}/{len(documents)}): {doc.get('archived_file_name') or doc.get('original_file_name') or f'document_{doc['id']}.bin'}")
        download_document(doc)
    print("Todos os documentos foram baixados!")

if __name__ == "__main__":
    main() 