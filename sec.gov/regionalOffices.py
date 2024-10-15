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
url = "https://www.sec.gov/about/regional-offices"
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

# Find the specific table (you may need to adjust the selector if there are multiple tables)
table = soup.find('table')

# Create a list to hold the scraped data
data = []

# Loop through the rows of the table
rows = table.find_all('tr')[1:]  # Skip the header row
for row in rows:
    columns = row.find_all('td')  # Get all the columns in the row
    if len(columns) >= 3:  # Ensure there are enough columns (Name, Phone, Email)
        regigonal_offices = columns[0].get_text(strip=True)
        address = columns[1].get_text(strip=True)
        phone = columns[2].get_text(strip=True)
       
        # Append the data to the list
        data.append({"Section Divisions": regigonal_offices, "Address": address, "Phone":phone})

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(data)

# Specify the directory and file name for the Excel file
data_dir = 'data'
file_path = os.path.join(data_dir, 'regionalOffices.xlsx')  # Save as .xlsx

# Create the data directory if it doesn't exist
os.makedirs(data_dir, exist_ok=True)

# Save the DataFrame to an Excel file
df.to_excel(file_path, index=False)

print(f"Data saved to {file_path}")

# Close the browser
driver.quit()
