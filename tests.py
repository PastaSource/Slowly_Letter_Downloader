import cefpython3
import os
from os.path import exists
import wget
import sys
from pyunpack import Archive
import pyunpack
import shutil
import urllib.request
import py7zr

pyunpack.Archive

# dir_temp = tempfile.gettempdir()
# files = []
# for i in os.listdir(dir_temp):
#     if os.path.isdir(os.path.join(dir_temp,i)) and '_MEI' in i:
#         files.append(i)
# dir_temp = dir_temp + str(files[0])
# dir_temp = os.path.join(dir_temp, str(files[0]))
# dir_temp_locale = os.path.join(dir_temp, 'locales')
# dir_temp_subprocess = os.path.join(dir_temp_subprocess, 'subprocess.exe')
#
# print dir_temp
# dir_temp = dir_temp.replace("\\", "\\\\")
# print dir_temp
# print dir_temp_locale
# dir_temp_locale = dir_temp_locale.replace("\\", "\\\\")
# print dir_temp_locale
# dir_temp_supbprocess = dir_temp_subprocess.replace("\\", "\\\\")
# print dir_temp_subprocess

# def bar_progress(current, total, width=80):
#     # progress_message = "Downloading: %d%% [%d / %d] bytes" % (current / total * 100, current, total)
#     progress_message = round((current / total), 2)
#     # Don't use print() as it will print in new line every time.
#     # sys.stdout.write("\r" + progress_message)
#     # sys.stdout.flush()
#     print(progress_message)
#
#
dir_path = os.getcwd()
# chrome_root_path = os.path.join(dir_path, "chrome_test")
chrome_executable_path = os.path.join(dir_path, "Chrome-bin\\chrome.exe")
chrome_sync_path = os.path.join(dir_path, "chrome.sync.7z")
#
# # if exists(chrome_root_path):
# #     pass
# # else:
# #     os.mkdir(chrome_root_path)
#
# if exists(chrome_executable_path):
#     pass
# else:
#     if exists(chrome_sync_path):
#         Archive(chrome_sync_path).extractall(dir_path)
#     else:
#         wget.download(
#             'https://github.com/Hibbiki/chromium-win64/releases/download/v105.0.5195.102-r856/chrome.sync.7z',
#             dir_path,
#             bar=bar_progress
#         )
#         Archive(chrome_sync_path).extractall(dir_path)
#     # shutil.rmtree(chrome_sync_path)
#     os.remove(chrome_sync_path)
link = "https://github.com/Hibbiki/chromium-win64/releases/download/v105.0.5195.102-r856/chrome.sync.7z"
file_name = "chrome.sync.7z"

def download_from_anon():
    urllib.request.urlretrieve(link, file_name)
    archive = py7zr.SevenZipFile(chrome_sync_path, mode='r')
    archive.extractall(path=dir_path)


download_from_anon()