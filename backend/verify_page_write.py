import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("NOTION_TOKEN")
# Using the ID from environment variable
parent_page_id = os.getenv("NOTION_DATABASE_ID")

notion = Client(auth=token)

try:
    print(f"Attempting to create a child PAGE in {parent_page_id}...")
    
    response = notion.pages.create(
        parent={"database_id": parent_page_id},
        properties={
            "Name": {
                "title": [{"text": {"content": "Test Note (Database Fallback)"}}]
            }
        },
        children=[
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "Category: Life"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": "This is the content of the note."}}]
                }
            }
        ]
    )
    print("Success! Created page:", response['url'])

except Exception as e:
    print(f"Failed to create page: {e}")
