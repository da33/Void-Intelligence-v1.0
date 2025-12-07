import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("NOTION_TOKEN")
notion = Client(auth=token)

try:
    print("Searching for everything...")
    response = notion.search()
    results = response.get("results", [])
    
    found_db = None
    found_page = None

    for obj in results:
        if obj.get('object') == 'database':
            found_db = obj
            break
        elif obj.get('object') == 'page' and not found_page:
            found_page = obj
    
    if found_db:
        print(f"FOUND DATABASE: {found_db['id']}")
        title_obj = found_db.get('title', [])
        title = title_obj[0].get('plain_text') if title_obj else "Untitled"
        print(f"Title: {title}")
    elif found_page:
        print(f"FOUND PAGE: {found_page['id']}")
        # title might be in properties -> Name/title
        print("Title: (Page detected)")
    else:
        print("No objects found.")

except Exception as e:
    print(f"Error: {e}")
