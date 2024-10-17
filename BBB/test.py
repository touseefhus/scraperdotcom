from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Set up Selenium
options = Options()
options.headless = True  # Run in headless mode for no UI

# Use ChromeDriverManager to manage the ChromeDriver installation
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Function to scrape data from each company profile page
def scrape_company_data(url):
    driver.get(url)
    time.sleep(2)  # Wait for the page to load
    
    # Extract phone numbers
    phone_numbers = set()
    try:
        phone_elements = driver.find_elements(By.CLASS_NAME, 'dtm-phone')
        for phone in phone_elements:
            phone_numbers.add(phone.text.strip())
    except Exception as e:
        print(f"Error extracting phone numbers: {e}")
    
    # Extract addresses
    addresses = set()
    try:
        address_elements = driver.find_elements(By.TAG_NAME, 'address')  # Find all <address> tags
        for address in address_elements:
            p_tags = address.find_elements(By.CLASS_NAME, 'bds-body')  # Look for <p> with class 'bds-body'
            for p in p_tags:
                addresses.add(p.text.strip())
    except Exception as e:
        print(f"Error extracting addresses: {e}")

    # Extract website links
    website_links = set()
    try:
        link_elements = driver.find_elements(By.CLASS_NAME, 'dtm-url')
        for link in link_elements:
            href = link.get_attribute('href')
            if 'http' in href:
                website_links.add(href)
    except Exception as e:
        print(f"Error extracting website links: {e}")

    return {
        'Phone Numbers': list(phone_numbers),
        'Addresses': list(addresses),
        'Website Links': list(website_links)
    }

# Function to scrape links from the search results page
def scrape_data(initial_url):
    driver.get(initial_url)
    time.sleep(3)  # Wait for the page to load

    # Extract all company profile links
    links = driver.find_elements(By.CSS_SELECTOR, 'a.text-blue-medium')
    company_urls = [link.get_attribute('href') for link in links]

    # Now visit each company page and extract data
    all_data = []
    for url in company_urls:
        print(f"Scraping data from: {url}")
        data = scrape_company_data(url)
        all_data.append(data)
        time.sleep(2)  # Wait before visiting the next page

    return all_data

# Function to save scraped data to an Excel file
def save_to_excel(data, file_name='scraped_data.xlsx'):
    df = pd.DataFrame(data)
    df.to_excel(file_name, index=False)
    print(f"Data has been saved to {file_name}")

# Main function
def main():
    initial_url = 'https://www.bbb.org/search?find_country=USA&find_entity=60429-200&find_id=2748_7500-1300&find_text=Health%20and%20Wellness&find_type=Category&page=1'
    data = scrape_data(initial_url)
    save_to_excel(data)

if __name__ == "__main__":
    main()
    driver.quit()  # Close the driver after scraping
