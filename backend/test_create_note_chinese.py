import asyncio
from services.notion_client import NotionClient
from dotenv import load_dotenv

load_dotenv()

async def list_databases():
    client = NotionClient()
    # Mock data as if coming from Gemini
    data = {
        "summary": "全中文測試筆記",
        "text": "這是一則用來驗證資料庫欄位全中文化的測試。",
        "category": "工作",
        "date": "2025-12-08T09:00:00"
    }
    print("Creating test note with Chinese schema...")
    url = await client.create_page(data)
    print(f"Test Note URL: {url}")

if __name__ == "__main__":
    asyncio.run(list_databases())
