from cefpython3 import cefpython as cef
import customtkinter
import tkinter as tk

class App(customtkinter.CTk):

    WIDTH = 960
    HEIGHT = 720

    customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

    def __init__(self, count):
        super().__init__()
        self.browser_frame = None

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

        self.frame_left_width = (App.WIDTH / 3)
        self.frame_left = customtkinter.CTkFrame(master=self, width=self.frame_left_width)
        self.frame_left.pack(side="left", expand=1, fill="both")

        self.frame_right_width = (App.WIDTH - self.frame_left_width)
        self.frame_right = customtkinter.CTkFrame(master=self, width=self.frame_right_width)
        self.frame_right.pack(side="right", anchor="e", expand=1, fill="both")
        # self.frame_right = tk.Frame(master=self, width=self.frame_right_width)
        # self.frame_right.pack(side="right", anchor="e", expand=1, fill="both")

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
            self.button = customtkinter.CTkCheckBox(
                master=self.frame_left_second, text=f"{penpal}", text_font=("Roboto Medium", -20))
            self.button.grid(row=(index + 2), column=0, pady=5, padx=20, sticky="nw")


        # ============ frame_right ============

        # # Create canvas
        # self.canvas_right = customtkinter.CTkCanvas(master=self.frame_right, width=self.frame_right_width)
        # self.canvas_right.pack(side="right", fill="y")
        #
        # # Create browser frame
        # # self.browser_frame = BrowserFrame(self.frame_right)
        # # self.browser_frame.pack(anchor="center", expand=1, fill="both")
        #
        # # Create second frame_right
        # self.frame_right_second = customtkinter.CTkFrame(master=self.canvas_right, width=self.frame_right_width)
        # # self.browser_frame = BrowserFrame(self.frame_right_second)
        #
        # # Create window inside canvas
        # self.canvas_right.create_window((0, 0), window=self.frame_right_second, anchor="nw")

        # BrowserFrame
        cef.Initialize()
        # self.browser_root = tk.Tk()
        self.browser_frame = BrowserFrame(self.frame_right)
        # self.browser_frame.grid(row=1, column=0, sticky="nsew")
        self.browser_frame.pack(fill="both", expand=1, anchor="e", side="right")

        # cef.Initialize()
        # self.browser_frame = MainBrowserFrame(self.browser_root)

        # self.frame_right_second.pack(fill="both", expand=1)
        self.frame_right.pack(fill="both", expand=1)




    def get_browser(self):
        if self.browser_frame:
            return self.browser_frame.browser
        return None

    def get_browser_frame(self):
        if self.browser_frame:
            return self.browser_frame
        return None

    def button_event(self):
        print("Button pressed")

    # def change_appearance_mode(self, new_appearance_mode):
    #     customtkinter.set_appearance_mode(new_appearance_mode)

    def on_closing(self, event=0):
        self.destroy()

#
# class MainBrowserFrame(tk.Frame):
#
#     def __init__(self, root):
#         self.browser_frame = None
#
#         # # Root
#         # self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
#         root.geometry("900x640")
#         tk.Grid.rowconfigure(root, 0, weight=1)
#         tk.Grid.columnconfigure(root, 0, weight=1)
#
#
#         # MainFrame
#         tk.Frame.__init__(self, root)
#         self.master.title("Tkinter example")
#         # self.master.protocol("WM_DELETE_WINDOW", self.on_close)
#
#         # BrowserFrame
#         # self.browser_frame = BrowserFrame(self)
#         self.browser_frame = BrowserFrame(self)
#         self.browser_frame.grid(row=1, column=0,
#                                 sticky=(tk.N + tk.S + tk.E + tk.W))
#         tk.Grid.rowconfigure(self, 1, weight=1)
#         tk.Grid.columnconfigure(self, 0, weight=1)
#
#         # Pack MainFrame
#         self.pack(fill=tk.BOTH, expand=tk.YES)


class BrowserFrame(tk.Frame):
    WIDTH = App.WIDTH
    FRAME_RIGHT_WIDTH = (WIDTH - (WIDTH / 3))
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
        self.message_loop_work()

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
    pen = ["Henry","Butt","Billy","George","Scooby Doo","pappalord420","Lily","Yamaha","Pepsi Max",
               "Shirt","8492028293","A bus stop","OMGABUS","bakedbeans","candle","footly","Latty","moo","JFIOW",
           "JFK KENNEDY","GOT SHOT BY","A MARTIAN","NOT AN","EARTHLING"]
    app = App(pen)
    # app.penpal_count(pen)
    app.mainloop()
    # root = tk.Tk()
    # cef.Initialize()
    # app = MainBrowserFrame(root)
    #
    # app.mainloop()
    # cef.Shutdown()
