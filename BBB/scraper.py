import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

# Function to extract contact numbers, addresses, and website links from a single URL
def scrape_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Retry mechanism
    retries = 3
    wait_time = 5
    for attempt in range(retries):
        try:
            # Fetch the website content
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"Successfully fetched the content from {url}")
                return response.content
            else:
                print(f"Error: Status code {response.status_code} for {url}, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
        except requests.exceptions.RequestException as e:
            print(f"Exception occurred for {url}: {e}, retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    
    print(f"Failed to retrieve the webpage after retries: {url}")
    return None

# Function to parse and extract the data from the HTML content
def parse_data(content):
    soup = BeautifulSoup(content, 'html.parser')

    # Extract phone numbers
    phone_numbers = set()
    phone_elements = soup.find_all('a', class_='dtm-phone')
    for phone in phone_elements:
        phone_numbers.add(phone.get_text(strip=True))
    
     # Extract addresses using tag <address> and then find <p> within it
    addresses = set()
    address_elements = soup.find_all('address')  # Find all <address> tags
    for address in address_elements:
        # Find <p> tags within each <address> tag
        p_tags = address.find_all('p', class_='bds-body')  # Look for <p> with class 'bds-body'
        for p in p_tags:
            addresses.add(p.get_text(strip=True))  # Add the text of the <p> to the set

    # Extract website links
    links = set()
    link_elements = soup.find_all('a', class_='dtm-url', href=True)
    for link in link_elements:
        href = link['href']
        if 'http' in href:
            links.add(href)

    return {
        'Phone Numbers': list(phone_numbers),
        'Addresses': list(addresses),
        'Website Links': list(links)
    }

# Function to scrape multiple websites
def scrape_multiple_websites(urls):
    all_data = {
        'Phone Numbers': [],
        'Addresses': [],
        'Website Links': []
    }

    for url in urls:
        content = scrape_data(url)
        if content:
            data = parse_data(content)
            all_data['Phone Numbers'].extend(data['Phone Numbers'])
            all_data['Addresses'].extend(data['Addresses'])
            all_data['Website Links'].extend(data['Website Links'])

    return all_data

# Function to save the aggregated data into an Excel file
def save_to_excel(data, file_name='aggregate_data.xlsx'):
    # Create a DataFrame from the data
    df = pd.DataFrame(dict([(key, pd.Series(value)) for key, value in data.items()]))
    
    # Save the DataFrame to an Excel file in the same directory as the script
    output_file = os.path.join(os.path.dirname(__file__), file_name)
    df.to_excel(output_file, index=False)
    
    print(f"Data has been saved to {output_file}")

# Main function to scrape data from multiple websites and save it
def main():
    # List of URLs that share the same structure
    urls = [
        'https://www.bbb.org/us/az/scottsdale/profile/health-and-wellness/for-wellness-1126-1000108482',  
        'https://www.bbb.org/us/ky/louisville/profile/health-club/vyfy-wellness-0402-159165244', 
        'https://www.bbb.org/us/az/phoenix/profile/health-and-wellness/execlevel-wellness-1126-1000045502',
        'https://www.bbb.org/us/ks/derby/profile/weight-loss/enhanced-wellness-0714-1000062286',
        'https://www.bbb.org/us/ca/san-diego/profile/health-and-wellness/health-and-wellness-bazaar-1126-1000086141',
        'https://www.bbb.org/us/tx/san-antonio/profile/mental-health-services/emotion-wellness-0825-1000228075',
        'https://www.bbb.org/us/az/scottsdale/profile/medical-equipment/trusted-wellness-1126-1000045837',
        'https://www.bbb.org/us/wi/bayview/profile/yoga-studio/integrative-wellness-0694-1000059892',
        'https://www.bbb.org/us/mi/zeeland/profile/health-care/wellness-co-0372-38284655',
        'https://www.bbb.org/us/ca/la-jolla/profile/health-and-wellness/cove-wellness-1126-171991535',
        'https://www.bbb.org/us/tn/bartlett/profile/health-and-wellness/nexgen-health-and-wellness-0543-44140541',
    ]
    
    # Step 1: Scrape data from multiple websites
    all_data = scrape_multiple_websites(urls)
    
    # Step 2: Save the aggregated data to Excel
    save_to_excel(all_data)

# Execute the main function
if __name__ == "__main__":
    main()
