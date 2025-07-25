import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
download_script = os.path.join(BASE_DIR, 'src', 'download_paperless_documents.py')
upload_script = os.path.join(BASE_DIR, 'src', 'upload_to_gdrive.py')

# Executa o script de download dos documentos e metadados
print('Baixando documentos e metadados do Paperless NGX...')
download_result = subprocess.run([sys.executable, download_script])
if download_result.returncode != 0:
    print('Erro ao baixar documentos/metadados. Abortando backup.')
    sys.exit(1)

# Executa o script de upload para o Google Drive
print('Enviando arquivos e metadados para o Google Drive...')
upload_result = subprocess.run([sys.executable, upload_script])
if upload_result.returncode != 0:
    print('Erro ao enviar arquivos/metadados para o Google Drive.')
    sys.exit(1)

print('Backup concluído com sucesso!')
