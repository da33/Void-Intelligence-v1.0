import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("No API Key found")
    exit()

genai.configure(api_key=api_key)

candidates = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.0-flash-lite-preview-02-05",
    "gemini-2.5-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-pro-latest",
    "gemini-2.0-flash-exp"
]

print(f"Testing {len(candidates)} models for availability and quota...\n")

for model_name in candidates:
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello")
        print(f"[SUCCESS] {model_name}: OK!")
    except Exception as e:
        print(f"[FAILED]  {model_name}: {e}")
