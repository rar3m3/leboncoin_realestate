import time
import random
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

BASE_URL = 'https://www.leboncoin.fr'

#human_delay to simulate a human browsing (scraping detection)
def human_delay(min_sec=2, max_sec=5):
    time.sleep(random.uniform(min_sec, max_sec))

#human_scroll to simulate a human scrollin (scraping detection)
def human_scroll(driver):
    scroll_steps = random.randint(3, 6)
    for i in range(scroll_steps):
        scroll_amount = random.randint(300, 700)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.uniform(0.5, 1.5))
    driver.execute_script("window.scrollBy(0, -300);")
    time.sleep(random.uniform(0.5, 1.0))
sudo apt install touchegg
#click element
def click(wait, selector):
    wait.until(ec.element_to_be_clickable(selector)).click()
    human_delay()

#selenium driver
def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument("--lang=fr-FR")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-popup-blocking")
    driver = uc.Chrome(options=options, version_main=148)
    driver.maximize_window()
    driver.delete_all_cookies()
    return driver

#get urls of listing on leboncoin page
def get_listing_urls(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    listing_column = soup.find('ul', attrs={'data-test-id': 'listing-column'})
    links = listing_column.select('a[href*="/ad/"]')
    urls = list(dict.fromkeys([link.get('href') for link in links]))
    return urls

#open each url previously, scrape data on page
def scrape_listing(driver, url):
    driver.execute_script(f"window.open('{BASE_URL + url}', '_blank');")
    human_delay()
    driver.switch_to.window(driver.window_handles[-1])
    human_delay(3, 6)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    row = {'url': url}

    price_tag = soup.find('p', class_='text-display-3')
    if price_tag:
        cleaned = ''.join(c for c in price_tag.text if c.isdecimal())
        row['price'] = int(cleaned) if cleaned else None
    else:
        row['price'] = None

    criteria_tag = soup.find(attrs={'data-test-id': 'adview-top-criteria-atttributes'})
    if criteria_tag:
        sr_text = criteria_tag.find('span', class_='sr-only')
        if sr_text:
            parts = [p.strip() for p in sr_text.text.split(',')]
            row['rooms']   = int(''.join(c for c in parts[0] if c.isdecimal())) if len(parts) > 0 else None
            row['surface'] = int(''.join(c for c in parts[1] if c.isdecimal())) if len(parts) > 1 else None

    location_tag = soup.find('a', attrs={'aria-label': lambda x: x and 'Paris' in x})
    if location_tag:
        aria = location_tag.get('aria-label', '')
        parts = [p.strip() for p in aria.split(',')]
        row['postcode'] = parts[0].replace('Paris ', '').strip() if parts else None
        row['quartier'] = parts[1].replace('Quartier ', '').strip() if len(parts) > 1 else None

    title_tag = soup.find(attrs={'data-qa-id': 'adview_title'})
    row['title'] = title_tag.text.strip() if title_tag else None

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    human_delay(1, 2)

    return row

#to to next page
def go_to_next_page(driver, wait):
    try:
        human_scroll(driver)
        next_button = wait.until(ec.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[aria-label='Page suivante']")
        ))
        next_button.click()
        human_delay(4, 8)
        return True
    except:
        print("No next page found — stopping")
        return False