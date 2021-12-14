# hexmappy
Hexagon tile based map editor.

## Installation

Download the repository and unzip it, alternatively clone the repository.

Hexmappy requires pygame (https://github.com/pygame/pygame) and python 3.

run the following commands in a terminal to install pygame then run Hexmappy.
```
pip install pygame
```
```
python hexmappy.py
```


## Controls:

W-A-S-D to move around the map

left click to interact

mouse wheel to zoom in/ zoom out.

**####Note Editor**

-on windows Notepad is the default.

-on other platforms a tkinter text box will open. When done adding text close the window and the text is saved automatically.

-A default text editor can be set by editing hexmappy.py and putting your default text editors name into the quotes on line 110.

Examples:

self._settings_default_editor = "notepad.exe"

self._settings_default_editor = "emacs"

self._settings_default_editor = "kate"



**Adding tilesets:** 

Place all images into a single folder named under the following scheme: <tileset_name>x<image_height>x<image_width>.

example: "defaultx200x175", "mytilesetx200x175"

*avoid using the letter x in your tileset name, at least for now.*

**Saves Folder**

Folders inside the saves directory be renamed safely, a new .hexmap file will be saved using the name of the folder on your next save.

Support for naming your maps before saving coming soon™
