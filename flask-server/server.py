from flask import Flask, request, jsonify
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from flask_cors import CORS

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
    urls_df = pd.DataFrame(urls)
    urls_df.to_csv("url_list.csv", index=False)

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

    # Iterate over the URLs to scrape data
    for url in url_list:
        # Call the extract_data function (example function for scraping)
        extract_data(driver, url)

    driver.quit()  # Ensure the driver quits after scraping

def extract_data(driver, url):
    # Navigate to the URL
    driver.get(url)

    # Add your scraping logic here (this is just an example)
    page_title = driver.title  # Example: scraping the page title
    print(f"Scraping {url}, Title: {page_title}")

    # Implement your own scraping logic here (e.g., extracting elements, saving data)

if __name__ == "__main__":
    app.run(debug=True)
