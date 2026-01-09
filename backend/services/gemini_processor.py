import google.generativeai as genai
import os
import json
import time
from datetime import datetime
from zoneinfo import ZoneInfo

class GeminiProcessor:
    def __init__(self):
        # Configure the implementation with the API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            # Use 2.5-flash-lite as it's verified available in the user's quota list
            self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        else:
            self.model = None

    async def process_audio(self, audio_path: str, mode: str = "note"):
        if not self.model:
            # Mock response if key is missing
            return {
                "summary": "Mock Note (Gemini Key Missing)",
                "text": "Error: No Google API Key found.",
                "category": "生活",
                "date": datetime.now().isoformat()
            }

        try:
            print(f"Uploading {audio_path} to Gemini...")
            audio_file = genai.upload_file(path=audio_path)
            
            while audio_file.state.name == "PROCESSING":
                print("Waiting for audio processing...")
                time.sleep(1)
                audio_file = genai.get_file(audio_file.name)

            if audio_file.state.name == "FAILED":
                raise ValueError("Audio processing failed.")

            print("Generating content...")
            # Use Asia/Taipei timezone for accurate local time
            current_time = datetime.now(ZoneInfo("Asia/Taipei")).isoformat()
            
            # Select Prompt based on Mode
            if mode == "meeting":
                system_instruction = f"""
                You are a professional secretary. Listen to this audio recording of a meeting.
                The audio is likely in Traditional Chinese (繁體中文).
                Current time is: {current_time}.
                
                Your goal is to extract:
                1. Key Decisions (what was decided).
                2. Action Items (who needs to do what).
                3. A brief summary.
                
                Extract the following information in strict JSON format:
                - summary: A concise title for the meeting.
                - text: A structured summary, including Key Decisions and Action Items.
                - category: Choose one from ["工作", "生活", "學習", "其他"] based on the meeting content.
                - date: The meeting date or next follow-up date in ISO 8601 format WITH timezone (Asia/Taipei UTC+8). Example: 2026-01-07T15:00:00+08:00
                """
            elif mode == "schedule":
                system_instruction = f"""
                You are a scheduling assistant. Listen to this audio to extract event details.
                The audio is likely in Traditional Chinese (繁體中文).
                Current time is: {current_time}.
                
                Your PRIMARY goal is to identify the DATE and TIME of the event.
                
                Extract the following information in strict JSON format:
                - summary: The name of the event.
                - text: The original transcription.
                - category: Choose one from ["工作", "生活", "學習", "其他"] based on context.
                - date: The exact date/time in ISO 8601 format WITH timezone (Asia/Taipei UTC+8). If "tomorrow" or "下午三點", calculate based on current time and include +08:00. Example: 2026-01-08T15:00:00+08:00
                """
            else: # "note" or default
                system_instruction = f"""
                You are a personal assistant. Listen to this audio note.
                The audio is likely in Traditional Chinese (繁體中文).
                Current time is: {current_time}.
                
                Extract the following information in strict JSON format:
                - summary: A short title for the note.
                - text: The full transcription.
                - category: Choose the best fit from ["工作", "生活", "靈感", "學習", "其他"].
                - date: ISO 8601 format WITH timezone (Asia/Taipei UTC+8) or null if no time mention. Example: 2026-01-07T15:00:00+08:00
                """

            prompt = f"""
            {system_instruction}
            
            Respond ONLY with the JSON string.
            """

            response = self.model.generate_content(
                [prompt, audio_file],
                generation_config={"response_mime_type": "application/json"}
            )
            
            # Clean up cleanup...
            raw_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(raw_text)

        except Exception as e:
            print(f"Gemini Error: {e}")
            return self._mock_response(error=str(e))

    async def process_text(self, text: str, mode: str = "note"):
        """Process user-pasted text directly without audio transcription."""
        if not self.model:
            # Mock response if key is missing
            return {
                "summary": "Mock Note (Gemini Key Missing)",
                "text": text,
                "category": "生活",
                "date": datetime.now().isoformat()
            }

        try:
            print(f"Processing text input (mode: {mode})...")
            # Use Asia/Taipei timezone for accurate local time
            current_time = datetime.now(ZoneInfo("Asia/Taipei")).isoformat()
            
            # Select Prompt based on Mode
            if mode == "auto":
                system_instruction = f"""
                You are an intelligent assistant. Analyze this text and:
                1. Classify the type into one of: ["meeting", "schedule", "note"].
                   - "meeting": Formal or informal meetings, discussions, or synced sessions.
                   - "schedule": Specific events, appointments, or tasks with a designated time.
                   - "note": General thoughts, ideas, or reminders WITHOUT a specific future time.
                2. Extract:
                   - summary: A concise title.
                   - text: Structured summary for meetings, or original text for others.
                   - category: Choose from ["工作", "生活", "靈感", "學習", "其他"].
                   - date: ISO 8601 format WITH timezone (Asia/Taipei UTC+8). 
                     Calculate from current time ({current_time}) for relative terms like "明天".
                     Set to null if no time in "note".
                
                Extract in strict JSON format.
                """
            elif mode == "meeting":
                system_instruction = f"""
                You are a professional secretary. Analyze this meeting note text.
                Current time is: {current_time}.
                
                Extract: 
                - summary (title)
                - text (structured with Key Decisions/Action Items)
                - category ["工作", "生活", "學習", "其他"]
                - date (ISO 8601 with timezone Asia/Taipei)
                """
            elif mode == "schedule":
                system_instruction = f"""
                You are a scheduling assistant. Extract event details.
                Current time is: {current_time}.
                
                Extract:
                - summary (event name)
                - text (original)
                - category ["工作", "生活", "學習", "其他"]
                - date (exact ISO 8601 with timezone Asia/Taipei)
                """
            else: # "note"
                system_instruction = f"""
                You are a personal assistant. Analyze this note.
                Current time is: {current_time}.
                
                Extract:
                - summary (title)
                - text (original)
                - category ["工作", "生活", "靈感", "學習", "其他"]
                - date (ISO 8601 with timezone Asia/Taipei or null)
                """

            prompt = f"""
            {system_instruction}
            
            Add a field "type" to the output JSON which is the classified type: "meeting", "schedule", or "note".
            If mode was "{mode}", use that for "type" unless mode was "auto".

            Text to analyze:
            {text}
            
            Respond ONLY with the JSON string.
            """

            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            # Clean up response
            raw_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(raw_text)

        except Exception as e:
            print(f"Gemini Text Processing Error: {e}")
            return self._mock_response(error=str(e))

    def _mock_response(self, error=None):
        return {
            "summary": "Mock Note ( Gemini Key Missing )",
            "text": f"Error processing note: {error}" if error else "This is a mock response because GOOGLE_API_KEY is missing.",
            "category": "Life",
            "date": datetime.now().isoformat()
        }
