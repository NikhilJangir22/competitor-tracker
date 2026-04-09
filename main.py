import os
import requests
import json
from google import genai # Updated to the 2026 library

# 1. SETUP
SCRAPINGBEE_API_KEY = os.environ.get("SCRAPINGBEE_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

TARGET_ASIN = "B07QXV6N1B" 

print(f"🚀 Mission Start: Analyzing {TARGET_ASIN}...")

# 2. THE FIX: Correctly formatting extraction rules
# We put the rules in a dictionary first...
rules = {
    "reviews": {
        "selector": "div.review",
        "type": "list",
        "output": {
            "body": "span.review-text",
            "rating": "i.review-rating span"
        }
    }
}

# ...then we turn it into a JSON string so ScrapingBee understands it.
params = {
    'api_key': SCRAPINGBEE_API_KEY,
    'url': f"https://www.amazon.com/product-reviews/{TARGET_ASIN}",
    'premium_proxy': 'true',
    'extract_rules': json.dumps(rules) # <--- THIS IS THE FIX
}

try:
    response = requests.get('https://app.scrapingbee.com/api/v1', params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
except Exception as e:
    print(f"❌ SCRAPING ERROR: {e}")
    if 'response' in locals(): print(f"Details: {response.text}")
    exit(1)

reviews = data.get('reviews', [])
if not reviews:
    print("⚠️ No reviews found. Check if the ASIN is correct or if Amazon changed layout.")
    exit(0)

print(f"✅ Secured {len(reviews)} reviews. Consulting AI...")

# 3. MODERN AI ANALYSIS (Using the new google-genai)
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"Analyze these Amazon reviews and give me a 3-point strategy report: {json.dumps(reviews)}"
    
    # New 2026 syntax for generating content
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    
    with open("report.md", "w") as file:
        file.write(response.text)
    print("🎯 Mission Accomplished! Report saved.")

except Exception as e:
    print(f"❌ AI ERROR: {e}")
    exit(1)
