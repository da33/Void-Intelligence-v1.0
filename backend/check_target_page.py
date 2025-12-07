import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("NOTION_TOKEN")
page_id = os.getenv("NOTION_DATABASE_ID")

notion = Client(auth=token)

try:
    print(f"Retrieving page {page_id}...")
    page = notion.pages.retrieve(page_id=page_id)
    
    # Try to find title
    # Title property key might vary, usually "title" or "Name"
    props = page.get("properties", {})
    title = "Untitled"
    for key, value in props.items():
        if value["type"] == "title":
            title_obj = value.get("title", [])
            if title_obj:
                title = title_obj[0].get("plain_text", "Untitled")
            break
            
    print(f"Title: {title}")
    print(f"URL: {page.get('url')}")

except Exception as e:
    print(f"Error: {e}")
