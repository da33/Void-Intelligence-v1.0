from services.drive_client import DriveClient

print("--- Google Drive Setup ---")
print("This script will help you authorize the application to access your Google Drive.")
print("Ensure you have 'credentials.json' in this folder.")
print("If you don't, go to Google Cloud Console -> APIs & Services -> Credentials -> Create Credentials -> OAuth Client ID (Desktop App) -> Download JSON.")

client = DriveClient()

if client.creds and client.creds.valid:
    print("\n✅ Authentication successful!")
    print("Token saved to 'token.pickle'.")
    print("You can now restart the backend to enable NotebookLM Bridge.")
else:
    print("\n❌ Authentication failed or cancelled.")
