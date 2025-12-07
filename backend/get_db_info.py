import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("NOTION_TOKEN")
db_id = os.getenv("NOTION_DATABASE_ID")

if not token or not db_id:
    print("Missing token or db_id")
    exit()

notion = Client(auth=token)

try:
    # Try retrieving as database first (since we set it up as one)
    db = notion.databases.retrieve(database_id=db_id)
    title = ""
    if db.get("title"):
        title = "".join([t["plain_text"] for t in db["title"]])
    
    url = db.get("url")
    print(f"Type: Database")
    print(f"Title: {title}")
    print(f"URL: {url}")

except Exception as e:
    # Fallback if it's a page (though we treated it as DB in setup)
    try:
        page = notion.pages.retrieve(page_id=db_id)
        title = ""
        # Accessing title property of a page is tricky without knowing prop name, 
        # but the request response usually has 'url'
        url = page.get("url")
        print(f"Type: Page")
        print(f"URL: {url}")
    except Exception as e2:
        print(f"Error: {e}")
