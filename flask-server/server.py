from flask import Flask, request, jsonify
from flask_cors import CORS
import csv

app = Flask(__name__)
CORS(app)

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        # Get the list of URLs from the POST request
        data = request.get_json()
        urls = data.get('urls', [])
        
        # Save the URLs to url_list.csv
        with open('url_list.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['URL'])  # Writing the header
            for url in urls:
                writer.writerow([url])
        
        # Placeholder for scraping logic
        scraped_data = []
        for url in urls:
            # Perform your web scraping logic here
            scraped_data.append({'url': url, 'content': 'Scraped content for ' + url})

        # Return the scraped data as a JSON response
        return jsonify(scraped_data), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
