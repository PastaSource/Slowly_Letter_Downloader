import logging
import os
from os.path import exists
from datetime import datetime

# Paths
dir_path = os.getcwd()
log_path = os.path.join(dir_path, "logs")
download_path = os.path.join(dir_path, "letters")
chrome_executable_path = os.path.join(dir_path, "Chrome-bin\\chrome.exe")
chrome_sync_path = os.path.join(dir_path, "chrome.sync.7z")
user_data_path = os.path.join(dir_path, "sessions")
cef_cache = os.path.join(dir_path, "cef_cache")
interface_path = os.path.join(dir_path, "interface")
venv_path = os.path.join(dir_path, "venv\\Lib\\site-packages")
compiled_path = os.path.join(dir_path, "lib")
settings_button_image_path = os.path.join(interface_path, "settings_button.png")

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


def show_folder_layout():
    folder_layout = os.listdir(dir_path)
    logger.debug("Root path items:")
    for item in folder_layout:
        logger.debug(os.path.join(dir_path, item))
        logger.debug("Module path items:")
    try:
        module_layout = os.listdir(compiled_path)
        module_path = compiled_path
    except:
        try:
            module_layout = os.listdir(venv_path)
            module_path = venv_path
        except Exception as e:
            logger.critical(e)
            return logger.critical("No module path could be found!!!")
    for item in module_layout:
        logger.debug(os.path.join(module_path, item))


try:
    import base64
    import ctypes
    import re
    import winreg
    import _winapi
    import json
    import time
    import urllib.request
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import TimeoutException
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver import Chrome, ChromeOptions
    from subprocess import CREATE_NO_WINDOW
    from pdfrw import PdfReader, PdfWriter
    import platform
    from cefpython3 import cefpython as cef
    import cefpython3
    import customtkinter
    import tkinter as tk
    from PIL import ImageTk, Image
    from itertools import count, cycle
    import pyglet
    import shutil
    import stat
    import inspect
    import threading
    from textwrap import dedent
except Exception as e:
    logger.critical(e)
    show_folder_layout()
    os._exit(1)
else:
    logger.debug("Modules successfully imported!")

# Platforms
WINDOWS = (platform.system() == "Windows")
LINUX = (platform.system() == "Linux")
MAC = (platform.system() == "Darwin")

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
letter_xpath = "//div[@class='col-6 col-xl-4 mb-3']"  # Letter outer HTML
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


def chrome_installed():
    try:
        reg_connection = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        winreg.OpenKeyEx(reg_connection, r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\chrome.exe")
    except:
        return False
    else:
        logger.debug("Chrome installation successfully found")
        return True


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
        self.reporthook_counter = 0  # reporthook for download progress
        self.loading_circle_loaded = False  # reports whether loading circle gif is currently loaded
        self.penpals = []
        self.check_var_dict = {}
        self.driver = None
        self.dpi = self.winfo_fpixels('1i')
        logger.info(f"DPI = {self.dpi}")

        self.title("Slowly Letter Downloader")
        self.bind
        self.bind("<Configure>", self.on_root_configure)
        # self.bind("<Configure>", self.on_configure)
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed
        self.iconbitmap(os.path.join(interface_path, "SLD_icon.ico"))

        self.count = count
        self.typewriter_font = "Mom´sTypewriter"

        # ============ create frames ============
        # Configure frame layout
        # self.grid_columnconfigure(1, weight=1)
        # self.grid_rowconfigure(0, weight=1)
        self.frame_left_scrollbar_width = 20
        self.frame_left_width = (App.WIDTH // 3)
        self.frame_right_width = (App.WIDTH - self.frame_left_width)

        self.frame_top = customtkinter.CTkFrame(
            master=self,
            height=100
        )
        self.frame_top.pack(anchor="n", fill="x")

        self.frame_left = customtkinter.CTkFrame(
            master=self,
            width=self.frame_left_width
        )
        self.frame_left.pack(side="left", fill="both")

        self.frame_bottom = customtkinter.CTkFrame(
            master=self,
            width=self.frame_right_width,
            height=100,
            fg_color=slowly_bg,
            bg_color=slowly_bg

        )
        self.frame_bottom.pack(side="bottom", fill="x")

        self.frame_right = customtkinter.CTkFrame(
            master=self,
            width=self.frame_right_width
        )
        self.frame_right.pack(anchor="e", expand=1, fill="both")
        self.frame_right.bind("<Configure>", self.on_configure)  # Allow cefpython resizing

        # Penpals title frame
        self.frame_left_penpals_title = customtkinter.CTkFrame(
            master=self.frame_left
        )
        self.frame_left_penpals_title.pack(side="top", expand=0, anchor="n")

        # Frames integrated browser
        self.frame_right_browser = customtkinter.CTkFrame(
            master=self.frame_right,
            width=self.frame_right_width
        )
        self.frame_right_browser.pack(expand=1, fill="both")

        self.frame_bottom_browser = customtkinter.CTkFrame(
            master=self.frame_bottom,
            fg_color=slowly_bg,
            bg_color=slowly_bg
        )
        self.frame_bottom_browser.pack(anchor="s", side="bottom")

        self.frame_left_browser = customtkinter.CTkFrame(
            master=self.frame_left,
            width=self.frame_left_width,
            fg_color=slowly_fg,
            bg_color=slowly_fg
        )
        self.frame_left_browser.pack(side="left", fill="both")

        # Frames progress bar
        self.frame_right_progress = customtkinter.CTkFrame(master=self.frame_right)

        self.frame_bottom_progress_l = customtkinter.CTkFrame(
            master=self.frame_bottom,
            fg_color=slowly_bg,
            bg_color=slowly_bg
        )

        self.frame_bottom_progress_r = customtkinter.CTkFrame(
            master=self.frame_bottom,
            fg_color=slowly_bg,
            bg_color=slowly_bg
        )

        self.frame_left_progress = customtkinter.CTkFrame(
            master=self.frame_left,
            width=self.frame_left_width - self.frame_left_scrollbar_width,
            fg_color=slowly_fg,
            bg_color=slowly_fg
        )

        # Frames loading penpals
        self.frame_right_loading = customtkinter.CTkFrame(
            master=self.frame_right
        )

        # Frames downloading chrome
        self.frame_right_download_chrome = customtkinter.CTkFrame(
            master=self.frame_right
        )

        # ============ frame_top ============
        self.app_title = customtkinter.CTkLabel(
            master=self.frame_top,
            text="Slowly Letter Downloader",
            text_font=(self.typewriter_font, -45)
        )
        # self.app_title.place(x=(App.WIDTH / 2), y=50, anchor="center")
        self.app_title.pack(anchor="center", pady=25)

        # ============ frame_bottom ============
        # self.frame_bottom.grid_columnconfigure(0, weight=3)
        # self.frame_bottom.grid_columnconfigure(1, weight=3)
        #
        # self.frame_bottom_browser.grid_columnconfigure(0, weight=0)
        # self.frame_bottom_browser.grid_columnconfigure(1, weight=1)
        # self.frame_bottom_progress.grid_columnconfigure(0, weight=0)
        # self.frame_bottom_progress.grid_columnconfigure(1, weight=2)
        # self.frame_bottom_progress.grid_columnconfigure(2, weight=2)
        # Integrated browser frame
        logger.debug(f"settings_button.png exists? {exists(settings_button_image_path)}")
        self.settings_button_image_open = Image.open(settings_button_image_path)
        self.settings_button_image = ImageTk.PhotoImage(self.settings_button_image_open)

        self.open_settings_button = customtkinter.CTkButton(
            master=self.frame_bottom_browser,
            image=self.settings_button_image,
            text="",
            fg_color=("#F7F7F7", "#1b1d24"),
            height=30,
            width=30,
            command=self.settings_popup
        )
        self.open_settings_button.grid(row=0, column=0, pady=20, padx=20, sticky="w")

        # self.load_penpals_button = customtkinter.CTkButton(
        #     master=self.frame_bottom_browser,
        #     text="Load Penpals",
        #     text_font=(self.typewriter_font, -20),
        #     text_color="#000000",
        #     fg_color=slowly_yellow,
        #     command=self.load_penpals_button_event
        # )
        # self.load_penpals_button.grid(row=8, column=1, columnspan=1, pady=20, padx=20, sticky="e")

        # Progress bar frame
        self.run_button = customtkinter.CTkButton(
            master=self.frame_bottom_progress_r,
            text="Run",
            text_font=(self.typewriter_font, -20),
            text_color="#000000",
            fg_color=slowly_yellow,
            command=self.run_button_click
        )
        self.run_button.grid(row=0, column=2, columnspan=3, pady=20, padx=20, sticky="se")

        self.select_all_button = customtkinter.CTkButton(
            master=self.frame_bottom_progress_r,
            text="Select All", text_font=(self.typewriter_font, -20),
            text_color="#000000",
            fg_color=slowly_yellow,
            command=self.select_all_button_event
        )
        self.select_all_button.grid(row=0, column=1, columnspan=1, pady=20, padx=20, sticky="sw")

        self.open_settings = customtkinter.CTkButton(
            master=self.frame_bottom_progress_l,
            image=self.settings_button_image,
            text="",
            fg_color=("#F7F7F7", "#1b1d24"),
            height=30,
            width=30,
            command=self.settings_popup
        )
        self.open_settings.grid(row=0, column=0, pady=18, padx=20, sticky="w")
        # self.open_settings.place(x=0, y=0, anchor="center")

        # ============ frame_left ============
        # Penpal label
        self.penpal_label = customtkinter.CTkLabel(
            master=self.frame_left_penpals_title,
            text="Penpals",
            text_font=(self.typewriter_font, -30),
            width=(self.frame_left_width - 20)
        )
        self.penpal_label.grid(row=1, column=0, pady=12, padx=12)
        # Integrated browser frame

        # Progress bar frame
        # Create canvas
        self.canvas_left_progress = customtkinter.CTkCanvas(
            master=self.frame_left_progress,
            width=self.frame_left_width - self.frame_left_scrollbar_width
        )
        self.canvas_left_progress.pack(side="left", fill="both")

        # Create scrollbar
        self.left_scrollbar_progress = customtkinter.CTkScrollbar(
            master=self.frame_left_progress,
            orientation="vertical",
            command=self.canvas_left_progress.yview,
            width=self.frame_left_scrollbar_width
        )
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
        self.canvas_left_progress.create_window(
            (0, 0),
            window=self.frame_left_second_progress,
            anchor="nw",
            width=self.frame_left_width
        )

        # configure grid layout (1x11)
        self.frame_left_second_progress.grid_rowconfigure(0, minsize=10)  # empty row with minsize as spacing
        self.frame_left_second_progress.grid_rowconfigure(len(count) + 2, weight=1)  # empty row as spacing

        # ============ frame_right ============
        # Integrated browser
        self.open_cefpython()
        self.browser_frame = BrowserFrame(self.frame_right_browser)
        self.browser_frame.pack(fill="both", expand=1, anchor="e", side="left")

        # Download letters progress bar
        self.progress_bar_title = customtkinter.CTkLabel(
            master=self.frame_right_progress,
            text="Select penpal(s)",
            text_font=("Roboto Medium", -30)
        )
        self.progress_bar_title.place(x=(self.frame_right_width // 2), y=260, anchor="center")

        # Download Chrome progress bar
        # self.progress_bar_download_chrome = customtkinter.CTkLabel(master=self.frame_right_download_chrome,
        #                                                  text="Downloading Chrome...",
        #                                                  text_font=("Roboto Medium", -30))
        # self.progress_bar_download_chrome.place(x=(self.frame_right_width // 2), y=260, anchor="center")

        # Loading penpals screen
        self.loading_frame_init()

        # Set global frame IDs
        App.FRAME_RIGHT_ID = self.frame_right.winfo_name()
        App.FRAME_RIGHT_BROWSER_ID = self.frame_right_browser.winfo_name()
        App.FRAME_RIGHT_PROGRESS_ID = self.frame_right_progress.winfo_name()
        App.FRAME_RIGHT_LOADING_ID = self.frame_right_loading.winfo_name()

    def load_gif(self, gif_frame):
        self.selected_gif_frame = gif_frame
        gif = os.path.join(interface_path, 'loading_circle.gif')

        if isinstance(gif, str):
            gif = Image.open(gif)
        frames = []

        try:
            for i in count(1):
                frames.append(ImageTk.PhotoImage(gif.copy()))
                gif.seek(i)
        except EOFError:
            pass
        self.gif_frames = cycle(frames[1:])
        try:
            self.gif_delay = gif.info['duration']
        except:
            self.gif_delay = 100

        self.loading_circle_loaded = True
        self.next_gif_frame()

    def next_gif_frame(self):
        if self.gif_frames:
            self.selected_gif_frame.configure(image=next(self.gif_frames))
            self.after(self.gif_delay, self.next_gif_frame)

    def unload_gif(self):
        self.loading_gif_label.configure(image=None)
        self.gif_frames = None
        self.loading_circle_loaded = False

    def loading_frame_init(self):
        self.frame_right_loading.grid_rowconfigure((0, 3), weight=1)
        self.frame_right_loading.grid_columnconfigure(0, weight=1)

        self.loading_title = customtkinter.CTkLabel(
            master=self.frame_right_loading,
            text="Loading penpals\nPlease wait...",
            text_font=(self.typewriter_font, -30)
        )
        # self.loading_title.place(x=(self.frame_right_width // 2), y=210, anchor="center")
        self.loading_title.grid(
            row=1,
            column=0,
            sticky='nsew'
        )

        self.loading_gif_label = customtkinter.CTkLabel(
            master=self.frame_right_loading
        )
        self.loading_gif_label.grid(
            row=2,
            column=0,
            sticky='nsew'
        )

    def loading_frame_load(self):
        self.frame_right_loading.pack(expand=1, fill="both")
        self.load_gif(self.loading_gif_label)

    def loading_frame_unload(self):
        self.unload_gif()
        self.frame_right_loading.forget()

    def settings_popup(self):
        self.settings_window = customtkinter.CTkToplevel(self)
        self.settings_window.title("Settings")
        self.settings_window.geometry("400x200")
        # self.grid_columnconfigure(1, weight=1)

        self.settings_popup_label = customtkinter.CTkLabel(self.settings_window,
                                                           text="SLD Settings",
                                                           text_font=(self.typewriter_font, -25))
        # settings_popup_label.grid(row=1, column=1, columnspan=1, pady=20, padx=20)
        self.settings_popup_label.pack(anchor="center", side="top", pady=20)

        self.appearance_selector = customtkinter.CTkOptionMenu(
            master=self.settings_window,
            values=["System", "Light", "Dark"],
            command=self.change_appearance_mode,
            text_font=(self.typewriter_font, -20),
            text_color="#000000"
        )
        # self.appearance_selector.grid(row=2, column=1, columnspan=1, pady=20, padx=20)
        self.appearance_selector.pack(anchor="center", pady=20)

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
        try:
            self.browser_frame.destroy()  # Closes cefpython integrated browser
            logger.info("Shutting down cefpython3 integrated browser")
            self.browser_frame.browser.CloseBrowser(True)
            # cef.QuitMessageLoop()
            # MAY BE IMPOSSIBLE TO START UP AGAIN ONCE SHUTDOWN
            cef.Shutdown()
            self.unbind("<Configure>")
            self.frame_right.unbind("<Configure>")
            self.frame_right_browser.forget()
        except Exception as e:
            logger.critical(e)
        else:
            logger.debug("successfully shut down cefpython")
        # if exists(chrome_executable_path):
        #     pass
        # else:
        #     self.download_chrome()

        logger.debug("packing frame_right_loading")
        # self.frame_right_loading.pack(expand=1, fill="both")
        self.loading_frame_load()
        self.frame_right.update()
        self.cache_cef_to_selenium()
        # penpals = ["test1", "test2", "test3"]
        # self.penpal_checkboxes(penpals)
        logger.info("calling self.open_selenium function")
        self.open_selenium()

    def cache_cef_to_selenium(self):
        # Check that cef_cache exists
        logger.debug(f"cef_cache = {cef_cache}")
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
        logger.debug("forgetting 'select_all_button'")
        self.select_all_button.destroy()
        logger.debug("gridding 'deselect_all_button'")
        self.deselect_all_button = customtkinter.CTkButton(
            master=self.frame_bottom_progress_r,
            text="Deselect All", text_font=(self.typewriter_font, -20),
            text_color="#000000",
            fg_color=slowly_yellow,
            command=self.deselect_all_button_event
        )
        self.deselect_all_button.grid(row=0, column=1, columnspan=1, pady=20, padx=20, sticky="sw")
        logger.debug("selecting all penpals")
        for chosen_penpal_index in self.check_var_dict.keys():
            if self.check_var_dict[chosen_penpal_index].get() == 1:
                pass
            if self.check_var_dict[chosen_penpal_index].get() == 0:
                self.check_var_dict[chosen_penpal_index].set(1)
        self.frame_left.update()
        self.frame_bottom_progress_r.update()
        self.frame_bottom.update()
        logger.info("select all button pressed")

    def deselect_all_button_event(self):
        logger.debug("forgetting 'dselect_all_button'")
        self.deselect_all_button.destroy()
        logger.debug("gridding 'select_all_button'")
        self.select_all_button = customtkinter.CTkButton(
            master=self.frame_bottom_progress_r,
            text="Select All", text_font=(self.typewriter_font, -20),
            text_color="#000000",
            fg_color=slowly_yellow,
            command=self.select_all_button_event
        )
        self.select_all_button.grid(row=0, column=1, columnspan=1, pady=20, padx=20, sticky="sw")
        logger.debug("deselecting all penpals")
        for chosen_penpal_index in self.check_var_dict.keys():
            if self.check_var_dict[chosen_penpal_index].get() == 1:
                self.check_var_dict[chosen_penpal_index].set(0)
            if self.check_var_dict[chosen_penpal_index].get() == 0:
                pass
        self.frame_left.update()
        self.frame_bottom_progress_r.update()
        self.frame_bottom.update()
        logger.info("deselect all button pressed")

    def deactivate_buttons(self):
        logger.debug("Deactivating buttons")
        if self.run_button.state == "normal":
            self.run_button.configure(state="disabled")
        try:
            if self.select_all_button.state == "normal":
                self.select_all_button.configure(state="disabled")
        except:
            if self.deselect_all_button.state == "normal":
                self.deselect_all_button.configure(state="disabled")

    def reactivate_buttons(self):
        logger.debug("Reactivating buttons")
        if self.run_button.state == "disabled":
            self.run_button.configure(state="normal")
        try:
            if self.select_all_button.state == "disabled":
                self.select_all_button.configure(state="normal")
        except:
            if self.deselect_all_button.state == "disabled":
                self.deselect_all_button.configure(state="normal")

    def run_button_click(self):
        logger.info("run button pressed")
        # thread = threading.Thread(
        #     target=self.run_button_event()
        # )
        # thread.start()
        self.deactivate_buttons()
        self.run_button_event()

    def run_button_event(self):
        logger.info("run button event")
        if exists(download_path):
            logger.info("Letter path already exists")
        else:
            logger.info("Letter path not found\nCreating path...")
            os.mkdir(download_path)
        penpal_xpath_list = available_penpals(self.driver)

        try:
            self.frame_right_progress_soft_reset()
        except Exception as e:
            logger.error("error with frame_right_progress_reset function")
            logger.error(e)
        else:
            logger.debug("frame_right_progress_reset function successfully ran")

        thread = threading.Thread(
            target=penpal_select_loop,
            args=(
                self.driver,
                self.penpals,
                penpal_xpath_list,
                self.check_var_dict
            )
        )
        thread.start()

    def run_button_end(self):
        logger.debug("Finished printing")
        # self.frame_right_progress_reset()
        # self.frame_right_progress_idle()

        # Printing process finished, now switching back to idle frame_right_progress frame
        try:
            self.frame_right_progress_reset()
        except Exception as e:
            logger.error("error with frame_right_progress_reset function")
            logger.error(e)
        else:
            logger.debug("frame_right_progress_reset function successfully ran")

        try:
            self.frame_right_progress_idle()
        except Exception as e:
            logger.error("error with frame_right_progress_idle function")
            logger.error(e)
        else:
            logger.debug("frame_right_progress_idle function successfully ran")

        self.reactivate_buttons()

        self.loading_circle_loaded = False
        logger.debug("End of run_button_event")

    def set_progress_bar(self, letter_amount, current_letter, penpal):
        self.frame_right_progress.grid_rowconfigure((0, 4), weight=1)
        self.frame_right_progress.grid_columnconfigure(0, weight=1)

        # try:
        #     self.unload_gif()
        # except Exception:
        #     pass

        self.progress_bar_title = customtkinter.CTkLabel(
            master=self.frame_right_progress,
            text=f"{penpal}",
            text_font=("Roboto Medium", -30)
        )
        # self.progress_bar_title.place(x=(self.frame_right_width // 2), y=210, anchor="center")
        self.progress_bar_title.grid(
            row=1,
            column=0,
            sticky='nsew'
        )

        # Removed as I feel this is redundant because we already have the progress_bar_footer
        # Will replace with a progress circle
        # self.progressbar = customtkinter.CTkProgressBar(
        #     master=self.frame_right_progress,
        #     width=500,
        #     height=40,
        # )
        # self.progressbar.set((current_letter / letter_amount))
        # self.progressbar.place(x=(self.frame_right_width // 2), y=260, anchor="center")

        if self.loading_circle_loaded == False:
            self.progress_circle = customtkinter.CTkLabel(
                master=self.frame_right_progress,
                text=""
            )
        self.progress_circle.grid(
            row=2,
            column=0,
            sticky='nsew'
        )

        self.progress_bar_footer = customtkinter.CTkLabel(
            master=self.frame_right_progress,
            text=f"Letter {current_letter} out of {letter_amount}",
            text_font=("Roboto Medium", -25)
        )
        # self.progress_bar_footer.place(x=(self.frame_right_width // 2), y=310, anchor="center")
        self.progress_bar_footer.grid(
            row=3,
            column=0,
            sticky='nsew'
        )

        self.frame_right.update()
        if self.loading_circle_loaded == False:
            self.load_gif(self.progress_circle)
        else:
            pass
        # time.sleep(0.2)

    def frame_right_progress_soft_reset(self):
        try:
            self.frame_right_progress.destroy()
        except Exception as e:
            logger.error(e)
        else:
            logger.debug("frame_right_progress destroyed")
        self.frame_right_progress = customtkinter.CTkFrame(master=self.frame_right)
        # self.frame_right_progress.forget()
        self.frame_right_progress.pack(expand=1, fill="both")

    def frame_right_progress_reset(self):
        try:
            self.frame_right_progress.destroy()
        except Exception as e:
            logger.error(e)
        else:
            logger.debug("frame_right_progress destroyed")
        self.frame_right_progress = customtkinter.CTkFrame(master=self.frame_right)
        # self.frame_right_progress.forget()
        self.frame_right_progress.pack(expand=1, fill="both")
        logger.debug("Deselecting printed penpals from checkbox list")
        for chosen_penpal_index in self.check_var_dict.keys():
            if self.check_var_dict[chosen_penpal_index].get() == 1:
                self.check_var_dict[chosen_penpal_index].set(0)
            if self.check_var_dict[chosen_penpal_index].get() == 0:
                pass
        self.frame_left.update()

    def frame_right_progress_idle(self):
        self.progress_bar_title = customtkinter.CTkLabel(
            master=self.frame_right_progress,
            text="Select penpal(s)",
            text_font=("Roboto Medium", -30)
        )
        self.progress_bar_title.place(x=(self.frame_right_width // 2), y=260, anchor="center")

    def open_selenium(self):
        logger.info("opening selenium")
        thread = threading.Thread(target=open_chrome)
        thread.start()
        # open_chrome()

    def open_cefpython(self):
        logger.info("Starting cefpython3")
        cefpython3_path = os.path.dirname(os.path.abspath(inspect.getsourcefile(cefpython3)))
        logger.debug(f"cefpython3 path: {cefpython3_path}")
        self.cef_settings = {
            'locales_dir_path': os.path.join(cefpython3_path, "locales"),
            'resources_dir_path': os.path.join(cefpython3_path),
            'browser_subprocess_path': os.path.join(cefpython3_path, "subprocess.exe"),
            'log_file': os.path.join(cefpython3_path, "debug.log"),
            "cache_path": cef_cache,
            "auto_zooming": "-1.0"
            # "windowless_rendering_enabled": "0"
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
        logger.debug("starting cef try statement")
        try:
            cef.Initialize(settings=self.cef_settings)  # Add settings
        except Exception as e:
            logger.critical(e)
            self.on_closing()
        else:
            logger.info("cefpython successfully initiated")

    def not_logged_in(self):
        logger.info("Login not detected!")
        logger.debug("forgetting frame_right_loading")
        # self.frame_right_loading.forget()
        self.loading_frame_unload()
        logger.debug("Calling open_cefpython function")
        self.open_cefpython()
        logger.debug("Packing frame_right_browser")
        self.frame_right_browser.pack(expand=1, fill="both")
        logger.debug("Updating frame_right")
        self.frame_right.update()
        self.open_settings.wait_variable()

    def switch_to_progress(self):
        logger.info("switch to progress")
        logger.debug("Forget frame_bottom_browser")
        self.frame_bottom_browser.forget()
        logger.debug("Forget frame_right_loading")
        # self.frame_right_loading.forget()
        self.loading_frame_unload()
        logger.debug("Forget frame_left_browser")
        self.frame_left_browser.forget()
        logger.debug("Packing progress frames")
        self.frame_bottom_progress_l.pack(anchor="se", side="left")
        self.frame_bottom_progress_r.pack(anchor="sw", side="right")
        self.frame_right_progress.pack(expand=1, fill="both")
        self.frame_left_progress.pack(side="left", fill="both")
        logger.debug("Updating frames left, right, and bottom")
        self.frame_bottom.update()
        self.frame_right.update()
        self.frame_left.update()
        logger.debug("Initiate run_button.wait_variable()")
        self.run_button.wait_variable()

    def download_chrome_progress(self):
        self.progress_bar_download_chrome_title = customtkinter.CTkLabel(
            master=self.frame_right_download_chrome,
            text="Downloading Chrome...",
            text_font=("Roboto Medium", -30)
        )
        # self.progress_bar_download_chrome_title.place(x=(self.frame_right_width // 2), y=210, anchor="center")
        self.progress_bar_download_chrome_title.grid(
            row=1,
            column=0,
            sticky="nsew"
        )

        self.progress_bar_footer = customtkinter.CTkLabel(
            master=self.frame_right_download_chrome,
            text="This will only happen once",
            text_font=("Roboto Medium", -25)
        )
        # self.progress_bar_footer.place(x=(self.frame_right_width // 2), y=310, anchor="center")
        self.progress_bar_footer.grid(
            row=3,
            column=0,
            sticky="nsew"
        )
        self.frame_right.update()

    def reporthook(self, count, block_size, total_size):
        # percent = int(count * block_size * 100 / total_size)
        downloaded = count * block_size
        downloaded_mb = int(downloaded / 1024 / 1024)
        if downloaded_mb > self.reporthook_counter:
            self.reporthook_counter = downloaded_mb
            self.download_text.set(f"{int(downloaded / 1024 / 1024)}mb / {int(total_size / 1024 / 1024)}mb")
        else:
            pass

    def download_chrome(self):
        if exists(chrome_executable_path):
            pass
        else:
            # self.frame_right_loading.forget()
            self.loading_frame_unload()

            self.frame_right_download_chrome.pack(expand=1, fill="both")
            self.frame_right_download_chrome.grid_rowconfigure((0, 4), weight=1)
            self.frame_right_download_chrome.grid_columnconfigure(0, weight=1)

            self.download_chrome_progress()
            try:
                import py7zr
            except Exception as e:
                logger.critical(e)
                os._exit(0)
            else:
                logger.debug("Successfully imported py7zr")
            if exists(chrome_sync_path):
                try:
                    os.remove(chrome_sync_path)
                except Exception as e:
                    logger.error(e)
            else:
                pass

            # self.progress_bar_chrome = customtkinter.CTkProgressBar(
            #     master=self.frame_right_download_chrome,
            #     width=500,
            #     height=40,
            # )
            # Progress bar might be slowing things down?

            self.download_text = customtkinter.StringVar()
            self.download_text.set("0mb / 0mb")
            self.progress_bar_chrome = customtkinter.CTkLabel(
                master=self.frame_right_download_chrome,
                textvariable=self.download_text,
                text_font=("Arial", -25)
            )
            self.progress_bar_chrome.grid(
                row=2,
                column=0,
                sticky="nsew",
            )

            chrome_url = get_current_chrome()
            # chrome_latest_url = urllib.request.urlopen("https://github.com/Hibbiki/chromium-win64/releases/latest")
            # updated_url = re.sub("tag", "download", chrome_latest_url.geturl())
            # chrome_url = f"{updated_url}/chrome.sync.7z"

            urllib.request.urlretrieve(
                chrome_url,
                'chrome.sync.7z',
                self.reporthook
            )
            # pyunpack.Archive(chrome_sync_path).extractall(dir_path)
            with py7zr.SevenZipFile(chrome_sync_path, mode='r') as archive:
                archive.extractall(path=dir_path)
            os.remove(chrome_sync_path)
            self.frame_right_download_chrome.forget()
            # Back to loading! We did it! We downloaded Chrome! Woohoo!
            # self.frame_right_loading.pack(expand=1, fill="both")
            self.loading_frame_load()

    def on_root_configure(self, _):
        logger.debug("MainFrame.on_root_configure")
        if self.browser_frame:
            self.browser_frame.on_root_configure()

    def on_configure(self, event):
        logger.debug("App.on_configure")
        if self.browser_frame:
            width = event.width
            height = event.height
            self.browser_frame.on_mainframe_configure(width, height)

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
    FRAME_RIGHT_WIDTH = (WIDTH - (WIDTH // 3)) + 13

    def __init__(self, master):
        logger.info("init")
        self.closing = False
        self.browser = None
        tk.Frame.__init__(self, master)
        self.bind("<Configure>", self.on_configure)
        self.focus_set()

    def embed_browser(self):
        logger.info("embed browser")
        window_info = cef.WindowInfo()
        rect = [0, 0, self.winfo_width(), self.winfo_height() + 17]
        window_info.SetAsChild(self.get_window_handle(), rect)
        self.browser = cef.CreateBrowserSync(window_info, url="https://web.slowly.app/")
        # logger.info(self.browser.GetUrl())
        assert self.browser

        self.message_loop_work()

    def get_window_handle(self):
        if self.winfo_id() > 0:
            return self.winfo_id()
        else:
            raise Exception("Couldn't obtain window handle")

    def message_loop_work(self):
        cef.MessageLoopWork()
        self.after(10, self.message_loop_work)

        # Scans current URL for changes and starts the load_penpals_button_event function when a change is detected
        if self.browser.GetUrl() != home_url:
            pass
        else:
            logger.debug(f"current cefpython URL: {self.browser.GetUrl()}")
            logger.info("cefpython3 login detected, initiating load penpals sequence")
            app.load_penpals_button_event()

        # print(self.browser.GetUrl())

    def on_configure(self, _):
        if not self.browser:
            self.embed_browser()

    def on_root_configure(self):
        # Root <Configure> event will be called when top window is moved
        if self.browser:
            self.browser.NotifyMoveOrResizeStarted()

    def on_mainframe_configure(self, width, height):
        if self.browser:
            if WINDOWS:
                ctypes.windll.user32.SetWindowPos(
                    self.browser.GetWindowHandle(), 0,
                    0, 0, width, height, 0x0002)
            elif LINUX:
                self.browser.SetBounds(0, 0, width, height)
            self.browser.NotifyMoveOrResizeStarted()

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
        scroll_pause_time = 1  # was originally 2, halved it and am hoping for the best
        # ideally we'd have something a bit more robust for scrolling rather than just an arbitrary number
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
        try:
            popup.click()
        except Exception as e:
            logger.error(f"Error clicking popup: {popup}")
            logger.error(e)
        else:
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
    # time.sleep(1) # I can't remember why I put this time.sleep here, I'll comment it and hope for the best.

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


def log_current_url(driver):
    logger.debug(f"Current URL: {driver.current_url}")


def image_load_check(driver):
    page_load = driver.execute_script("return document.readyState")
    if page_load == "complete":
        print("page loaded, counting images")
        images = driver.execute_script("return document.images.length")
        print(images)
        loaded_count = 0
        while loaded_count != images:
            for image in range(images):
                result = driver.execute_script(f"return document.images[{image}].complete")
                if result:
                    loaded_count += 1
            print(f"loaded: {loaded_count}, to load: {images}")
        print("Done! All images should be loaded!")


def open_letter(driver, letter_int, letter_count, penpal_dir, penpal):
    log_current_url(driver)
    letters = driver.find_elements(By.XPATH, letter_xpath)
    logger.debug(f"Penpal: {penpal}, letter count: {len(letters)}, letter_int: {letter_int}")
    letter = letters[letter_int]
    try:
        letter.click()
    except Exception as e:
        logger.critical(e)
    else:
        logger.debug(f"Letter {letter} clicked")
    time.sleep(1)
    scroll_down(driver)
    photos_exist = check_for_photos(driver)
    if photos_exist:
        amount = photo_amount(driver)
        next_button = driver.find_element(By.XPATH, next_button_xpath)
        logger.info("Loading images...")
        for clicker in range(0, amount - 1):
            try:
                next_button.click()
            except Exception as e:
                logger.error(e)
            time.sleep(0.5)
        logger.info("Please allow time for the images to properly load.")
        # time.sleep(5)
        image_load_check(driver)
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


def penpal_select_loop(driver, penpals, xpath_list, penpal_dict):
    for chosen_penpal_index in penpal_dict.keys():
        if penpal_dict[chosen_penpal_index].get() == 1:
            logger.info(f"Loading {penpals[chosen_penpal_index]}")
            penpal_select(
                driver,
                chosen_penpal_index,
                penpals[chosen_penpal_index],
                xpath_list
            )
        else:
            pass
    app.run_button_end()


def penpal_select(driver, chosen_penpal_int, chosen_penpal_name, available_penpals):
    logger.info("Selecting penpal")
    chosen_penpal = available_penpals[chosen_penpal_int]
    logger.info("Clicking penpal")
    try:
        chosen_penpal.click()
    except Exception as e:
        logger.critical(e)
    else:
        logger.debug(f"Clicked {chosen_penpal}")
    driver = driver
    load_and_print(driver, chosen_penpal_name)

    # next_button = driver.find_element(By.XPATH, next_button_xpath)
    # next_button.click()
    return logger.debug("end of penpal_select function")


def load_and_print(driver, penpal):
    logger.info("Waiting until current URL matches penpal URL")
    # Wait until URL matches expected friend URL
    while re.search(current_url_regex, driver.current_url).group(2) != "friend":
        pass
    logger.info(f"Penpal {penpal} selected!")

    # Scroll down to load all letters
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, letter_xpath)))
        logger.info("Loading letters")
        scroll_down(driver)
    except TimeoutException:
        logger.critical("Could not load letters :(")
    else:
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
                    existing_letters.append(int(value))
    # logger.info(existing_letters)
    # find letters and count how many have been sent/received on SLOWLY
    letters = driver.find_elements(By.XPATH, letter_xpath)
    current_letter_int = len(letters)  # tracks which letter is currently being processed
    amount_letters = current_letter_int  # amount of letters available to download
    logger.debug("load_and_print")
    logger.debug(f"Letter count: {len(letters)}")

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
            try:
                back_button.click()
            except Exception as e:
                logger.critical(e)
            time.sleep(2)
    else:
        logger.info(f"{amount_letters} letters successfully printed!")

    # driver.quit()
    # chrome_running = False
    return logger.debug("end of load and print function")


def get_current_chrome():
    chrome_latest_url = urllib.request.urlopen("https://github.com/Hibbiki/chromium-win64/releases/latest")
    updated_url = re.sub("tag", "download", chrome_latest_url.geturl())
    chrome_url = f"{updated_url}/chrome.sync.7z"
    return chrome_url

def open_chrome():
    logger.debug("Setting Chrome options")
    options = ChromeOptions()
    logger.debug("Checking for Chrome installation")
    if chrome_installed() == True:
        logger.info("Chrome installation found")
    else:
        logger.info("Initiating Chrome download")
        app.download_chrome()
        logger.info("Chrome download process finished")
        options.binary_location = chrome_executable_path
    # try:
    #     reg_connection = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    #     winreg.OpenKeyEx(reg_connection, r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\chrome.exe")
    # except Exception as e:
    #     logger.debug(f"{e}")
    #     logger.info("Initiating Chrome download")
    #     app.download_chrome()
    #     logger.info("Chrome download process finished")
    #     options.binary_location = chrome_executable_path
    # else:
    #     logger.info("Chrome installation found")
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
        # Had to comment out show_download_progress(resp) from http.py file to stop NoneType error
        chrome_url = get_current_chrome()
        latest_version_code = re.search(r"v(\d*)", chrome_url)
        driver_latest_url = urllib.request.urlopen(
            f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{latest_version_code.group(1)}"
        )
        driver_html_bytes = driver_latest_url.read()
        driver_latest = driver_html_bytes.decode("utf-8")
        chrome_service = Service(ChromeDriverManager(path=r".\\drivers", version=driver_latest).install())
        chrome_service.creationflags = CREATE_NO_WINDOW
        driver = Chrome(service=chrome_service, options=options)
        logger.info("Opening Slowly")
        driver.get(website)
    except Exception as e:
        logger.critical(e, exc_info=True)
        app.on_closing()

    # wait = WebDriverWait(driver, 30)
    chrome_running = True
    chrome_main(driver)


def chrome_main(driver):
    logger.debug("chrome_main init")
    logger.debug("Attempting to login using selenium")
    attempt = 0
    while driver.current_url != home_url and attempt <= 10:
        logger.warning(f"Load attempt {attempt} failed!")
        time.sleep(1)
        # tk.Tk.after(1000, logger.debug("after(1000) complete"))
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
    logger.debug("chrome_main WebDriverWait")
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, penpals_xpath)))
    except TimeoutException:
        logger.critical("Could not load penpals_xpath :(")
    else:
        logger.debug("penpals_xpath found! Yay!!!")
    # logger.debug("time.sleep(3)")
    # time.sleep(3)  # Bandaid until above is fixed
    # tk.Tk.after(1000, logger.debug("after(1000) complete"))
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
