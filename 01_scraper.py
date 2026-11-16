"""
====================================================================
 GenData Project - Nairobi Rental Market Intelligence System
 FILE 1: Python Scraper + Fallback Data Loader
====================================================================
 WHAT THIS DOES:
  1. Tries to scrape Property24 Kenya for Nairobi apartment listings
  2. If scraping is blocked (common), it AUTOMATICALLY creates a
     realistic sample dataset so your project NEVER fails tomorrow
  3. Saves everything to listings.csvpip
  4. Loads the CSV into MySQL (if MySQL is set up)

 HOW TO RUN (see STEP-BY-STEP guide for where to click):
  - Double-click run_scraper.bat  OR
  - In VS Code: press Ctrl + ` then type:  python 01_scraper.py  then press Enter

 REQUIREMENTS:
  pip install requests beautifulsoup4 pandas mysql-connector-python
====================================================================
"""

import csv
import random
import sys
from datetime import date, timedelta

# ------------------------------------------------------------------
# CONFIG - Change these if needed
# ------------------------------------------------------------------
OUTPUT_CSV = "listings.csv"
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"          # <-- CHANGE THIS to your MySQL password
MYSQL_DATABASE = "nairobi_rentals"
LOAD_TO_MYSQL = True             # Set False if you only want the CSV

# ------------------------------------------------------------------
# PART 1: Try to scrape Property24 (best effort)
# ------------------------------------------------------------------
def try_scrape_property24():
    """Attempt to scrape Property24. Returns list of dicts or empty list."""
    print("\n[1/3] Trying to scrape Property24 Kenya...")
    try:
        import requests
        from bs4 import BeautifulSoup

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0 Safari/537.36"
        }
        url = "https://www.property24.co.ke/property-for-sale-in-nairobi-kenya"
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        listings = []
        # Property24 cards - selector may change, so we try a few
        cards = soup.select(".p24_propertyCard") or soup.select("[data-testid='property-card']")
        for card in cards[:30]:
            title_el = card.select_one(".p24_propertyCardHeading") or card.select_one("h2")
            price_el = card.select_one(".p24_propertyCardPrice") or card.select_one(".price")
            title = title_el.get_text(strip=True) if title_el else "Apartment in Nairobi"
            price_text = price_el.get_text(strip=True) if price_el else ""
            price = int("".join(ch for ch in price_text if ch.isdigit()) or 0)
            if price > 0:
                listings.append({
                    "title": title,
                    "estate_name": "Nairobi",
                    "property_type": "Apartment",
                    "bedrooms": 2,
                    "bathrooms": 2,
                    "size_sqm": 90,
                    "price_kes": price,
                    "listing_url": url,
                    "scraped_date": str(date.today()),
                })
        if listings:
            print(f"      SUCCESS: Scraped {len(listings)} listings from Property24")
            return listings
        print("      Property24 returned no usable listings (site may have changed). Using fallback data...")
        return []
    except Exception as e:
        print(f"      Property24 scrape blocked/failed ({e}). Using fallback data...")
        return []

# ------------------------------------------------------------------
# PART 2: Fallback realistic Nairobi dataset (GUARANTEED to work)
# ------------------------------------------------------------------
def generate_fallback_data(n=120):
    """Creates realistic Nairobi rental data so you can present tomorrow."""
    print("\n[2/3] Generating realistic fallback Nairobi dataset...")
    estates = [
        # estate, county, base price for 1-bed, multiplier
        ("Kilimani", "Nairobi", 45000, 1.0),
        ("Kileleshwa", "Nairobi", 55000, 1.1),
        ("Westlands", "Nairobi", 60000, 1.2),
        ("Upperhill", "Nairobi", 50000, 1.0),
        ("Lavington", "Nairobi", 70000, 1.3),
        ("South B", "Nairobi", 35000, 0.8),
        ("Eastleigh", "Nairobi", 28000, 0.7),
        ("Ruaka", "Kiambu", 25000, 0.6),
        ("Kahawa West", "Nairobi", 22000, 0.55),
        ("Ruaraka", "Nairobi", 30000, 0.7),
        ("Kasarani", "Nairobi", 32000, 0.75),
        ("Embakasi", "Nairobi", 26000, 0.65),
        ("Syokimau", "Machakos", 24000, 0.6),
        ("Thika Road", "Kiambu", 28000, 0.65),
        ("Ngong Road", "Nairobi", 38000, 0.85),
    ]
    types = ["Apartment", "Flat", "Townhouse", "Bungalow", "Studio"]
    agents = ["Pamela Properties", "HassConsult", "Knight Frank KE", "Private Landlord", "Rentals.co.ke"]
    listings = []
    today = date.today()

    for i in range(n):
        estate, county, base, mult = random.choice(estates)
        bedrooms = random.choice([1, 1, 2, 2, 2, 3, 3, 4])
        bathrooms = max(1, bedrooms - random.choice([0, 1]))
        ptype = random.choice(types)
        size = 45 + bedrooms * 30 + random.randint(-10, 25)
        # Price: base * bedrooms factor * random variation
        price = int(base * (0.7 + bedrooms * 0.35) * mult * random.uniform(0.85, 1.25) / 100) * 100
        days_ago = random.randint(0, 60)
        listings.append({
            "title": f"{bedrooms} Bed {ptype} in {estate}",
            "estate_name": estate,
            "county": county,
            "property_type": ptype,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "size_sqm": size,
            "price_kes": price,
            "agent_name": random.choice(agents),
            "listing_url": f"https://www.property24.co.ke/sample-listing-{i+1}",
            "scraped_date": str(today - timedelta(days=days_ago)),
        })
    print(f"      Generated {len(listings)} listings across {len(estates)} estates")
    return listings

# ------------------------------------------------------------------
# PART 3: Save to CSV
# ------------------------------------------------------------------
def save_to_csv(listings, path):
    print(f"\n[3/3] Saving {len(listings)} listings to {path} ...")
    fields = ["title", "estate_name", "county", "property_type", "bedrooms",
              "bathrooms", "size_sqm", "price_kes", "agent_name",
              "listing_url", "scraped_date"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in listings:
            writer.writerow({k: row.get(k, "") for k in fields})
    print(f"      DONE. Open {path} to check your data.")

# ------------------------------------------------------------------
# PART 4: Load CSV into MySQL (optional)
# ------------------------------------------------------------------
def load_to_mysql(path):
    print("\n[MySQL] Loading CSV into MySQL...")
    try:
        import mysql.connector
    except ImportError:
        print("      mysql-connector not installed. Skipping MySQL load.")
        print("      Run:  pip install mysql-connector-python")
        return

    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST, user=MYSQL_USER,
            password=MYSQL_PASSWORD, database=MYSQL_DATABASE)
        cursor = conn.cursor()
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        # Clear old data
        cursor.execute("DELETE FROM properties")
        cursor.execute("DELETE FROM locations")
        cursor.execute("DELETE FROM agents")
        conn.commit()

        location_ids = {}
        agent_ids = {}
        for r in rows:
            estate = r["estate_name"]
            if estate not in location_ids:
                cursor.execute(
                    "INSERT INTO locations (estate_name, county) VALUES (%s, %s)",
                    (estate, r.get("county", "Nairobi")))
                location_ids[estate] = cursor.lastrowid
            agent = r.get("agent_name", "Private Landlord")
            if agent not in agent_ids:
                cursor.execute(
                    "INSERT INTO agents (agent_name) VALUES (%s)", (agent,))
                agent_ids[agent] = cursor.lastrowid
            cursor.execute(
                """INSERT INTO properties
                   (title, location_id, agent_id, property_type, bedrooms,
                    bathrooms, size_sqm, price_kes, listing_url, scraped_date)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (r["title"], location_ids[estate], agent_ids[agent],
                 r["property_type"], int(r["bedrooms"]), int(r["bathrooms"]),
                 int(r["size_sqm"]), int(r["price_kes"]),
                 r["listing_url"], r["scraped_date"]))
        conn.commit()
        print(f"      SUCCESS: Loaded {len(rows)} rows into MySQL database '{MYSQL_DATABASE}'")
        cursor.close(); conn.close()
    except Exception as e:
        print(f"      MySQL load failed: {e}")
        print("      -> Make sure MySQL is running and you ran 02_mysql_database.sql FIRST.")
        print("      -> Check MYSQL_PASSWORD at the top of this file.")

# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print(" Nairobi Rental Market Intelligence - Data Pipeline")
    print("=" * 60)
    listings = try_scrape_property24()
    if not listings:
        listings = generate_fallback_data()
    save_to_csv(listings, OUTPUT_CSV)
    if LOAD_TO_MYSQL:
        load_to_mysql(OUTPUT_CSV)
    print("\n" + "=" * 60)
    print(" ALL DONE! Next steps:")
    print("  1. Open listings.csv to see your data")
    print("  2. Open MySQL Workbench and run the queries in 02_mysql_database.sql")
    print("  3. Follow 00_START_HERE_STEP_BY_STEP.md for Excel + Tableau")
    print("=" * 60)
    input("\nPress Enter to close...")
