def run_workflow():
    session = requests.Session()
    try:
        print("📡 Requesting data from Amazon US via Stealth Tunnel...")
        response = session.get(
            'https://app.scrapingbee.com/api/v1', 
            params=params, 
            timeout=120 
        )
        
        if response.status_code == 200:
            data = response.json()
            reviews = data.get('reviews', [])
            
            if not reviews:
                print("⚠️ No reviews found in the data.")
                # FIX: Create the file even if empty so GitHub doesn't error out
                with open("report.md", "w") as f:
                    f.write("# Observation\nAmazon blocked the view or no reviews exist for this ASIN today.")
                return

            print(f"✅ Success! Captured {len(reviews)} reviews.")
            analyze_with_ai(reviews)
            
        else:
            # FIX: Even on error, create a report file with the error details
            with open("report.md", "w") as f:
                f.write(f"# Error\nScraper returned status: {response.status_code}")
            print(f"❌ Scraping Error: {response.status_code}")

    except Exception as e:
        with open("report.md", "w") as f:
            f.write(f"# Connection Failure\nDetails: {str(e)}")
        print(f"❌ Connection Failed: {str(e)}")
