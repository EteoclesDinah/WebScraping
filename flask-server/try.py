import os
import glob
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

# Ensure the directories exist
os.makedirs('./html_dumps', exist_ok=True)
os.makedirs('./screenshots', exist_ok=True)

options = Options()
options.headless = False

driver = webdriver.Chrome(options=options)

def set_fixed_window_size(driver, width=1920, height=1080):
    driver.set_window_size(width, height)

only_title = []
only_links = []
only_content = []
header = ['Title', 'Value']

xpath = ("//h3//parent::a/ancestor::div[@data-hveid and @data-ved]/parent::div[contains(@class,'g')][not("
         "ancestor::div[contains(@class,'answered-question')])][not(./ancestor::ul)]/parent::div[not(@id) or "
         "@id='rso']/div[contains(@class,'g')][not(./ancestor::ul)][not(@data-md)][not(descendant::table)][not("
         "./g-card)][not(parent::div[contains(@class,'V3FYCf')])][not(ancestor::div[contains(@class,'sinMW') or "
         "contains(@class,'bCOlv')])] | //h3//parent::a/ancestor::div[@data-hveid and @data-ved]/ancestor::div["
         "@class='g']/parent::div[@data-hveid]//div[@data-hveid and @data-ved][not(./ancestor::ul)]/ancestor::div["
         "@class='g'][not(ancestor::div[contains(@class,'bCOlv')])] | //h3/ancestor::a/parent::div[contains(@class,"
         "'kCrYT')]/parent::div | //a[contains(@href,'youtube') or contains(@href,'tiktok')][./h3][not(ancestor::div["
         "contains(@style,'display:none')])][not(preceding-sibling::a[contains(@class,'no-hover')])][not(./div["
         "contains(@class,'kp-wholepage')] or ./div[contains(@class,'knowledge-panel')])][not(descendant::div["
         "contains(@class,'d4rhi')])][not(descendant::h2[contains(text(), 'Featured snippet')])][not(ancestor::div["
         "preceding-sibling::h2[contains(text(),'Featured snippet')]])][not(./div[@class='g'])][not(@style='')][not("
         "./g-card)][not(preceding-sibling::a)][not(ancestor::div[@class='tF2Cxc'])] | //h3/parent::a/ancestor::div["
         "@data-hveid and @data-ved][contains(@class,'g Ww4FFb')][not(ancestor::div[contains(@class,'MjjYud')]["
         "preceding-sibling::a[contains(@class,'no-hover-decoration')]])][not(./a[contains(@class,"
         "'no-hover-decoration')])][not(ancestor::div[preceding-sibling::div[contains(@jsaction,'click:trigger')]])]")

def extract_data(url, url_num):
    driver.get(url)
    set_fixed_window_size(driver)  # Ensure fixed window size before extraction
    screenshots(url_num)
    html_dump(url_num)

    content_list = []
    link_list = []
    title_list = []

    title_path = '(' + xpath + ')' + '//div//h3[@class="LC20lb MBeuO DKV0Md"]'
    link_path = '(' + xpath + ')' + '//div[@class="yuRUbf"]/div/span/a[@jsname="UWckNb"]'
    content_path = '(' + xpath + ')' +'//div[@class="VwiC3b yXK7lf lVm3ye r025kc hJNv6b Hdw6tb"] | //div[@class="VwiC3b yXK7lf lVm3ye r025kc hJNv6b"]'

    wait = WebDriverWait(driver, 10)

    try:
        titles = wait.until(EC.presence_of_all_elements_located((By.XPATH, title_path)))
        only_title.clear()
        only_links.clear()
        only_content.clear()

        for title in titles:
            title_list.append(title.text)
            only_title.append('Title')

        links = wait.until(EC.presence_of_all_elements_located((By.XPATH, link_path)))
        for link in links:
            link_list.append(link.get_attribute("href"))
            only_links.append('Link')

        contents = wait.until(EC.presence_of_all_elements_located((By.XPATH, content_path)))
        for content in contents:
            content_list.append(content.text)
            only_content.append('Content')

        if not (len(title_list) == len(link_list) == len(content_list)):
            print(
                f"Warning: Mismatch in lengths of extracted lists. Titles: {len(title_list)}, Links: {len(link_list)}, Contents: {len(content_list)}")

        df_title = pd.DataFrame(title_list)
        df_link = pd.DataFrame(link_list)
        df_content = pd.DataFrame(content_list)

        emb_title = pd.Series(only_title)
        emb_link = pd.Series(only_links)
        emb_content = pd.Series(only_content)

        df_title.insert(0, '', emb_title)
        df_link.insert(0, '', emb_link)
        df_content.insert(0, '', emb_content)

        final_df = pd.concat([df_title, df_link, df_content], axis=0)
        index_file = []

        for i in range(3):
            for j in range(len(df_title)):
                a = (str(url_num) + '.' + str(j + 1) + '.' + str(i + 1))
                index_file.append(a)

        index_file = pd.Series(index_file)
        final_df.index = index_file
        final_df.columns = header

        return final_df

    except Exception as e:
        print(f"Error extracting data from URL {url}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error

def read_csv():
    df = pd.read_csv('url_list.csv')  # Ensure this file exists in the same directory
    return df

def screenshots(url_num):
    viewport_height = driver.execute_script("return window.innerHeight")
    viewport_height -= 80  # To obtain full data screenshot
    height = driver.execute_script("return document.body.scrollHeight")
    i = 0  # For file name
    y = 0  # For equating height left to scroll

    while y < height:
        driver.get_screenshot_as_file(f"./screenshots/{url_num}_v" + str(i) + '.png')
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

def html_dump(url_num):
    driver.implicitly_wait(2)
    with open(f'./html_dumps/webpage{url_num}.html', "w", encoding='utf-8') as f:
        h = driver.page_source
        f.write(h)

def main():
    output = pd.DataFrame()
    url_list = read_csv()

    for index, row in url_list.iterrows():
        url = row['URL']
        url_num = index + 1  # URL index starts from 1
        try:
            final_df = extract_data(url, url_num)
            if not final_df.empty:
                output = pd.concat([output, final_df])
        except Exception as e:
            print(f"Error processing URL {url}: {e}")

    output.index.name = "Index"
    print(output)
    output_file_path = os.path.join(os.getcwd(), 'output.csv')  # Save the final output to a CSV file
    output.to_csv(output_file_path)
    driver.quit()

if __name__ == "__main__":
    main()
