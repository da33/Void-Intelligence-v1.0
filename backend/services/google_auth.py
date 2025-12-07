import os
import pickle
import base64
import json
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes for both Drive and Calendar
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/calendar'
]

class GoogleAuthClient:
    def __init__(self):
        self.creds = None
        self.authenticate()

    def authenticate(self):
        # 1. Try checking local file (for local dev)
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                try:
                    self.creds = pickle.load(token)
                except Exception:
                    print("Error loading token.pickle")
        
        # 2. Try loading token from Env Var (for Zeabur)
        elif os.getenv("GOOGLE_TOKEN_BASE64"):
            try:
                token_bytes = base64.b64decode(os.getenv("GOOGLE_TOKEN_BASE64"))
                self.creds = pickle.loads(token_bytes)
                print("Loaded Google token from Environment Variable.")
            except Exception as e:
                print(f"Failed to load token from Env: {e}")

        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception:
                    print("Token expired and refresh failed.")
                    # Fall through to re-login
            
            # If still invalid, try new login
            if not self.creds or not self.creds.valid:
                # 3. Try loading credentials.json (Local vs Env)
                if os.path.exists('credentials.json'):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                elif os.getenv("GOOGLE_CREDENTIALS_JSON"):
                     print("Interactive login not supported in this env without token.")
                     return
                else:
                    print("No credentials found. Google services disabled.")
                    return
                
                # Interactive flow (Only works locally)
                try:
                    print("Launching browser for Google Login (Drive + Calendar)...")
                    self.creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Authentication failed: {e}")
                    return
 
            # Save the credentials for the next run (Local only)
            if self.creds and not os.getenv("GOOGLE_TOKEN_BASE64"):
                with open('token.pickle', 'wb') as token:
                    pickle.dump(self.creds, token)
        
    def get_service(self, service_name, version):
        if not self.creds:
            return None
        try:
            return build(service_name, version, credentials=self.creds)
        except Exception as e:
            print(f"Failed to build {service_name} service: {e}")
            return None
