+++
author = "rl1987"
title = "Compiling Python programs with Pyinstaller"
date = "2022-04-19"
tags = ["python", "devops"]
+++

[Pyinstaller](https://pyinstaller.org/en/stable/) is a CLI tool that compiles Python scripts into executable binaries,
installable through PIP. Let us go through a couple of examples of using this tool.

SMTP enumeration script from [previous post](/post/smtp-user-enumeration-for-fun-and-profit/) can be trivially compiled
with this tool by running the following commnd:

```
$ pyinstaller smtp_enum.py
```

This creates two directories - build/ for intermediate files and dist/ for the results of compilation. However we
find that dist/ contains multiple binary files, whereas it is generally more convenient to compile it into single
file that statically links all the dependencies. Adding `--onefile` argument to our command tells the Pyinstaller
to do so:

```
$ pyinstaller --onefile smtp_enum.py
```

On Windows this create an .exe file; on Linux and macOS it will create a platform specific binary. Cross-compilation
is not supported.

However things will not always be so simple. We may want to compile something like the following code that imports
third party modules and has a GUI with image to be loaded from the file. This code is largely based on someone
elses [educational example](https://github.com/flatplanet/Intro-To-TKinter-Youtube-Course/blob/master/bitcoin.py)
that I took the liberty to update and clean up a little. It will scrape Bitcoin price from Coindesk and show it
in a GUI window.

```python3
#!/usr/bin/python3

from tkinter import *
from datetime import datetime

import requests
from lxml import html

previous = None

# Grab the bitcoin price
def Update():
    global previous

    resp = requests.get("https://www.coindesk.com/price/bitcoin")
    print(resp.url)
        
    tree = html.fromstring(resp.text)
    price_large = tree.xpath('//span[contains(@class, "briNjb")]')[0].text
    price_large = price_large.replace(",", "")

    print(price_large)

    # Update our bitcoin label
    bit_label.config(text=price_large)
    # Set timer to 30 seconds
    # 1 second = 1000
    root.after(30000, Update)

    # Get Current Time
    now = datetime.now()
    current_time = now.strftime("%I:%M:%S %p")

    # Update the status bar
    status_bar.config(text=f"Last Updated: {current_time}   ")

    # Determine Price Change
    # grab current Price
    current = price_large

    # remove the comma
    current = current.replace(",", "")

    if previous is not None:
        if float(previous) > float(current):
            latest_price.config(
                text=f"Price Down {round(float(previous)-float(current), 2)}", fg="red"
            )

        elif float(previous) == float(current):
            latest_price.config(text="Price Unchanged", fg="grey")

        else:
            latest_price.config(
                text=f"Price Up {round(float(current)-float(previous), 2)}", fg="green"
            )
    else:
        previous = current
        latest_price.config(text="Price Unchanged", fg="grey")


def main():
    global root
    global bit_label
    global status_bar
    global previous
    global latest_price

    root = Tk()
    root.title("Bitcoin Price Grabber")
    root.geometry("550x210")
    root.config(bg="black")

    now = datetime.now()
    current_time = now.strftime("%I:%M:%S %p")

    my_frame = Frame(root, bg="black")
    my_frame.pack(pady=20)

    logo = PhotoImage(file="images/bitcoin.png")
    logo_label = Label(my_frame, image=logo, bd=0)
    logo_label.grid(row=0, column=0, rowspan=2)

    bit_label = Label(
        my_frame, text="TEST", font=("Helvetica", 45), bg="black", fg="green", bd=0
    )
    bit_label.grid(row=0, column=1, padx=20, sticky="s")

    latest_price = Label(
        my_frame, text="move test", font=("Helvetica", 8), bg="black", fg="grey"
    )
    latest_price.grid(row=1, column=1, sticky="n")

    # Create status bar
    status_bar = Label(
        root,
        text=f"Last Updated {current_time}   ",
        bd=0,
        anchor=E,
        bg="black",
        fg="grey",
    )

    status_bar.pack(fill=X, side=BOTTOM, ipady=2)

    # On program start, run update function
    Update()

    root.mainloop()


if __name__ == "__main__":
    main()
```

As our first attempt, we run the following command:

```
$ pyinstaller --onefile bitcoin.py
```

Compilation succeeds, but the program crashes due to not being able to find an image file:

```
$ cd dist/
$ ./bitcoin 
Traceback (most recent call last):
  File "bitcoin.py", line 113, in <module>
  File "bitcoin.py", line 80, in main
  File "tkinter/__init__.py", line 4064, in __init__
  File "tkinter/__init__.py", line 4009, in __init__
_tkinter.TclError: couldn't open "images/bitcoin.png": no such file or directory
[26587] Failed to execute script 'bitcoin' due to unhandled exception!
```

This is because we have a hardcoded relative path to the file that the program is not generally
able to resolve. It would be best if the image file was compiled into executable as well.
Turn out, according to a certain helpful [StackOverflow answer](https://stackoverflow.com/a/54926684)
there are two simple fixes we need to do (altough the question was about compiling PyGame-based
game that includes graphical and sound assets, the answer can be applied for the scripts
like the one we are dealing with).

The first fix is to introduce a following function to resolve a relative path to an
asset file, then making sure that all code uses it instead of trying to access hardcoded paths
directly:

```python
import sys
import os

def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
```

For the script in question, we only need to update the `PhotoImage()` constructor call to use
`resource_path()` function:

```python
    logo = PhotoImage(file=resource_path("images/bitcoin.png"))
```

Now we rerun the command from before:

```
$ pyinstaller --onefile bitcoin.py
```

However, the binary executable file still crashes when we try to run it. The second fix we have to
do is to update bitcoin.spec file that originally looks like this:

```python
# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['bitcoin.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='bitcoin',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

Think of this file as a build configuration file. Like we can see, it specifies a script name and various build options.
We need to update `datas` line with a list of tuples for each asset (1 entry in our case). First element in the tuple
is source path of the asset. Second element is destination directory path. We want these to be consistent, as 
launching the Python script from binary version and from the source should load exactly the same file. Thus we update
this line as follows:

```python
    datas=[("images/bitcoin.png", "images/")],
```

Now we can compile the script based on the spec file:

```
$ pyinstaller bitcoin.spec
```

This generates a functional executable we can run. On macOS, it even creates an .app package we can copy into /Applications
directory.

[Screenshot](/2022-04-19_20.31.10.png)

