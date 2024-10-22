from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

# URL of the page
url = "https://www.bbb.org/us/ca/cordelia/categories"

# Setup Selenium WebDriver using WebDriver Manager
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run browser in headless mode (optional)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open the website
driver.get(url)

# Wait for the 'ul' element with both classes 'list-reset' and 'cluster' to be present
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ul.list-reset.cluster"))
    )
    print("Navigation ul found!")
except Exception as e:
    print(f"Error: Could not find the 'ul' tag with class 'list-reset cluster'. The page structure might have changed.")
    driver.quit()

# Get the page source after JavaScript execution
html_content = driver.page_source

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Initialize list to store category name and link data
category_data = []

# Find the ul tag with class 'list-reset cluster'
alpha_ul = soup.find('ul', class_='list-reset cluster')

# Check if the navigation ul is found
if alpha_ul is None:
    print("Error: Could not find the 'ul' tag with class 'list-reset cluster'. The page structure might have changed.")
else:
    # Extract alpha links (A-Z)
    alpha_links = alpha_ul.find_all('a', class_='dtm-all-categories-alpha-pager')

    # Loop through each letter (A-Z) and extract the categories
    for alpha_link in alpha_links:
        # Get the link for the alphabet
        alpha_url = alpha_link['href']

        # Click on the link in Selenium to navigate to the corresponding page
        driver.get(alpha_url)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "bds-body"))
            )
        except Exception as e:
            print(f"Error: Could not load categories for {alpha_link.text.strip()}.")
            continue

        # Get the page source for the selected alphabet category
        category_html = driver.page_source
        category_soup = BeautifulSoup(category_html, "html.parser")

        # Find the second level of categories
        category_ul = category_soup.find('ul', class_='bds-body css-f0ef99 e1kid4h70')

        if category_ul:
            # Find all category links
            category_links = category_ul.find_all('a', class_='dtm-all-categories-category')

            # Extract category name and link
            for category_link in category_links:
                category_name = category_link.text.strip()
                category_href = category_link['href']
                category_data.append([category_name, category_href])

        else:
            print(f"Warning: No categories found for {alpha_link.text.strip()}")

# Close the browser
driver.quit()

# If categories were found, export them to an Excel file
if category_data:
    # Create a pandas DataFrame with the scraped data
    df = pd.DataFrame(category_data, columns=['Category Name', 'Link'])

    # Save the DataFrame to an Excel file
    df.to_excel('bbb_categories.xlsx', index=False)

    print("Data has been successfully scraped and saved to 'bbb_categories.xlsx'.")
else:
    print("No category data was found.")
