#!/bin/bash
source .env
curl -X POST "https://api.notion.com/v1/databases/$NOTION_DATABASE_ID/query" \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2022-06-28" \
  --data '{
    "page_size": 1,
    "sorts": [
      {
        "timestamp": "created_time",
        "direction": "descending"
      }
    ]
  }'
