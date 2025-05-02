from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def scrape_service_details():
    url = "https://www.urbancompany.com/mumbai-plumber"
    results = []

    options = Options()
    options.add_argument("--headless=new")  # Optional: remove for debugging
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    driver.get(url)
    time.sleep(5)

    # Grab all service cards with “View details”
    cards = driver.find_elements(
        By.CSS_SELECTOR, "div[data-testid='service-card']")

    print(f"Found {len(cards)} cards")

    for index in range(len(cards)):
        try:
            # Re-select cards every loop (DOM may change)
            cards = driver.find_elements(
                By.CSS_SELECTOR, "div[data-testid='service-card']")
            card = cards[index]

            # Extract main service name
            title_elem = card.find_element(By.TAG_NAME, "h3")
            main_service_title = title_elem.text if title_elem else f"Service #{index+1}"

            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView(true);", card)
            time.sleep(1)

            # Click "View details"
            view_details = card.find_element(
                By.PARTIAL_LINK_TEXT, "View details")
            view_details.click()

            # Wait for modal to appear
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'css-1n2mv2k')]")))

            # Get all sub-services in modal
            sub_items = driver.find_elements(
                By.XPATH, "//div[@role='button']//ancestor::div[contains(@class,'r-1udh08x')]")

            for sub in sub_items:
                try:
                    name = sub.find_element(
                        By.XPATH, ".//div[contains(@class, 'css-1m1f8hn')]").text
                    price = sub.find_element(
                        By.XPATH, ".//span[contains(text(), '₹')]").text
                    description = sub.find_element(
                        By.XPATH, ".//div[contains(@class, 'css-1dbjc4n')]").text
                    results.append({
                        "main_service": main_service_title,
                        "sub_service": name,
                        "price": price,
                        "description": description
                    })
                except:
                    continue

            # Close modal
            close_btn = driver.find_element(
                By.XPATH, "//div[@role='dialog']//div[@aria-label='Close']")
            close_btn.click()
            time.sleep(2)

        except Exception as e:
            print(f"[!] Error at card {index}: {e}")
            continue

    driver.quit()
    return results
