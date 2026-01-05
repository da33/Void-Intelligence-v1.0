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
        # Scopes for both Drive and Calendar
        self.scopes = [
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/calendar'
        ]
        self.creds = None
        self.authenticate(interactive=False) # Start with non-interactive load

    def authenticate(self, interactive=False):
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

        # If there are credentials, try to refresh if expired
        if self.creds and not self.creds.valid:
            if self.creds.expired and self.creds.refresh_token:
                try:
                    print("Attempting to refresh Google token...")
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"Token refresh failed: {e}")
                    # Don't null out creds yet, maybe we can try interactive later
            
        # 3. Interactive flow (Only if requested and credentials.json exists)
        if (not self.creds or not self.creds.valid) and interactive:
            if os.path.exists('credentials.json'):
                try:
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.scopes)
                    print("Launching browser for interactive login...")
                    self.creds = flow.run_local_server(port=0)
                    # Save for next time
                    with open('token.pickle', 'wb') as token:
                        pickle.dump(self.creds, token)
                except Exception as e:
                    print(f"Interactive authentication failed: {e}")
            else:
                print("Can't run interactive auth: credentials.json missing.")

        if not self.creds or not self.creds.valid:
            print("Google Services: UNAUTHORIZED (Integration disabled until re-auth)")
        
    def get_service(self, service_name, version):
        if not self.creds:
            return None
        try:
            return build(service_name, version, credentials=self.creds)
        except Exception as e:
            print(f"Failed to build {service_name} service: {e}")
            return None
