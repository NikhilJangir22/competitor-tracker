def run_workflow():
    # Use a 'Session' to keep the connection stable
    session = requests.Session()
    
    try:
        print("📡 Requesting data from Amazon US via Stealth Tunnel...")
        print("⏳ Note: Stealth mode can take up to 90 seconds. Please wait...")
        
        # INCREASED TIMEOUT: From 60 to 120 seconds
        response = session.get(
            'https://app.scrapingbee.com/api/v1', 
            params=params, 
            timeout=120 
        )
        
        if response.status_code == 200:
            data = response.json()
            reviews = data.get('reviews', [])
            
            if not reviews:
                print("⚠️ Connection successful, but no reviews were found by the selectors.")
                # We save a note so the workflow still "succeeds" but tells you it was empty
                with open("report.md", "w") as f: f.write("No reviews found. Amazon may have a CAPTCHA.")
                return

            print(f"✅ Success! Captured {len(reviews)} reviews.")
            analyze_with_ai(reviews)
            
        elif response.status_code == 401:
            print("❌ ERROR: Your ScrapingBee API Key is invalid or expired.")
        elif response.status_code == 429:
            print("❌ ERROR: You have run out of ScrapingBee credits!")
        else:
            print(f"❌ Scraping Error: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.Timeout:
        print("❌ TIMEOUT ERROR: The connection took too long. Amazon's wall is very thick today.")
        print("Try running the workflow again in 10 minutes.")
    except Exception as e:
        print(f"❌ Connection Failed: {str(e)}")
