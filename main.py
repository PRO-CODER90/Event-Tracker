import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from datetime import datetime
import time

# --- CONFIGURATION ---
SHEET_NAME = "My Event Tracker"  # Must match your Google Sheet name exactly
CITY = "mumbai"                 # e.g., mumbai, bengaluru, delhi-ncr

def get_bms_data(city):
    options = Options()
    # options.add_argument("--headless") # Commented out so you can see it working. Uncomment later for silent mode.
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Stealth settings to act like a real browser
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    url = f"https://in.bookmyshow.com/explore/events-{city}"
    print(f"Opening URL: {url}")
    driver.get(url)
    
    # Allow extra time for the page and dynamic elements to load
    time.sleep(8) 

    # Scroll down twice to trigger lazy loading of event cards
    driver.execute_script("window.scrollTo(0, 1000);")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, 2000);")
    time.sleep(2)

    events = []
    # Targeted search for anchor tags that lead to event details
    cards = driver.find_elements(By.XPATH, "//a[contains(@href, '/events/')]")
    
    print(f"Found {len(cards)} potential event cards. Extracting details...")

    for card in cards:
        try:
            # BMS layout: The name is usually inside the first few div layers of the card
            # We use a relative path to find the text inside the card link
            raw_text = card.text.split('\n')
            if len(raw_text) < 2: continue # Skip if it's an empty card
            
            title = raw_text[0]
            link = card.get_attribute("href")
            
            # Extract basic category or date info if available in text
            category = "Event"
            if len(raw_text) > 1:
                category = raw_text[1]

            # Prevent duplicate entries in the same scrape run
            if not any(e['URL'] == link for e in events):
                events.append({
                    "Event ID": link.split('/')[-2], # Extracts ID from URL
                    "Name": title,
                    "Category": category,
                    "City": city.capitalize(),
                    "URL": link,
                    "Status": "Active",
                    "Last Updated": datetime.now().strftime("%Y-%m-%d")
                })
        except Exception as e:
            continue

    driver.quit()
    return pd.DataFrame(events)

def update_google_sheet(df):
    if df.empty:
        print("No events scraped. Sheet will not be updated.")
        return

    # Authenticate
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    
    try:
        sheet = client.open(SHEET_NAME).sheet1
    except Exception as e:
        print(f"Error: Could not find sheet '{SHEET_NAME}'. Check the name and sharing permissions.")
        return

    # Get existing data
    existing_records = sheet.get_all_records()
    existing_data = pd.DataFrame(existing_records)
    
    if existing_data.empty:
        # First time setup: Add headers and all data
        # Note: update() requires a specific format in newer gspread versions
        data_to_upload = [df.columns.values.tolist()] + df.values.tolist()
        sheet.update('A1', data_to_upload)
        print(f"Initial setup complete. Added {len(df)} events.")
    else:
        # Merge logic: Append only if URL/ID is not in the sheet
        existing_urls = existing_data['URL'].astype(str).tolist()
        new_rows = []
        
        for _, row in df.iterrows():
            if str(row['URL']) not in existing_urls:
                new_rows.append(row.values.tolist())
        
        if new_rows:
            sheet.append_rows(new_rows)
            print(f"Added {len(new_rows)} new events.")
        else:
            print("Everything is up to date. No new events found.")

# --- RUN ---
if __name__ == "__main__":
    print("Step 1: Starting Scraper...")
    scraped_df = get_bms_data(CITY)
    
    print(f"Step 2: Scraper found {len(scraped_df)} events.")
    
    print("Step 3: Syncing with Google Sheets...")
    update_google_sheet(scraped_df)
    
    print("Process Finished!")
