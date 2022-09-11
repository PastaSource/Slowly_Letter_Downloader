import base64
import os
from os.path import exists
import json
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome, ChromeOptions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFParser
from pdfminer.pdfpage import PDFDocument

# Paths
dir_path = os.getcwd()
download_path = os.path.join(dir_path, "letters")
chrome_path = os.path.join(dir_path, "chromium\\app\\Chrome-bin\\chrome.exe")
user_data_path = os.path.join(dir_path, "sessions")

website = "https://www.google.com/"


def main():
    print_settings = {
        "recentDestinations": [{
            "id": "Save as PDF",
            "origin": "local",
            "account": "",
        }],
        "selectedDestinationId": "Save as PDF",
        "version": 2,
        "isHeaderFooterEnabled": False,
        "isLandscapeEnabled": True
    }

    options = ChromeOptions()
    options.binary_location = chrome_path
    options.add_argument("--start-maximized")
    options.add_argument('--window-size=1920,1080')
    options.add_argument(f"user-data-dir={user_data_path}")
    # options.add_argument("--disable-infobars")
    # options.add_argument("--disable-extensions")
    # options.add_argument("--disable-popup-blocking")
    options.add_argument("--headless")
    options.add_argument('--enable-print-browser')
    options.add_experimental_option("prefs", {
        "printing.print_preview_sticky_settings.appState": json.dumps(print_settings),
        "savefile.default_directory": download_path,  # Change default directory for downloads
        "download.default_directory": download_path,  # Change default directory for downloads
        "download.prompt_for_download": False,  # To auto download the file
        "download.directory_upgrade": True,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "safebrowsing.enabled": True
    })
    options.add_argument("--kiosk-printing")

    driver = Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(website)
    # driver.execute_script("window.print();")
    data = driver.execute_cdp_cmd("Page.printToPDF", print_settings)
    with open(os.path.join(download_path, "Google.pdf"), 'wb') as file:
        file.write(base64.b64decode(data['data']))
    # time.sleep(30)
    if exists(os.path.join(download_path, "Google.pdf")):
        print("YAY!")
    else:
        print(":(")


if __name__ == '__main__':
    main()
