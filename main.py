import os
import requests
import json
import google.generativeai as genai

# Pull your secret keys from the GitHub vault
SCRAPINGBEE_API_KEY = os.environ.get("SCRAPINGBEE_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Choose a competitor to track (Example: Anker Power Bank ASIN)
TARGET_ASIN = "B07QXV6N1B" # <-- Change this to your competitor's ASIN

print(f"Starting mission: Fetching reviews for {TARGET_ASIN}...")

# 1. Fetch data through ScrapingBee
url = f"https://www.amazon.com/product-reviews/{TARGET_ASIN}"
params = {
    'api_key': SCRAPINGBEE_API_KEY,
    'url': url,
    'extract_rules': '{"reviews": {"selector": "div.review", "type": "list", "output": {"body": "span.review-text", "rating": "i.review-rating span"}}}'
}
response = requests.get('https://app.scrapingbee.com/api/v1', params=params)
reviews_data = response.json()

print("Data secured! Sending to Gemini for analysis...")

# 2. AI Analysis
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

prompt = f"""
You are an expert product strategist. Analyze these recent Amazon reviews: {json.dumps(reviews_data)}

Write a concise Intelligence Report formatted in Markdown. Include:
1. **The Biggest Failure:** What is breaking or frustrating users?
2. **The Hidden Gem:** What is a feature users love that we should copy?
3. **Actionable Advice:** Give me one marketing hook to steal these customers.
"""
ai_response = model.generate_content(prompt)

# 3. Save the report
with open("report.md", "w") as file:
    file.write(ai_response.text)

print("Mission accomplished! Report saved.")
