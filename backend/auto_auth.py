#!/usr/bin/env python3
"""
Automated Google OAuth Authentication Script
Generates token.pickle for Google Calendar and Drive access
"""

import os
import sys
from services.google_auth import GoogleAuthClient

def main():
    print("=== Google OAuth 自動授權 ===")
    print("這個腳本會開啟瀏覽器進行 Google 授權...")
    print()
    
    # Check for credentials.json
    if not os.path.exists('credentials.json'):
        print("❌ 錯誤：找不到 credentials.json")
        print("請從 Google Cloud Console 下載 OAuth 憑證檔案")
        sys.exit(1)
    
    print("✓ 找到 credentials.json")
    
    # Initialize auth client with interactive mode
    print("正在啟動授權流程...")
    auth_client = GoogleAuthClient()
    
    # Force interactive authentication
    auth_client.authenticate(interactive=True)
    
    if auth_client.creds and auth_client.creds.valid:
        print()
        print("✅ 授權成功！")
        print("✓ token.pickle 已建立")
        print()
        print("授權範圍：")
        if hasattr(auth_client.creds, 'scopes'):
            for scope in auth_client.creds.scopes:
                print(f"  - {scope}")
        return 0
    else:
        print()
        print("❌ 授權失敗")
        print("請檢查 credentials.json 是否正確")
        return 1

if __name__ == "__main__":
    sys.exit(main())
