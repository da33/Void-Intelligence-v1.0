import os
import json
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("NOTION_TOKEN")
db_id = os.getenv("NOTION_DATABASE_ID")
notion = Client(auth=token)

print(f"Fetching latest note from DB: {db_id}")
try:
    # Query database, sort by created_time desc, limit 1
    response = notion.databases.query(
        database_id=db_id,
        sorts=[{"timestamp": "created_time", "direction": "descending"}],
        page_size=1
    )
    
    if not response["results"]:
        print("No notes found!")
    else:
        page = response["results"][0]
        props = page["properties"]
        
        print("\n--- Latest Note Data ---")
        print(f"Title: {props['Name']['title'][0]['text']['content']}")
        
        # Check Category
        if "Category" in props and props["Category"]["select"]:
            print(f"Category: {props['Category']['select']['name']}")
        else:
            print("Category: [Empty] or [Missing]")
            
        # Check Date
        if "日期" in props and props["日期"]["date"]:
            print(f"Date: {props['日期']['date']['start']}")
        else:
            print("Date: [Empty] or [Missing]")
            
        print(f"URL: {page['url']}")

except Exception as e:
    print(f"Error: {e}")
