from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from services.gemini_processor import GeminiProcessor
from services.notion_client import NotionClient
from services.calendar_client import CalendarClient
from services.drive_client import DriveClient
from services.google_auth import GoogleAuthClient
import shutil
import base64
import os
import time
import logging
from dotenv import load_dotenv

load_dotenv()

# [Compatibility] Flush importlib.metadata shim for Python < 3.10
import importlib.metadata
if not hasattr(importlib.metadata, 'packages_distributions'):
    try:
        import importlib_metadata
        importlib.metadata.packages_distributions = importlib_metadata.packages_distributions
    except ImportError:
        # If even importlib_metadata is missing, provide a dummy to prevent crashes
        importlib.metadata.packages_distributions = lambda: {}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    error_msg = traceback.format_exc()
    print(f"Global Error caught: {error_msg}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error", 
            "message": str(exc), 
            "detail": error_msg
        },
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*"
        }
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

@app.post("/api/echo")
async def echo(data: dict):
    return {"status": "ok", "received": data}

@app.post("/api/process-text")
async def process_text_input(data: dict):
    """Process user-pasted text directly without audio recording."""
    try:
        text = data.get("text", "").strip()
        mode = data.get("mode", "note")
        
        # Validation
        if not text:
            raise HTTPException(status_code=400, detail="文字內容不能為空")
        
        if len(text) < 5:
            raise HTTPException(status_code=400, detail="文字內容太短，請至少輸入 5 個字元")
        
        if len(text) > 10000:
            raise HTTPException(status_code=400, detail="文字內容太長，請限制在 10000 字元以內")
        
        print(f"Processing text input (length: {len(text)}, mode: {mode})...")
        
        # 1. Process with Gemini (Analyze text)
        print("Processing with Gemini...")
        gemini_data = await gemini.process_text(text, mode=mode)
        print(f"Gemini result: {gemini_data}")
        
        # 2. Update Notion
        print("Updating Notion...")
        notion_url = await notion.create_page(gemini_data)
        
        # 3. Google Drive Export (for meeting mode)
        google_doc_link = None
        if mode == 'meeting':
            try:
                print("Exporting to Google Drive for NotebookLM...")
                
                folder_name = "Voice Notes"
                folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
                if not folder_id:
                    folder_id = drive.find_or_create_folder(folder_name)
                
                doc_title = f"Meeting: {gemini_data.get('summary', 'Untitled')}"
                doc_content = f"Title: {gemini_data.get('summary')}\nDate: {gemini_data.get('date')}\n\n{text}"
                
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
            ics_content = calendar.create_ics(gemini_data)
            google_cal_link = calendar.create_google_link(gemini_data)
        except Exception as e:
             print(f"[WARNING] Calendar Asset Gen Failed: {e}")

        # 5. Auto-create Event in Google Calendar
        auto_event_link = None
        if gemini_data.get("date"):
            try:
                print("Auto-syncing to Google Calendar...")
                auto_event_link = calendar.create_event(gemini_data)
            except Exception as e:
                print(f"[WARNING] Calendar Auto-Sync Failed: {e}")
        
        return {
            "status": "success",
            "notion_url": notion_url,
            "google_calendar_link": google_cal_link,
            "google_doc_link": google_doc_link,
            "auto_event_link": auto_event_link,
            "ics_content": ics_content,
            "gemini_data": gemini_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = f"API Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return {"status": "error", "message": str(e), "detail": error_msg if os.getenv("DEBUG") else None}


@app.post("/api/record")
async def process_audio(file: UploadFile = File(...), mode: str = Form("note")):
    try:
        filename = file.filename or "recording.webm"
        base_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
        temp_filename = f"temp_{base_name}_{int(time.time())}.webm" # Standardize ext for ffmpeg input
        mp3_filename = f"{temp_filename}.mp3"
        # Save temp file
        with open(temp_filename, "wb") as buffer:
            style_content = await file.read()
            buffer.write(style_content)
        
        file_size = os.path.getsize(temp_filename)
        print(f"Saved temp file: {temp_filename}, Size: {file_size} bytes")
        
        # Guard clause: Fail early if file is suspiciously small (< 500 bytes)
        if file_size < 500:
            print(f"File {temp_filename} is too small ({file_size} bytes). Likely corrupt or silent.")
            os.remove(temp_filename)
            return {"status": "error", "message": "音訊檔案太小，請重新錄音"}

        # TRANSCODE to MP3 using ffmpeg to ensure compatibility
        import subprocess
        print(f"Transcoding {temp_filename} to {mp3_filename}...")
        try:
            subprocess.run([
                "ffmpeg", "-i", temp_filename, 
                "-vn", "-acodec", "libmp3lame", "-b:a", "192k", "-y", mp3_filename
            ], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Transcoding failed (ffmpeg exit {e.returncode}): {e.stderr}")
            os.remove(temp_filename)
            return {"status": "error", "message": "音訊格式轉換失敗，請確認 ffmpeg 已安裝"}
        
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
        import traceback
        error_msg = f"API Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return {"status": "error", "message": str(e), "detail": error_msg if os.getenv("DEBUG") else None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
