import tkinter as tk
import customtkinter as ctk
import win32gui, win32con, win32process
import psutil, keyboard, ctypes, threading, webbrowser, time, json, os, sys

myappid = 'hellkai.hellwindow.management.1' 
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

CONFIG_FILE = "config.json"
BG_COLOR = "#000000"
RED_MAIN = "#990000"
RED_HOVER = "#660000"
TEXT_MAIN = "#CCCCCC"
TEXT_DIM = "#555555"
BORDER_COLOR = "#222222"
GREY_HOVER = "#282828"

CYR_TO_LAT = {
    'ф': 'a', 'и': 'b', 'с': 'c', 'в': 'd', 'у': 'e', 'а': 'f', 'п': 'g', 'р': 'h',
    'ш': 'i', 'о': 'j', 'л': 'k', 'д': 'l', 'ь': 'm', 'т': 'n', 'щ': 'o', 'з': 'p',
    'й': 'q', 'к': 'r', 'ы': 's', 'е': 't', 'г': 'u', 'м': 'v', 'ц': 'w', 'ч': 'x',
    'н': 'y', 'я': 'z', 'х': '[', 'ъ': ']', 'ж': ';', 'э': "'", 'б': ',', 'ю': '.'
}

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class HellWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.title("HELLWINDOW")
        self.geometry("400x530")
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)
        
        self.set_icons()

        self.last_target_hwnd = None
        self.modified_windows = {}
        self.is_recording = False
        
        self.setup_ui()
        threading.Thread(target=self.track_active_window, daemon=True).start()
        self.apply_hotkeys()

    def set_icons(self):
        icon_png = resource_path("icon.png")
        icon_ico = resource_path("icon.ico")
        
        if os.path.exists(icon_png):
            try:
                img = tk.PhotoImage(file=icon_png)
                self.wm_iconphoto(True, img)
            except: pass
            
        if os.path.exists(icon_ico):
            try:
                self.iconbitmap(icon_ico)
            except: pass

    def load_config(self):
        defaults = {"hk_toggle": "ctrl+alt+h", "hk_reset": "ctrl+alt+r", "opacity": 180, "ghost_mode": True, "always_on_top": True}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f: return {**defaults, **json.load(f)}
            except: pass
        return defaults

    def save_config(self):
        self.config["opacity"] = int(self.slider.get())
        self.config["ghost_mode"] = self.check_click.get()
        self.config["always_on_top"] = self.check_top.get()
        with open(CONFIG_FILE, "w") as f: json.dump(self.config, f)

    def setup_ui(self):
        self.label_title = ctk.CTkLabel(self, text="HELLWINDOW", font=("Consolas", 32, "bold"), text_color=RED_MAIN)
        self.label_title.pack(pady=(15, 5))

        self.info_frame = ctk.CTkFrame(self, fg_color="#050505", border_width=1, border_color=BORDER_COLOR)
        self.info_frame.pack(pady=5, padx=35, fill="x")
        self.label_window_name = ctk.CTkLabel(self.info_frame, text="SEARCHING...", font=("Consolas", 11), text_color=TEXT_DIM)
        self.label_window_name.pack(pady=3)

        self.trans_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.trans_frame.pack(pady=(10, 0), padx=45, fill="x")
        ctk.CTkLabel(self.trans_frame, text="TRANSPARENCY", font=("Consolas", 13, "bold"), text_color=TEXT_MAIN).pack(side="left")
        self.label_pct = ctk.CTkLabel(self.trans_frame, text="0%", font=("Consolas", 13, "bold"), text_color=RED_MAIN)
        self.label_pct.pack(side="right")
        
        self.slider = ctk.CTkSlider(self, from_=20, to=255, height=16, button_color=RED_MAIN, button_hover_color=RED_HOVER, progress_color=RED_MAIN, fg_color="#151515", command=self.update_pct_label)
        self.slider.set(self.config["opacity"])
        self.slider.pack(pady=(5, 10), padx=45, fill="x")
        self.update_pct_label(self.config["opacity"])

        self.check_click = ctk.CTkCheckBox(self, text="GHOST MODE", font=("Consolas", 12), fg_color=RED_MAIN, hover_color=RED_HOVER, border_color="#333", text_color=TEXT_MAIN)
        if self.config["ghost_mode"]: self.check_click.select()
        self.check_click.pack(pady=2, padx=50, anchor="w")

        self.check_top = ctk.CTkCheckBox(self, text="ALWAYS ON TOP", font=("Consolas", 12), fg_color=RED_MAIN, hover_color=RED_HOVER, border_color="#333", text_color=TEXT_MAIN)
        if self.config["always_on_top"]: self.check_top.select()
        self.check_top.pack(pady=2, padx=50, anchor="w")

        self.hk_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.hk_frame.pack(pady=10, padx=45, fill="x")
        self.btn_hk_toggle = self.create_hk_button("TOGGLE", self.config["hk_toggle"], 0)
        self.btn_hk_reset = self.create_hk_button("RESET", self.config["hk_reset"], 1)

        self.btn_apply = ctk.CTkButton(self, text="EXECUTE", font=("Consolas", 18, "bold"), fg_color=RED_MAIN, hover_color=RED_HOVER, text_color="#FFF", height=45, command=self.transform_window)
        self.btn_apply.pack(pady=10, padx=45, fill="x")

        ctk.CTkLabel(self, text="SPIRITS", font=("Consolas", 10, "bold"), text_color=TEXT_DIM).pack()
        self.list_frame = ctk.CTkFrame(self, height=65, fg_color="#030303", border_width=1, border_color=BORDER_COLOR)
        self.list_frame.pack(pady=2, padx=45, fill="x")
        self.list_frame.pack_propagate(False) 
        self.list_inner = ctk.CTkScrollableFrame(self.list_frame, fg_color="transparent", height=65)
        self.list_inner.pack(fill="both", expand=True)
        self.update_list_ui()

        self.footer = ctk.CTkLabel(self, text="hellkai", font=("Consolas", 11, "underline"), text_color="#333333", cursor="hand2")
        self.footer.pack(side="bottom", pady=10)
        self.footer.bind("<Button-1>", lambda e: webbrowser.open("https://t.me/k41h311"))

    def create_hk_button(self, label, default, row):
        btn = ctk.CTkButton(self.hk_frame, text=default, width=120, height=24, font=("Consolas", 11), fg_color="#050505", border_width=1, border_color=BORDER_COLOR, text_color=RED_MAIN, hover_color=GREY_HOVER)
        btn.grid(row=row, column=0, pady=2)
        btn.configure(command=lambda b=btn, l=label: self.start_recording(b, l))
        ctk.CTkLabel(self.hk_frame, text=label, font=("Consolas", 11), text_color=TEXT_DIM).grid(row=row, column=1, padx=10, sticky="w")
        return btn

    def start_recording(self, button, label):
        if self.is_recording: return
        self.is_recording = True
        button.configure(text="...", text_color=TEXT_MAIN)
        def record():
            new_hk = keyboard.read_hotkey(suppress=False)
            cleaned = "+".join([CYR_TO_LAT.get(p.lower(), p.lower()) for p in new_hk.split('+')])
            self.after(0, lambda: self.finish_recording(button, label, cleaned))
        threading.Thread(target=record, daemon=True).start()

    def finish_recording(self, button, label, new_hk):
        button.configure(text=new_hk, text_color=RED_MAIN)
        if label == "TOGGLE": self.config["hk_toggle"] = new_hk
        else: self.config["hk_reset"] = new_hk
        self.save_config()
        self.apply_hotkeys()
        self.is_recording = False

    def update_pct_label(self, val):
        self.label_pct.configure(text=f"{int((float(val) / 255) * 100)}%")

    def apply_hotkeys(self):
        try:
            keyboard.unhook_all()
            keyboard.add_hotkey(self.config["hk_toggle"], self.transform_window)
            keyboard.add_hotkey(self.config["hk_reset"], self.release_all)
        except: pass

    def track_active_window(self):
        while True:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd != self.winfo_id() and win32gui.GetWindowText(hwnd) != "HELLWINDOW":
                if hwnd:
                    self.last_target_hwnd = hwnd
                    try:
                        title = win32gui.GetWindowText(hwnd)
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        proc = psutil.Process(pid).name()
                        self.label_window_name.configure(text=f"{proc} > {title[:20]}", text_color=TEXT_DIM)
                    except: pass
            time.sleep(0.4)

    def update_list_ui(self):
        for widget in self.list_inner.winfo_children(): widget.destroy()
        if not self.modified_windows:
            ctk.CTkLabel(self.list_inner, text="-- empty --", font=("Consolas", 11), text_color="#222").pack(pady=15)
            return
        for hwnd in self.modified_windows:
            if not win32gui.IsWindow(hwnd): continue
            row = ctk.CTkFrame(self.list_inner, fg_color="#080808", height=30)
            row.pack(fill="x", pady=1, padx=2)
            row.pack_propagate(False)
            ctk.CTkLabel(row, text="⛧", font=("Consolas", 15, "bold"), text_color=RED_MAIN).pack(side="left", padx=(5, 5))
            ctk.CTkLabel(row, text=win32gui.GetWindowText(hwnd)[:22], font=("Consolas", 12), text_color=TEXT_MAIN).pack(side="left")
            ctk.CTkButton(row, text="X", width=24, height=20, fg_color="transparent", hover_color=RED_HOVER, text_color=RED_MAIN, font=("Consolas", 13, "bold"), command=lambda h=hwnd: self.release_window(h)).pack(side="right", padx=5)

    def transform_window(self):
        hwnd = self.last_target_hwnd
        if not hwnd or not win32gui.IsWindow(hwnd): return
        if hwnd not in self.modified_windows:
            try:
                style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                self.modified_windows[hwnd] = style
                new_style = style | win32con.WS_EX_LAYERED
                if self.check_click.get(): new_style |= win32con.WS_EX_TRANSPARENT
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_style)
                ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, int(self.slider.get()), 0x2)
                if self.check_top.get(): win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                self.save_config()
                self.update_list_ui()
            except: pass
        else: self.release_window(hwnd)

    def release_window(self, hwnd):
        if hwnd in self.modified_windows:
            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, self.modified_windows[hwnd])
            win32gui.RedrawWindow(hwnd, None, None, win32con.RDW_INVALIDATE | win32con.RDW_FRAME)
            del self.modified_windows[hwnd]
            self.update_list_ui()

    def release_all(self):
        for hwnd in list(self.modified_windows.keys()): self.release_window(hwnd)

if __name__ == "__main__":
    app = HellWindow()
    app.mainloop()