from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from services.gemini_processor import GeminiProcessor
from services.notion_client import NotionClient
from services.calendar_client import CalendarClient
from services.drive_client import DriveClient
from services.google_auth import GoogleAuthClient
import shutil
import base64
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Shared Auth
google_auth = GoogleAuthClient()

# Inject into clients
gemini = GeminiProcessor()
notion = NotionClient()
calendar = CalendarClient(google_auth_client=google_auth)
drive = DriveClient(google_auth_client=google_auth)

@app.get("/")
def read_root():  
    return {"status": "ok"}

@app.get("/api/health")
def health_check():
    """Checks the health of the system and auth status."""
    auth_status = "Uninitialized"
    scopes = []
    
    if google_auth.creds:
        if google_auth.creds.valid:
            auth_status = "Valid"
            scopes = google_auth.creds.scopes if hasattr(google_auth.creds, 'scopes') else []
        else:
            auth_status = "Expired/Invalid"
    else:
        auth_status = "No Credentials Found (Check GOOGLE_TOKEN_BASE64)"
        
    return {
        "status": "online",
        "auth_status": auth_status,
        "scopes": scopes,
        "env_var_present": bool(os.getenv("GOOGLE_TOKEN_BASE64"))
    }

@app.post("/api/record")
async def process_audio(file: UploadFile = File(...), mode: str = Form("note")):
    temp_filename = f"temp_{file.filename}"
    mp3_filename = f"{temp_filename}.mp3"
    
    try:
        # Save temp file
        with open(temp_filename, "wb") as buffer:
            style_content = await file.read()
            buffer.write(style_content)
        
        print(f"Saved temp file: {temp_filename}, Size: {os.path.getsize(temp_filename)} bytes")
        
        # TRANSCODE to MP3 using ffmpeg to ensure compatibility
        import subprocess
        print(f"Transcoding {temp_filename} to {mp3_filename}...")
        subprocess.run([
            "ffmpeg", "-i", temp_filename, 
            "-vn", "-acodec", "libmp3lame", "-b:a", "192k", "-y", mp3_filename
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        target_file = mp3_filename
            
        # 1. Process with Gemini (Transcribe + Analyze)
        print("Processing with Gemini...")
        data = await gemini.process_audio(target_file, mode=mode)
        text = data.get("text", "")
        print(f"Gemini result: {data}")
        
        # 2. Update Notion
        print("Updating Notion...")
        notion_url = await notion.create_page(data)
        
        # 3. Google Drive Export (NotebookLM Bridge)
        google_doc_link = None
        if mode == 'meeting':
            try:
                print("Exporting to Google Drive for NotebookLM...")
                
                # Find or Create Folder
                folder_name = "Voice Notes"
                folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
                if not folder_id:
                    folder_id = drive.find_or_create_folder(folder_name)
                
                doc_title = f"Meeting: {data.get('summary', 'Untitled')}"
                doc_content = f"Title: {data.get('summary')}\nDate: {data.get('date')}\n\n{text}"
                
                google_doc_link = drive.create_doc(doc_title, doc_content, folder_id=folder_id)
                
                if google_doc_link:
                    print(f"Google Doc created in '{folder_name}' ({folder_id}): {google_doc_link}")
            except Exception as e:
                print(f"[WARNING] Drive Export Failed: {e}")

        # 4. Generate Calendar Assets
        ics_content = None
        google_cal_link = None
        try:
            print("Generating Calendar assets...")
            ics_content = calendar.create_ics(data)
            google_cal_link = calendar.create_google_link(data)
        except Exception as e:
             print(f"[WARNING] Calendar Asset Gen Failed: {e}")

        # [NEW] Auto-create Event in Google Calendar (Mac Sync)
        # Attempt to create if date is present
        auto_event_link = None
        if data.get("date"):
            try:
                print("Auto-syncing to Google Calendar...")
                auto_event_link = calendar.create_event(data)
            except Exception as e:
                print(f"[WARNING] Calendar Auto-Sync Failed: {e}")
        
        # Cleanup
        os.remove(temp_filename)
        os.remove(mp3_filename)
        
        return {
            "status": "success",
            "notion_url": notion_url,
            "google_calendar_link": google_cal_link,
            "google_doc_link": google_doc_link,
            "auto_event_link": auto_event_link,
            "ics_content": ics_content, # Frontend can download this as .ics
            "gemini_data": data # [DEBUG] Return full analysis for client-side inspection
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
