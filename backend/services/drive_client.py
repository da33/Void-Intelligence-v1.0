import os.path
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

class DriveClient:

    def __init__(self, google_auth_client=None):
        self.service = None
        if google_auth_client:
             self.service = google_auth_client.get_service('drive', 'v3')
        
    # Legacy authenticate method removed as it is now handled by GoogleAuthClient

    def find_or_create_folder(self, folder_name):
        """Finds a folder by name or creates it if it doesn't exist."""
        if not self.service: return None
        
        try:
            # Check if folder exists
            query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
            results = self.service.files().list(q=query, fields="files(id, name)").execute()
            files = results.get('files', [])
            
            if files:
                print(f"Found existing folder: {folder_name} ({files[0]['id']})")
                return files[0]['id']
            
            # Create if not found
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            file = self.service.files().create(body=file_metadata, fields='id').execute()
            print(f"Created new folder: {folder_name} ({file.get('id')})")
            return file.get('id')
            
        except Exception as e:
            print(f"Error finding/creating folder: {e}")
            return None

    def create_doc(self, title, content, folder_id=None):
        if not self.service:
            print("Drive service not initialized.")
            return None

        file_metadata = {
            'name': title,
            'mimeType': 'application/vnd.google-apps.document'
        }
        
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        # Simple text upload
        media = MediaIoBaseUpload(io.BytesIO(content.encode('utf-8')), mimetype='text/plain')
        
        try:
            file = self.service.files().create(body=file_metadata,
                                                media_body=media,
                                                fields='id, webViewLink').execute()
            print(f'File ID: {file.get("id")}')
            return file.get('webViewLink')
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
