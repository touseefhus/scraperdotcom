from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os
import pandas as pd  # Import pandas for Excel handling

# Set up Selenium with ChromeDriver
options = webdriver.ChromeOptions()
# Uncomment if you want to run in headless mode
# options.add_argument('--headless')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Load the SEC contact page
url = "https://www.uspto.gov/patents/basics/international-protection/filing-patents-abroad"
driver.get(url)

# Wait for the relevant table element to load
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'table'))
    )
    print("Table found, proceeding with scraping...")
except Exception as e:
    print("Table not found or took too long to load. Error:", str(e))
    driver.quit()
    exit()

# Get the page source
html = driver.page_source

# Parse the page source with BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Find the specific table
table = soup.find('table')

# Create a list to hold the scraped data
data = []

# Loop through the rows of the table
# Loop through the rows of the table
rows = table.find_all('tr')[1:]  # Skip the header row
for row in rows:
    columns = row.find_all('td')  # Get all the columns in the row
    if len(columns) >= 9:  # Adjust as necessary for the number of columns
        entry = {}

        # Get Country/Region and its link
        country_region_th = row.find_previous('th', string=lambda x: x is not None)
        entry["Country/region"] = country_region_th.get_text(strip=True)
        entry["Country/region URL"] = country_region_th.find('a')['href'] if country_region_th.find('a') else ''

        # Get IP Office and its link
        ip_office_td = columns[0]  # First column (IP Office)
        entry["IP Office"] = ip_office_td.get_text(strip=True)
        entry["IP Office URL"] = ip_office_td.find('a')['href'] if ip_office_td.find('a') else ''

        # Capture remaining headings and links
        headings = [header.get_text(strip=True) for header in table.find_all('th')[2:]]
        for i in range(len(headings)):
            if i < len(columns) - 1:  # Ensure the index is valid
                link = columns[i + 1].find('a')  # Adjust index as needed
                entry[headings[i]] = link.get_text(strip=True) if link else ''
                entry[f"{headings[i]} URL"] = link['href'] if link else ''

        # Append the entry to the data list
        data.append(entry)


# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(data)

# Specify the directory and file name for the JSON file
data_dir = 'data'
json_file_path = os.path.join(data_dir, 'stakeholder_resources.json')  # Save as .json

# Create the data directory if it doesn't exist
os.makedirs(data_dir, exist_ok=True)

# Save the DataFrame to a JSON file
df.to_json(json_file_path, orient='records', lines=True)

print(f"Data saved to {json_file_path}")

# Close the browser
driver.quit()
