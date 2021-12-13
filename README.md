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
self._settings_default_editor = ""


**###Planned Changes:**

-Add visual for which tool (pencil or bucket) is selected.

-Make pop-up windows appear at a location that makes sense.

-add an undo/redo queue

-add a config file for users to set controls/ default behavior of the app.

-implement the grow/shrink map feature to add rows/columns to existing maps.

-import existing images to be used as hexmap background (overlay a grid onto existing image)
