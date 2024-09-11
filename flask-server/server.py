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

def extract_data(driver, url, url_num):
    # Navigate to the URL
    driver.get(url)
    
    set_fixed_window_size(driver)
    screenshots(url_num, driver)
    html_dump(url_num, driver)

    content_list = []
    link_list = []
    title_list = []

    title_path = '//div//h3[@class="LC20lb MBeuO DKV0Md"]'
    link_path = '//div[@class="yuRUbf"]/div/span/a[@jsname="UWckNb"]'
    content_path = '//div[@class="VwiC3b yXK7lf lVm3ye r025kc hJNv6b Hdw6tb"] | //div[@class="VwiC3b yXK7lf lVm3ye r025kc hJNv6b"]'

    wait = WebDriverWait(driver, 10)

    try:
        titles = wait.until(EC.presence_of_all_elements_located((By.XPATH, title_path)))
        links = wait.until(EC.presence_of_all_elements_located((By.XPATH, link_path)))
        contents = wait.until(EC.presence_of_all_elements_located((By.XPATH, content_path)))

        for title in titles:
            title_list.append(title.text)
        for link in links:
            link_list.append(link.get_attribute("href"))
        for content in contents:
            content_list.append(content.text)

        # Check length consistency
        if len(title_list) == len(link_list) == len(content_list):
            df_title = pd.DataFrame(title_list, columns=['Title'])
            df_link = pd.DataFrame(link_list, columns=['Link'])
            df_content = pd.DataFrame(content_list, columns=['Content'])

            final_df = pd.concat([df_title, df_link, df_content], axis=1)
            final_df.index = [f"{url_num}.{i+1}" for i in range(len(df_title))]

            return final_df
        else:
            print(f"Warning: Mismatch in lengths of extracted lists for URL {url_num}.")
            return pd.DataFrame()

    except Exception as e:
        print(f"Error extracting data from URL {url}: {e}")
        return pd.DataFrame()

def set_fixed_window_size(driver, width=1920, height=1080):
    driver.set_window_size(width, height)

def screenshots(url_num, driver):
    viewport_height = driver.execute_script("return window.innerHeight")
    height = driver.execute_script("return document.body.scrollHeight")
    i = 0
    y = 0

    while y < height:
        driver.get_screenshot_as_file(f"./screenshots/{url_num}_v{i}.png")
        driver.execute_script(f"window.scrollBy(0,{viewport_height})")
        sleep(2)
        y += viewport_height
        i += 1

    s = lambda X: driver.execute_script('return document.body.parentNode.scroll' + X)
    driver.set_window_size(s('Width'), s('Height'))
    driver.find_element(by=By.TAG_NAME, value='body').screenshot(f'./screenshots/{url_num}.png')
    driver.set_window_size(s('Width'), viewport_height)

    remove_invalid_screenshots()

def remove_invalid_screenshots():
    screenshot_files = glob.glob('./screenshots/*.png')
    for file in screenshot_files:
        if '_' not in os.path.basename(file):
            os.remove(file)

def html_dump(url_num, driver):
    driver.implicitly_wait(2)
    with open(f'./html_dumps/webpage{url_num}.html', "w", encoding='utf-8') as f:
        f.write(driver.page_source)

if __name__ == "__main__":
    app.run(debug=True)
