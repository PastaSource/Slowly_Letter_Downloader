
from cefpython3 import cefpython as cef
import customtkinter as customtkinter, customtkinter as tk

# import tkinter as tk
import os

class MainFrame(customtkinter.CTk):
    WIDTH = 900
    HEIGHT = 640

    customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

    def __init__(self):
        super().__init__()
        self.title("Browser Tester")
        self.browser_frame = None

        # # Root
        self.geometry(f"{MainFrame.WIDTH}x{MainFrame.HEIGHT}")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)



        # MainFrame
        self.host_frame = customtkinter.CTkFrame(master=self, height=MainFrame.HEIGHT, width=MainFrame.WIDTH)



        # BrowserFrame
        self.browser_frame = BrowserFrame(self.host_frame)
        self.browser_frame.grid(row=1, column=0, sticky="nsew")



        # Pack MainFrame
        self.host_frame.pack(fill="both", expand=1)

    def on_close(self):
        if self.browser_frame:
            self.browser_frame.on_root_close()
        self.master.destroy()

    def get_browser(self):
        if self.browser_frame:
            return self.browser_frame.browser
        return None

    def get_browser_frame(self):
        if self.browser_frame:
            return self.browser_frame
        return None

class BrowserFrame(tk.CTkFrame):

    def __init__(self, master_frame):
        self.closing = False
        self.browser = None
        # customtkinter.CTkFrame.__init__(self, master)
        # self.embed_frame = customtkinter.CTkFrame(master=master_frame)
        tk.CTkFrame.__init__(self, master_frame, height=MainFrame.HEIGHT, width=MainFrame.WIDTH)
        # self.bind("<Configure>", self.on_configure)
        self.on_configure(self)
        # self.app_title = customtkinter.CTkLabel(master=self, text="This is a test",
        #                                         text_font=("Roboto Medium", -50))
        # self.app_title.place(x=(MainFrame.WIDTH/2), y=50, anchor="center")

        self.focus_set()

    def embed_browser(self):
        print("embed")
        dir_path = os.getcwd()
        cache = os.path.join(dir_path, "cef_cache")
        # Settings for Chromium browser
        settings = {"cache_path": cache,
                    "auto_zooming": "-1.0"}
        cef.Initialize(settings=settings)
        window_info = cef.WindowInfo()
        # rect = [0, 0, MainFrame.WIDTH, MainFrame.HEIGHT]
        rect = [0, 0, self.winfo_width(), self.winfo_height()]
        window_info.SetAsChild(self.get_window_handle(), rect)
        self.browser = cef.CreateBrowserSync(window_info,
                                             url="https://web.slowly.app/")
        assert self.browser

        # self.app_title = customtkinter.CTkLabel(master=self, text="This is a test",
        #                                         text_font=("Roboto Medium", -50))
        # self.app_title.place(x=(MainFrame.WIDTH / 2), y=50, anchor="center")
        #
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

if __name__ == '__main__':
    # root = customtkinter.CTk()
    app = MainFrame() # originally had root has argument
    # Tk must be initialized before CEF otherwise fatal error (Issue #306)
    app.mainloop()
    cef.Shutdown()