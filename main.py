from helpers import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import pandas as pd

SELECTORS = {
    "cookies":      (By.ID, "didomi-agree-to-all"),
    "price_filter": (By.CSS_SELECTOR, "button[aria-label='Ouvrir le filtre Prix']"),
    "maison":       (By.CSS_SELECTOR, "button[aria-label='Maison']"),
    "appartement":  (By.CSS_SELECTOR, "button[aria-label='Appartement']"),
    "rechercher":   (By.CSS_SELECTOR, "button[aria-label='Rechercher']"),
}

BASE_URL_PARIS = 'https://www.leboncoin.fr/recherche?category=9&locations=Paris__48.86017419624389_2.337177366534126_9370'

driver = setup_driver()
wait = WebDriverWait(driver, timeout=60, poll_frequency=1)

try:
    driver.get('https://www.google.fr/')
    human_delay()
    driver.get('https://www.leboncoin.fr')
    human_delay()
    click(wait, SELECTORS["cookies"])
    driver.get(BASE_URL_PARIS)
    click(wait, SELECTORS["price_filter"])
    click(wait, SELECTORS["maison"])
    click(wait, SELECTORS["appartement"])
    click(wait, SELECTORS["rechercher"])
    human_delay(10, 15)

    rows = []
    page = 1

    while True:
        print(f"\n=== Scraping page {page} ===")
        human_delay(3, 6)

        results = get_listing_urls(driver)

        for i, url in enumerate(results):
            try:
                row = scrape_listing(driver, url)
                rows.append(row)
            except Exception as e:
                print(f"  Failed: {e}")
                rows.append({'url': url})

        df = pd.DataFrame(rows)
        df.to_csv('leboncoin_scraped.csv', index=False)
        print(f"Page {page} done — {len(rows)} total listings saved")

        human_delay(15, 15)

        has_next = go_to_next_page(driver, wait)
        if not has_next:
            break

        page += 1

finally:
    driver.quit()