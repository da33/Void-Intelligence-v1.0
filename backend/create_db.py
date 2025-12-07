import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("NOTION_TOKEN")
# This is the PAGE ID where we will create the DB
parent_page_id = "2c19115e-ac54-810f-8a3c-cc9b93beb456" 

notion = Client(auth=token)

try:
    print(f"Creating new Database under page {parent_page_id}...")
    
    new_db = notion.databases.create(
        parent={"type": "page_id", "page_id": parent_page_id},
        title=[{"type": "text", "text": {"content": "語音筆記 (Voice Notes)"}}],
        properties={
            "Name": {"title": {}},
            "Category": {
                "select": {
                    "options": [
                        {"name": "Job", "color": "blue"},
                        {"name": "Life", "color": "green"},
                        {"name": "Idea", "color": "yellow"}
                    ]
                }
            },
            "Date": {"date": {}},
            "Content": {"rich_text": {}}
        }
    )
    
    print("Success! Created Database.")
    print(f"NEW DATABASE ID: {new_db['id']}")
    print(f"URL: {new_db['url']}")

except Exception as e:
    print(f"Failed to create database: {e}")
