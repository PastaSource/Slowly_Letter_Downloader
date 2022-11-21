import cx_Freeze
import sys
# import base64
# import re
import os
from os.path import exists
# import _winapi
# import json
# import time
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver import Chrome, ChromeOptions
# from pdfrw import PdfReader, PdfWriter
# from cefpython3 import cefpython as cef
# import customtkinter
# import tkinter as tk
# import pyglet

dir_path = os.getcwd()
interface_path = os.path.join(dir_path, "interface")

base = None

if sys.platform == 'win32':
    base = 'Win32GUI'

options = {"build_exe": {
    "packages": [
        "base64",
        "re",
        "os",
        "inspect",
        "_winapi",
        "json",
        "time",
        "selenium",
        "webdriver_manager",
        "tqdm",
        "pdfrw",
        "cefpython3",
        "customtkinter",
        "tkinter",
        "pyglet",
        "urllib",
        "py7zr",
        "brotli",
        "brotlicffi", # Needed for py7zr
        "winreg",
        "requests",
        "shutil",
        "stat",
        "inspect",
        "threading",
        "ctypes"
        ],
    "path": sys.path + ["venv\\Lib\\site-packages"],
    "include_files": [
        # "yellow.json",
        ("venv\\Lib\\site-packages\\brotli.py", "lib\\brotli.py"),
        "interface"
        # "cefpython3"
        ],
    "excludes": [
        "numpy",
        "pandas"
    ]
    # "replace_paths": [("*", "")]
    }
}
executables = [cx_Freeze.Executable(
    "main.py",
    base=base,
    target_name="SLD.exe",
    icon=os.path.join(interface_path, "SLD_icon.ico")
    )
]

cx_Freeze.setup(
    name="Slowly Letter Downloader",
    options=options,
    author="PastaSource",
    version="0.2",
    description="Automates the downloading of letters from Slowly",
    executables=executables
)
