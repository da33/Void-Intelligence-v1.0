import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("NOTION_TOKEN")
db_id = os.getenv("NOTION_DATABASE_ID")
notion = Client(auth=token)

print(f"Localizing Database: {db_id}")

try:
    # 1. Rename 'Name' to '摘要'
    # 2. Rename 'Category' to '分類' and update options
    
    properties_update = {
        "Name": {"name": "摘要"},
        "Category": {
            "name": "分類",
            "select": {
                "options": [
                    {"name": "工作", "color": "blue"},
                    {"name": "生活", "color": "green"},
                    {"name": "靈感", "color": "yellow"}
                ]
            }
        }
    }
    
    print("Sending schema update...")
    notion.databases.update(database_id=db_id, properties=properties_update)
    print("Schema localized successfully!")

except Exception as e:
    print(f"Error during localization: {e}")
    print("Attempting fallback: If 'Category' doesn't exist, we might need to create '分類' instead.")
