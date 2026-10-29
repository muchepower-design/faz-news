# save as get_long_lived_token.py
import requests

APP_ID = "869549952848975"
APP_SECRET = "32d7b7fd52d7ff3ce5fd1c2ae4783806"

# Get a short-lived Page Token from Graph API Explorer first
short_lived_token = input("Paste your short-lived Page Token: ")

# Exchange for long-lived token
url = "https://graph.facebook.com/v18.0/oauth/access_token"
params = {
    "grant_type": "fb_exchange_token",
    "client_id": APP_ID,
    "client_secret": APP_SECRET,
    "fb_exchange_token": short_lived_token
}

response = requests.get(url, params=params)
result = response.json()

if 'access_token' in result:
    print("\n" + "="*60)
    print("✅ LONG-LIVED PAGE TOKEN (60 days):")
    print("="*60)
    print(result['access_token'])
    print("="*60)
    print(f"\nExpires in: {result.get('expires_in', 0)} seconds (~{int(result.get('expires_in', 0)/86400)} days)")
    print("\nCopy this token to your .env file!")
else:
    print("Error:", result)