import os
import glob
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

SCOPES = ['https://www.googleapis.com/auth/drive.file']
FOLDER_NAME = 'PaperlessBackup'

# Caminho absoluto para o credentials.json ao lado deste script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials.json')

def authenticate():
    creds = None
    if os.path.exists(os.path.join(BASE_DIR, 'token.pickle')):
        with open(os.path.join(BASE_DIR, 'token.pickle'), 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(os.path.join(BASE_DIR, 'token.pickle'), 'wb') as token:
            pickle.dump(creds, token)
    return creds


def get_or_create_folder(service, folder_name):
    # Procura pasta existente
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])
    if items:
        return items[0]['id']
    # Cria pasta se não existir
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    file = service.files().create(body=file_metadata, fields='id').execute()
    return file.get('id')


def find_file_in_folder(service, file_name, folder_id):
    # Escapa aspas simples para a query do Drive
    safe_file_name = file_name.replace("'", "\\'")
    query = f"name='{safe_file_name}' and '{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])
    return items[0]['id'] if items else None

def delete_file(service, file_id):
    service.files().delete(fileId=file_id).execute()


def upload_file(service, file_path, folder_id):
    file_name = os.path.basename(file_path)
    # Verifica se já existe arquivo com o mesmo nome na pasta
    existing_file_id = find_file_in_folder(service, file_name, folder_id)
    if existing_file_id:
        print(f"Arquivo já existe no Drive, removendo: {file_name}")
        delete_file(service, existing_file_id)
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Enviado: {file_name}")


def main():
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    folder_id = get_or_create_folder(service, FOLDER_NAME)

    # Upload dos arquivos da pasta docs/
    for file_path in glob.glob('docs/*'):
        if os.path.isfile(file_path):
            upload_file(service, file_path, folder_id)

    # Upload do JSON de metadados
    if os.path.exists('paperless_metadata.json'):
        upload_file(service, 'paperless_metadata.json', folder_id)
    else:
        print('Arquivo paperless_metadata.json não encontrado!')

    print('Upload concluído!')

if __name__ == '__main__':
    main() 