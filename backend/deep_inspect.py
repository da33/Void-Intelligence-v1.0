import os
from notion_client import Client
from dotenv import load_dotenv
import json

load_dotenv()

token = os.getenv("NOTION_TOKEN")
db_id = os.getenv("NOTION_DATABASE_ID")
notion = Client(auth=token)

try:
    print(f"Deep inspecting {db_id}...")
    db = notion.databases.retrieve(database_id=db_id)
    print(json.dumps(db, indent=2))
    print("PROPERTIES FOUND:", list(db.get("properties", {}).keys()))
except Exception as e:
    print(f"Error: {e}")
