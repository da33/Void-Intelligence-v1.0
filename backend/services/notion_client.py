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
                        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": transcript}}]}}
                    ]
                )
                print("Success: Database mode")
                return response["url"]
            except Exception as e1:
                print(f"Database Rich Mode failed: {e1}")

            # Try 2: Treat as Database (Simple Title only) - In case schema is different
            try:
                # Most databases have a 'Name' or 'Title' property. In Chinese Notion it might be "名稱" or just "title".
                # But 'title' is a safe bet for the primary column.
                response = self.notion.pages.create(
                    parent={"database_id": PARENT_PAGE_ID},
                    properties={
                        "title": {"title": [{"text": {"content": f"[{category}] {summary}"}}]}
                    },
                    children=[
                        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": transcript}}]}}
                    ]
                )
                print("Success: Database Simple Mode")
                return response["url"]
            except Exception as e2:
                print(f"Database Simple Mode failed: {e2}")

            # Try 3: Treat as Page (Sub-page mode)
            try:
                response = self.notion.pages.create(
                    parent={"page_id": PARENT_PAGE_ID},
                    properties={
                        "title": [{"text": {"content": f"[{category}] {summary}"}}]
                    },
                    children=[
                        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": transcript}}]}}
                    ]
                )
                print("Success: Page mode")
                return response["url"]
            except Exception as e3:
                print(f"Page mode failed: {e3}")
                raise e3  # Final fail mechanism
        
        except Exception as e:
            print(f"Notion Error: {e}")
            return None
