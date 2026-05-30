<h1 align="center">⛧ HELLWINDOW ⛧</h1>

<p align="center">
  a brutalist, amoled-style windows utility for advanced window management. inspired by tools like WindowTop, but focused on speed, minimalism, and a dark aesthetic.
</p>

<p align="center">
  <img src="assets/preview.png" alt="HELLWINDOW Preview" width="400">
</p>

  disclaimer: this tool is intended for personal productivity. use it wisely.  
  
  ![License](https://img.shields.io/badge/license-MIT-990000?style=flat-square)

## ⛧ features
- **ghost mode**: make any window non-clickable (click-through).
- **transparency**: adjust opacity from 7% to 100%.
- **always on top**: pin target window above everything else.
- **spirit list**: manage active transformations in a micro-ui.
- **hotkey recording**: rebind keys by clicking on them.
- **amoled design**: pure black, deep blood-red accents.
- **auto-save**: all your preferences and hotkeys are saved to `config.json`.

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

1. install pyinstaller:

```bash
pip install pyinstaller
```

2. run the build script:

```bash
 pyinstaller --noconsole --onefile --uac-admin --collect-all customtkinter --icon=icon.ico --add-data "icon.png;." --name HELLWINDOW hellwindow.py
 ```
 
## ⛧ warning
antivirus software may flag the .exe as a false positive due to keyboard hooks and pyinstaller packaging. this is normal for low-level system utilities.

## ⛧ author
created by **hellkai**
[telegram](https://t.me/k41h311)