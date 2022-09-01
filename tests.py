import os
from os.path import exists
import re
import json
from pdfrw import  PdfReader, PdfWriter, IndirectPdfDict
from PyPDF2 import PdfFileReader, PdfFileWriter
import sys
import glob
import customtkinter
import tkinter
import tkinter.messagebox

#
# dir_path = os.getcwd()
# download_path = os.path.join(dir_path, "letters")
# file = "test.pdf"
# file_path = os.path.join(download_path, file)
# attribute = "LetterNumber"
# letter_number = 1
# penpal = "Yasdnil"
# penpal_path = os.path.join(download_path, penpal)
#
#
# # data = PdfReader(file_path)
# # data.Info.Letter = "3"
# # data.Info.Penpal = "Billy"
# #
# # os.remove(file_path)
# # PdfWriter(file_path, trailer=data).write()
#
#
#
# letter_list = []
# for pdf in os.listdir(penpal_path):
#     if pdf.endswith(".pdf"):
#         pdf_path = os.path.join(penpal_path, pdf)
#         check = PdfReader(pdf_path).Info
#         for key,value in check.items():
#             if key == "/Letter" or key == "/Penpal":
#                 print(key, value)
#                 if key == "/Letter":
#                     # value = int(re.search("\((\d*)\)", value).group(1))
#                     letter_list.append(int(value))
# print(sorted(letter_list))
# # for pdf in glob.glob(penpal_path, "*.pdf"):
# #     print(pdf)
# #     print("work")

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

penpal_amount = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]




customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):

    WIDTH = 780
    HEIGHT = 520

    def __init__(self):
        super().__init__()

        self.title("CustomTkinter complex_example.py")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed

        # ============ create two frames ============

        # configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # self.frame_left = customtkinter.CTkFrame(master=self,
        #                                          width=180,
        #                                          corner_radius=0)
        # self.frame_left.grid(row=0, column=0, sticky="nswe")
        self.frame_left = customtkinter.CTkFrame(master=self, width=200)
        # self.frame_left.grid(row=0, column=0, sticky="nswe")
        self.frame_left.pack(side="left", expand=1, fill="both")
        # self.frame_left.pack(expand=1)

        self.frame_right = customtkinter.CTkFrame(master=self)
        # self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)
        self.frame_right.pack(anchor="e", padx=20, pady=20)

        # ============ frame_left ============
        # Create canvas
        self.canvas_left = customtkinter.CTkCanvas(master=self.frame_left, width=200)
        self.canvas_left.pack(side="left", fill="y")

        # Create scrollbar
        self.left_scrollbar = customtkinter.CTkScrollbar(
            master=self.frame_left, orientation="vertical", command=self.canvas_left.yview)
        self.left_scrollbar.pack(side="left", fill="y")

        # Configure canvas
        self.canvas_left.configure(yscrollcommand=self.left_scrollbar.set)
        self.canvas_left.bind(
            "<Configure>", lambda e: self.canvas_left.configure(scrollregion=self.canvas_left.bbox("all")))

        # Create second frame_left
        self.frame_left_second = customtkinter.CTkFrame(master=self.canvas_left, width=200)

        # Create window inside canvas
        self.canvas_left.create_window((0,0), window=self.frame_left_second, anchor="nw")

        # configure grid layout (1x11)
        self.frame_left_second.grid_rowconfigure(0, minsize=10)   # empty row with minsize as spacing
        self.frame_left_second.grid_rowconfigure(len(penpal_amount) + 2, weight=1)  # empty row as spacing

        self.label_1 = customtkinter.CTkLabel(master=self.frame_left_second,
                                              text="Penpals",
                                              text_font=("Roboto Medium", -16), width=180)  # font name and size in px
        self.label_1.grid(row=1, column=0, pady=10, padx=10)

        # Button creation
        # for penpal in range(0, len(penpal_amount)):
        #     self.button = customtkinter.CTkButton(
        #         master=self.frame_left_second, text=f"CTkButton{penpal + 1}",
        #         command=self.button_event, height=1, width=160)
        #     self.button.grid(row=(penpal + 2), column=0, pady=5, padx=20)
        for penpal in range(0, len(penpal_amount)):
            self.button = customtkinter.CTkCheckBox(
                master=self.frame_left_second, text=f"Penpal {penpal + 1}")
            self.button.grid(row=(penpal + 2), column=0, pady=5, padx=20)

        # self.label_mode = customtkinter.CTkLabel(master=self.frame_left, text="Appearance Mode:")
        # self.label_mode.grid(row=9, column=0, pady=0, padx=20, sticky="w")
        #
        # self.optionmenu_1 = customtkinter.CTkOptionMenu(master=self.frame_left,
        #                                                 values=["Light", "Dark", "System"],
        #                                                 command=self.change_appearance_mode)
        # self.optionmenu_1.grid(row=10, column=0, pady=10, padx=20, sticky="w")


        # ============ frame_right ============

        # configure grid layout (3x7)
        self.frame_right.rowconfigure((0, 1, 2, 3), weight=1)
        self.frame_right.rowconfigure(7, weight=10)
        self.frame_right.columnconfigure((0, 1), weight=1)
        self.frame_right.columnconfigure(2, weight=0)

        self.frame_info = customtkinter.CTkFrame(master=self.frame_right)
        self.frame_info.grid(row=0, column=0, columnspan=2, rowspan=4, pady=20, padx=20, sticky="nsew")

        # ============ frame_info ============

        # configure grid layout (1x1)
        self.frame_info.rowconfigure(0, weight=1)
        self.frame_info.columnconfigure(0, weight=1)

        self.label_info_1 = customtkinter.CTkLabel(master=self.frame_info,
                                                   text="CTkLabel: Lorem ipsum dolor sit,\n" +
                                                        "amet consetetur sadipscing elitr,\n" +
                                                        "sed diam nonumy eirmod tempor" ,
                                                   height=100,
                                                   corner_radius=6,  # <- custom corner radius
                                                   fg_color=("white", "gray38"),  # <- custom tuple-color
                                                   justify=tkinter.LEFT)
        self.label_info_1.grid(column=0, row=0, sticky="nwe", padx=15, pady=15)

        self.progressbar = customtkinter.CTkProgressBar(master=self.frame_info)
        self.progressbar.grid(row=1, column=0, sticky="ew", padx=15, pady=15)

        # ============ frame_right ============

        self.radio_var = tkinter.IntVar(value=0)

        self.label_radio_group = customtkinter.CTkLabel(master=self.frame_right,
                                                        text="CTkRadioButton Group:")
        self.label_radio_group.grid(row=0, column=2, columnspan=1, pady=20, padx=10, sticky="")

        self.radio_button_1 = customtkinter.CTkRadioButton(master=self.frame_right,
                                                           variable=self.radio_var,
                                                           value=0)
        self.radio_button_1.grid(row=1, column=2, pady=10, padx=20, sticky="n")

        self.radio_button_2 = customtkinter.CTkRadioButton(master=self.frame_right,
                                                           variable=self.radio_var,
                                                           value=1)
        self.radio_button_2.grid(row=2, column=2, pady=10, padx=20, sticky="n")

        self.radio_button_3 = customtkinter.CTkRadioButton(master=self.frame_right,
                                                           variable=self.radio_var,
                                                           value=2)
        self.radio_button_3.grid(row=3, column=2, pady=10, padx=20, sticky="n")

        self.slider_1 = customtkinter.CTkSlider(master=self.frame_right,
                                                from_=0,
                                                to=1,
                                                number_of_steps=3,
                                                command=self.progressbar.set)
        self.slider_1.grid(row=4, column=0, columnspan=2, pady=10, padx=20, sticky="we")

        self.slider_2 = customtkinter.CTkSlider(master=self.frame_right,
                                                command=self.progressbar.set)
        self.slider_2.grid(row=5, column=0, columnspan=2, pady=10, padx=20, sticky="we")

        self.switch_1 = customtkinter.CTkSwitch(master=self.frame_right,
                                                text="CTkSwitch")
        self.switch_1.grid(row=4, column=2, columnspan=1, pady=10, padx=20, sticky="we")

        self.switch_2 = customtkinter.CTkSwitch(master=self.frame_right,
                                                text="CTkSwitch")
        self.switch_2.grid(row=5, column=2, columnspan=1, pady=10, padx=20, sticky="we")

        self.combobox_1 = customtkinter.CTkComboBox(master=self.frame_right,
                                                    values=["Value 1", "Value 2"])
        self.combobox_1.grid(row=6, column=2, columnspan=1, pady=10, padx=20, sticky="we")

        self.check_box_1 = customtkinter.CTkCheckBox(master=self.frame_right,
                                                     text="CTkCheckBox")
        self.check_box_1.grid(row=6, column=0, pady=10, padx=20, sticky="w")

        self.check_box_2 = customtkinter.CTkCheckBox(master=self.frame_right,
                                                     text="CTkCheckBox")
        self.check_box_2.grid(row=6, column=1, pady=10, padx=20, sticky="w")

        self.entry = customtkinter.CTkEntry(master=self.frame_right,
                                            width=120,
                                            placeholder_text="CTkEntry")
        self.entry.grid(row=8, column=0, columnspan=2, pady=20, padx=20, sticky="we")

        self.button_5 = customtkinter.CTkButton(master=self.frame_right,
                                                text="CTkButton",
                                                border_width=2,  # <- custom border_width
                                                fg_color=None,  # <- no fg_color
                                                command=self.button_event)
        self.button_5.grid(row=8, column=2, columnspan=1, pady=20, padx=20, sticky="we")

        # set default values
        # self.optionmenu_1.set("Dark")
        # self.button_3.configure(state="disabled", text="Disabled CTkButton")
        self.combobox_1.set("CTkCombobox")
        self.radio_button_1.select()
        self.slider_1.set(0.2)
        self.slider_2.set(0.7)
        self.progressbar.set(0.5)
        self.switch_2.select()
        self.radio_button_3.configure(state=tkinter.DISABLED)
        self.check_box_1.configure(state=tkinter.DISABLED, text="CheckBox disabled")
        self.check_box_2.select()

    def button_event(self):
        print("Button pressed")

    # def change_appearance_mode(self, new_appearance_mode):
    #     customtkinter.set_appearance_mode(new_appearance_mode)

    def on_closing(self, event=0):
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()

