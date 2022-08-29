import os
from os.path import exists
import re
import json
from pdfrw import  PdfReader, PdfWriter, IndirectPdfDict
from PyPDF2 import PdfFileReader, PdfFileWriter
import sys
import glob



dir_path = os.getcwd()
download_path = os.path.join(dir_path, "letters")
file = "test.pdf"
file_path = os.path.join(download_path, file)
attribute = "LetterNumber"
letter_number = 1
penpal = "Billy"
penpal_path = os.path.join(download_path, penpal)


# data = PdfReader(file_path)
# data.Info.Letter = "3"
# data.Info.Penpal = "Billy"
#
# os.remove(file_path)
# PdfWriter(file_path, trailer=data).write()




for pdf in os.listdir(penpal_path):
    if pdf.endswith(".pdf"):
        pdf_path = os.path.join(penpal_path, pdf)
        check = PdfReader(pdf_path).Info
        for key,value in check.items():
            if key == "/Letter" or key == "/Penpal":
                print(key, value)

# for pdf in glob.glob(penpal_path, "*.pdf"):
#     print(pdf)
#     print("work")
