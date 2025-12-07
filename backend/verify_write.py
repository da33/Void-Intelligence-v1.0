import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("NOTION_TOKEN")
db_id = os.getenv("NOTION_DATABASE_ID")
notion = Client(auth=token)

try:
    print(f"Attempting to create a test page in DB {db_id}...")
    new_page = {
        "Name": {"title": [{"text": {"content": "Test Note from API"}}]},
        "Category": {"select": {"name": "Life"}},
        # "Date": {"date": {"start": "2025-12-06"}} 
        # Commenting out Date for now to isolate, actually let's try just Name first if we are unsure
    }
    
    # Try adding properties we supposedly created
    properties = {
        "Name": {"title": [{"text": {"content": "Test Note"}}]},
        "Category": {"select": {"name": "Life"}},
        "Content": {"rich_text": [{"text": {"content": "This is a test content"}}]}
    }
    
    response = notion.pages.create(parent={"database_id": db_id}, properties=properties)
    print("Success! Created page:", response['url'])

except Exception as e:
    print(f"Failed to create page: {e}")
