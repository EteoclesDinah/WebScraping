from flask import Flask, request, jsonify
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from flask_cors import CORS
import os
import csv
import glob
from time import sleep

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route("/scrape", methods=["POST"])
def scrape():
    data = request.json
    url_list = data.get('urls', [])

    if not url_list:
        return jsonify({"error": "No URLs provided"}), 400

    # Save URLs to CSV file
    urls = {"URL": url_list}
    urls = pd.DataFrame(urls)
    urls.to_csv("url_list.csv", index=False)

    # Trigger the scraping process
    try:
        run_scraping(url_list)
        return jsonify({"message": "Scraping completed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_scraping(url_list):
    # Set up Chrome options for headless mode (no GUI)
    options = Options()
    options.headless = False  # Set True if you want headless scraping
    driver = webdriver.Chrome(options=options)

    # Ensure directories exist
    os.makedirs('./html_dumps', exist_ok=True)
    os.makedirs('./screenshots', exist_ok=True)

    # Iterate over the URLs to scrape data
    for i, url in enumerate(url_list):
        try:
            # Call the extract_data function
            final_df = extract_data(driver, url, i + 1)
            if not final_df.empty:
                output_file_path = os.path.join(os.getcwd(), 'output.csv')
                final_df.to_csv(output_file_path, mode='a', header=not os.path.exists(output_file_path))
        except Exception as e:
            print(f"Error processing URL {url}: {e}")

    driver.quit()  # Ensure the driver quits after scraping

def set_fixed_window_size(driver, width=1920, height=1080):
    driver.set_window_size(width, height)

def extract_data(driver, url, url_num):
    try:
        # Navigate to the URL
        driver.get(url)
        
        set_fixed_window_size(driver)
        screenshots(driver, url_num)
        html_dump(driver, url_num)

        content_list = []
        link_list = []
        title_list = []

        xpath = ("//h3//parent::a/ancestor::div[@data-hveid and @data-ved]/parent::div[contains(@class,'g')][not(ancestor::div[contains(@class,'answered-question')])][not(./ancestor::ul)]")

        title_path = '(' + xpath + ')' + '//div//h3[@class="LC20lb MBeuO DKV0Md"]'
        link_path = '(' + xpath + ')' + '//div[@class="yuRUbf"]/div/span/a[@jsname="UWckNb"]'
        content_path = '(' + xpath + ')' + '//div[@class="VwiC3b yXK7lf lVm3ye r025kc hJNv6b Hdw6tb"] | //div[@class="VwiC3b yXK7lf lVm3ye r025kc hJNv6b"]'

        wait = WebDriverWait(driver, 10)

        titles = wait.until(EC.presence_of_all_elements_located((By.XPATH, title_path)))
        links = wait.until(EC.presence_of_all_elements_located((By.XPATH, link_path)))
        contents = wait.until(EC.presence_of_all_elements_located((By.XPATH, content_path)))

        # Clear lists before adding
        title_list.clear()
        link_list.clear()
        content_list.clear()

        for title in titles:
            title_list.append(title.text)
        for link in links:
            link_list.append(link.get_attribute("href"))
        for content in contents:
            content_list.append(content.text)

        # Check length consistency
        if not (len(title_list) == len(link_list) == len(content_list)):
            print(f"Warning: Mismatch in lengths of extracted lists. Titles: {len(title_list)}, Links: {len(link_list)}, Contents: {len(content_list)}")

        # Create DataFrames
        df_title = pd.DataFrame(title_list, columns=['Title'])
        df_link = pd.DataFrame(link_list, columns=['Link'])
        df_content = pd.DataFrame(content_list, columns=['Content'])

        final_df = pd.concat([df_title, df_link, df_content], axis=1)
        final_df['URL_Number'] = url_num  # Add URL number for reference

        return final_df
    
    except Exception as e:
        print(f"Error extracting data from URL {url}: {e}")
        # Additional debug information
        print("Current URL:", url)
        print("Exception message:", e)
        return pd.DataFrame()


def screenshots(driver, url_num):
    viewport_height = driver.execute_script("return window.innerHeight")
    viewport_height -= 80  # To obtain full data screenshot
    height = driver.execute_script("return document.body.scrollHeight")
    y = 0  # For equating height left to scroll
    i = 0  # For file name

    while y < height:
        driver.get_screenshot_as_file(f"./screenshots/{url_num}_v" + str(i) + '.png')
        driver.execute_script(f"window.scrollBy(0,{viewport_height})")
        sleep(2)
        y += viewport_height
        i += 1

    # Full-page screenshot
    driver.find_element(by=By.TAG_NAME, value='body').screenshot(f'./screenshots/{url_num}.png')
    remove_invalid_screenshots()

def remove_invalid_screenshots():
    screenshot_files = glob.glob('./screenshots/*.png')
    for file in screenshot_files:
        if '_' not in os.path.basename(file):
            os.remove(file)

def html_dump(driver, url_num):
    driver.implicitly_wait(2)
    with open(f'./html_dumps/webpage{url_num}.html', "w", encoding='utf-8') as f:
        h = driver.page_source
        f.write(h)

def read_csv():
    df = pd.read_csv('url_list.csv')  # Ensure this file exists in the same directory
    return df

if __name__ == "__main__":
    app.run(debug=True)
