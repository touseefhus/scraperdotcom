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
    
    # Extract addresses using tag <address> and find <p> within it
    addresses = []
    address_elements = soup.find_all('address')
    for address in address_elements:
        p_tags = address.find_all('p', class_='bds-body')
        if len(p_tags) == 2:
            street = p_tags[0].get_text(strip=True)
            city_state_zip = p_tags[1].get_text(strip=True)
            addresses.append(f"{street}, {city_state_zip}")

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
def save_to_excel(data, file_name='dentist-data.xlsx'):
    # Prepare the data for the DataFrame
    rows = []
    for i in range(max(len(data['Phone Numbers']), len(data['Addresses']), len(data['Website Links']))):
        row = {
            'Phone Numbers': data['Phone Numbers'][i] if i < len(data['Phone Numbers']) else '',
            'Addresses': data['Addresses'][i] if i < len(data['Addresses']) else '',
            'Website Links': data['Website Links'][i] if i < len(data['Website Links']) else ''
        }
        rows.append(row)

    # Create a DataFrame from the data
    df = pd.DataFrame(rows)
    
    # Save the DataFrame to an Excel file in the same directory as the script
    output_file = os.path.join(os.path.dirname(__file__), file_name)
    df.to_excel(output_file, index=False)
    
    print(f"Data has been saved to {output_file}")

# Main function to scrape data from multiple websites and save it
def main():
    # List of URLs that share the same structure
    urls = [
    "https://www.bbb.org/us/ca/san-francisco/profile/dentist/dr-kenneth-g-louie-dds-1116-11857",
    "https://www.bbb.org/us/ca/riverside/profile/dentist/vm-dental-group-1066-89074216",
    "https://www.bbb.org/us/tx/houston/profile/dentist/thomas-e-wright-iii-dds-inc-0915-64620",
    "https://www.bbb.org/us/wi/milwaukee/profile/dentist/king-family-dentistry-0694-44266265",
    "https://www.bbb.org/us/wi/waukesha/profile/orthodontist/bubon-associates-orthodontics-sc-0694-44108420",
    "https://www.bbb.org/us/wi/waukesha/profile/orthodontist/bubon-associates-orthodontics-sc-0694-44108420",
    "https://www.bbb.org/us/wi/waukesha/profile/orthodontist/bubon-associates-orthodontics-sc-0694-44108420",
    "https://www.bbb.org/us/wi/waukesha/profile/orthodontist/bubon-associates-orthodontics-sc-0694-44108420",
    "https://www.bbb.org/us/wi/waukesha/profile/orthodontist/bubon-associates-orthodontics-sc-0694-44108420",
    "https://www.bbb.org/us/wi/green-bay/profile/dentist/first-impression-dental-llc-0694-44099744",
    "https://www.bbb.org/us/il/river-forest/profile/dentist/catrambone-dental-associates-pc-0654-12000526",
    "https://www.bbb.org/us/nm/albuquerque/profile/dentist/roderick-a-garcia-dmd-pc-0806-99122558",
    "https://www.bbb.org/us/nm/farmington/profile/dentist/desert-hills-dental-care-llc-0806-99121291",
    "https://www.bbb.org/us/nm/albuquerque/profile/dentist/desert-willow-dental-care-llc-0806-4837",
    "https://www.bbb.org/us/mn/new-hope/profile/dental-implants/dentures-asap-0704-96175590",
    "https://www.bbb.org/us/ma/milton/profile/periodontist/fugazzotto-rost-brodsky-0021-132276",
    "https://www.bbb.org/us/vt/randolph/profile/dentist/wilson-dentistry-0021-128078",
    "https://www.bbb.org/us/ma/salem/profile/dentist/paradise-dental-associates-llc-0021-124999",
    "https://www.bbb.org/us/ct/hamden/profile/dentist/cosmetic-and-implant-dentistry-of-ct-0111-87068569",
    "https://www.bbb.org/us/ny/new-york/profile/cosmetic-dentistry/esthetix-dentist-nycs-dental-implant-cosmetic-specialist-0121-120728",
    "https://www.bbb.org/us/ny/bellmore/profile/dentist/gerard-h-menzies-dmd-pc-0121-120498",
    "https://www.bbb.org/us/pa/erie/profile/dentist/beautiful-smiles-childrens-dental-health-0141-71014861",
    "https://www.bbb.org/us/ny/clifton-park/profile/dentist/clifton-park-dental-0041-125358936",
    "https://www.bbb.org/us/ma/newburyport/profile/dentist/norma-colletta-dmd-pc-0021-94206",
    "https://www.bbb.org/us/ny/amherst/profile/dentist/university-pediatric-dentistry-pc-0041-46003121",
    "https://www.bbb.org/us/ny/amherst/profile/dentist/university-pediatric-dentistry-pc-0041-46003121",
    "https://bbb.org/us/ct/newington/profile/dentist/east-cedar-dental-inc-0111-87118794",
    "https://www.bbb.org/us/ny/watertown/profile/dentist/mccue-dental-0041-235966802",
    "https://www.bbb.org/us/ny/watertown/profile/dentist/mccue-dental-0041-235966802",
    "https://www.bbb.org/us/ny/geneva/profile/dentist/lake-country-dental-pllc-0041-235963835",
    "https://www.bbb.org/us/ny/cortland/profile/dentist/cortland-dental-0041-63001281",
    "https://www.bbb.org/us/ny/albany/profile/dentist/andrew-t-frank-and-associates-dmd-0041-60009024",
    "https://www.bbb.org/us/ny/kenmore/profile/dentist/advantage-dentistry-llp-0041-57104921",
    "https://www.bbb.org/us/ma/brockton/profile/dentist/david-s-gould-dds-0021-53068",
    "https://www.bbb.org/us/ma/arlington/profile/dentist/dr-michael-f-fitzpatrick-0021-14222",
    "https://www.bbb.org/us/ma/walpole/profile/dentist/kevin-p-mischley-dmd-0021-135213",
    "https://www.bbb.org/us/ny/new-hyde-park/profile/dentist/adina-simone-dmd-0121-149765",
    "https://www.bbb.org/us/pa/munhall/profile/dentist/joseph-dalesio-dds-0141-12007177",
    "https://www.bbb.org/us/pa/edinboro/profile/dentist/james-r-schmitt-dmd-0141-12006019",
    "https://www.bbb.org/us/ct/cos-cob/profile/dentist/garrick-f-wong-dmd-ms-0111-14000653",
    "https://bbb.org/us/ct/fairfield/profile/dentist/whole-body-dentistry-0111-10001995",
    "https://www.bbb.org/us/ny/utica/profile/dentist/donald-a-flihan-dds-md-pc-0041-66008179",
    "https://www.bbb.org/us/oh/warren/profile/dentist/family-first-dental-group-llc-0432-15000797",
    "https://www.bbb.org/us/tx/tyler/profile/dentist/brick-street-dental-pllc-1075-23000596",
    "https://www.bbb.org/us/hi/pearl-city/profile/children-dentist/kidshine-pediatric-dental-group-1296-1000083202",
    
    ]
    
    # Step 1: Scrape data from multiple websites
    all_data = scrape_multiple_websites(urls)
    
    # Step 2: Save the aggregated data to Excel
    save_to_excel(all_data)

# Execute the main function
if __name__ == "__main__":
    main()
