from services.google_auth import GoogleAuthClient
from services.calendar_client import CalendarClient
from datetime import datetime, timedelta

def test_insert():
    print("Initializing Auth...")
    # Hack: ensure we find the token if running from root
    import os
    if os.path.exists('backend/token.pickle'):
        print("Found token in backend/, switching context...")
        os.chdir('backend')
    
    auth = GoogleAuthClient()
    
    if not auth.creds:
        print("ERROR: No credentials found (token.pickle or env var).")
        return

    print("Initializing Calendar Client...")
    calendar = CalendarClient(google_auth_client=auth)
    
    # Fake data
    now_iso = datetime.now().isoformat()
    data = {
        "summary": "VOID System Test Event",
        "date": now_iso
    }
    
    print(f"Attempting to insert event: {data}")
    link = calendar.create_event(data)
    
    if link:
        print(f"\nSUCCESS! Event created.")
        print(f"Link: {link}")
        print("Please check your Google Calendar (Primary) for 'VOID System Test Event' at the current time.")
    else:
        print("\nFAILED: No link returned. Check console for error details.")

if __name__ == "__main__":
    test_insert()
