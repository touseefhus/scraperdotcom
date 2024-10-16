from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Set up Selenium
options = Options()
options.headless = True  # Run in headless mode for no UI

# Use ChromeDriverManager to manage the ChromeDriver installation
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

def scrape_data(url):
    driver.get(url)
    time.sleep(3)  # Wait for the page to load

    # Extract data
    phone_numbers = []
    addresses = []
    website_links = []

    # Find anchor tags with class name 'text-blue-medium'
    links = driver.find_elements(By.CSS_SELECTOR, 'a.text-blue-medium')
    for link in links:
        link_url = link.get_attribute('href')
        driver.get(link_url)
        time.sleep(3)  # Wait for the new page to load
        
        # Extract phone numbers, addresses, and website links on the new page
        phone_elements = driver.find_elements(By.CLASS_NAME, 'dtm-phone')
        for phone in phone_elements:
            phone_numbers.append(phone.text)

        address_elements = driver.find_elements(By.CLASS_NAME, 'bds-body')
        for address in address_elements:
            addresses.append(address.text)

        link_elements = driver.find_elements(By.CLASS_NAME, 'dtm-url')
        for link in link_elements:
            href = link.get_attribute('href')
            if href:
                website_links.append(href)

        # driver.back()  # Go back to the previous page
        time.sleep(3)  # Wait for the previous page to load again

    return {
        'Phone Numbers': phone_numbers,
        'Addresses': addresses,
        'Website Links': website_links
    }

def save_to_excel(data, file_name='scraped_data.xlsx'):
    df = pd.DataFrame(data)
    df.to_excel(file_name, index=False)
    print(f"Data has been saved to {file_name}")

def main():
    initial_url = 'https://www.bbb.org/search?filter_type=Business&find_country=USA&find_entity=60429-200&find_id=2748_7500-1300&find_text=Health%20and%20Wellness&find_type=Category&page=1&touched=1'
    data = scrape_data(initial_url)
    save_to_excel(data)

if __name__ == "__main__":
    main()
    driver.quit()  # Close the driver after scraping
