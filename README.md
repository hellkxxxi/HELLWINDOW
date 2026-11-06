<h1 align="center">⛧ HELLWINDOW ⛧</h1>

<p align="center">
  a brutalist, amoled-style windows utility for advanced window management. inspired by tools like WindowTop, but focused on speed, minimalism, and a dark aesthetic. made for those who prefer ritualistic minimalism and total control over their workspace.
</p>

<p align="center">
  <img src="assets/preview v1.2.png" alt="HELLWINDOW Preview" width="402">
</p>

the tool monitors your focus and captures the last active window before you switch to hellwindow

  *disclaimer: this tool is intended for personal productivity. use it wisely.*
  
  <p align="center">
  <img src="https://img.shields.io/github/v/release/hellkxxxi/HELLWINDOW?color=990000&label=version&style=flat-square">
  <img src="https://img.shields.io/github/license/hellkxxxi/HELLWINDOW?color=990000&style=flat-square">
  <img src="https://img.shields.io/github/downloads/hellkxxxi/HELLWINDOW/total?color=990000&style=flat-square">
</p>

## ⛧ how it works
hellwindow manipulates the deep windows api to grant you powers over any active window:
- **ghost mode**: injects `WS_EX_TRANSPARENT` style, making the window a "spirit" that your mouse ignores. clicks pass through it to whatever is behind.
- **transparency**: controls the alpha channel of the window layer (7% to 100%).
- **always on top**: forces the window to stay at the top of the z-order (`HWND_TOPMOST`).
- **auto-save**: all your preferences and hotkeys are saved to `config.json`.

## ⛧ quick rituals (tools)
- **center**: snaps the targeted window to the screen's dead center.
- **hide**: removes the window from sight and taskbar. tagged as `[HIDDEN]` in the list.
- **mute**: silences the targeted process's audio stream.
- **size**: opens a themed ritual dialog to define custom window dimensions (width/height).
- **kill**: instantly terminates the process. no confirmation, no mercy.

## ⛧ spirit list
this is your necronomicon. every window you transform is tracked here:
- use **reveal** to bring back windows lost in the **hide** ritual.
- click **X** to release a window and restore its original state.
- the tool monitors your focus and automatically targets the last active window.

## ⛧ hotkeys
- **toggle**: click the button to record a new key combination.
- **reset**: clear all active spirits and return them to the mortal realm.

## ⛧ installation
1. clone the ritual:
```bash
git clone https://github.com/hellkxxxi/HELLWINDOW.git
```
2. install dependencies:

```bash
pip install -r requirements.txt
```
3. run as administrator:

```bash
python hellwindow.py
```

## ⛧ building exe
to create a standalone portable executable:

1. install dependencies:

```bash
pip install customtkinter pywin32 keyboard psutil pycaw comtypes pystray Pillow
```

2. run the build script:

```bash
pyinstaller --noconsole --onefile --uac-admin --collect-all customtkinter --icon=icon.ico --add-data "icon.png;." --add-data "icon.ico;." --name HELLWINDOW hellwindow.py
 ```
 
## ⛧ warning
antivirus software may flag the .exe as a false positive due to keyboard hooks and pyinstaller packaging. this is normal for low-level system utilities.

## ⛧ tech stack
- **customtkinter**: for the amoled interface.
- **pywin32**: for deep windows api integration.
- **keyboard**: for global ritual hooks.
- **psutil**: for process soul harvesting.
- **pycaw**: for audio session manipulation.
- **pystray & Pillow**: for system tray manifestation.

## ⛧ author
created by **hellkai \\ hellkxxxi**
