import os
import requests
import json
from google import genai

# 1. SETUP
SCRAPINGBEE_API_KEY = os.environ.get("SCRAPINGBEE_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# If B07QXV6N1B keeps 404ing, try a newer one like B0D1Y7F6Y8 (Anker 737)
TARGET_ASIN = "B07QXV6N1B" 

print(f"🚀 Mission Start: Analyzing {TARGET_ASIN}...")

# 2. THE FIX: Robust Selectors & URL Parameters
rules = {
    "reviews": {
        "selector": "div[data-hook='review']", # More stable than 'div.review'
        "type": "list",
        "output": {
            "body": "span[data-hook='review-body']",
            "rating": "i[data-hook='review-star-rating'] span"
        }
    }
}

params = {
    'api_key': SCRAPINGBEE_API_KEY,
    'url': f"https://www.amazon.in/product-reviews/{TARGET_ASIN}/", # Note the .in
    'render_js': 'true',
    'stealth_proxy': 'true',
    'country_code': 'in', # This tells ScrapingBee to use an Indian IP
    'wait_for': "div[data-hook='review']",
    'extract_rules': json.dumps(rules)
}

try:
    response = requests.get('https://app.scrapingbee.com/api/v1', params=params, timeout=30)
    
    # If it's a 404, don't crash, just tell us why
    if response.status_code == 404:
        print(f"⚠️ Amazon returned 404. The ASIN {TARGET_ASIN} might be inactive or regional.")
        exit(0)
        
    response.raise_for_status()
    data = response.json()
except Exception as e:
    print(f"❌ SCRAPING ERROR: {e}")
    if 'response' in locals(): print(f"Details: {response.text}")
    exit(1)

reviews = data.get('reviews', [])
if not reviews:
    print("⚠️ No reviews found. The page loaded but no data matched our selectors.")
    exit(0)

print(f"✅ Secured {len(reviews)} reviews. Consulting AI...")

# 3. AI ANALYSIS
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"Summarize these reviews into a 3-point competitor battlecard: {json.dumps(reviews)}"
    
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
