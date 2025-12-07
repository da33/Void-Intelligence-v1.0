import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("NOTION_TOKEN")
notion = Client(auth=token)

try:
    print("Searching for 'Voice Notes'...")
    response = notion.search(query="Voice Notes")
    results = response.get("results", [])
    
    for obj in results:
        print(f"ID: {obj['id']} | Type: {obj['object']}")
        if obj['object'] == 'database':
            title = obj.get('title', [{}])[0].get('plain_text', 'Untitled')
            print(f" -> DB Title: {title}")

except Exception as e:
    print(f"Error: {e}")
