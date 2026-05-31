import tkinter as tk
import customtkinter as ctk
import win32gui, win32con, win32process, win32api
import psutil, keyboard, ctypes, threading, webbrowser, time, json, os, sys
from pycaw.pycaw import AudioUtilities
from PIL import Image
import pystray

myappid = 'hellkai.hellwindow.management.1' 
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

CONFIG_FILE = "config.json"
BG_COLOR = "#000000"
RED_MAIN = "#990000"
RED_BRIGHT = "#FF0000"
RED_HOVER = "#660000"
TEXT_MAIN = "#CCCCCC"
TEXT_DIM = "#666666"
BORDER_COLOR = "#222222"
ITEM_BG = "#111111"
GREY_HOVER = "#282828"

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

CYR_TO_LAT = {
    'ф': 'a', 'и': 'b', 'с': 'c', 'в': 'd', 'у': 'e', 'а': 'f', 'п': 'g', 'р': 'h',
    'ш': 'i', 'о': 'j', 'л': 'k', 'д': 'l', 'ь': 'm', 'т': 'n', 'щ': 'o', 'з': 'p',
    'й': 'q', 'к': 'r', 'ы': 's', 'е': 't', 'г': 'u', 'м': 'v', 'ц': 'w', 'ч': 'x',
    'н': 'y', 'я': 'z', 'х': '[', 'ъ': ']', 'ж': ';', 'э': "'", 'б': ',', 'ю': '.'
}

class SizeRitual(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("SIZE RITUAL")
        self.geometry("260x230") 
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)
        self.callback = callback
        self.after(200, lambda: self.iconbitmap(resource_path("icon.ico")))
        self.attributes("-topmost", True)
        self.grab_set()

        ctk.CTkLabel(self, text="SIZE RITUAL", font=("Consolas", 16, "bold"), text_color=RED_MAIN).pack(pady=(8, 0))

        ctk.CTkLabel(self, text="WIDTH", font=("Consolas", 12, "bold"), text_color=TEXT_DIM).pack(pady=(9, 0))
        self.w_entry = ctk.CTkEntry(self, width=180, height=28, corner_radius=6, fg_color="#050505", border_color=BORDER_COLOR, text_color=RED_MAIN, font=("Consolas", 14, "bold"), justify="center")
        self.w_entry.pack(pady=1)
        self.w_entry.insert(0, "1280")

        ctk.CTkLabel(self, text="HEIGHT", font=("Consolas", 12, "bold"), text_color=TEXT_DIM).pack(pady=(9, 0))
        self.h_entry = ctk.CTkEntry(self, width=180, height=28, corner_radius=6, fg_color="#050505", border_color=BORDER_COLOR, text_color=RED_MAIN, font=("Consolas", 14, "bold"), justify="center")
        self.h_entry.pack(pady=1)
        self.h_entry.insert(0, "720")

        self.btn_save = ctk.CTkButton(self, text="SAVE", width=180, height=28, corner_radius=6, font=("Consolas", 12, "bold"), fg_color=RED_MAIN, hover_color=RED_HOVER, command=self.apply)
        self.btn_save.pack(pady=15)

    def apply(self):
        try:
            w, h = int(self.w_entry.get()), int(self.h_entry.get())
            self.callback(w, h)
            self.destroy()
        except: pass

class HellWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.title("HELLWINDOW")
        self.geometry("400x560") 
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)
        
        self.set_icons()
        self.last_target_hwnd = None
        self.modified_windows = {}
        self.hidden_windows = set()
        self.is_recording = False
        self.is_picking = False
        self.process_cache = {}
        
        self.setup_ui()
        threading.Thread(target=self.track_active_window, daemon=True).start()
        self.apply_hotkeys()
        self.animate_scan_dot()
        self.create_tray_icon()
        
        self.protocol('WM_DELETE_WINDOW', self.hide_to_tray)
        self.save_config()

    def set_icons(self):
        try:
            self.wm_iconphoto(True, tk.PhotoImage(file=resource_path("icon.png")))
            self.iconbitmap(resource_path("icon.ico"))
        except: pass

    def load_config(self):
        defaults = {"hk_toggle": "ctrl+alt+h", "hk_reset": "ctrl+alt+r", "opacity": 180, "ghost_mode": True, "always_on_top": True}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f: return {**defaults, **json.load(f)}
            except: pass
        return defaults

    def save_config(self):
        self.config.update({"opacity": int(self.slider.get()), "ghost_mode": self.check_click.get(), "always_on_top": self.check_top.get()})
        with open(CONFIG_FILE, "w") as f: json.dump(self.config, f)

    def setup_ui(self):
        ctk.CTkLabel(self, text="HELLWINDOW", font=("Consolas", 32, "bold"), text_color=RED_MAIN).pack(pady=(8, 5))
        
        self.btn_tray = ctk.CTkButton(self, text="▼", width=30, height=26, fg_color="transparent", hover_color=GREY_HOVER, text_color=TEXT_DIM, font=("Consolas", 14, "bold"), command=self.withdraw)
        self.btn_tray.place(x=365, y=15)

        self.info_f = ctk.CTkFrame(self, fg_color="#050505", border_width=1, border_color=BORDER_COLOR, height=34)
        self.info_f.pack(pady=5, padx=35, fill="x"); self.info_f.pack_propagate(False)
        
        self.btn_picker = ctk.CTkButton(self.info_f, text="⌖", width=30, height=26, fg_color="transparent", hover_color=GREY_HOVER, text_color=RED_MAIN, font=("Consolas", 18, "bold"), command=self.start_picker)
        self.btn_picker.pack(side="right", padx=2)

        self.scan_canvas = tk.Canvas(self.info_f, width=10, height=10, bg="#050505", highlightthickness=0)
        self.scan_dot = self.scan_canvas.create_oval(2, 2, 8, 8, fill=RED_MAIN, outline="")
        self.scan_canvas.place(x=12, y=12)
        
        self.label_window_name = ctk.CTkLabel(self.info_f, text="SEARCHING...", font=("Consolas", 12, "bold"), text_color=TEXT_DIM, anchor="w")
        self.label_window_name.pack(side="left", padx=(32, 5), fill="x", expand=True)

        self.t_f = ctk.CTkFrame(self, fg_color="transparent")
        self.t_f.pack(pady=(4, 0), padx=35, fill="x")
        ctk.CTkLabel(self.t_f, text="TRANSPARENCY", font=("Consolas", 14, "bold"), text_color=TEXT_MAIN).pack(side="left")
        self.label_pct = ctk.CTkLabel(self.t_f, text="70%", font=("Consolas", 14, "bold"), text_color=RED_MAIN)
        self.label_pct.pack(side="right")
        self.slider = ctk.CTkSlider(self, from_=20, to=255, height=16, button_color=RED_MAIN, button_hover_color=RED_HOVER, progress_color=RED_MAIN, fg_color="#151515", command=self.update_pct_label)
        self.slider.set(self.config["opacity"])
        self.slider.pack(pady=(2, 10), padx=35, fill="x")
        self.update_pct_label(self.config["opacity"])

        self.check_click = ctk.CTkCheckBox(self, text="GHOST MODE", font=("Consolas", 12, "bold"), fg_color=RED_MAIN, hover_color=RED_HOVER, border_color="#333", text_color=TEXT_MAIN)
        if self.config["ghost_mode"]: self.check_click.select()
        self.check_click.pack(pady=2, padx=35, anchor="w")
        self.check_top = ctk.CTkCheckBox(self, text="ALWAYS ON TOP", font=("Consolas", 12, "bold"), fg_color=RED_MAIN, hover_color=RED_HOVER, border_color="#333", text_color=TEXT_MAIN)
        if self.config["always_on_top"]: self.check_top.select()
        self.check_top.pack(pady=2, padx=35, anchor="w")

        tool_f = ctk.CTkFrame(self, fg_color="transparent")
        tool_f.pack(pady=10, padx=33, fill="x")
        tools = [("CENTER", self.center_window), ("HIDE", self.hide_window), ("MUTE", self.mute_window), ("SIZE", self.open_size_ritual), ("KILL", self.kill_process)]
        for i, (txt, cmd) in enumerate(tools):
            btn = ctk.CTkButton(tool_f, text=txt, font=("Consolas", 11, "bold"), 
                               fg_color=RED_MAIN if txt=="KILL" else "#111", 
                               hover_color=RED_HOVER, height=28, border_width=1, 
                               border_color=BORDER_COLOR, command=cmd)
            btn.grid(row=0, column=i, padx=1, sticky="ew")
        tool_f.grid_columnconfigure((0,1,2,3,4), weight=1)

        self.hk_f = ctk.CTkFrame(self, fg_color="transparent")
        self.hk_f.pack(pady=(2, 8), padx=35, fill="x")
        self.btn_hk_toggle = self.create_hk_button("TOGGLE", self.config["hk_toggle"], 0)
        self.btn_hk_reset = self.create_hk_button("RESET", self.config["hk_reset"], 1)

        self.btn_execute = ctk.CTkButton(self, text="EXECUTE", font=("Consolas", 18, "bold"), fg_color=RED_MAIN, hover_color=RED_HOVER, text_color="#FFF", height=40, command=self.transform_window)
        self.btn_execute.pack(pady=4, padx=35, fill="x")

        ctk.CTkLabel(self, text="SPIRITS", font=("Consolas", 12, "bold"), text_color=TEXT_DIM).pack(pady=(0, 2))
        self.list_border = ctk.CTkFrame(self, fg_color="#030303", border_width=1, border_color=BORDER_COLOR, height=94)
        self.list_border.pack(pady=0, padx=35, fill="x")
        self.list_border.pack_propagate(False)
        self.list_inner = ctk.CTkScrollableFrame(self.list_border, height=70, fg_color="transparent", scrollbar_button_color="#151515")
        self.list_inner.pack(fill="both", expand=True, padx=1, pady=1)

        self.footer = ctk.CTkLabel(self, text="github.com/hellkxxxi", font=("Consolas", 10, "underline"), text_color=TEXT_DIM, cursor="hand2")
        self.footer.pack(side="bottom", pady=15)
        self.footer.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/hellkxxxi"))
        self.footer.bind("<Enter>", lambda e: self.footer.configure(text_color=RED_MAIN))
        self.footer.bind("<Leave>", lambda e: self.footer.configure(text_color=TEXT_DIM))

        self.update_list_ui()

    def hide_to_tray(self):
        self.save_config()
        self.withdraw()

    def create_tray_icon(self):
        def on_clicked(icon, item):
            self.after(0, self.deiconify)
        
        def on_quit():
            self.save_config()
            self.tray.stop()
            self.destroy()
            os._exit(0)
        
        try: img = Image.open(resource_path("icon.png"))
        except: img = Image.new('RGB', (64, 64), color=RED_MAIN)

        self.tray = pystray.Icon("hellwindow", img, "HELLWINDOW", menu=pystray.Menu(
            pystray.MenuItem("Show", on_clicked),
            pystray.MenuItem("Exit", on_quit)
        ))
        self.tray.on_activate = on_clicked
        threading.Thread(target=self.tray.run, daemon=True).start()

    def open_size_ritual(self):
        if self.last_target_hwnd:
            SizeRitual(self, self.resize_window)

    def flash_effect(self):
        self.info_f.configure(border_color=RED_BRIGHT)
        self.after(200, lambda: self.info_f.configure(border_color=BORDER_COLOR))

    def create_hk_button(self, label, default, row):
        btn = ctk.CTkButton(self.hk_f, text=default, width=120, height=24, font=("Consolas", 12, "bold"), fg_color="#050505", border_width=1, border_color=BORDER_COLOR, text_color=TEXT_MAIN, hover_color=GREY_HOVER)
        btn.grid(row=row, column=0, pady=2)
        btn.configure(command=lambda b=btn, l=label: self.start_recording(b, l))
        ctk.CTkLabel(self.hk_f, text=label, font=("Consolas", 12, "bold"), text_color=TEXT_DIM).grid(row=row, column=1, padx=10, sticky="w")
        return btn

    def animate_scan_dot(self):
        try:
            c = self.scan_canvas.itemcget(self.scan_dot, "fill")
            self.scan_canvas.itemconfig(self.scan_dot, fill=RED_BRIGHT if c == RED_MAIN else RED_MAIN)
        except: pass
        self.after(800, self.animate_scan_dot)

    def track_active_window(self):
        while True:
            if not self.is_picking:
                try:
                    hwnd = win32gui.GetForegroundWindow()
                    if hwnd and win32gui.IsWindow(hwnd) and hwnd != self.winfo_id():
                        title = win32gui.GetWindowText(hwnd)
                        if title and title not in ["HELLWINDOW", "SIZE RITUAL"] and win32gui.IsWindowVisible(hwnd):
                            self.last_target_hwnd = hwnd
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            if pid not in self.process_cache:
                                try: self.process_cache[pid] = psutil.Process(pid).name()
                                except: self.process_cache[pid] = "Unknown"
                            proc = self.process_cache[pid]
                            self.label_window_name.configure(text=f"{proc} > {title}", text_color=TEXT_MAIN)
                except: pass
            if int(time.time()) % 5 == 0: self.after(0, self.auto_prune)
            time.sleep(0.4)

    def auto_prune(self):
        dead = [h for h in self.modified_windows if not win32gui.IsWindow(h)]
        dead += [h for h in self.hidden_windows if not win32gui.IsWindow(h)]
        if dead:
            for h in dead:
                self.modified_windows.pop(h, None)
                if h in self.hidden_windows: self.hidden_windows.remove(h)
            self.update_list_ui()

    def start_picker(self):
        if self.is_picking: return
        self.is_picking = True
        self.btn_picker.configure(text_color=RED_BRIGHT)
        self.label_window_name.configure(text="SELECT TARGET WINDOW...", text_color=RED_BRIGHT)
        
        def pick_logic():
            time.sleep(0.5)
            while self.is_picking:
                if win32api.GetAsyncKeyState(0x01) < 0:
                    point = win32api.GetCursorPos()
                    hwnd = win32gui.WindowFromPoint(point)
                    hwnd = win32gui.GetAncestor(hwnd, win32con.GA_ROOT)
                    if hwnd and win32gui.IsWindow(hwnd) and hwnd != self.winfo_id():
                        self.last_target_hwnd = hwnd
                        self.after(0, self.transform_window)
                        break
                time.sleep(0.05)
            self.is_picking = False
            self.after(0, lambda: self.btn_picker.configure(text_color=RED_MAIN))
        threading.Thread(target=pick_logic, daemon=True).start()

    def mute_window(self):
        hwnd = self.last_target_hwnd
        if not hwnd or not win32gui.IsWindow(hwnd): return
        def run_mute():
            try:
                ctypes.windll.ole32.CoInitialize(None)
                _, target_pid = win32process.GetWindowThreadProcessId(hwnd)
                p_name = psutil.Process(target_pid).name().lower()
                sessions = AudioUtilities.GetAllSessions()
                for session in sessions:
                    if (session.Process and session.Process.pid == target_pid) or \
                       (session.Process and session.Process.name().lower() == p_name):
                        session.SimpleAudioVolume.SetMute(not session.SimpleAudioVolume.GetMute(), None)
                self.after(0, self.flash_effect)
            except: pass
        threading.Thread(target=run_mute, daemon=True).start()

    def kill_process(self):
        if self.last_target_hwnd:
            try:
                self.flash_effect()
                _, pid = win32process.GetWindowThreadProcessId(self.last_target_hwnd)
                psutil.Process(pid).kill()
                self.last_target_hwnd = None
                self.label_window_name.configure(text="SEARCHING...", text_color=TEXT_DIM)
            except: pass

    def center_window(self):
        if self.last_target_hwnd and win32gui.IsWindow(self.last_target_hwnd):
            r = win32gui.GetWindowRect(self.last_target_hwnd)
            w, h = r[2]-r[0], r[3]-r[1]
            sw, sh = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
            win32gui.SetWindowPos(self.last_target_hwnd, 0, (sw-w)//2, (sh-h)//2, 0, 0, 1)
            self.flash_effect()

    def resize_window(self, w, h):
        if self.last_target_hwnd and win32gui.IsWindow(self.last_target_hwnd):
            win32gui.SetWindowPos(self.last_target_hwnd, 0, 0, 0, w, h, 6)
            self.flash_effect()

    def hide_window(self):
        hwnd = self.last_target_hwnd
        if hwnd and win32gui.IsWindow(hwnd) and hwnd not in self.hidden_windows:
            self.flash_effect()
            win32gui.ShowWindow(hwnd, 0)
            self.hidden_windows.add(hwnd)
            if hwnd not in self.modified_windows: self.modified_windows[hwnd] = win32gui.GetWindowLong(hwnd, -20)
            self.update_list_ui()

    def reveal_window(self, hwnd):
        if win32gui.IsWindow(hwnd): win32gui.ShowWindow(hwnd, 5)
        if hwnd in self.hidden_windows: self.hidden_windows.remove(hwnd)
        self.update_list_ui()

    def update_list_ui(self):
        for widget in self.list_inner.winfo_children(): widget.destroy()
        targets = [h for h in (set(self.modified_windows.keys()) | self.hidden_windows) if win32gui.IsWindow(h)]
        if not targets:
            ctk.CTkLabel(self.list_inner, text="-- empty --", font=("Consolas", 12, "bold"), text_color="#222").pack(pady=25)
            return
        for hwnd in targets:
            row = ctk.CTkFrame(self.list_inner, fg_color=ITEM_BG, height=30)
            row.pack(fill="x", pady=1, padx=2); row.pack_propagate(False)
            ctk.CTkButton(row, text="X", width=24, height=20, fg_color="transparent", hover_color=GREY_HOVER, text_color=RED_MAIN, font=("Consolas", 13, "bold"), command=lambda h=hwnd: self.release_window(h)).pack(side="right", padx=5)
            if hwnd in self.hidden_windows:
                ctk.CTkButton(row, text="REVEAL", width=50, height=18, fg_color="#050505", font=("Consolas", 10, "bold"), hover_color=GREY_HOVER, command=lambda h=hwnd: self.reveal_window(h)).pack(side="right", padx=2)
            ctk.CTkLabel(row, text="⛧", font=("Consolas", 15, "bold"), text_color=RED_MAIN).pack(side="left", padx=5)
            title = win32gui.GetWindowText(hwnd) or "Spirit"
            if hwnd in self.hidden_windows: title = f"[HIDDEN] {title}"
            ctk.CTkLabel(row, text=title, font=("Consolas", 12, "bold"), text_color=TEXT_MAIN, anchor="w").pack(side="left", fill="x", expand=True, padx=(5, 8))

    def transform_window(self):
        hwnd = self.last_target_hwnd
        if not hwnd or not win32gui.IsWindow(hwnd) or hwnd == self.winfo_id(): return
        self.flash_effect()
        if hwnd not in self.modified_windows:
            try:
                s = win32gui.GetWindowLong(hwnd, -20); self.modified_windows[hwnd] = s
                ns = s | 0x80000
                if self.check_click.get(): ns |= 0x20
                win32gui.SetWindowLong(hwnd, -20, ns)
                ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, int(self.slider.get()), 0x2)
                if self.check_top.get(): win32gui.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 3)
                self.update_list_ui()
            except: pass
        else: self.release_window(hwnd)

    def release_window(self, hwnd):
        try:
            if hwnd in self.hidden_windows: self.reveal_window(hwnd)
            if hwnd in self.modified_windows:
                if win32gui.IsWindow(hwnd):
                    win32gui.SetWindowPos(hwnd, -2, 0, 0, 0, 0, 3)
                    win32gui.SetWindowLong(hwnd, -20, self.modified_windows[hwnd])
                    win32gui.RedrawWindow(hwnd, None, None, 1283)
                del self.modified_windows[hwnd]
        except: pass
        self.update_list_ui()

    def release_all(self):
        for hwnd in list(self.modified_windows.keys()) + list(self.hidden_windows): self.release_window(hwnd)

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
        button.configure(text=new_hk)
        self.config["hk_toggle" if label == "TOGGLE" else "hk_reset"] = new_hk
        self.save_config(); self.apply_hotkeys(); self.is_recording = False

    def update_pct_label(self, val):
        self.label_pct.configure(text=f"{int((float(val) / 255) * 100)}%")
        v = int(float(val))
        color = f"#{max(40, v):02x}0000"
        self.slider.configure(progress_color=color)

    def apply_hotkeys(self):
        try:
            keyboard.unhook_all()
            keyboard.add_hotkey(self.config["hk_toggle"], self.transform_window)
            keyboard.add_hotkey(self.config["hk_reset"], self.release_all)
        except: pass

if __name__ == "__main__":
    app = HellWindow()
    app.mainloop()