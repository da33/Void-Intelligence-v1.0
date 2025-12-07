#!/bin/bash
source .env
# Set property to null to delete it
curl -X PATCH "https://api.notion.com/v1/databases/$NOTION_DATABASE_ID" \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2022-06-28" \
  --data '{
    "properties": {
      "Category": null
    }
  }'
