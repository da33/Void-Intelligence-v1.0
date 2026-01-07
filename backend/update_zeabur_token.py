#!/usr/bin/env python3
"""
自動更新 Zeabur 環境變數
將 token.pickle 轉換為 Base64 並更新到 Zeabur
"""

import os
import pickle
import base64

def main():
    print("=== Zeabur 環境變數更新工具 ===")
    print()
    
    # Check for token.pickle
    if not os.path.exists('token.pickle'):
        print("❌ 錯誤：找不到 token.pickle")
        print("請先執行 auto_auth.py 進行授權")
        return 1
    
    # Convert to base64
    with open('token.pickle', 'rb') as f:
        token_bytes = f.read()
        token_base64 = base64.b64encode(token_bytes).decode()
    
    print("✓ token.pickle 已轉換為 Base64")
    print(f"✓ Base64 長度: {len(token_base64)} 字元")
    print()
    
    # Save to file for manual use if needed
    with open('token_base64.txt', 'w') as f:
        f.write(token_base64)
    print("✓ Base64 已儲存至 token_base64.txt")
    print()
    
    print("=" * 60)
    print("📋 請手動完成以下步驟：")
    print("=" * 60)
    print()
    print("1. 登入 Zeabur Dashboard: https://zeabur.com")
    print("2. 選擇您的專案 (Notion 記事)")
    print("3. 選擇 'backend' 服務")
    print("4. 點擊 'Variables' 標籤")
    print("5. 找到或新增 'GOOGLE_TOKEN_BASE64' 變數")
    print("6. 貼上以下 Base64 字串：")
    print()
    print("-" * 60)
    print(token_base64)
    print("-" * 60)
    print()
    print("7. 點擊 'Save' 儲存")
    print("8. 等待服務自動重新部署（約 1-2 分鐘）")
    print()
    print("=" * 60)
    print()
    print("💡 提示：Base64 字串已複製到剪貼簿（如果支援）")
    
    # Try to copy to clipboard (macOS)
    try:
        import subprocess
        subprocess.run(['pbcopy'], input=token_base64.encode(), check=True)
        print("✅ Base64 已自動複製到剪貼簿！")
    except:
        print("⚠️  請手動複製上方的 Base64 字串")
    
    print()
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
