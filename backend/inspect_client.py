import os
import json
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("NOTION_TOKEN")
db_id = os.getenv("NOTION_DATABASE_ID")
notion = Client(auth=token)

print(f"Methods of notion.databases:")
print(dir(notion.databases))

print(f"\nRetrieving DB: {db_id}")
db = notion.databases.retrieve(database_id=db_id)
print("DB Keys:", db.keys())
if "properties" in db:
    print("Properties found:", list(db["properties"].keys()))
else:
    print("No properties key in response!")
