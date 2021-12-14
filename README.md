# hexmappy
Hexmappy is a hex-grid map making tool intended for creating region maps for ttrpgs and hex-crawls. It has a simple MS paint-like interface for painting maps, and is almost as visually appealing.  It has simple note taking functionality that allows you to link text files to individual hex tiles, to aid in encounter planning or world-building. Hexmappy is written in python and has been tested and runs on windows, mac, and linux. 

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

- _**Your tileset is required to have a tile named "grass.png" and a tile named "water.png".**_

- Place all images into a single folder named under the following scheme: <tileset_name>x<image_height>x<image_width>.

- tile images should have a pointy side of the hexagon pointed directly up, flat sides on the left and right of the image.
example: "defaultx200x175", "mytilesetx420x69"

- *avoid using the letter x in your tileset name for now.*


**Saving Maps**

The name of the current map can be found in the title of the window after "Hexmappy Vx.y -- ", and should be a sequence of numbers. The default save folder is named "saves" in the same directory as hexmappy.py. Folders inside the saves directory be renamed safely, a new .hexmap file will be saved using the name of the folder on your next save.

Support for naming your maps before saving coming soon™
