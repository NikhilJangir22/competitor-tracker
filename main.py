import os
import requests
import json
from google import genai

# 1. SETUP
SCRAPINGBEE_API_KEY = os.environ.get("SCRAPINGBEE_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TARGET_ASIN = "B07QXV6N1B" 

def save_report(content):
    """Ensures a report file is ALWAYS created for GitHub to find."""
    with open("report.md", "w") as f:
        f.write(content)

# 2. UPDATED 2026 SELECTORS
# Amazon changed how review text is tagged in early 2026
rules = {
    "reviews": {
        "selector": "div[data-hook='review']",
        "type": "list",
        "output": {
            "body": "span[data-hook='review-body']",
            "rating": "i[data-hook='review-star-rating'] span"
        }
    }
}

params = {
    'api_key': SCRAPINGBEE_API_KEY,
    'url': f"https://www.amazon.com/product-reviews/{TARGET_ASIN}/",
    'render_js': 'true',
    'stealth_proxy': 'true',
    'country_code': 'us',
    'wait_for': "div[data-hook='review']", 
    'extract_rules': json.dumps(rules)
}

print(f"🚀 Mission Start: Analyzing {TARGET_ASIN}...")

try:
    # Increased timeout to 120s for India-to-US Stealth routing
    response = requests.get('https://app.scrapingbee.com/api/v1', params=params, timeout=120)
    
    if response.status_code != 200:
        save_report(f"# Error\nAmazon blocked the request (Status {response.status_code}). Try running again in 10 minutes.")
        print(f"❌ Scraping Error: {response.status_code}")
        exit(0) # Exit gracefully so GitHub can still upload the error report

    data = response.json()
    reviews = data.get('reviews', [])

    if not reviews:
        save_report("# Warning\nConnection successful, but Amazon returned 0 reviews. This ASIN might have no reviews or is a variation that Amazon recently 'separated'.")
        print("⚠️ No reviews found.")
        exit(0)

    # 3. AI ANALYSIS
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"Summarize these reviews into a 3-point competitor battlecard: {json.dumps(reviews)}"
    
    ai_response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
    save_report(ai_response.text)
    print("🎯 Mission Accomplished!")

except Exception as e:
    save_report(f"# Technical Failure\nAn error occurred: {str(e)}")
    print(f"❌ System Error: {e}")
