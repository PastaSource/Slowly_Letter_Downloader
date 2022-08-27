import re
import os
from os.path import exists
import json
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome, ChromeOptions

dir_path = os.getcwd()
download_path = os.path.join(dir_path, "letters")
# chrome_path = os.path.join(dir_path, "chromium\\app\\Chrome-bin\\chrome.exe")
website = 'https://web.slowly.app/'
home_url = 'https://web.slowly.app/home'
current_url_regex = '([\w]*:\/\/[\w.]*\/)([\w]*)'
friend_regex = '([\w]*:\/\/[\w.]*\/)(friend)(\/[\w\d]*)'
signature_regex = '>(.*)<\/h5><p>(.* \d\d\d\d) .*<br>'
dot_regex = '<button>\d*<\/button>'
xpath = "//div[@class='col-6 col-xl-4 mb-3']" # Outer HTML
signature_xpath = "//div[@class='media-body mx-3 mt-2']" # Finds name and date printed on letter
dot_xpath = "//ul[@class='slick-dots']"
next_button_xpath = "//button[@class='slick-arrow slick-next']"
back_button_xpath = "//a[@class='no-underline link py-2 px-2 ml-n2 col-pixel-width-50 flip active']"

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
# options.binary_location = chrome_path
options.add_experimental_option("prefs", {
    "printing.print_preview_sticky_settings.appState": json.dumps(print_settings),
    "savefile.default_directory": download_path, #Change default directory for downloads
    "download.default_directory": download_path, #Change default directory for downloads
    "download.prompt_for_download": False, #To auto download the file
    # "download.open_pdf_in_system_reader": False,
    "download.directory_upgrade": True,
    "profile.default_content_setting_values.automatic_downloads": 1,
    "safebrowsing.enabled": True
    # "profile.default_content_settings.popups": 0,
    # "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
})
options.add_argument("--kiosk-printing")


driver = Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(website)
wait = WebDriverWait(driver, 30)

def scroll_down():
    try:
        # scrolls through letters to load them
        scroll_pause_time = 2
        page_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            print("Scrolling...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(scroll_pause_time)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == page_height:
                break
            page_height = new_height
    finally:
        pass

def check_for_photos():
    if len(driver.find_elements(By.XPATH, dot_xpath)) > 0:
        return True
    else:
        return False



def photo_amount():
    photos = driver.find_element(By.XPATH, dot_xpath)
    photos_innerhtml = photos.get_attribute('innerHTML')
    search = re.findall(dot_regex, photos_innerhtml)
    photo_count = len(search)
    return photo_count

def make_pdf(letter_count):
    print(f"Printing letter {letter_count}")
    driver.execute_script("window.print()")
    time.sleep(2)
    # driver.print_page()
    letter = driver.find_element(By.XPATH, signature_xpath)
    innerhtml = letter.get_attribute('innerHTML')
    username = re.search(signature_regex, innerhtml).group(1)
    date = re.search(signature_regex, innerhtml).group(2)
    pdf_name = f"{username}_letter{letter_count}_{date}.pdf"
    file = "SLOWLY.pdf"
    os.rename(f"{download_path}\\{file}", f"{download_path}\\{pdf_name}") # perhaps moved this into if exists block
                                                                          # to prevent errors if file exists
    if exists(f"{download_path}\\{pdf_name}"):
        print(f"Letter {letter_count} successfully printed!")
    else:
        print(f"Letter {letter_count} failed to print.")

def open_letter(letter_int, letter_count):
    letters = driver.find_elements(By.XPATH, xpath)
    letter = letters[letter_int]
    letter.click()
    time.sleep(1)
    scroll_down()
    photos_exist = check_for_photos()
    if photos_exist:
        amount = photo_amount()
        next_button = driver.find_element(By.XPATH, next_button_xpath)
        print("Loading images...")
        for clicker in range(0, amount - 1):
            next_button.click()
            time.sleep(0.5)
        print("Please allow time for the images to properly load.")
        time.sleep(5)
    else:
        pass

    # may be able to use isDisplay() method that returns a boolean if the image is displayed.
    # whether or not this will confirm if it is loaded or just being displayed, I'm not sure.
    # could use the driver.wait.until method for this (or whatever it is).
    make_pdf(letter_count)
    print("Going back to letters...")

def main():
    while driver.current_url != home_url:
        pass
    print("Successful login detected! \nPlease select a penpal.")
    while re.search(current_url_regex, driver.current_url).group(2) != "friend":
        pass
    print("Penpal selected!")
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, xpath)))
        print("Loading letters")
        scroll_down()
    finally:
        pass

    letters = driver.find_elements(By.XPATH, xpath)
    current_letter_int = len(letters)
    amount_letters = current_letter_int
    for letter in range(0, amount_letters):
        open_letter(letter, current_letter_int)
        current_letter_int -= 1
        back_button = driver.find_element(By.XPATH, back_button_xpath)
        back_button.click()
        time.sleep(2)
    # for letter in letters:
    #     print(f"Letter {current_letter_int} loaded...")
    #     open_letter(letter, current_letter_int)
    #     current_letter_int -= 1
    #     back_button = driver.find_element(By.XPATH, back_button_xpath)
    #     back_button.click()
    #     time.sleep(2)
    #     letters = driver.find_elements(By.XPATH, xpath)
    # else:
    #     print(f"{amount_letters} letters successfully printed!")



if __name__ == '__main__':
    main()