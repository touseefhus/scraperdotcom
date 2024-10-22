from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import re

# Set up Selenium for headless browsing
options = Options()
options.headless = True

# Use ChromeDriverManager to manage the ChromeDriver installation
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Function to scrape data from a single page and return the company profile links
def get_company_links(page_url):
    driver.get(page_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.text-blue-medium')))

    # Extract all company profile links
    links = driver.find_elements(By.CSS_SELECTOR, 'a.text-blue-medium')
    company_urls = [link.get_attribute('href') for link in links]

    return company_urls

# Function to extract contact numbers, addresses, and websites from a company profile URL
def scrape_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Retry mechanism
    retries = 3
    wait_time = 5
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=1000)
            if response.status_code == 200:
                print(f"Successfully fetched content from {url}")
               
                return response.content
            else:
                print(f"Error: Status code {response.status_code} for {url}, retrying...")
                time.sleep(wait_time)
        except requests.exceptions.RequestException as e:
            print(f"Exception for {url}: {e}, retrying...")
            time.sleep(wait_time)
    
    print(f"Failed to retrieve the webpage after retries: {url}")
    return None

# Parse address components (Street, City, State, Zip)
def parse_address_components(address_text):
    # Updated pattern to capture 5 digits and optional 4-digit extension for the zip code
    pattern = r'(?P<street>[\d\w\s]+),?\s*(?P<city>[\w\s]+),?\s*(?P<state>[A-Z]{2})?\s*(?P<zip>\d{5}(?:-\d{4})?)?'
    match = re.search(pattern, address_text)
    if match:
        return match.groupdict()
    return {'street': '', 'city': '', 'state': '', 'zip': ''}


# Parse data from a company profile page
def parse_data(content):
    soup = BeautifulSoup(content, 'html.parser')

    # Extract phone numbers
    phone_numbers = set()
    phone_elements = soup.find_all('a', class_='dtm-phone')
    for phone in phone_elements:
        phone_numbers.add(phone.get_text(strip=True))
    
    # Extract addresses using <address> tag and handle the <p> structure inside it
    addresses = []
    address_elements = soup.find_all('address')
    for address in address_elements:
        p_tags = address.find_all('p', class_='bds-body')
        if len(p_tags) == 2:
            street = p_tags[0].get_text(strip=True)
            city_state_zip = p_tags[1].get_text(strip=True)
            structured_address = parse_address_components(f"{street}, {city_state_zip}")
            addresses.append(structured_address)

    # Extract business name
    business_name = None
    business_name_element = soup.find('span', class_='bds-h2 font-normal text-black', translate='no')
    if business_name_element:
        business_name = business_name_element.get_text(strip=True)

    # Extract website links
    links = set()
    link_elements = soup.find_all('a', class_='dtm-url', href=True)
    for link in link_elements:
        href = link['href']
        if 'http' in href:
            links.add(href)
    
    return {
        'Phone Number': list(phone_numbers),
        'Addresses': addresses,
        'Website Links': list(links),
        'Business Name': business_name  # Correctly capturing the business name
    }



# Function to scrape multiple websites
def scrape_multiple_websites(urls):
    all_data = []

    for url in urls:
        content = scrape_data(url)
        if content:
            data = parse_data(content)
            all_data.append(data)
    
    return all_data

# Function to save scraped data into an Excel file
def save_to_excel(data):
    rows = []
    
    for entry in data:
        phone_numbers = ', '.join(entry['Phone Numbers'])
        websites = ', '.join(entry['Website Links'])

        for addr in entry['Addresses']:
            rows.append({
                'Phone Numbers': phone_numbers,
                'Street': addr['street'],
                'City': addr['city'],
                'State': addr['state'],
                'Zip Code': addr['zip'],
                'Website Links': websites,
                'Business Name': entry['Business Name']
            })
    
    df = pd.DataFrame(rows)
    output_path = 'data.xlsx'
    df.to_excel(output_path, index=False)
    print(f"Data saved to {output_path}")

# here we will the all pages from pagination
def scrape_all_pages(base_url, total_pages):
    all_data = []

    # Loop for all pages
    for page_num in range(1, total_pages + 1):
        page_url = f"{base_url}&page={page_num}"
        print(f"Scraping page: {page_num} - URL: {page_url}")

        # Scrape the company profile links from the current page
        company_urls = get_company_links(page_url)
        
        # Scrape the data from each company profile page
        page_data = scrape_multiple_websites(company_urls)
        all_data.extend(page_data)

    return all_data

# Main function to scrape data and save to Excel
def main():
    base_url = 'https://www.bbb.org/search?filter_type=Business&find_country=USA&find_entity=60429-200&find_id=2748_7500-1300&find_text=Health%20and%20Wellness&find_type=Category&page=1&sort=Relevance'
    total_pages = 15  # All pages
    
    # Step 1: Scrape all pages
    all_data = scrape_all_pages(base_url, total_pages)
    data = all_data
    # Step 2: Save the aggregated data to Excel
    save_to_excel(all_data)

# Execute the main function
if __name__ == "__main__":
    main()
    driver.quit()  
