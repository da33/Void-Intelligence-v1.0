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
            
            # Create a Child Page (treated as a row in the DB)
            response = self.notion.pages.create(
                parent={"database_id": PARENT_PAGE_ID},
                properties={
                    "摘要": {
                        "title": [{"text": {"content": summary}}]
                    },
                    "分類": {
                        "select": {"name": category}
                    },
                    "日期": {
                        "date": {"start": date_str}
                    }
                },
                children=[
                    {
                        "object": "block",
                        "type": "callout",
                        "callout": {
                            "rich_text": [{"text": {"content": f"Category: {category} | Date: {date_str}"}}],
                            "icon": {"emoji": "📅"}
                        }
                    },
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [{"text": {"content": "Transcript"}}]
                        }
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"text": {"content": transcript}}]
                        }
                    }
                ]
            )
            return response["url"]
        
        except Exception as e:
            print(f"Notion Error: {e}")
            return None
