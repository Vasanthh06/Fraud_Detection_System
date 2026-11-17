import os
import json
import urllib.request
from dotenv import load_dotenv

# Load the exact same way the app does
load_dotenv()

key = os.getenv("RESEND_API_KEY", "")
print(f"Key in Python: '{key}'")
print(f"Key length: {len(key)}") # Should be exactly 36

if len(key) != 36:
    print("🚨 WARNING: Key length is not 36. You have hidden spaces, quotes, or missing characters in your .env file!")

payload = {
    "from": "ShopZone <noreply@fraudetect.site>",
    "to": ["vasanthyash77@gmail.com"],
    "subject": "Python App Test",
    "html": "<p>Testing from Python urllib</p>"
}

req = urllib.request.Request(
    "https://api.resend.com/emails",
    data=json.dumps(payload).encode(),
    headers={
        "Authorization": f"Bearer {key}",
        "User-Agent": "ShopZone/1.0",
        "Content-Type": "application/json",
    },
    method="POST",
)

try:
    with urllib.request.urlopen(req) as res:
        print("✅ SUCCESS! Python can send emails.")
        print(res.read().decode())
except Exception as e:
    print(f"❌ FAILED: {e}")
    if hasattr(e, 'read'):
        print(e.read().decode())