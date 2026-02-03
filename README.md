**BookMyShow Events Tracker**
A Python automation tool that scrapes live event listings from BookMyShow for a given city and syncs them automatically to Google Sheets.
Ideal for event tracking, monitoring new listings, or building city-wise event dashboards.

🚀 Features

1. 🔍 Scrapes live event data from BookMyShow
2. 🌆 City-specific tracking (Mumbai, Bengaluru, Delhi-NCR, etc.)
3. 📊 Auto-syncs results to Google Sheets
4. 🆕 Appends only new events (no duplicates)
5. 🕵️ Uses browser stealth techniques to reduce bot detection
6. 🧩 Modular & easy to extend

**Tech Stack**
* Python 3
* Libraries
1. Selenium – browser automation
2. selenium-stealth – avoid detection
3. pandas – data processing
4. gspread – Google Sheets API
5. Google Service Account authentication
6. ChromeDriver (auto-managed)

**Project Structure**
.
├── main.py              # Main scraper + Google Sheets sync logic
├── credentials.json     # Google service account credentials
└── README.md

**Install dependencies**
pip install gspread pandas oauth2client selenium selenium-stealth webdriver-manager
