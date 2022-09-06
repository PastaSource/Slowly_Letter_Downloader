from cefpython3 import cefpython as cef
import customtkinter

import tkinter as tk
import tkinter.messagebox

class App(customtkinter.CTk):

    WIDTH = 960
    HEIGHT = 720

    customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

    def __init__(self, count):
        super().__init__()

        self.title("Slowly Letter Downloader")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed
        self.count = count
        # ============ create three frames ============

        # configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_top = customtkinter.CTkFrame(master=self, height=100)
        self.frame_top.pack(anchor="n", fill="both")

        self.frame_left_width = 350
        self.frame_left = customtkinter.CTkFrame(master=self, width=self.frame_left_width)
        self.frame_left.pack(side="left", expand=1, fill="both")

        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.pack(anchor="e", expand=1, fill="both")

        # ============ frame_top ============
        self.app_title = customtkinter.CTkLabel(master=self.frame_top, text="Slowly Letter Downloader",
                                                text_font=("Roboto Medium", -50))
        self.app_title.place(x=(App.WIDTH/2), y=50, anchor="center")
        # self.app_title.grid(row=1, column=0, pady=15, sticky="n")

        # ============ frame_left ============
        # Create canvas
        self.canvas_left = customtkinter.CTkCanvas(master=self.frame_left, width=self.frame_left_width)
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
        self.frame_left_second = customtkinter.CTkFrame(master=self.canvas_left, width=self.frame_left_width)

        # Create window inside canvas
        self.canvas_left.create_window((0,0), window=self.frame_left_second, anchor="nw")

        # configure grid layout (1x11)
        self.frame_left_second.grid_rowconfigure(0, minsize=10)   # empty row with minsize as spacing
        self.frame_left_second.grid_rowconfigure(len(count) + 2, weight=1)  # empty row as spacing

        self.label_1 = customtkinter.CTkLabel(master=self.frame_left_second,
                                              text="Penpals",
                                              text_font=("Roboto Medium", -30), width=(self.frame_left_width - 20))  # font name and size in px
        self.label_1.grid(row=1, column=0, pady=10, padx=10)


        # Button creation
        for index, penpal in enumerate(self.count):
            # self.button = customtkinter.CTkCheckBox(
            #     master=self.frame_left_second, text=f"{penpal}", text_font=("Roboto Medium", -20))
            self.button = tk.Checkbutton(
                master=self.frame_left_second, text=f"{penpal}")
            self.button.grid(row=(index + 2), column=0, pady=5, padx=20, sticky="nw")

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


        self.run_button = customtkinter.CTkButton(master=self.frame_right,
                                                text="Run", text_font=("Roboto Medium", -20),
                                                border_width=2,  # <- custom border_width
                                                fg_color=None,  # <- no fg_color
                                                command=self.button_event)
        self.run_button.grid(row=8, column=2, columnspan=1, pady=20, padx=20, sticky="se")

        # set default values
        # self.optionmenu_1.set("Dark")
        # self.button_3.configure(state="disabled", text="Disabled CTkButton")
        # self.combobox_1.set("CTkCombobox")
        # self.radio_button_1.select()
        # self.slider_1.set(0.2)
        # self.slider_2.set(0.7)
        # self.progressbar.set(0.5)
        # self.switch_2.select()
        # self.radio_button_3.configure(state=tkinter.DISABLED)
        # self.check_box_1.configure(state=tkinter.DISABLED, text="CheckBox disabled")
        # self.check_box_2.select()

    # def penpal_count(self, count):
    #     self.penpals = count
    #     return self.penpals

    def button_event(self):
        print("Button pressed")

    # def change_appearance_mode(self, new_appearance_mode):
    #     customtkinter.set_appearance_mode(new_appearance_mode)

    def on_closing(self, event=0):
        self.destroy()


if __name__ == "__main__":
    pen = ["Henry","Butt","Billy","George","Scooby Doo","pappalord420","Lily","Yamaha","Pepsi Max",
               "Shirt","8492028293","A bus stop","OMGABUS","bakedbeans","candle","footly","Latty","moo","JFIOW",
           "JFK KENNEDY","GOT SHOT BY","A MARTIAN","NOT AN","EARTHLING"]
    app = App(pen)
    # app.penpal_count(pen)
    app.mainloop()

