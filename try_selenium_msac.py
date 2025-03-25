from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("disable-infobars")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
)

# Start Chrome WebDriver
driver = webdriver.Chrome(options=chrome_options)

# URL to scrape
url = 'https://www.msac.gov.au/applications/1801'
driver.get(url)

# Increase wait time for JavaScript content to load properly
time.sleep(10)  # Increase to 10-15 seconds if necessary

# Get the page source after JavaScript execution
html = driver.page_source

# Parse the HTML with BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Print HTML for verification
print(soup.prettify())
