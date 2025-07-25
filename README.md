# Paperless NGX Automated Backup to Google Drive

This project automates the backup of all documents and metadata from a [Paperless NGX](https://github.com/paperless-ngx/paperless-ngx) server to a specific folder in your Google Drive. It ensures your digital archive is safely stored in the cloud, with robust logging and support for scheduled (cron) execution.

---

## Features
- Downloads all documents and their metadata from your Paperless NGX instance
- Uploads documents and metadata JSON to a Google Drive folder
- Overwrites files in Drive if they already exist (no duplicates)
- Logs all actions to both a log file and the terminal
- Can be run manually or scheduled via cron

---

## Prerequisites
- Python 3.8+
- [Paperless NGX](https://github.com/paperless-ngx/paperless-ngx) server running and accessible
- Google account with Drive API enabled
- OAuth credentials (`credentials.json`) for Google Drive (Desktop app)
- Required Python packages:
  - `requests`
  - `google-api-python-client`
  - `google-auth-httplib2`
  - `google-auth-oauthlib`

---

## Setting up a Virtual Environment

It is recommended to use a Python virtual environment to isolate dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Setup

### 1. Paperless NGX API Token
- Generate your API token using the provided script:
  ```bash
  python src/generate_paperless_token.py
  ```
- Set the token as an environment variable:
  ```bash
  export PAPERLESS_TOKEN=your_token_here
  ```

### 2. Google Drive OAuth Credentials
- In the [Google Cloud Console](https://console.cloud.google.com/):
  - Enable the Google Drive API
  - Create OAuth credentials (Desktop app)
  - Download `credentials.json` and place it in the `src/` directory

### 3. .gitignore
- Ensure sensitive files are not committed:
  ```
  token.pickle
  src/token.pickle
  credentials.json
  src/credentials.json
  backup.log
  docs/
  paperless_metadata.json
  paperless_metadata.csv
  ```

---

## Usage

### Manual Run
From the project root, run:
```bash
export PAPERLESS_TOKEN=your_token_here
python src/main.py
```
- This will download all documents and metadata, then upload them to Google Drive.
- Progress and errors are shown in the terminal and logged to `backup.log`.

### Scheduling with Cron
To automate daily backups (e.g., at 2:00 AM), add to your crontab (`crontab -e`):
```cron
0 2 * * * PAPERLESS_TOKEN=your_token_here /path/to/venv/bin/python /path/to/project/src/main.py >> /path/to/project/backup.log 2>&1
```
- Use absolute paths for reliability.
- Check `backup.log` for execution details.

---

## Logging
- All actions, warnings, and errors are logged to `backup.log` (in the project root by default).
- Key events are also printed to the terminal for real-time feedback.
- Adjust the log file path in the scripts if you want to store logs elsewhere.

---

## Security Notes
- **Never commit your `token.pickle` or `credentials.json` to version control.**
- The API token and Google credentials grant access to your documents and Google Drive.
- Restrict permissions and keep credentials safe.

---

## Troubleshooting
- **No logs in `backup.log`?**
  - Ensure the script has write permission to the log file location.
  - Use absolute paths for the log file if needed.
- **Google Drive upload fails?**
  - Check if `credentials.json` is in the correct location (`src/`).
  - Ensure you have completed the OAuth flow (first run will open a browser).
- **Paperless NGX download fails?**
  - Verify the API URL and that your token is valid.
- **Cron job not running?**
  - Check the cron log (`/var/log/syslog` or `backup.log`).
  - Make sure all paths and environment variables are set correctly in the crontab.

---

## Project Structure
```
project-root/
├── docs/                      # Downloaded documents (auto-created)
├── paperless_metadata.json    # Downloaded metadata (auto-created)
├── paperless_metadata.csv     # Downloaded metadata in CSV (auto-created)
├── backup.log                 # Log file
├── src/
│   ├── main.py                # Orchestrates the backup process
│   ├── download_paperless_documents.py
│   ├── upload_to_gdrive.py
│   └── generate_paperless_token.py
└── requirements.txt
```

---

## License
This project is provided as-is for personal use. Adapt and extend as needed for your environment.
