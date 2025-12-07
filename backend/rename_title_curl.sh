#!/bin/bash
source .env
curl -X PATCH "https://api.notion.com/v1/databases/$NOTION_DATABASE_ID" \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2022-06-28" \
  --data '{
    "properties": {
      "Name": {
        "name": "摘要"
      },
      "分類": {
        "select": {
           "options": [
              {"name": "工作", "color": "blue"},
              {"name": "生活", "color": "green"},
              {"name": "靈感", "color": "yellow"}
           ]
        }
      }
    }
  }'
