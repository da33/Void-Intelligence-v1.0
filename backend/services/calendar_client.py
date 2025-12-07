from datetime import datetime, timedelta
import urllib.parse

class CalendarClient:
    def __init__(self, google_auth_client=None):
        self.service = None
        if google_auth_client:
             self.service = google_auth_client.get_service('calendar', 'v3')

    def create_event(self, data: dict):
        """Creates an event in Google Calendar."""
        if not self.service:
            print("Calendar service not initialized.")
            return None

        summary = data.get("summary", "Event")
        start_time = data.get("date") # ISO format expected
        
        try:
            dt_start = datetime.fromisoformat(start_time)
            dt_end = dt_start + timedelta(hours=1)
            
            event = {
                'summary': summary,
                'start': {
                    'dateTime': dt_start.isoformat(),
                    'timeZone': 'Asia/Taipei', # Hardcoded for now
                },
                'end': {
                    'dateTime': dt_end.isoformat(),
                    'timeZone': 'Asia/Taipei',
                },
            }

            event = self.service.events().insert(calendarId='primary', body=event).execute()
            print(f"Event created: {event.get('htmlLink')}")
            return event.get('htmlLink')
            
        except Exception as e:
            print(f"Error creating calendar event: {e}")
            return None

    def generate_google_link(self, summary: str, start_time: str, end_time: str = None):
        """Generates a Google Calendar event link."""
        # start_time format expected: YYYYMMDDTHHMMSS
        # If input is ISO 8601 (YYYY-MM-DDTHH:MM), convert it
        
        try:
            dt_start = datetime.fromisoformat(start_time)
            if end_time:
                dt_end = datetime.fromisoformat(end_time)
            else:
                dt_end = dt_start + timedelta(hours=1) # Default 1 hour
            
            fmt = "%Y%m%dT%H%M00"
            dates = f"{dt_start.strftime(fmt)}/{dt_end.strftime(fmt)}"
            
            base_url = "https://calendar.google.com/calendar/render?action=TEMPLATE"
            params = {
                "text": summary,
                "dates": dates,
            }
            return f"{base_url}&{urllib.parse.urlencode(params)}"
        except ValueError:
            return None

    def generate_ics_content(self, summary: str, start_time: str, end_time: str = None) -> str:
        """Generates content for an .ics file."""
        try:
            dt_start = datetime.fromisoformat(start_time)
            if end_time:
                dt_end = datetime.fromisoformat(end_time)
            else:
                dt_end = dt_start + timedelta(hours=1)
            
            fmt = "%Y%m%dT%H%M00"
            
            ics_content = [
                "BEGIN:VCALENDAR",
                "VERSION:2.0",
                "PRODID:-//Voice Note System//EN",
                "BEGIN:VEVENT",
                f"SUMMARY:{summary}",
                f"DTSTART:{dt_start.strftime(fmt)}",
                f"DTEND:{dt_end.strftime(fmt)}",
                "END:VEVENT",
                "END:VCALENDAR"
            ]
            return "\n".join(ics_content)
        except ValueError:
            return ""

    def create_ics(self, data: dict) -> str:
        """Wrapper to create ICS from data dict."""
        return self.generate_ics_content(data.get("summary", "Event"), data.get("date"))

    def create_google_link(self, data: dict) -> str:
        """Wrapper to create Google Link from data dict."""
        return self.generate_google_link(data.get("summary", "Event"), data.get("date"))
