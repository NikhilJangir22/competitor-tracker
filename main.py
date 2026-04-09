import os
import requests
import json
import google.generativeai as genai

# 1. SETUP & SAFETY CHECK
SCRAPINGBEE_API_KEY = os.environ.get("SCRAPINGBEE_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not SCRAPINGBEE_API_KEY or not GEMINI_API_KEY:
    print("❌ ERROR: Missing API keys in GitHub Secrets!")
    exit(1)

TARGET_ASIN = "B07QXV6N1B"  # Change this to your competitor's ASIN

print(f"🚀 Mission Start: Analyzing {TARGET_ASIN}...")

# 2. FETCH DATA WITH ERROR HANDLING
url = f"https://www.amazon.com/product-reviews/{TARGET_ASIN}"
params = {
    'api_key': SCRAPINGBEE_API_KEY,
    'url': url,
    'premium_proxy': 'true',  # Crucial for Amazon in 2026
    'extract_rules': {
        'reviews': {
            'selector': 'div.review',
            'type': 'list',
            'output': {
                'body': 'span.review-text',
                'rating': 'i.review-rating span'
            }
        }
    }
}

try:
    response = requests.get('https://app.scrapingbee.com/api/v1', params=params, timeout=30)
    response.raise_for_status() # This checks if the website actually loaded
    data = response.json()
except Exception as e:
    print(f"❌ SCRAPING ERROR: {e}")
    if 'response' in locals(): print(f"Response details: {response.text}")
    exit(1)

# Check if we actually got reviews
reviews = data.get('reviews', [])
if not reviews:
    print("⚠️ WARNING: No reviews found. Amazon might have changed their layout.")
    # We create a dummy report so the workflow doesn't fail completely
    with open("report.md", "w") as f: f.write("# Report Failed\nAmazon blocked the scrape or no reviews were found.")
    exit(0) 

print(f"✅ Secured {len(reviews)} reviews. Consulting AI...")

# 3. AI ANALYSIS WITH ERROR HANDLING
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"Analyze these Amazon reviews and give me a 3-point strategy report: {json.dumps(reviews)}"
    ai_response = model.generate_content(prompt)
    
    with open("report.md", "w") as file:
        file.write(ai_response.text)
    print("🎯 Mission Accomplished! Report saved.")

except Exception as e:
    print(f"❌ AI ERROR: {e}")
    exit(1)
