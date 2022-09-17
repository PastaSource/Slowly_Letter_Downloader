import base64
import re
import os
from os.path import exists
import winreg
import _winapi
import json
import time
import urllib.request
import py7zr
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome, ChromeOptions
from pdfrw import PdfReader, PdfWriter
from cefpython3 import cefpython as cef
import cefpython3
import customtkinter
import tkinter as tk
import pyglet
import logging
from datetime import datetime
import shutil
import stat
import inspect

# Paths
dir_path = os.getcwd()
log_path = os.path.join(dir_path, "logs")
download_path = os.path.join(dir_path, "letters")
# chrome_path = os.path.join(dir_path, "chromium\\app\\Chrome-bin\\chrome.exe")
chrome_executable_path = os.path.join(dir_path, "Chrome-bin\\chrome.exe")
chrome_sync_path = os.path.join(dir_path, "chrome.sync.7z")
user_data_path = os.path.join(dir_path, "sessions")
cef_cache = os.path.join(dir_path, "cef_cache")
interface_path = os.path.join(dir_path, "interface")

# Logger setup
if exists(log_path):
    pass
else:
    os.mkdir(log_path)

now = datetime.now()
log_name_format = now.strftime("%Y.%m.%d_%H.%M.%S.log")
log_name = f"SLD_{log_name_format}"

log_file = os.path.join(log_path, log_name)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

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
xpath = "//div[@class='col-6 col-xl-4 mb-3']"  # Outer HTML
signature_xpath = "//div[@class='media-body mx-3 mt-2']"  # Finds name and date logger.infoed on letter
dot_xpath = "//ul[@class='slick-dots']"
next_button_xpath = "//button[@class='slick-arrow slick-next']"
back_button_xpath = "//a[@class='no-underline link py-2 px-2 ml-n2 col-pixel-width-50 flip active']"
penpal_xpath = "//div[@class='col-9 pt-2']"
penpals_xpath = "//h6[@class='col pl-0 pr-0 mt-1 mb-0 text-truncate ']"  # Used to create list of all penpals
popup_xpath = "//button[@class='Toastify__close-button Toastify__close-button--warning']"

# colors
slowly_bg = ("#F7F7F7", "#1b1d24")
slowly_fg = ("#FFFFFF", "#2b2f39")
slowly_yellow = ("#F9C32B", "#f9c32b")

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

chrome_running = False


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

    colour_scheme_path = os.path.join(interface_path, "yellow.json")
    customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    customtkinter.set_default_color_theme(colour_scheme_path)  # Themes: "blue" (standard), "green", "dark-blue"

    def __init__(self, count):
        super().__init__()
        # self.tk.call('tk', 'scaling', 3.0)
        # self.call('tk', 'scaling', 3.0)
        # ctypes.windll.shcore.SetProcessDpiAwareness(2)

        self.browser_frame = None
        self.penpals = []
        self.check_var_dict = {}
        self.driver = None
        self.dpi = self.winfo_fpixels('1i')
        logger.info(f"DPI = {self.dpi}")

        self.title("Slowly Letter Downloader")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed
        self.iconbitmap(os.path.join(interface_path, "SLD_icon.ico"))

        self.count = count
        self.typewriter_font = "Mom´sTypewriter"

        # ============ create frames ============
        # Configure frame layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.frame_left_scrollbar_width = 20
        self.frame_left_width = (App.WIDTH // 3)
        self.frame_right_width = (App.WIDTH - self.frame_left_width - self.frame_left_scrollbar_width)
        # May no longer need to have scrollbar_width subtracted since it's integrated into progress frame now ^^^

        self.frame_top = customtkinter.CTkFrame(master=self, height=100)
        self.frame_top.pack(anchor="n", fill="x")

        self.frame_left = customtkinter.CTkFrame(master=self,
                                                 width=self.frame_left_width
                                                 )
        self.frame_left.pack(side="left", fill="both")

        self.frame_bottom = customtkinter.CTkFrame(master=self, width=self.frame_right_width, height=100)
        self.frame_bottom.pack(anchor="se", side="bottom")

        self.frame_right = customtkinter.CTkFrame(master=self, width=self.frame_right_width)
        self.frame_right.pack(anchor="e", expand=1, fill="both")

        # Penpals title frame
        self.frame_left_penpals_title = customtkinter.CTkFrame(master=self.frame_left)
        self.frame_left_penpals_title.pack(side="top", expand=0, anchor="n")

        # Frames integrated browser
        self.frame_right_browser = customtkinter.CTkFrame(master=self.frame_right)
        self.frame_right_browser.pack(expand=1, fill="both")

        self.frame_bottom_browser = customtkinter.CTkFrame(master=self.frame_bottom)
        self.frame_bottom_browser.pack(anchor="se", side="bottom")

        self.frame_left_browser = customtkinter.CTkFrame(master=self.frame_left,
                                                         width=self.frame_left_width,
                                                         fg_color=slowly_fg,
                                                         bg_color=slowly_fg
                                                         )
        self.frame_left_browser.pack(side="left", fill="both")

        # Frames progress bar
        self.frame_right_progress = customtkinter.CTkFrame(master=self.frame_right)

        self.frame_bottom_progress = customtkinter.CTkFrame(master=self.frame_bottom)

        self.frame_left_progress = customtkinter.CTkFrame(master=self.frame_left,
                                                          width=self.frame_left_width - self.frame_left_scrollbar_width,
                                                          fg_color=slowly_fg,
                                                          bg_color=slowly_fg
                                                          )

        # Frames loading penpals
        self.frame_right_loading = customtkinter.CTkFrame(master=self.frame_right)

        # Frames downloading chrome
        self.frame_right_download_chrome = customtkinter.CTkFrame(master=self.frame_right)

        # ============ frame_top ============
        self.app_title = customtkinter.CTkLabel(master=self.frame_top, text="Slowly Letter Downloader",
                                                text_font=(self.typewriter_font, -45))
        self.app_title.place(x=(App.WIDTH / 2), y=50, anchor="center")

        # ============ frame_bottom ============
        # Integrated browser frame
        # self.run_button = customtkinter.CTkButton(master=self.frame_bottom_browser,
        #                                           text="Run", text_font=(self.typewriter_font, -20),
        #                                           border_width=2,  # <- custom border_width
        #                                           fg_color=None,  # <- no fg_color
        #                                           command=self.run_button_event)
        # self.run_button.grid(row=8, column=2, columnspan=1, pady=20, padx=20, sticky="se")

        self.appearance_selector = customtkinter.CTkOptionMenu(master=self.frame_bottom_browser,
                                                               values=["System", "Light", "Dark"],
                                                               command=self.change_appearance_mode,
                                                               text_font=(self.typewriter_font, -20),
                                                               text_color="#000000")
        self.appearance_selector.grid(row=8, column=0, columnspan=1, pady=20, padx=20, sticky="w")


        self.load_penpals_button = customtkinter.CTkButton(master=self.frame_bottom_browser,
                                                           text="Load Penpals",
                                                           text_font=(self.typewriter_font, -20),
                                                           text_color="#000000",
                                                           fg_color=slowly_yellow,
                                                           command=self.load_penpals_button_event)
        self.load_penpals_button.grid(row=8, column=1, columnspan=1, pady=20, padx=20, sticky="e")

        # Progress bar frame
        self.run_button = customtkinter.CTkButton(master=self.frame_bottom_progress,
                                                  text="Run",
                                                  text_font=(self.typewriter_font, -20),
                                                  text_color="#000000",
                                                  fg_color=slowly_yellow,
                                                  command=self.run_button_event)
        self.run_button.grid(row=8, column=2, columnspan=1, pady=20, padx=20, sticky="se")

        self.select_all_button = customtkinter.CTkButton(master=self.frame_bottom_progress,
                                                           text="Select All", text_font=(self.typewriter_font, -20),
                                                           text_color="#000000",
                                                           fg_color=slowly_yellow,
                                                           command=self.select_all_button_event)
        self.select_all_button.grid(row=8, column=1, columnspan=1, pady=20, padx=20, sticky="sw")

        self.appearance_selector = customtkinter.CTkOptionMenu(master=self.frame_bottom_progress,
                                                               values=["System", "Light", "Dark"],
                                                               command=self.change_appearance_mode,
                                                               text_font=(self.typewriter_font, -20),
                                                               text_color="#000000")
        self.appearance_selector.grid(row=8, column=0, columnspan=1, pady=20, padx=20, sticky="w")

        # self.check_button = customtkinter.CTkButton(master=self.frame_bottom_progress,
        #                                             text="Show state",
        #                                             text_font=(self.typewriter_font, -20),
        #                                             border_width=2,  # <- custom border_width
        #                                             fg_color=None,  # <- no fg_color
        #                                             command=self.penpal_checkbox_event)
        # self.check_button.grid(row=8, column=0, columnspan=1, pady=20, padx=20, sticky="sw")

        # ============ frame_left ============
        # Penpal label
        self.penpal_label = customtkinter.CTkLabel(master=self.frame_left_penpals_title,
                                                           text="Penpals",
                                                           text_font=(self.typewriter_font, -30),
                                                           width=(self.frame_left_width - 20))
        self.penpal_label.grid(row=1, column=0, pady=12, padx=12)
        # Integrated browser frame



        # Progress bar frame
        # Create canvas
        self.canvas_left_progress = customtkinter.CTkCanvas(master=self.frame_left_progress,
                                                            width=self.frame_left_width -
                                                                  self.frame_left_scrollbar_width)
        self.canvas_left_progress.pack(side="left", fill="both")

        # Create scrollbar
        self.left_scrollbar_progress = customtkinter.CTkScrollbar(
            master=self.frame_left_progress,
            orientation="vertical",
            command=self.canvas_left_progress.yview,
            width=self.frame_left_scrollbar_width)
        self.left_scrollbar_progress.pack(side="left", fill="y")

        # Configure canvas
        self.canvas_left_progress.configure(yscrollcommand=self.left_scrollbar_progress.set)

        self.canvas_left_progress.bind(
            "<Configure>", lambda e: self.canvas_left_progress.configure(
                scrollregion=self.scroll_bbox()))

        # Create second frame_left
        self.frame_left_second_progress = customtkinter.CTkFrame(
            master=self.canvas_left_progress,
            width=self.frame_left_width - self.frame_left_scrollbar_width,
            fg_color=slowly_fg,
            bg_color=slowly_fg
        )

        # Create window inside canvas
        self.canvas_left_progress.create_window((0, 0), window=self.frame_left_second_progress, anchor="nw", width=self.frame_left_width)

        # configure grid layout (1x11)
        self.frame_left_second_progress.grid_rowconfigure(0, minsize=10)  # empty row with minsize as spacing
        self.frame_left_second_progress.grid_rowconfigure(len(count) + 2, weight=1)  # empty row as spacing

        # ============ frame_right ============
        # Integrated browser
        self.open_cefpython()
        self.browser_frame = BrowserFrame(self.frame_right_browser)
        self.browser_frame.pack(fill="both", expand=1, anchor="e", side="left")

        # Download letters progress bar
        self.progress_bar_title = customtkinter.CTkLabel(master=self.frame_right_progress,
                                                         text="Select penpal(s)",
                                                         text_font=("Roboto Medium", -30))
        self.progress_bar_title.place(x=(self.frame_right_width // 2), y=260, anchor="center")

        # Download Chrome progress bar
        # self.progress_bar_download_chrome = customtkinter.CTkLabel(master=self.frame_right_download_chrome,
        #                                                  text="Downloading Chrome...",
        #                                                  text_font=("Roboto Medium", -30))
        # self.progress_bar_download_chrome.place(x=(self.frame_right_width // 2), y=260, anchor="center")

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

    #     self.logger.info_ids()
    #     logger.info(self.frame_right.pack_slaves())
    #
    # def logger.info_ids(self):
    #     logger.info(f"frame_right: {App.FRAME_RIGHT_ID}")
    #     logger.info(f"frame_right_browser: {App.FRAME_RIGHT_BROWSER_ID}")
    #     logger.info(f"frame_right_progress: {App.FRAME_RIGHT_PROGRESS_ID}")
    #     logger.info(f"frame_right_loading: {App.FRAME_RIGHT_LOADING_ID}")

    def change_appearance_mode(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def scroll_bbox(self):
        '''Modifies self.canvas_left_progress.bbox to remove 2 white pixels at the top and bottom
        of the penpal checkbox list'''
        self.bbox = self.canvas_left_progress.bbox("all")
        self.bbox_mod = list(self.bbox)
        self.bbox_mod[1] = 2
        self.bbox_mod[3] = self.bbox_mod[3] - 2
        # logger.critical(f"BBOX VALUE: {self.bbox_mod}")
        return self.bbox_mod

    def get_browser(self):
        if self.browser_frame:
            return self.browser_frame.browser
        return None

    def get_browser_frame(self):
        if self.browser_frame:
            return self.browser_frame
        return None

    def load_penpals_button_event(self):
        # logger.info("load penpals button pressed")
        self.browser_frame.destroy()  # Closes cefpython integrated browser
        self.browser_frame.browser.CloseBrowser(True)
        cef.Shutdown()
        self.frame_right_browser.forget()
        # if exists(chrome_executable_path):
        #     pass
        # else:
        #     self.download_chrome()

        self.frame_right_loading.pack(expand=1, fill="both")
        self.frame_right.update()
        self.cache_cef_to_selenium()
        # penpals = ["test1", "test2", "test3"]
        # self.penpal_checkboxes(penpals)

        self.open_selenium()

    def cache_cef_to_selenium(self):
        # Check that cef_cache exists
        if exists(cef_cache):
            pass
        else:
            logger.error("cef_cache folder not found")
            return "Error, cef_cache folder not found!"

        if exists(user_data_path):
            logger.info(f"{user_data_path} already exists")
            pass
        else:
            logger.info(f"{user_data_path} not found, creating...")
            os.mkdir(user_data_path)

        sessions_root_dict = {
            "sessions_default": os.path.join(user_data_path, "Default"),
            "sessions_cache": os.path.join(user_data_path, "Default\\Cache"),
        }

        for session_path in sessions_root_dict.values():
            if exists(session_path):
                logger.info(f"{session_path} already exists")
                pass
            else:
                logger.info(f"Creating {session_path}")
                os.mkdir(session_path)

        # selenium subdirectories
        sessions_sub_dict = {
            "sessions_blob": [os.path.join(cef_cache, "blob_storage"),
                              os.path.join(user_data_path, "Default\\blob_storage")],
            "sessions_cache_cachedata": [os.path.join(cef_cache, "Cache"),
                                         os.path.join(user_data_path, "Default\\Cache\\Cache_Data")],
            "sessions_gpu": [os.path.join(cef_cache, "GPUCache"),
                             os.path.join(user_data_path, "Default\\GPUCache")],
            "sessions_localstorage": [os.path.join(cef_cache, "Local Storage"),
                                      os.path.join(user_data_path, "Default\\Local Storage")]
        }

        logger.info("Making symlink junctions...")
        for subdirs in sessions_sub_dict.values():
            # junction = self.is_junction(subdirs[1])
            # print(f"{subdirs[1]} is a junction? {junction}")
            if exists(subdirs[1]):
                logger.info(f"{subdirs[1]} already exists")
                if self.is_junction(subdirs[1]):
                    logger.info(f"{subdirs[1]} junction already exists")
                else:
                    self.junction_creation(subdirs[0], subdirs[1])
            else:
                self.junction_creation(subdirs[0], subdirs[1])
        logger.debug("Finished copying/creating junctions")

    def is_junction(self, path: str) -> bool:
        try:
            return bool(os.readlink(path))
        except OSError:
            return False

    def junction_creation(self, src, dst):
        try:
            _winapi.CreateJunction(src, dst)
            logger.info(f"making junction between {src} > {dst}")
        except Exception as e:
            logger.error(e)
            try:
                logger.info("Trying alternate copytree method")
                try:
                    self.chmodtree(src)
                    self.chmodtree(dst)
                    shutil.rmtree(dst)
                except Exception as e:
                    logger.error(e)
                shutil.copytree(src, dst)
                logger.info(f"Copying {src} > {dst}")
            except Exception as e:
                logger.error(e)
                # self.on_closing()
            else:
                logger.info("File copy attempt successful!!!")
        else:
            logger.info("Junction creation attempt successful!!!")

    def chmodtree(self, top):
        for root, dirs, files in os.walk(top, topdown=False):
            for name in files:
                filename = os.path.join(root, name)
                try:
                    logger.debug(f"chmoding {filename}")
                    os.chmod(filename, stat.S_IWUSR)
                    # os.remove(filename)
                    # shutil.rmtree(filename)
                    logger.debug(f"Successfully chmod {filename}")
                except Exception as e:
                    logger.error(e)


    def penpal_checkboxes(self, penpals, driver):
        # self.check_var_dict = {}
        # Button creation
        logger.debug("Set self.driver as driver")
        self.driver = driver
        self.penpals = penpals
        logger.info("loading penpals to GUI...")
        # logger.info(penpals)
        logger.debug("Create checkboxes from penpal list")
        for index, penpal in enumerate(penpals):
            self.check_var_dict[index] = customtkinter.IntVar()
            self.penpal_checkbox = customtkinter.CTkCheckBox(
                master=self.frame_left_second_progress,
                text=f"{penpal}",
                text_font=("Roboto Medium", -20),
                variable=self.check_var_dict[index]
                # bg_color=slowly_fg,
                # fg_color=slowly_fg
            )
            self.penpal_checkbox.grid(row=(index + 2), column=0, pady=5, padx=20, sticky="nw")
        # logger.info(self.check_var_dict)
        logger.debug("Updating frame_left_second_progress")
        self.frame_left_second_progress.update()
        logger.debug("Initiate switch_to_progress function")
        self.switch_to_progress()

    def penpal_checkbox_event(self):
        for chosen_penpal_index in self.check_var_dict.keys():
            if self.check_var_dict[chosen_penpal_index].get() == 1:
                logger.info(f"{self.penpals[chosen_penpal_index]}")

    def select_all_button_event(self):
        for chosen_penpal_index in self.check_var_dict.keys():
            if self.check_var_dict[chosen_penpal_index].get() == 1:
                pass
            if self.check_var_dict[chosen_penpal_index].get() == 0:
                self.check_var_dict[chosen_penpal_index].set(1)
        self.frame_left.update()
        logger.info("select all button pressed")

    def run_button_event(self):
        logger.info("run button pressed")
        if exists(download_path):
            logger.info("Letter path already exists")
        else:
            logger.info("Letter path not found\nCreating path...")
            os.mkdir(download_path)
        penpal_xpath_list = available_penpals(self.driver)
        for chosen_penpal_index in self.check_var_dict.keys():
            if self.check_var_dict[chosen_penpal_index].get() == 1:
                logger.info(f"Loading {self.penpals[chosen_penpal_index]}")
                penpal_select(self.driver, chosen_penpal_index, self.penpals[chosen_penpal_index], penpal_xpath_list)
            else:
                pass
        self.frame_right_progress_idle()

    def set_progress_bar(self, letter_amount, current_letter, penpal):

        self.progress_bar_title = customtkinter.CTkLabel(master=self.frame_right_progress, text=f"{penpal}",
                                                         text_font=("Roboto Medium", -30))
        self.progress_bar_title.place(x=(self.frame_right_width // 2), y=210, anchor="center")

        self.progressbar = customtkinter.CTkProgressBar(
            master=self.frame_right_progress,
            width=500,
            height=40,
        )
        self.progressbar.set((current_letter / letter_amount))
        self.progressbar.place(x=(self.frame_right_width // 2), y=260, anchor="center")

        self.progress_bar_footer = customtkinter.CTkLabel(master=self.frame_right_progress,
                                                          text=f"Letter {current_letter} out of {letter_amount}",
                                                          text_font=("Roboto Medium", -25))
        self.progress_bar_footer.place(x=(self.frame_right_width // 2), y=310, anchor="center")
        self.frame_right.update()
        # time.sleep(0.2)

    def frame_right_progress_reset(self):
        self.frame_right_progress.destroy()
        self.frame_right_progress = customtkinter.CTkFrame(master=self.frame_right)
        # self.frame_right_progress.forget()
        self.frame_right_progress.pack(expand=1, fill="both")

    def frame_right_progress_idle(self):
        self.progress_bar_title = customtkinter.CTkLabel(master=self.frame_right_progress, text="Select penpal(s)",
                                                         text_font=("Roboto Medium", -30))
        self.progress_bar_title.place(x=(self.frame_right_width // 2), y=260, anchor="center")

    def open_selenium(self):
        logger.info("opening selenium")
        open_chrome()

    def open_cefpython(self):
        logger.info("Starting cefpython3")
        cefpython3_path = os.path.dirname(os.path.abspath(inspect.getsourcefile(cefpython3)))
        logger.info(f"cefpython3 path: {cefpython3_path}")
        self.cef_settings = {
            'locales_dir_path': os.path.join(cefpython3_path, "locales"),
            'resources_dir_path': os.path.join(cefpython3_path),
            'browser_subprocess_path': os.path.join(cefpython3_path, "subprocess.exe"),
            'log_file': os.path.join(cefpython3_path, "debug.log"),
            "cache_path": cef_cache,
            "auto_zooming": "-1.0"
        }
        # try:
        #     # Here as a bandaid until I sort out permission issues
        #     # Lol "permission issues" could've \been  caused by Chromium and Chrome Driver persisting in background
        #     logger.info("Attempting to chmod cef_cache")
        #     self.chmodtree(cef_cache)
        # except Exception as e:
        #     logger.error(e)
        # else:
        #     logger.info("chmod cef_cache successful")
        try:
            cef.Initialize(settings=self.cef_settings)  # Add settings
        except Exception as e:
            logger.critical(e)
            self.on_closing()
        else:
            logger.info("cefpython successfully initiated")


    def not_logged_in(self):
        logger.info("Login not detected!")
        self.frame_right_loading.forget()
        logger.debug("Calling open_cefpython function")
        self.open_cefpython()
        logger.debug("Packing frame_right_browser")
        self.frame_right_browser.pack(expand=1, fill="both")
        logger.debug("Updating frame_right")
        self.frame_right.update()
        self.load_penpals_button.wait_variable()

    def switch_to_progress(self):
        logger.info("switch to progress")
        logger.debug("Forget frame_bottom_browser")
        self.frame_bottom_browser.forget()
        logger.debug("Forget frame_right_loading")
        self.frame_right_loading.forget()
        logger.debug("Forget frame_left_browser")
        self.frame_left_browser.forget()
        logger.debug("Packing progress frames")
        self.frame_bottom_progress.pack(anchor="se", side="bottom")
        self.frame_right_progress.pack(expand=1, fill="both")
        self.frame_left_progress.pack(side="left", fill="both")
        logger.debug("Updating frames left, right, and bottom")
        self.frame_bottom.update()
        self.frame_right.update()
        self.frame_left.update()
        logger.debug("Initiate run_button.wait_variable()")
        self.run_button.wait_variable()

    # def change_appearance_mode(self, new_appearance_mode):
    #     customtkinter.set_appearance_mode(new_appearance_mode)

    def download_chrome_progress(self):
        self.progress_bar_download_chrome_title = customtkinter.CTkLabel(master=self.frame_right_download_chrome,
                                                                         text="Downloading Chrome...",
                                                                         text_font=("Roboto Medium", -30))
        self.progress_bar_download_chrome_title.place(x=(self.frame_right_width // 2), y=210, anchor="center")

        # self.progress_bar_chrome = customtkinter.CTkProgressBar(
        #     master=self.frame_right_download_chrome,
        #     width=500,
        #     height=40,
        # )
        #
        # self.progress_bar_chrome.set(round((current / total), 3) * 10)
        # logger.info(round((current / total), 3) * 10)
        # self.progress_bar_chrome.place(x=(self.frame_right_width // 2), y=260, anchor="center")

        self.progress_bar_footer = customtkinter.CTkLabel(master=self.frame_right_download_chrome,
                                                          text="This will only happen once",
                                                          text_font=("Roboto Medium", -25))
        self.progress_bar_footer.place(x=(self.frame_right_width // 2), y=310, anchor="center")
        self.frame_right.update()

    def download_chrome(self):
        self.frame_right_loading.forget()
        self.frame_right_download_chrome.pack(expand=1, fill="both")
        if exists(chrome_executable_path):
            pass
        else:
            self.download_chrome_progress()
            if exists(chrome_sync_path):
                # Archive(chrome_sync_path).extractall(dir_path)
                with py7zr.SevenZipFile(chrome_sync_path, mode='r') as archive:
                    archive.extractall(path=dir_path)
                os.remove(chrome_sync_path)
            else:
                # wget.download(
                #     'https://github.com/Hibbiki/chromium-win64/releases/download/v105.0.5195.102-r856/chrome.sync.7z',
                #     dir_path,
                #     bar=self.download_chrome_progress
                # )

                urllib.request.urlretrieve(
                    'https://github.com/Hibbiki/chromium-win64/releases/download/v105.0.5195.102-r856/chrome.sync.7z',
                    'chrome.sync.7z'
                )
                # pyunpack.Archive(chrome_sync_path).extractall(dir_path)
                with py7zr.SevenZipFile(chrome_sync_path, mode='r') as archive:
                    archive.extractall(path=dir_path)
            os.remove(chrome_sync_path)
        self.frame_right_download_chrome.forget()

    def on_closing(self, event=0):
        logger.debug("Iniating shutdown sequence")
        if self.driver != None:
            self.driver.quit()
            logger.debug("Shutting down selenium driver")
        if self.browser_frame:
            self.browser_frame.destroy()
            self.browser_frame.browser.CloseBrowser(True)
            self.browser_frame.clear_browser_references()
            cef.Shutdown()
            logger.debug(f"cef WindowInfo: {cef.WindowInfo}")
            logger.debug("Shutting down cefpython")
        self.browser_frame.destroy()
        self.destroy()
        # sys.exit()
        logger.info("Program exit")
        os._exit(0)  # Won't close properly without this


# ============ Integrated Browser Frame Code ============
class BrowserFrame(tk.Frame):
    WIDTH = App.WIDTH
    FRAME_RIGHT_WIDTH = (WIDTH - (WIDTH // 3))

    def __init__(self, master):
        logger.info("init")
        self.closing = False
        self.browser = None
        tk.Frame.__init__(self, master)
        # self.app_title = tk.Label(self, text="This is a test", anchor="center")
        self.bind("<Configure>", self.on_configure)
        # self.embed_browser()
        self.focus_set()

    def embed_browser(self):
        logger.info("embed")
        window_info = cef.WindowInfo()
        rect = [0, 0, BrowserFrame.FRAME_RIGHT_WIDTH, self.winfo_height()]
        window_info.SetAsChild(self.get_window_handle(), rect)
        self.browser = cef.CreateBrowserSync(window_info, url="https://web.slowly.app/")
        assert self.browser
        # self.browser.SetClientCallback("OnLoadEnd", self.OnLoadEnd)
        # self.browser.GetUrl()
        self.message_loop_work()
        # self.close_browser()

    # def OnLoadEnd(browser, frame, httpCode):
    #     logger.info("onload")
    #     if frame == browser.GetMainFrame():
    #     # if frame == self.browser.GetMainFrame():
    #         logger.info("Finished loading main frame: %s (http code = %d)"
    #               % (frame.GetUrl(), httpCode))
    #     # else:
    #     #     logger.info("Hello!")

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


def scroll_down(driver):
    try:
        # Scrolls through letters to load them
        scroll_pause_time = 2
        page_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            logger.info("Scrolling...")
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


def popup_check(driver):
    # popups = False
    # driver.find_element(By.XPATH, popup_xpath)
    popup = driver.find_elements(By.XPATH, popup_xpath)
    if len(popup) >= 1:
        popup.click()
        logger.info("Popup closed!!!")
    else:
        logger.info("No popups detected, phew!")


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
    # file = "SLOWLY.pdf"
    #
    # # Checks for left over SLOWLY.pdf files and removes if present
    # if exists(f"{download_path}\\{file}"):
    #     os.remove(f"{download_path}\\{file}")
    # # Checks if letter already exists in penpal dir, and skips over it
    # if exists(f"{penpal_dir}\\{file}"):
    #     os.remove(f"{penpal_dir}\\{file}")
    #     # return logger.info("Letter already exists! \nSkipping...") # unnecessary

    # Prints letter as PDF with name "SLOWLY.pdf" in download_path
    logger.info(f"Printing letter {letter_count}")
    # driver.execute_script("window.logger.info();")
    pdf_data = driver.execute_cdp_cmd("Page.printToPDF", print_settings)
    with open(os.path.join(download_path, penpal_dir, pdf_name), 'wb') as file:
        file.write(base64.b64decode(pdf_data['data']))
    time.sleep(1)

    # # Moves PDF into penpal_dir and renames it to pdf_name
    # os.replace(f"{download_path}\\{file}", f"{penpal_dir}\\{file}")  # Moves SLOWLY.pdf into penpal_dir
    # os.rename(f"{penpal_dir}\\{file}", f"{penpal_dir}\\{pdf_name}")  # Renames SLOWLY.pdf to pdf_name var

    # Write meta information into PDF file
    data = PdfReader(f"{penpal_dir}\\{pdf_name}")
    data.Info.Letter = letter_count
    data.Info.Penpal = penpal
    os.remove(f"{penpal_dir}\\{pdf_name}")
    PdfWriter(f"{penpal_dir}\\{pdf_name}", trailer=data).write()

    if exists(f"{penpal_dir}\\{pdf_name}"):
        logger.info(f"Letter {letter_count} successfully printed!")
    else:
        logger.info(f"Letter {letter_count} failed to print.")


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
        logger.info("Loading images...")
        for clicker in range(0, amount - 1):
            next_button.click()
            time.sleep(0.5)
        logger.info("Please allow time for the images to properly load.")
        time.sleep(5)
    else:
        pass

    # may be able to use isDisplay() method that returns a boolean if the image is displayed.
    # whether or not this will confirm if it is loaded or just being displayed, I'm not sure.
    # could use the driver.wait.until method for this (or whatever it is).
    make_pdf(driver, letter_count, penpal_dir, penpal)
    logger.info("Going back to letters...")


def mk_penpal_dir(penpal):
    penpal_dir = os.path.join(download_path, penpal)
    if exists(penpal_dir):
        logger.info("Penpal downloaded directory already exists in 'letters' folder.")
    else:
        logger.info(f"Making download directory for {penpal}")
        os.mkdir(penpal_dir)
    return penpal_dir


def quit_chrome(driver):
    return driver


def available_penpals(driver):
    penpals = driver.find_elements(By.XPATH, penpals_xpath)
    return penpals


def penpal_select(driver, chosen_penpal_int, chosen_penpal_name, available_penpals):
    logger.info("Selecting penpal")
    chosen_penpal = available_penpals[chosen_penpal_int]
    logger.info("Clicking penpal")
    chosen_penpal.click()
    driver = driver
    load_and_print(driver, chosen_penpal_name)

    # next_button = driver.find_element(By.XPATH, next_button_xpath)
    # next_button.click()


def load_and_print(driver, penpal):
    logger.info("Waiting until current URL matches penpal URL")
    # Wait until URL matches expected friend URL
    while re.search(current_url_regex, driver.current_url).group(2) != "friend":
        pass
    logger.info(f"Penpal {penpal} selected!")

    # Scroll down to load all letters
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, xpath)))
        logger.info("Loading letters")
        scroll_down(driver)
    finally:
        logger.info("Letters loaded!")
        pass

    # mkdir with name of penpal
    # penpal_name_obtain = driver.find_element(By.XPATH, penpal_xpath).get_attribute('innerHTML')
    # penpal = re.search(penpal_regex, penpal_name_obtain).group(1)
    penpal_dir = mk_penpal_dir(penpal)

    # check penpal name and letter count on PDFs if they currently exist within the penpals directory.
    logger.info("Checking for existing letters")
    existing_letters = []
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
    # logger.info(existing_letters)
    # find letters and count how many have been sent/received on SLOWLY
    letters = driver.find_elements(By.XPATH, xpath)
    current_letter_int = len(letters)  # tracks which letter is currently being processed
    amount_letters = current_letter_int  # amount of letters available to download

    # Printing process
    logger.info("Beginning letter printer process")
    for index, letter in enumerate(range(0, amount_letters)):
        # logger.info(letter)
        app.set_progress_bar(amount_letters, (index + 1), penpal)
        if current_letter_int in existing_letters:
            logger.info(f"Letter {current_letter_int} already exists! Skipping...")
            current_letter_int -= 1
        else:
            logger.info(f"Opening letter {current_letter_int}")
            open_letter(driver, letter, current_letter_int, penpal_dir, penpal)
            logger.info(f"Letter {current_letter_int} finished processing")
            current_letter_int -= 1
            back_button = driver.find_element(By.XPATH, back_button_xpath)
            back_button.click()
            time.sleep(2)
    else:
        logger.info(f"{amount_letters} letters successfully printeded!")
    app.frame_right_progress_reset()
    # driver.quit()
    chrome_running = False


def open_chrome():
    logger.debug("Setting Chrome options")
    options = ChromeOptions()
    logger.debug("Checking for Chrome installation")
    try:
        reg_connection = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        winreg.OpenKeyEx(reg_connection, r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\chrome.exe")
    except Exception as e:
        logger.debug(f"{e}")
        logger.info("Initiating Chrome download")
        app.download_chrome()
        logger.info("Chrome download process finished")
        options.binary_location = chrome_executable_path
    else:
        logger.info("Chrome installation found")
    options.add_argument("--start-maximized")
    options.add_argument('--window-size=1920,1080')
    options.add_argument(f"user-data-dir={user_data_path}")
    options.add_argument("--headless")
    options.add_argument('--enable-logger.info-browser')
    options.add_experimental_option("prefs", {  # May not be needed with new PDF logger.infoing implementation
        "printing.print_preview_sticky_settings.appState": json.dumps(print_settings),
        "savefile.default_directory": download_path,  # Change default directory for downloads
        "download.default_directory": download_path,  # Change default directory for downloads
        "download.prompt_for_download": False,  # To auto download the file
        "download.directory_upgrade": True,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "safebrowsing.enabled": True
    })
    options.add_argument("--kiosk-printing")

    logger.info("Starting selenium")
    try:
        # logger.info(f"EC path: {os.path.dirname(os.path.abspath(inspect.getsourcefile(EC)))}")
        # logger.info(f"WDW path: {os.path.dirname(os.path.abspath(inspect.getsourcefile(WebDriverWait)))}")
        # logger.info(f"By path: {os.path.dirname(os.path.abspath(inspect.getsourcefile(By)))}")
        # logger.info(f"CDM path: {os.path.dirname(os.path.abspath(inspect.getsourcefile(ChromeDriverManager)))}")
        # logger.info(f"SChrome path: {os.path.dirname(os.path.abspath(inspect.getsourcefile(Chrome)))}")
        # logger.info(f"ChromeO path: {os.path.dirname(os.path.abspath(inspect.getsourcefile(ChromeOptions)))}")
        # Had to comment out show_download_progress(resp) from http.py file to stop NoneType error
        driver = Chrome(service=Service(ChromeDriverManager().install()), options=options)
        logger.info("Opening Slowly")
        driver.get(website)
    except Exception as e:
        logger.critical(e, exc_info=True)
        app.on_closing()

    # wait = WebDriverWait(driver, 30)
    chrome_running = True
    chrome_main(driver)


def chrome_main(driver):
    logger.debug("Attempting to login using selenium")
    attempt = 0
    while driver.current_url != home_url and attempt <= 10:
        logger.warning(f"Load attempt {attempt} failed!")
        time.sleep(1)
        attempt += 1
    if driver.current_url != home_url:
        driver.close()
        logger.warning("Closing Selenium")
        app.not_logged_in()
        return logger.warning("Login not detected, please try again")
    else:
        pass
    logger.info("Successful login detected! Please select a penpal.")
    # logger.info(driver.current_url)
    # Why no work?!
    # try:
    #     WebDriverWait(driver, 30).until(
    #         EC.presence_of_element_located((By.XPATH, penpals_xpath)))
    # finally:
    #     pass
    logger.debug("time.sleep(3)")
    time.sleep(3)  # Bandaid until above is fixed
    logger.debug("Get list of available penpals via xpath")
    available_penpals = driver.find_elements(By.XPATH, penpals_xpath)
    penpals_list = []
    logger.debug("For loop to get penpal names")
    for available_penpal in available_penpals:
        penpal = available_penpal.get_attribute('outerHTML')
        penpal_name = re.search(penpals_regex, penpal).group(1)
        penpals_list.append(penpal_name)
    # create new function in app class that receives the penpals list and then have that function send that list to
    # the checkbutton for loop
    logger.debug("Start popup_check function")
    popup_check(driver)
    logger.debug("Send penpal list to app.penpal_checkboxes")
    app.penpal_checkboxes(penpals_list, driver)


def main():
    logger.info("opening GUI")
    app.mainloop()
    if chrome_running:  # Will probably remove at some point
        logger.info("Closing selenium from main()")
        driver = quit_chrome()  # might not work
        driver.quit()
    else:
        pass

    logger.info("End of script")


if __name__ == '__main__':
    penpals_list = []
    app = App(penpals_list)
    main()
