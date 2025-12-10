import os
from notion_client import Client

from datetime import datetime

class NotionClient:
    def __init__(self):
        # Initialize client with token from env
        self.notion = Client(auth=os.getenv("NOTION_TOKEN"))

    async def create_page(self, data: dict):
        try:
            # We are using a Page as parent (Fallback mode)
            PARENT_PAGE_ID = os.getenv("NOTION_DATABASE_ID") # Reusing variable name for Parent Page ID
            
            summary = data.get("summary", "New Note")
            category = data.get("category", "Life")
            
            # Safe Date Handling
            date_str = data.get("date")
            if not date_str or date_str == "None":
                date_str = datetime.now().isoformat()
            
            transcript = data.get("text", "")
            
            # Try 1: Treat as Database (Rich Properties)
            try:
                print(f"Attempting to write to Database {PARENT_PAGE_ID}...")
                response = self.notion.pages.create(
                    parent={"database_id": PARENT_PAGE_ID},
                    properties={
                        "摘要": {"title": [{"text": {"content": summary}}]},
                        "分類": {"select": {"name": category}},
                        "日期": {"date": {"start": date_str}}
                    },
                    children=[
                        # Content blocks
                        {
                            "object": "block",
                            "type": "heading_2",
                            "heading_2": {"rich_text": [{"text": {"content": "Transcript"}}]}
                        },
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {"rich_text": [{"text": {"content": transcript}}]}
                        }
                    ]
                )
                print("Successfully wrote to Database.")
                return response["url"]
            except Exception as db_error:
                print(f"Database write failed ({db_error}), falling back to Page mode...")

            # Try 2: Treat as Page (Simple Append)
            # This works if ID is a Page OR if Database Schema doesn't match
            response = self.notion.pages.create(
                parent={"page_id": PARENT_PAGE_ID}, # Use page_id this time
                properties={
                    "title": [{"text": {"content": f"{category}: {summary}"}}] # Standard 'title' property always exists
                },
                children=[
                    {
                        "object": "block",
                        "type": "callout",
                        "callout": {
                            "rich_text": [{"text": {"content": f"Date: {date_str} | Category: {category} (Fallback Mode)"}}],
                            "icon": {"emoji": "⚠️"}
                        }
                    },
                     {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {"rich_text": [{"text": {"content": "Transcript"}}]}
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {"rich_text": [{"text": {"content": transcript}}]}
                    }
                ]
            )
            print("Successfully created sub-page.")
            return response["url"]
        
        except Exception as e:
            print(f"Notion Error: {e}")
            return None
