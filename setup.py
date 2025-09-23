from setuptools import setup

APP = ['main.py']
OPTIONS = {
    'argv_emulation': True,  # lets the app handle drag-and-drop files
    'packages': ['requests'], # any external packages your app uses
    "includes": ["tkinter"],      # 👈 force Tkinter
    "frameworks": ["/System/Library/Frameworks/Tk.framework"], 
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)