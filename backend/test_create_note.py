import asyncio
from services.notion_client import NotionClient
from dotenv import load_dotenv

load_dotenv()

async def list_databases():
    client = NotionClient()
    data = {
        "summary": "System Integration Test",
        "text": "This is a test note to verify Category and Date fields.",
        "category": "Job",
        "date": "2025-12-08T10:00:00"
    }
    print("Creating test note...")
    url = await client.create_page(data)
    print(f"Test Note URL: {url}")

if __name__ == "__main__":
    asyncio.run(list_databases())
