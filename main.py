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
chrome_path = os.path.join(dir_path, "chromium\\app\\Chrome-bin\\chrome.exe")
website = 'https://web.slowly.app/'
home_url = 'https://web.slowly.app/home'
current_url_regex = '([\w]*:\/\/[\w.]*\/)([\w]*)'
friend_regex = '([\w]*:\/\/[\w.]*\/)(friend)(\/[\w\d]*)'
signature_regex = '>(.*)<\/h5><p>(.* \d\d\d\d) .*<br>'
dot_regex = '<button>\d*<\/button>'
penpal_regex = '<span.*mt-1">(\w*)<\/span>'
xpath = "//div[@class='col-6 col-xl-4 mb-3']" # Outer HTML
signature_xpath = "//div[@class='media-body mx-3 mt-2']" # Finds name and date printed on letter
dot_xpath = "//ul[@class='slick-dots']"
next_button_xpath = "//button[@class='slick-arrow slick-next']"
back_button_xpath = "//a[@class='no-underline link py-2 px-2 ml-n2 col-pixel-width-50 flip active']"
penpal_xpath = "//div[@class='col-9 pt-2']"

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
    "download.directory_upgrade": True,
    "profile.default_content_setting_values.automatic_downloads": 1,
    "safebrowsing.enabled": True
})
options.add_argument("--kiosk-printing")


driver = Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(website)
wait = WebDriverWait(driver, 30)

def scroll_down():
    try:
        # Scrolls through letters to load them
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

def make_pdf(letter_count, penpal_dir):
    letter = driver.find_element(By.XPATH, signature_xpath)
    innerhtml = letter.get_attribute('innerHTML')
    username = re.search(signature_regex, innerhtml).group(1)
    date = re.search(signature_regex, innerhtml).group(2)
    pdf_name = f"letter{letter_count}_{username}_{date}.pdf"
    file = "SLOWLY.pdf"

    if exists(f"{download_path}\\{file}"):
        os.remove(f"{download_path}\\{file}")
    if exists(f"{penpal_dir}\\{file}"):
        return print("Letter already exists! \nSkipping...")

    # Prints letter as PDF with name "SLOWLY.pdf" in download_path
    print(f"Printing letter {letter_count}")
    driver.execute_script("window.print()")
    time.sleep(2)

    os.replace(f"{download_path}\\{file}", f"{penpal_dir}\\{file}") # Moves SLOWLY.pdf into penpal_dir
    os.rename(f"{penpal_dir}\\{file}", f"{penpal_dir}\\{pdf_name}") # Renames SLOWLY.pdf to pdf_name var

    if exists(f"{penpal_dir}\\{pdf_name}"):
        print(f"Letter {letter_count} successfully printed!")
    else:
        print(f"Letter {letter_count} failed to print.")

def open_letter(letter_int, letter_count, penpal_dir):
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
    make_pdf(letter_count, penpal_dir)
    print("Going back to letters...")

def mk_penpal_dir(penpal):
    penpal_dir = os.path.join(download_path, penpal)
    if exists(penpal_dir):
        print("Penpal downloaded directory already exists in 'letters' folder.")
    else:
        print(f"Making download directory for {penpal}")
        os.mkdir(penpal_dir)
    return penpal_dir

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

    # mkdir with name of penpal
    penpal_name_obtain = driver.find_element(By.XPATH, penpal_xpath).get_attribute('innerHTML')
    penpal = re.search(penpal_regex, penpal_name_obtain).group(1)
    penpal_dir = mk_penpal_dir(penpal)

    letters = driver.find_elements(By.XPATH, xpath)
    current_letter_int = len(letters) # tracks which letter is currently being processed
    amount_letters = current_letter_int # amount of letters available to download
    for letter in range(0, amount_letters):
        open_letter(letter, current_letter_int, penpal_dir)
        current_letter_int -= 1
        back_button = driver.find_element(By.XPATH, back_button_xpath)
        back_button.click()
        time.sleep(2)
    else:
        print(f"{amount_letters} letters successfully printed!")
        driver.quit()

if __name__ == '__main__':
    main()