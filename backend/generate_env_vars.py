import base64
import os
import json

def generate():
    print("=== Zeabur Environment Variables Generator ===\n")
    
    # 1. Google Token
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as f:
            token_bytes = f.read()
            token_b64 = base64.b64encode(token_bytes).decode('utf-8')
            print(f"GOOGLE_TOKEN_BASE64={token_b64}")
    else:
        print("# token.pickle not found (Run the app locally once to login)")

    print("\n" + "-"*40 + "\n")

    # 2. Credentials JSON
    if os.path.exists('credentials.json'):
        with open('credentials.json', 'r') as f:
            creds_content = f.read()
            # Mini-fy JSON
            creds_json = json.dumps(json.loads(creds_content))
            print(f"GOOGLE_CREDENTIALS_JSON={creds_json}")
    else:
        print("# credentials.json not found")

    print("\n=== End of Output ===")

if __name__ == "__main__":
    generate()
