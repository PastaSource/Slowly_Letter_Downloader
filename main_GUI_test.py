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
from pdfrw import  PdfReader, PdfWriter
from cefpython3 import cefpython as cef
import customtkinter
import tkinter as tk
import pyglet

# Paths
dir_path = os.getcwd()
download_path = os.path.join(dir_path, "letters")
chrome_path = os.path.join(dir_path, "chromium\\app\\Chrome-bin\\chrome.exe")
user_data_path = os.path.join(dir_path, "sessions")

# URLs
website = 'https://web.slowly.app/'
home_url = 'https://web.slowly.app/home'

# Regex
current_url_regex = '([\w]*:\/\/[\w.]*\/)([\w]*)'
friend_regex = '([\w]*:\/\/[\w.]*\/)(friend)(\/[\w\d]*)'
signature_regex = '>(.*)<\/h5><p>(.* \d\d\d\d) .*<br>'
dot_regex = '<button>\d*<\/button>'
penpal_regex = '<span.*mt-1">(\w*)<\/span>'
penpals_regex = '">(.*)<\/h6>'
id_regex = 'object .*\.(.*)>'

# xpath
xpath = "//div[@class='col-6 col-xl-4 mb-3']" # Outer HTML
signature_xpath = "//div[@class='media-body mx-3 mt-2']" # Finds name and date printed on letter
dot_xpath = "//ul[@class='slick-dots']"
next_button_xpath = "//button[@class='slick-arrow slick-next']"
back_button_xpath = "//a[@class='no-underline link py-2 px-2 ml-n2 col-pixel-width-50 flip active']"
penpal_xpath = "//div[@class='col-9 pt-2']"
penpals_xpath = "//h6[@class='col pl-0 pr-0 mt-1 mb-0 text-truncate ']" # Used to create list of all penpals

# GUI class
class App(customtkinter.CTk):

    WIDTH = 960
    HEIGHT = 720

    # Load fonts
    if exists(os.path.join(os.getcwd(), "interface\\fonts")):
        FONT_PATH = os.path.join(os.getcwd(), "interface\\fonts")
    else:
        FONT_PATH = os.path.join(os.getcwd(), "fonts")
    FONT_POTRA = pyglet.font.add_file(os.path.join(FONT_PATH, "potra.ttf"))
    FONT_STONE = pyglet.font.add_file(os.path.join(FONT_PATH, "stone.ttf"))
    FONT_BOTTERILL = pyglet.font.add_file(os.path.join(FONT_PATH, "Botterill Signature.ttf"))
    FONT_ENCHANTED = pyglet.font.add_file(os.path.join(FONT_PATH, "EnchantedPrairieDog.ttf"))
    FONT_TYPEWRITER = pyglet.font.add_file(os.path.join(FONT_PATH, "typewriter.ttf"))

    # Frame IDs
    FRAME_RIGHT_ID = None
    FRAME_RIGHT_BROWSER_ID = None
    FRAME_RIGHT_PROGRESS_ID = None
    FRAME_RIGHT_LOADING_ID = None

    customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

    def __init__(self, count):
        super().__init__()
        self.browser_frame = None
        self.penpals = count

        self.title("Slowly Letter Downloader")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed
        self.count = count
        self.typewriter_font = "Mom´sTypewriter"

        # ============ create frames ============
        # Configure frame layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.frame_left_scrollbar_width = 20
        self.frame_left_width = (App.WIDTH // 3)
        self.frame_right_width = (App.WIDTH - self.frame_left_width - self.frame_left_scrollbar_width)

        self.frame_top = customtkinter.CTkFrame(master=self, height=100)
        self.frame_top.pack(anchor="n", fill="x")

        self.frame_left = customtkinter.CTkFrame(master=self, width=self.frame_left_width)
        self.frame_left.pack(side="left", fill="both")

        self.frame_bottom = customtkinter.CTkFrame(master=self, width=self.frame_right_width, height=100)
        self.frame_bottom.pack(anchor="se", side="bottom")

        self.frame_right = customtkinter.CTkFrame(master=self, width=self.frame_right_width)
        self.frame_right.pack(anchor="e", expand=1, fill="both")

        # Frames integrated browser
        self.frame_right_browser = customtkinter.CTkFrame(master=self.frame_right)
        self.frame_right_browser.pack(expand=1, fill="both")

        self.frame_bottom_browser = customtkinter.CTkFrame(master=self.frame_bottom)
        self.frame_bottom_browser.pack(anchor="se", side="bottom")

        self.frame_left_browser = customtkinter.CTkFrame(master=self.frame_left)
        self.frame_left_browser.pack(side="left", fill="both")

        # Frames progress bar
        self.frame_right_progress = customtkinter.CTkFrame(master=self.frame_right)

        self.frame_bottom_progress = customtkinter.CTkFrame(master=self.frame_bottom)

        self.frame_left_progress = customtkinter.CTkFrame(master=self.frame_left)

        # Frames loading penpals
        self.frame_right_loading = customtkinter.CTkFrame(master=self.frame_right)


        # ============ frame_top ============
        self.app_title = customtkinter.CTkLabel(master=self.frame_top, text="Slowly Letter Downloader",
                                                text_font=(self.typewriter_font, -50))
        self.app_title.place(x=(App.WIDTH/2), y=50, anchor="center")

        # ============ frame_bottom ============
        # Integrated browser frame
        self.run_button = customtkinter.CTkButton(master=self.frame_bottom_browser,
                                                text="Run", text_font=(self.typewriter_font, -20),
                                                border_width=2,  # <- custom border_width
                                                fg_color=None,  # <- no fg_color
                                                command=self.run_button_event)
        self.run_button.grid(row=8, column=2, columnspan=1, pady=20, padx=20, sticky="se")

        self.load_penpals_button = customtkinter.CTkButton(master=self.frame_bottom_browser,
                                                text="Load Penpals", text_font=(self.typewriter_font, -20),
                                                border_width=2,  # <- custom border_width
                                                fg_color=None,  # <- no fg_color
                                                command=self.load_penpals_button_event)
        self.load_penpals_button.grid(row=8, column=1, columnspan=1, pady=20, padx=20, sticky="sw")

        # Progress bar frame
        self.run_button = customtkinter.CTkButton(master=self.frame_bottom_progress,
                                                text="Run", text_font=(self.typewriter_font, -20),
                                                border_width=2,  # <- custom border_width
                                                fg_color=None,  # <- no fg_color
                                                command=self.run_button_event)
        self.run_button.grid(row=8, column=2, columnspan=1, pady=20, padx=20, sticky="se")

        self.load_penpals_button = customtkinter.CTkButton(master=self.frame_bottom_progress,
                                                text="Select All", text_font=(self.typewriter_font, -20),
                                                border_width=2,  # <- custom border_width
                                                fg_color=None,  # <- no fg_color
                                                command=self.load_penpals_button_event)
        self.load_penpals_button.grid(row=8, column=1, columnspan=1, pady=20, padx=20, sticky="sw")

        # ============ frame_left ============
        # Integrated browser frame
        # Create canvas
        self.canvas_left_browser = customtkinter.CTkCanvas(
            master=self.frame_left_browser, width=self.frame_left_width)
        self.canvas_left_browser.pack(side="left", fill="y")

        # Create second frame_left
        self.frame_left_second_browser = customtkinter.CTkFrame(
            master=self.canvas_left_browser, width=self.frame_left_width)

        # Create window inside canvas
        self.canvas_left_browser.create_window((0,0), window=self.frame_left_second_browser, anchor="nw")

        # configure grid layout (1x11)
        self.frame_left_second_browser.grid_rowconfigure(0, minsize=10)   # empty row with minsize as spacing
        self.frame_left_second_browser.grid_rowconfigure(len(count) + 2, weight=1)  # empty row as spacing


        self.penpal_label_progress = customtkinter.CTkLabel(master=self.frame_left_second_browser,
                                              text="Penpals",
                                              text_font=(self.typewriter_font, -30), width=(self.frame_left_width - 20))
        self.penpal_label_progress.grid(row=1, column=0, pady=10, padx=10)


        # Progress bar frame
        # Create canvas
        self.canvas_left_progress = customtkinter.CTkCanvas(master=self.frame_left_progress, width=self.frame_left_width)
        self.canvas_left_progress.pack(side="left", fill="y")

        # Create scrollbar
        self.left_scrollbar_progress = customtkinter.CTkScrollbar(
            master=self.frame_left_progress, orientation="vertical", command=self.canvas_left_progress.yview, width=20)
        self.left_scrollbar_progress.pack(side="left", fill="y")

        # Configure canvas
        self.canvas_left_progress.configure(yscrollcommand=self.left_scrollbar_progress.set)
        self.canvas_left_progress.bind(
            "<Configure>", lambda e: self.canvas_left_progress.configure(
                scrollregion=self.canvas_left_progress.bbox("all")))

        # Create second frame_left
        self.frame_left_second_progress = customtkinter.CTkFrame(
            master=self.canvas_left_progress, width=self.frame_left_width)

        # Create window inside canvas
        self.canvas_left_progress.create_window((0, 0), window=self.frame_left_second_progress, anchor="nw")

        # configure grid layout (1x11)
        self.frame_left_second_progress.grid_rowconfigure(0, minsize=10)  # empty row with minsize as spacing
        self.frame_left_second_progress.grid_rowconfigure(len(count) + 2, weight=1)  # empty row as spacing

        self.penpal_label_browser = customtkinter.CTkLabel(master=self.frame_left_second_progress,
                                              text="Penpals",
                                              text_font=(self.typewriter_font, -30), width=(self.frame_left_width - 20))
        self.penpal_label_browser.grid(row=1, column=0, pady=10, padx=10)


        self.check_var_dict = {}
        # Button creation
        for index, penpal in enumerate(self.count):
            # check_var = customtkinter.IntVar()
            self.check_var_dict[index] = customtkinter.IntVar()
            self.penpal_checkbox = customtkinter.CTkCheckBox(
                master=self.frame_left_second_progress,
                text=f"{penpal}",
                text_font=("Roboto Medium", -20),
                variable=self.check_var_dict[index])
            self.penpal_checkbox.grid(row=(index + 2), column=0, pady=5, padx=20, sticky="nw")
        # print(f"index 0:{self.check_var_list[0]}")

        self.check_button = customtkinter.CTkButton(master=self.frame_bottom_progress,
                                                text="Show state",
                                                text_font=(self.typewriter_font, -20),
                                                border_width=2,  # <- custom border_width
                                                fg_color=None,  # <- no fg_color
                                                command=self.penpal_checkbox_event)
        self.check_button.grid(row=8, column=0, columnspan=1, pady=20, padx=20, sticky="sw")


        # ============ frame_right ============
        # Integrated browser
        dir_path = os.getcwd()
        cache = os.path.join(dir_path, "cef_cache")
        settings = {"auto_zooming": "-1.0"} # "cache_path": cache,
        cef.Initialize(settings=settings) # Add settings
        self.browser_frame = BrowserFrame(self.frame_right_browser)
        self.browser_frame.pack(fill="both", expand=1, anchor="e", side="left")

        # Progress bar
        self.progress_bar_title = customtkinter.CTkLabel(master=self.frame_right_progress, text="This is a test",
                                                text_font=("Roboto Medium", -30))
        self.progress_bar_title.place(x=(self.frame_right_width//2), y=210, anchor="center")

        self.progressbar = customtkinter.CTkProgressBar(master=self.frame_right_progress, width=500, height=40)
        self.progressbar.place(x=(self.frame_right_width//2), y=260, anchor="center")

        self.progress_bar_footer = customtkinter.CTkLabel(master=self.frame_right_progress,
                                                          text="Letter 5O out of 1OO",
                                                          text_font=("Roboto Medium", -25))
        self.progress_bar_footer.place(x=(self.frame_right_width // 2), y=310, anchor="center")

        # Loading penpals screen
        self.loading_title = customtkinter.CTkLabel(master=self.frame_right_loading,
                                                    text="Loading penpals\nPlease wait...",
                                                    text_font=(self.typewriter_font, -30))
        self.loading_title.place(x=(self.frame_right_width // 2), y=210, anchor="center")

        # Set global frame IDs
        App.FRAME_RIGHT_ID = self.frame_right.winfo_name()
        App.FRAME_RIGHT_BROWSER_ID = self.frame_right_browser.winfo_name()
        App.FRAME_RIGHT_PROGRESS_ID = self.frame_right_progress.winfo_name()
        App.FRAME_RIGHT_LOADING_ID = self.frame_right_loading.winfo_name()
        self.print_ids()
        print(self.frame_right.pack_slaves())



    def print_ids(self):
        print(f"frame_right: {App.FRAME_RIGHT_ID}")
        print(f"frame_right_browser: {App.FRAME_RIGHT_BROWSER_ID}")
        print(f"frame_right_progress: {App.FRAME_RIGHT_PROGRESS_ID}")
        print(f"frame_right_loading: {App.FRAME_RIGHT_LOADING_ID}")



    def get_browser(self):
        if self.browser_frame:
            return self.browser_frame.browser
        return None

    def get_browser_frame(self):
        if self.browser_frame:
            return self.browser_frame
        return None

    def penpal_checkbox_event(self):
        for chosen_penpal_index in self.check_var_dict.keys():
            if self.check_var_dict[chosen_penpal_index].get() == 1:
                print(f"{self.penpals[chosen_penpal_index]}")
        # print(f"checkbox 1 state: {self.check_var_dict[0].get()}")
        # self.test_label = customtkinter.CTkLabel(master=self.frame_bottom_progress, text=self.check_var_dict[0])
        # self.test_label.place(x=(self.frame_right_width // 2), y=400, anchor="center")

    def run_button_event(self):
        print("run button pressed")

    def load_penpals_button_event(self):
        # print("load penpals button pressed")
        # print(f"name: {self.frame_right.winfo_name()}")
        # print(f"children: {self.frame_right.winfo_children}")
        # print(f"pack slaves: {self.frame_right.pack_slaves()}")

        self.frame_right_browser.forget()
        self.frame_right_loading.pack(expand=1, fill="both")
        # self.frame_right_loading.focus()
        self.frame_right.update()
        if App.FRAME_RIGHT_LOADING_ID == re.search(id_regex, str(self.frame_right.pack_slaves())).group(1):
            self.open_selenium()
        else:
            pass

        # print(f"progress: {self.frame_right_progress.pack_info()}")
        # print(f"loading: {self.frame_right.pack_slaves()}")
        # print(f"loading: {self.frame_right.pack_slaves()}")
        # time.sleep(5)
        # self.wait_window()
        # self.open_selenium()

    def open_selenium(self):
        print("opening selenium")
        open_chrome()

    def not_logged_in(self):
        self.frame_right_loading.forget()
        self.frame_right_browser.pack(expand=1, fill="both")
        self.frame_right.update()

    def switch_to_progress(self):
        self.frame_right_browser.forget()
        # BrowserFrame.on_root_close() # no idea if integrated browser is closing or not
        # cef.Shutdown()
        # cef.Shutdown()
        # self.browser_frame.browser.CloseBrowser(True)
        self.frame_bottom_browser.forget()
        self.frame_left_browser.forget()
        self.frame_bottom_progress.pack(anchor="se", side="bottom")
        self.frame_right_progress.pack(expand=1, fill="both")
        self.frame_left_progress.pack(side="left", fill="both")


    # def change_appearance_mode(self, new_appearance_mode):
    #     customtkinter.set_appearance_mode(new_appearance_mode)

    def on_closing(self, event=0):
        self.destroy()

class BrowserFrame(tk.Frame):

    WIDTH = App.WIDTH
    FRAME_RIGHT_WIDTH = (WIDTH - (WIDTH // 3))

    def __init__(self, master):
        print("init")
        self.closing = False
        self.browser = None
        tk.Frame.__init__(self, master)
        # self.app_title = tk.Label(self, text="This is a test", anchor="center")
        self.bind("<Configure>", self.on_configure)
        # self.embed_browser()
        self.focus_set()

    def embed_browser(self):
        print("embed")
        window_info = cef.WindowInfo()
        rect = [0, 0, BrowserFrame.FRAME_RIGHT_WIDTH, self.winfo_height()]
        window_info.SetAsChild(self.get_window_handle(), rect)
        self.browser = cef.CreateBrowserSync(window_info, url="https://web.slowly.app/")
        assert self.browser
        # self.browser.SetClientCallback("OnLoadEnd", self.OnLoadEnd)
        # self.browser.GetUrl()
        self.message_loop_work()

    # def OnLoadEnd(browser, frame, httpCode):
    #     print("onload")
    #     if frame == browser.GetMainFrame():
    #     # if frame == self.browser.GetMainFrame():
    #         print("Finished loading main frame: %s (http code = %d)"
    #               % (frame.GetUrl(), httpCode))
    #     # else:
    #     #     print("Hello!")

    def get_window_handle(self):
        if self.winfo_id() > 0:
            return self.winfo_id()
        else:
            raise Exception("Couldn't obtain window handle")

    def message_loop_work(self):
        cef.MessageLoopWork()
        self.after(10, self.message_loop_work)

    def on_configure(self, _):
        if not self.browser:
            self.embed_browser()

    def on_root_close(self):
        if self.browser:
            self.browser.CloseBrowser(True)
            self.clear_browser_references()
        self.destroy()

    def clear_browser_references(self):
        self.browser = None

def open_chrome():
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
    # options.add_argument(f"user-data-dir={user_data_path}")
    # options.add_argument("--headless")
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
    # wait = WebDriverWait(driver, 30)
    chrome_main(driver)

def scroll_down(driver):
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

def check_for_photos(driver):
    if len(driver.find_elements(By.XPATH, dot_xpath)) > 0:
        return True
    else:
        return False

def photo_amount(driver):
    photos = driver.find_element(By.XPATH, dot_xpath)
    photos_innerhtml = photos.get_attribute('innerHTML')
    search = re.findall(dot_regex, photos_innerhtml)
    photo_count = len(search)
    return photo_count

def make_pdf(driver, letter_count, penpal_dir, penpal):
    letter = driver.find_element(By.XPATH, signature_xpath)
    innerhtml = letter.get_attribute('innerHTML')
    username = re.search(signature_regex, innerhtml).group(1)
    date = re.search(signature_regex, innerhtml).group(2)
    pdf_name = f"letter{letter_count}_{username}_{date}.pdf"
    file = "SLOWLY.pdf"

    # Checks for left over SLOWLY.pdf files and removes if present
    if exists(f"{download_path}\\{file}"):
        os.remove(f"{download_path}\\{file}")
    # Checks if letter already exists in penpal dir, and skips over it
    if exists(f"{penpal_dir}\\{file}"):
        os.remove(f"{penpal_dir}\\{file}")
        # return print("Letter already exists! \nSkipping...") # unnecessary

    # Prints letter as PDF with name "SLOWLY.pdf" in download_path
    print(f"Printing letter {letter_count}")
    driver.execute_script("window.print()")
    time.sleep(2)

    # Moves PDF into penpal_dir and renames it to pdf_name
    os.replace(f"{download_path}\\{file}", f"{penpal_dir}\\{file}") # Moves SLOWLY.pdf into penpal_dir
    os.rename(f"{penpal_dir}\\{file}", f"{penpal_dir}\\{pdf_name}") # Renames SLOWLY.pdf to pdf_name var

    # Write meta information into PDF file
    data = PdfReader(f"{penpal_dir}\\{pdf_name}")
    data.Info.Letter = letter_count
    data.Info.Penpal = penpal
    os.remove(f"{penpal_dir}\\{pdf_name}")
    PdfWriter(f"{penpal_dir}\\{pdf_name}", trailer=data).write()

    if exists(f"{penpal_dir}\\{pdf_name}"):
        print(f"Letter {letter_count} successfully printed!")
    else:
        print(f"Letter {letter_count} failed to print.")

def open_letter(driver, letter_int, letter_count, penpal_dir, penpal):
    letters = driver.find_elements(By.XPATH, xpath)
    letter = letters[letter_int]
    letter.click()
    time.sleep(1)
    scroll_down(driver)
    photos_exist = check_for_photos(driver)
    if photos_exist:
        amount = photo_amount(driver)
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
    make_pdf(driver, letter_count, penpal_dir, penpal)
    print("Going back to letters...")

def mk_penpal_dir(penpal):
    penpal_dir = os.path.join(download_path, penpal)
    if exists(penpal_dir):
        print("Penpal downloaded directory already exists in 'letters' folder.")
    else:
        print(f"Making download directory for {penpal}")
        os.mkdir(penpal_dir)
    return penpal_dir

# def gui(count):
#     app=App(count)
#     print("opening GUI")
#     app.mainloop()

def chrome_main(driver):
    attempt = 0
    while driver.current_url != home_url and attempt <= 10:
        print(f"Load attempt {attempt} failed!")
        time.sleep(1)
        attempt += 1
    if driver.current_url != home_url:
        driver.close()
        print("Closing Selenium")
        app.not_logged_in()
        return print("Login not detected\nPlease try again")
    else:
        pass
    print("Successful login detected! \nPlease select a penpal.")

    # Why no work?!
    # try:
    #     WebDriverWait(driver, 30).until(
    #         EC.presence_of_element_located((By.XPATH, penpals_xpath)))
    # finally:
    #     pass
    time.sleep(3) # Bandaid until above is fixed
    available_penpals = driver.find_elements(By.XPATH, penpals_xpath)
    penpals_list = []
    for available_penpal in available_penpals:
        penpal = available_penpal.get_attribute('outerHTML')
        penpal_name = re.search(penpals_regex, penpal).group(1)
        penpals_list.append(penpal_name)
    # gui(penpals_list)


    while re.search(current_url_regex, driver.current_url).group(2) != "friend":
        pass
    print("Penpal selected!")
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, xpath)))
        print("Loading letters")
        scroll_down(driver)
    finally:
        pass

    # mkdir with name of penpal
    penpal_name_obtain = driver.find_element(By.XPATH, penpal_xpath).get_attribute('innerHTML')
    penpal = re.search(penpal_regex, penpal_name_obtain).group(1)
    penpal_dir = mk_penpal_dir(penpal)

    # check penpal name and letter count on PDFs if they currently exist within the penpals directory.
    existing_letters = [] # currently useless
    for penpal_file in os.listdir(penpal_dir):
        if penpal_file.endswith(".pdf"):
            penpal_file_path = os.path.join(penpal_dir, penpal_file)
            meta_check = PdfReader(penpal_file_path).Info
            for key, value in meta_check.items():
                if key == "/Letter":
                    # value = int(re.search("\((\d*)\)", value).group(1))
                    # int_value = int(value)
                    # int_minus_one = (int_value - 1)
                    existing_letters.append(int(value))
    # print(existing_letters)
    # find letters and count how many have been sent/received on SLOWLY
    letters = driver.find_elements(By.XPATH, xpath)
    current_letter_int = len(letters) # tracks which letter is currently being processed
    amount_letters = current_letter_int # amount of letters available to download

    for letter in range(0, amount_letters):
        # print(letter)
        if (current_letter_int) in existing_letters:
            print("Letter already exists! \nSkipping...")
            current_letter_int -= 1
        else:
            open_letter(driver, letter, current_letter_int, penpal_dir, penpal)
            current_letter_int -= 1
            back_button = driver.find_element(By.XPATH, back_button_xpath)
            back_button.click()
            time.sleep(2)
    else:
        print(f"{amount_letters} letters successfully printed!")
        driver.quit()

def main():
    # penpals_list = []
    # app = App(penpals_list)
    print("opening GUI")
    app.mainloop()
    # if app.current_frame_state() == "init":
    #     print("YAY!")
    # else:
    #     print(":(")
    # gui(penpals_list)
    print("Hello!")

if __name__ == '__main__':
    penpals_list = []
    app = App(penpals_list)
    main()