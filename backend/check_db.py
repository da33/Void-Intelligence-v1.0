import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

try:
    token = os.getenv("NOTION_TOKEN")
    db_id = os.getenv("NOTION_DATABASE_ID")
    
    print(f"Checking Token: {token[:4]}...{token[-4:]}")
    print(f"Checking DB ID: {db_id}")
    
    notion = Client(auth=token)
    
    db = notion.databases.retrieve(database_id=db_id)
    print("Success! It is a Valid Database.")
    
    title_obj = db.get("title", [])
    title = title_obj[0].get("plain_text") if title_obj else "Untitled"
    print(f"Database Name: {title}")
    
    print("Properties:")
    for name, prop in db.get("properties", {}).items():
        print(f"- {name} ({prop['type']})")

except Exception as e:
    print(f"Error: {e}")
