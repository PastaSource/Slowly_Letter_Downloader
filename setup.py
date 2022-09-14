import cx_Freeze
import sys
import base64
import re
import os
from os.path import exists
import _winapi
import json
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome, ChromeOptions
from pdfrw import PdfReader, PdfWriter
from cefpython3 import cefpython as cef
import customtkinter
import tkinter as tk
import pyglet

base = None

if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [cx_Freeze.Executable("main.py", base=base)]

cx_Freeze.setup(
    name = "Slowly_Letter_Downloader",
    options = {
                "build_exe": {
                    "packages": [
                                "base64",
                                "re",
                                "os",
                                "inspect",
                                # "exists",
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
                                # "pyunpack",
                                # "patoolib"
                                "py7zr"
                                "winreg"
                    ],
                    "include_files": [
                                "yellow.json",
                                # "chromium",
                                "interface",
                                "cefpython3"
                    ]
            }
        },
    version = "0.1",
    description = "Automates the downloading of letters from Slowly",
    executables = executables
    )