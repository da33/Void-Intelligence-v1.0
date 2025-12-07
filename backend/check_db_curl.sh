#!/bin/bash
source .env
curl "https://api.notion.com/v1/databases/$NOTION_DATABASE_ID" \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Notion-Version: 2022-06-28"
