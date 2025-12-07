import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("NOTION_TOKEN")
db_id = os.getenv("NOTION_DATABASE_ID")
notion = Client(auth=token)

def setup_schema():
    print(f"Fetching database {db_id}...")
    db = notion.databases.retrieve(database_id=db_id)
    
    current_props = db.get("properties", {})
    print("Current Properties:", list(current_props.keys()))
    
    # Identify Title property (it's immutable, just need to know its name)
    title_prop_name = next((k for k, v in current_props.items() if v['type'] == 'title'), "Name")
    print(f"Title Property is: {title_prop_name}")

    properties_to_create = {}

    # 1. Date
    if "Date" not in current_props and "日期" not in current_props:
        properties_to_create["Date"] = {"date": {}}
        print(" -> Will create 'Date' property")
    
    # 2. Category (Select)
    if "Category" not in current_props and "分類" not in current_props:
        properties_to_create["Category"] = {
            "select": {
                "options": [
                    {"name": "Job", "color": "blue"},
                    {"name": "Life", "color": "green"},
                    {"name": "Idea", "color": "yellow"}
                ]
            }
        }
        print(" -> Will create 'Category' property")
        
    # 3. Content (Text) - Optional, we can put text in body, but user agreed to schema with "Content" prop
    if "Content" not in current_props and "內容" not in current_props:
        properties_to_create["Content"] = {"rich_text": {}}
        print(" -> Will create 'Content' property")

    if properties_to_create:
        print("Updating Database Schema...")
        try:
            resp = notion.databases.update(database_id=db_id, properties=properties_to_create)
            print("Schema Updated Response:", resp)
        except Exception as e:
            print(f"Failed to update schema: {e}")
            return None
    else:
        print("Schema looks good! No changes needed.")

    # Return the mapping for our client to use
    return {
        "title": title_prop_name,
        "date": "Date" if "Date" in current_props or "Date" in properties_to_create else "日期",
        "category": "Category" if "Category" in current_props or "Category" in properties_to_create else "分類",
        "content": "Content" if "Content" in current_props or "Content" in properties_to_create else "內容"
    }

if __name__ == "__main__":
    mapping = setup_schema()
    print("Final Mapping:", mapping)
