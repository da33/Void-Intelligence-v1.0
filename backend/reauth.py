from services.google_auth import GoogleAuthClient
import os

def reauth():
    print("Deleting old token.pickle to force re-authentication with new scopes (Calendar)...")
    if os.path.exists('token.pickle'):
        os.remove('token.pickle')
    
    print("Initializing GoogleAuthClient...")
    # This will trigger the browser flow
    auth = GoogleAuthClient()
    
    if auth.creds and auth.creds.valid:
        print("\nSUCCESS! New token.pickle generated with Calendar support.")
        # Print Base64 for Zeabur
        import pickle
        import base64
        token_b64 = base64.b64encode(pickle.dumps(auth.creds)).decode('utf-8')
        print("\n=== ZEABUR ENV VAR (GOOGLE_TOKEN_BASE64) ===")
        print(token_b64)
        print("============================================")
        print("Please update this in your Zeabur Backend Variables.")

if __name__ == "__main__":
    reauth()
