import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')
PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')

print(f"Testing token from .env file...")
print(f"Token length: {len(TOKEN)} chars")
print(f"Token starts with: {TOKEN[:20]}...")

url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/feed"
params = {
    "access_token": TOKEN,
    "limit": 3
}

response = requests.get(url, params=params)
data = response.json()

if 'data' in data:
    print(f"\n✅ SUCCESS! Found {len(data['data'])} posts")
    for post in data['data']:
        print(f"  - {post.get('message', 'No text')[:50]}")
else:
    print(f"\n❌ Failed: {data.get('error', {}).get('message', 'Unknown error')}")
    print("\nYour .env file still has an invalid token!")