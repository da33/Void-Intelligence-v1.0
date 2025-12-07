import os.path
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class DriveClient:
    def __init__(self):
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        # 1. Try checking local file (for local dev)
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        # 2. Try loading token from Env Var (for Zeabur)
        elif os.getenv("GOOGLE_TOKEN_BASE64"):
            try:
                import base64
                token_bytes = base64.b64decode(os.getenv("GOOGLE_TOKEN_BASE64"))
                self.creds = pickle.loads(token_bytes)
                print("Loaded Drive token from Environment Variable.")
            except Exception as e:
                print(f"Failed to load token from Env: {e}")

        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception:
                    print("Token expired and refresh failed.")
                    return # Caller handles re-auth
            else:
                # 3. Try loading credentials.json (Local vs Env)
                if os.path.exists('credentials.json'):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                elif os.getenv("GOOGLE_CREDENTIALS_JSON"):
                     # Write temp file for the library to read (or use from_client_config if parsed)
                     import json
                     import tempfile
                     creds_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))
                     # For simplicity, we skip the interactive flow on server
                     print("Interactive login not supported in this env without token.")
                     return
                else:
                    print("No credentials found. Drive upload disabled.")
                    return
                
                # Interactive flow (Only works locally)
                try:
                    self.creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Authentication failed: {e}")
                    return
 
            # Save the credentials for the next run (Local only)
            if self.creds and not os.getenv("GOOGLE_TOKEN_BASE64"):
                with open('token.pickle', 'wb') as token:
                    pickle.dump(self.creds, token)

        try:
            self.service = build('drive', 'v3', credentials=self.creds)
        except Exception as e:
            print(f"Failed to build Drive service: {e}")

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
