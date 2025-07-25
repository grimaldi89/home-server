import os
import glob
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

logging.basicConfig(
    filename='backup.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    force=True
)
logger = logging.getLogger(__name__)


SCOPES = ['https://www.googleapis.com/auth/drive.file']
FOLDER_NAME = 'PaperlessBackup'

# Caminho absoluto para o credentials.json ao lado deste script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials.json')

def authenticate():
    creds = None
    token_path = os.path.join(BASE_DIR, 'token.pickle')
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    return creds

def get_or_create_folder(service, folder_name):
    try:
        query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
        results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])
        if items:
            logger.info(f"Found existing folder '{folder_name}' in Google Drive.")
            print(f"Found existing folder '{folder_name}' in Google Drive.")
            return items[0]['id']
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        file = service.files().create(body=file_metadata, fields='id').execute()
        logger.info(f"Created new folder '{folder_name}' in Google Drive.")
        print(f"Created new folder '{folder_name}' in Google Drive.")
        return file.get('id')
    except Exception as e:
        logger.error(f"Error getting or creating folder '{folder_name}': {e}", exc_info=True)
        print(f"Error getting or creating folder '{folder_name}': {e}")
        raise

def find_file_in_folder(service, file_name, folder_id):
    safe_file_name = file_name.replace("'", "\\'")
    query = f"name='{safe_file_name}' and '{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])
    return items[0]['id'] if items else None

def delete_file(service, file_id):
    try:
        service.files().delete(fileId=file_id).execute()
        logger.info(f"Deleted existing file with id {file_id} from Google Drive.")
        print(f"Deleted existing file with id {file_id} from Google Drive.")
    except Exception as e:
        logger.error(f"Error deleting file with id {file_id}: {e}", exc_info=True)
        print(f"Error deleting file with id {file_id}: {e}")

def upload_file(service, file_path, folder_id):
    file_name = os.path.basename(file_path)
    try:
        existing_file_id = find_file_in_folder(service, file_name, folder_id)
        if existing_file_id:
            logger.info(f"File already exists in Drive, removing: {file_name}")
            print(f"File already exists in Drive, removing: {file_name}")
            delete_file(service, existing_file_id)
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        logger.info(f"Uploaded: {file_name}")
        print(f"Uploaded: {file_name}")
    except Exception as e:
        logger.error(f"Failed to upload {file_name}: {e}", exc_info=True)
        print(f"Failed to upload {file_name}: {e}")

def main():
    logger.info("Starting upload to Google Drive...")
    print("Starting upload to Google Drive...")
    try:
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
            logger.warning('paperless_metadata.json not found!')
            print('paperless_metadata.json not found!')

        logger.info('Upload to Google Drive completed!')
        print('Upload to Google Drive completed!')
    except Exception as e:
        logger.exception("Error during upload to Google Drive")
        print(f"Error during upload to Google Drive: {e}")
        raise

if __name__ == '__main__':
    main() 