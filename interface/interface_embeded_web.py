from cefpython3 import cefpython as cef
import customtkinter
import tkinter as tk
import os
from os.path import exists
import pyglet

class App(customtkinter.CTk):

    WIDTH = 960
    HEIGHT = 720
    if exists(os.path.join(os.getcwd(), "interface\\fonts")):
        FONT_PATH = os.path.join(os.getcwd(), "interface\\fonts")
    else:
        FONT_PATH = os.path.join(os.getcwd(), "fonts")
    FONT_POTRA = pyglet.font.add_file(os.path.join(FONT_PATH, "potra.ttf"))
    FONT_STONE = pyglet.font.add_file(os.path.join(FONT_PATH, "stone.ttf"))
    FONT_BOTTERILL = pyglet.font.add_file(os.path.join(FONT_PATH, "Botterill Signature.ttf"))
    FONT_ENCHANTED = pyglet.font.add_file(os.path.join(FONT_PATH, "EnchantedPrairieDog.ttf"))
    FONT_TYPEWRITER = pyglet.font.add_file(os.path.join(FONT_PATH, "typewriter.ttf"))
    customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

    def __init__(self, count):
        super().__init__()
        self.browser_frame = None
        self.penpals = count
        self.current_frame_state("init")

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

        # print(BrowserFrame.GetUrl)

        print("end of init")


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
        print("load penpals button pressed")
        self.frame_right_browser.forget()
        # BrowserFrame.on_root_close() # no idea if integrated browser is closing or not
        # cef.Shutdown()
        # cef.Shutdown()
        self.browser_frame.browser.CloseBrowser(True)
        self.frame_bottom_browser.forget()
        self.frame_left_browser.forget()
        self.frame_bottom_progress.pack(anchor="se", side="bottom")
        self.frame_right_progress.pack(expand=1, fill="both")
        self.frame_left_progress.pack(side="left", fill="both")
        self.current_frame_state("load_penpals")

    def current_frame_state(self, state):
        return state

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

if __name__ == "__main__":
    pen = ["Ryan","Harry","Billy","George","Scooby Doo","legoman","Lily","Yamaha","Pepsi Max",
               "Shirt","8492028293","A bus stop","OMGABUS","bakedbeans","candle","footly","Latty","moo","JFIOW",
           "J.F. KENNEDY","GOT SHOT BY","A MARTIAN","NOT AN","EARTHLING"]
    app = App(pen)
    # app.penpal_count(pen)
    app.mainloop()
    # root = tk.Tk()
    # cef.Initialize()
    # app = MainBrowserFrame(root)
    #
    # app.mainloop()
    # cef.Shutdown()
