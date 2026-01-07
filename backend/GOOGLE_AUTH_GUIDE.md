# Google Calendar 授權設定指南

## 為什麼需要重新授權？

Google OAuth Token 會過期，需要定期更新。目前系統顯示 `auth_status: "Expired/Invalid"`，表示需要重新授權才能使用 Google Calendar 和 Google Drive 功能。

## 授權步驟

### 1. 確認您有 `credentials.json`

這個檔案包含您的 Google API 憑證。如果沒有，請到 [Google Cloud Console](https://console.cloud.google.com/) 下載。

```bash
# 檢查檔案是否存在
ls -la /Users/mac/代碼程式/Notion\ 記事/backend/credentials.json
```

### 2. 執行授權腳本

```bash
cd /Users/mac/代碼程式/Notion\ 記事/backend
source ../.venv/bin/activate
python3 setup_drive.py
```

這會：
- 開啟瀏覽器要求您登入 Google 帳號
- 授權存取 Google Calendar 和 Drive
- 產生 `token.pickle` 檔案

### 3. 轉換 Token 為 Base64

```bash
python3 -c "import pickle, base64; print(base64.b64encode(open('token.pickle', 'rb').read()).decode())"
```

複製輸出的 Base64 字串。

### 4. 更新 Zeabur 環境變數

1. 登入 [Zeabur Dashboard](https://zeabur.com)
2. 找到您的 `void-backend` 服務
3. 進入 **Variables** 設定
4. 更新或新增 `GOOGLE_TOKEN_BASE64` 變數，貼上剛才複製的 Base64 字串
5. 儲存並重新部署

### 5. 驗證授權狀態

等待部署完成後，檢查健康狀態：

```bash
curl https://void-backend.zeabur.app/api/health
```

應該會看到：
```json
{
  "status": "online",
  "auth_status": "Valid",
  "scopes": ["https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/calendar"],
  "env_var_present": true
}
```

## 常見問題

### Q: 我沒有 `credentials.json` 怎麼辦？

A: 請參考 [Google Calendar API 快速入門](https://developers.google.com/calendar/api/quickstart/python) 建立專案並下載憑證。

### Q: 授權後還是顯示 "Expired/Invalid"？

A: 請確認：
1. Base64 字串完整複製（沒有換行或空格）
2. Zeabur 環境變數已儲存並重新部署
3. 等待約 1-2 分鐘讓服務完全重啟

### Q: 可以跳過 Google Calendar 授權嗎？

A: 可以！核心的「語音轉 Notion 筆記」功能不需要 Google 授權。只有以下功能需要：
- 自動建立 Google Calendar 事件
- 匯出會議記錄到 Google Drive

## 時區修復已完成

✅ 系統現在會正確處理台北時區（UTC+8）  
✅ 說「下午三點」會建立 15:00 的事件，不會再變成 23:00  
✅ Gemini AI 會回傳帶有 `+08:00` 的時間格式

授權完成後，所有功能都會正常運作！
