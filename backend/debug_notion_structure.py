import os
import json
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("NOTION_TOKEN")
db_id = os.getenv("NOTION_DATABASE_ID")
notion = Client(auth=token)

print(f"Inspecting Database: {db_id}")
try:
    db = notion.databases.retrieve(database_id=db_id)
    print("--- DB Properties ---")
    for name, prop in db.get("properties", {}).items():
        print(f"Name: {name}, Type: {prop['type']}")
        
    print("\n--- Recent Pages (First 3) ---")
    pages = notion.databases.query(database_id=db_id, page_size=3)
    for p in pages["results"]:
        print(f"Page ID: {p['id']}")
        props = p.get("properties", {})
        # Print keys of properties and their values if simple
        for k, v in props.items():
            type_ = v['type']
            content = "..."
            if type_ == "title":
                content = v['title'][0]['plain_text'] if v['title'] else ""
            elif type_ == "rich_text":
                content = v['rich_text'][0]['plain_text'] if v['rich_text'] else ""
            elif type_ == "select":
                content = v['select']['name'] if v['select'] else "None"
            elif type_ == "date":
                content = v['date']['start'] if v['date'] else "None"
            
            print(f"  - {k} ({type_}): {content}")

except Exception as e:
    print(f"Error: {e}")
