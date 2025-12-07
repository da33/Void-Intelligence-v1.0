import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

try:
    token = os.getenv("NOTION_TOKEN")
    if not token:
        print("Error: No token found")
        exit(1)
        
    notion = Client(auth=token)
    
    # Search for everything
    response = notion.search()
    results = response.get("results", [])
    
    print(f"Found {len(results)} objects")
    for obj in results:
        obj_type = obj.get('object')
        print(f"Type: {obj_type} | ID: {obj['id']}")
        if obj_type == 'database':
            title_obj = obj.get("title", [])
            title = title_obj[0].get("plain_text") if title_obj else "Untitled"
            print(f" -> DB Title: {title}")
        elif obj_type == 'page':
             # Try to see parent or title
             props = obj.get("properties", {})
             # title_prop = next((v for k, v in props.items() if v['type'] == 'title'), None)
             print(f" -> Page detected. url: {obj.get('url')}")

except Exception as e:
    print(f"Error: {e}")
