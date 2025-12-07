import google.generativeai as genai
import os
import json
import time
from datetime import datetime

class GeminiProcessor:
    def __init__(self):
        # Configure the implementation with the API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            # Switch to 2.0-flash as 1.5 appears unavailable for this key/region
            self.model = genai.GenerativeModel('gemini-2.0-flash')
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
            current_time = datetime.now().isoformat()
            
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
                - date: The meeting date or next follow-up date. ISO 8601 format.
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
                - date: The exact date/time mentioned. If "tomorrow", calculate based on current time.
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
                - date: ISO 8601 format or null if no time mention.
                """

            prompt = f"""
            {system_instruction}
            
            Respond ONLY with the JSON string.
            """

            response = self.model.generate_content([prompt, audio_file])
            
            # Clean up cleanup...
            raw_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(raw_text)

        except Exception as e:
            print(f"Gemini Error: {e}")
            return self._mock_response(error=str(e))

    def _mock_response(self, error=None):
        return {
            "summary": "Mock Note ( Gemini Key Missing )",
            "text": f"Error processing note: {error}" if error else "This is a mock response because GOOGLE_API_KEY is missing.",
            "category": "Life",
            "date": datetime.now().isoformat()
        }
