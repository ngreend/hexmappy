# hexmappy
Hexagon tile based map editor.

## Controls:

W-A-S-D to move around the map

left click to interact

mouse wheel to zoom in/ zoom out.

**####Note Editor**

-on windows Notepad is the default.

-on other platforms a tkinter text box will open. When done adding text close the window and the text is saved automatically.

-A default text editor can be set by editing hexmappy.py and putting your default text editors name into the quotes on line 110.

**Examples:**

self._settings_default_editor = "notepad.exe"

self._settings_default_editor = "emacs"

self._settings_default_editor = "kate"


**Planned Changes:**

Adding tilesets:
  Place all images into a single folder named under the following scheme: <tileset_name>x<image_height>x<image_width>.
  
  example: "defaultx200x175", "mytilesetx200x175"
  
  *avoid using the letter x in your tileset name, at least for now.*
