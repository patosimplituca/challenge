from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json

class DriveService:
    def autenticar(self):
        scopes = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.metadata',
        'https://www.googleapis.com/auth/drive.metadata.readonly'
        ]
        with open('config.json') as f:
            config = json.load(f)
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", scopes
        )
        credenciales = flow.run_local_server()
        servicio_drive = build('drive', 'v3', credentials=credenciales)
        return servicio_drive
