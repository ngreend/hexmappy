"""
    Hexmappy is an application designed to create and edit hexagon based tile maps and notes related to created maps.

    Copyright 2021 Nathan Green

    Hexmappy is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    Hexmappy is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Hexmappy.  If not, see <https://www.gnu.org/licenses/>.
"""

import sys, os
import platform
import random
import math
from operator import floordiv
import pygame
from pygame.locals import *
import threading
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.scrolledtext

import utils
import mapgen
import hextile
import button

class Main():
    def __init__(self):
        pygame.init()
        self.CLOCK = pygame.time.Clock()
        #self.LABEL_FONT = pygame.font.SysFont("DejaVu Sans Mono", 48, bold=True)
        
        pygame.key.set_repeat(0)

        self.SCREEN_WIDTH = 1440
        self.SCREEN_HEIGHT = 1080
        self.SCREEN_ASPECT_RATIO = [4, 3]
        self.MIN_VIEW_DISTANCE = 692
        self.MAX_VIEW_DISTANCE = 9999999 #this is a large number that is changed later based on the SCREEN_ASPECT_RATIO
        
        self.CAMERA = pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.CAMERA.center = (self.CAMERA.width/2, self.CAMERA.height/2)
        self.FOV = 60
        self.LAST_VIEW_DISTANCE = self.MIN_VIEW_DISTANCE
        self.VIEW_DISTANCE = self.MIN_VIEW_DISTANCE
        self.ZOOM_ENABLED = True
        self.ZOOM_IN = False
        
        self.MOUSE_X = 0
        self.MOUSE_Y = 0
        self.LAST_MOUSE_X = 0
        self.LAST_MOUSE_Y = 0
        self.MOUSE_CLICK_X = -1
        self.MOUSE_CLICK_Y = -1

        self.MOUSE_STATES = {
            "LEFT" : False,
            "RIGHT" : False,
            "MIDDLE" : False
        }
        
        self.KEY_STATES = {
            "CAM_UP" : False,
            "CAM_LEFT" : False,
            "CAM_DOWN" : False,
            "CAM_RIGHT" : False
        }
        
        info = pygame.display.Info()
        self.HOST_MONITOR_SIZE = [info.current_w, info.current_h]
        self.SCREEN = pygame.display.set_mode((self.CAMERA.width, self.CAMERA.height), RESIZABLE)
        self.COPY_OF_SCREEN = self.SCREEN.copy()
        self.BACKGROUND = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT)).convert()
        self.BACKGROUND.fill(utils.CREAM)
        #info = pygame.display.Info()
        #print(info)

        self.NOTES_THREADS = []
                
        self._map_orientation = "H"
        self._map_width = 45
        self._map_height = 45
        self.genny = mapgen.MapGen(self._map_width, self._map_height, self._map_orientation)
        self._map, self._map_name= self.genny.getNewWorldMap() #self.makeWorldMap(self._map_orientation)
        self._map_tiles_to_update = []
        self._map_notes_save_path = None

        #used for 'optimized' mode LOL
        self.map_surface_rect = None
        #used for _settings_IMAGE_IN_RAM_MODE
        self.map_surface_source = None
        self.map_surface_source_rect = None
        self.visible_surface = None
        self.visible_surface_rect = None
        
        #SETTINGS
        self._settings_draw_grid = True
        self._settings_draw_cell_names = True
        self._settings_default_editor = ""
        self._settings_IMAGE_IN_RAM_MODE = True
        self._settings_default_save_location = os.path.join(os.path.dirname(__file__), "saves")

        if not os.path.isdir(self._settings_default_save_location):
            os.mkdir(self._settings_default_save_location)
        
        self.current_tileset = os.path.join(os.path.dirname(__file__), "tilesets", "defaultx200x175")
        self.tiles = {"H": {}, "V": {}}
        self.tile_size = {"H": (0,0), "V": (0,0)}
        self.loadTileset(self.current_tileset)
        self._tileset_map = []
        self._tileset_map_orientation = "V"
        self.palette_tiles_across = 9
        self.palette_surface = None
        self.palette_surface_rect = None
        self.palette_scaled_tile_width = 0
        self.palette_scaled_tile_height = 0
        self._tileset_primary = list(self.tiles[self._map_orientation].keys())[0]
        self._tileset_secondary = list(self.tiles[self._map_orientation].keys())[-1]
        #tools = PENCIL, BUCKET, NOTE,  
        self.current_tool = "PENCIL" 
        #print(self._tileset_primary + ", " + self._tileset_secondary)

        #UI
        self._ui_hexLabel_fontsize = 24
        self._ui_button_font = pygame.font.SysFont("default", 24)
        self._ui_header_font = pygame.font.SysFont("default", 40)        
        self._ui_toolbar_horizontal_size = int(self.SCREEN_WIDTH / 5)
        self._ui_toolbar_vertical_size = self.SCREEN_HEIGHT
        self._ui_rect = pygame.Rect(0,0,self._ui_toolbar_horizontal_size, self._ui_toolbar_vertical_size)
        self._ui_surface = pygame.Surface((self._ui_rect.width, self._ui_rect.height)).convert()        
        self._ui_surface.fill(utils.GRAY_DARK)
        
        self._ui_padding_amt = 5.0
        self._ui_panels = {"MAPPING": [], "NOTES": []}
        self._ui_visible_panel = "MAPPING"
        #This will decode the button actions to things we want to do, ie swap panels, etc.
        self._ui_action_dict = {
            "Mapping": self.swapToMappingPanel,
            "Notes": self.swapToNotesPanel,
            "Tileset": self.chooseTileset, #choose tileset folder to load
            "?Palette?": self.update_selected_palette_tile,
            "Pencil": self.swapToPencil,
            "Bucket": self.swapToBucket,
            "Load Map": self.loadMap,
            "Save Map": self.saveMap,
#            "Grow/Shrink Map": self.growShrinkMap,
            "New Blank Map": self.newBlankMap,
            "Generate Map": self.generateNewMap,
            "Show/Hide Grid": self.toggleGrid,
            "Show/Hide Cell Names": self.toggleCellNames,
            "Export Visible to PNG": self.exportToPNG,
#            "Import Background": self.import_image_as_background,
#            "Set Grid Size": self.ui_action_not_supported
        }
        #self._ui_action_dict["Save Map"]()
        
        self.makeUI()
        
        self.caption = "Hexmappy 1.0"
        pygame.display.set_caption(f'{self.caption} -- {self._map_name}')

        if self._settings_IMAGE_IN_RAM_MODE:
            self.makeMapSurface()
        else:
            self.makeMapRect()


    def ui_action_not_supported(self):
        print(f'Action not yet supported.')
        
    #This function creates buttons according to the almighty LIST_OF_BUTTONS,
    #not the prettiest but it works.
    #Phrases separated by '|' will be on the same horizontal,
    #?Palette?" is where our tileset palette surface goes.
    def makeUI(self):
        LIST_OF_BUTTONS = {
            "MAPPING" : [
                "Mapping|Notes",
                "Tileset",
                "?Palette?",
                "Pencil|Bucket",
                "Load Map|Save Map",
#                "Grow/Shrink Map",
                "New Blank Map",
                "Generate Map",
                "Show/Hide Grid",
                "Show/Hide Cell Names",
                "Export Visible to PNG"],
            
            "NOTES" : [
                "Mapping|Notes"
#                "Import Background",
#                "Set Grid Size"]
                ]
            }
                
        for b in LIST_OF_BUTTONS:
            y_start = 0
            for br in LIST_OF_BUTTONS[b]:
                y_start += self._ui_padding_amt
                button_padding = 4*self._ui_padding_amt
                s = br.split("|")
                if len(s) > 1:
                    #print(s)
                    bs = self._ui_button_font.size(s[0])
                    button_size = [button_padding + bs[0], button_padding + bs[1]]
                    surf = pygame.Surface((button_size[0],button_size[1])).convert()
                    surf.fill(utils.GRAY_DARK)
                    surf_clicked = surf.copy()
                    text = self._ui_button_font.render(s[0], True, utils.BLACK)
                    surf.blit(text, (button_padding/2, button_padding/2))
                    surf_clicked.blit(text, (button_padding/2, button_padding/2))
                    
                    bs2 = self._ui_button_font.size(s[1])
                    button_size2 = [button_padding + bs2[0], button_padding + bs2[1]]
                    surf2 = pygame.Surface((button_size2[0],button_size2[1])).convert()
                    surf2.fill(utils.GRAY_DARK)
                    surf_clicked2 = surf2.copy()
                    text2 = self._ui_button_font.render(s[1], True, utils.BLACK)
                    surf2.blit(text2, (button_padding/2, button_padding/2))
                    surf_clicked2.blit(text2, (button_padding/2, button_padding/2))
                    
                    combined_width = button_size[0] + button_size2[0] + self._ui_padding_amt
                    x_start = (self._ui_rect.centerx - (combined_width/2))
                    x_start2 = (x_start + button_size[0] + self._ui_padding_amt)
                    self._ui_panels[b].append(button.Button(x_start, y_start, surf, surf_clicked, s[0]))
                    self._ui_panels[b].append(button.Button(x_start2, y_start, surf2, surf_clicked2, s[1]))

                    y_start += button_size[1]
                elif br[0] == "?":
                    ts_width, ts_height = self.makeTilesetPalette()
                    surf = pygame.Surface((ts_width, ts_height)).convert()
                    surf.fill(utils.MISSING_TEXTURE_PURPLE)
                    surf.set_colorkey(utils.MISSING_TEXTURE_PURPLE)
                    surf_clicked = surf.copy()
                    x = self._ui_rect.centerx - (ts_width/2)
                    y = y_start
                    self.draw_tile_palette_surface()
                    self.update_selected_palette_tile()
                    self._ui_panels[b].append(button.Button(x, y, surf_clicked, surf, br))
                    self.palette_surface_rect.left = x
                    self.palette_surface_rect.top = y
                    y_start += ts_height
                else:
                    #print(b)
                    bs = self._ui_button_font.size(br)
                    button_size = [button_padding + bs[0], button_padding + bs[1]]
                    surf = pygame.Surface((button_size[0],button_size[1])).convert()
                    surf.fill(utils.GRAY_DARK)
                    surf_clicked = surf.copy()
                    text = self._ui_button_font.render(br, True, utils.BLACK)
                    surf.blit(text, (button_padding/2, button_padding/2))
                    surf_clicked.blit(text, (button_padding/2, button_padding/2))
                    self._ui_panels[b].append(button.Button(self._ui_rect.centerx - (button_size[0]/2), y_start, surf, surf_clicked, br))
                    y_start += button_size[1]
        #Down here we swap the surface_clicked and surface fields for the Mapping and Notes buttons,
        #because when one is open the button should be depressed.
        tempS = self._ui_panels["MAPPING"][0].surface_clicked
        self._ui_panels["MAPPING"][0].surface_clicked = self._ui_panels["MAPPING"][0].surface
        self._ui_panels["MAPPING"][0].surface = tempS
        tempS = self._ui_panels["NOTES"][1].surface_clicked
        self._ui_panels["NOTES"][1].surface_clicked = self._ui_panels["NOTES"][1].surface
        self._ui_panels["NOTES"][1].surface = tempS
        self._ui_panels["MAPPING"][3].surface = self._ui_panels["MAPPING"][3].surface_clicked

    #called on resizing the window and when loading a new tileset
    #this function just adjusts where the buttons should be drawn, and rebuilds the
    #tile palette surface.
    def rebuild_UI(self):     
        change = False
        y = 0
        
        for b in self._ui_panels["MAPPING"]:
            if change:
                if b.action == "Bucket" or b.action == "Save Map":
                    y -= b.rect.height
                    b.rect.top = y
                    y += b.rect.height
                else:
                    y += self._ui_padding_amt
                    b.rect.top = y
                    y += b.rect.height            
            if b.action == "?Palette?":
                ts_width, ts_height = self.makeTilesetPalette()
                surf = pygame.Surface((ts_width, ts_height)).convert()
                surf.fill(utils.MISSING_TEXTURE_PURPLE)
                surf.set_colorkey(utils.MISSING_TEXTURE_PURPLE)
                surf_clicked = surf.copy()
                x = self._ui_rect.centerx - (ts_width/2)
                y = b.rect.top
                self.draw_tile_palette_surface()
                self.update_selected_palette_tile()
                b.updateSurf(surf_clicked, surf)
                self.palette_surface_rect.left = x
                self.palette_surface_rect.top = y               
                change = True
                y = b.rect.bottom
                b.surface = b.surface_clicked

    #creates a surface to hold every tile in our tileset (scaled down)
    #and updates our _tileset_map so we can find out which tile we clicked on.
    def makeTilesetPalette(self):
        scaled_tile_width = 32
        scaled_tile_height = 32
        num_rows = math.ceil(len(self.tiles["V"]) / self.palette_tiles_across)
        tileset_surface_width = self.palette_tiles_across * (3*scaled_tile_width/4) + (scaled_tile_height/4)
        tileset_surface_height = (num_rows * scaled_tile_height) + (scaled_tile_height/2)
        self.palette_scaled_tile_width = scaled_tile_width
        self.palette_scaled_tile_height = scaled_tile_height
        
        self.palette_surface = pygame.Surface((tileset_surface_width, tileset_surface_height)).convert()
        self.palette_surface.fill(utils.GRAY_DARK)
        self.palette_surface_rect = self.palette_surface.get_rect()

        #So I do this kinda stupidly for how i use it. I do the same thing as making
        #a map map, but that just makes things more long winded for this use case.
        #should rewrite this to make the tile palette map be a 1D list.
        m = []
        row = 0
        col = 0
        r = []
        for key, val in self.tiles["V"].items():
            r.append(key)          
            col += 1
            if col > self.palette_tiles_across-1:
                col = 0
                row += 1
                m.append(r.copy())
                r.clear()
        m.append(r)
        self._tileset_map = m
        return (4 + tileset_surface_width, 4 + tileset_surface_height)

    #draws each tile in our tileset to the tileset surface
    def draw_tile_palette_surface(self):
        self.palette_surface.fill(utils.GRAY_DARK)
        row = 0
        col = 0
        for i in range(len(self._tileset_map)):
            for j in range(len(self._tileset_map[i])):
                x = col * (3*self.palette_scaled_tile_width/4)
                y = row * self.palette_scaled_tile_height
                if col % 2 != 0:
                    y = (row * self.palette_scaled_tile_width) + (self.palette_scaled_tile_height/2)
                val = self.tiles["V"][self._tileset_map[i][j]]
                self.palette_surface.blit(pygame.transform.scale(val, (self.palette_scaled_tile_width, self.palette_scaled_tile_height)), (x, y))
                col += 1
                if col > self.palette_tiles_across - 1:
                    col = 0
                    row += 1

    #outlines the selected tile on our palette
    def update_selected_palette_tile(self):
        x = int(self.palette_scaled_tile_width/2)
        y = int(self.palette_scaled_tile_height/2)
        self.draw_tile_palette_surface()
        offset_row_toggle = 0
        points = utils.hex_corners_vertical_scaled(x, y, self.palette_scaled_tile_width+2, self.palette_scaled_tile_height)
        for i in range(6):
            j = i + 1
            if j == len(points):
                j = 0
            pygame.draw.lines(self.palette_surface, utils.GRID_LINE_COLOR, False, (points[i], points[j]), width=4)
            if offset_row_toggle == 0:
                offset_row_toggle = 1
            else:
                offset_row_toggle = 0
                                
        mousex_on_palette = self.MOUSE_X - self.palette_surface_rect.left
        mousey_on_palette = self.MOUSE_Y - self.palette_surface_rect.top
        numhexes = len(self.tiles["V"])
        list_of_center_points = []
        col = 0
        row = 0
        for i in range(numhexes):
            x = int(col * (3 * self.palette_scaled_tile_width/4) + (self.palette_scaled_tile_width/2))
            y = int((row * self.palette_scaled_tile_height) + (self.palette_scaled_tile_height/2))
            if col % 2 != 0:
                y = int((row * self.palette_scaled_tile_height) + (self.palette_scaled_tile_height))
            list_of_center_points.append((x,y))
            col += 1
            if col > self.palette_tiles_across-1:
                col = 0
                row += 1
        radius = (self.palette_scaled_tile_height-1)/2
        #print("searching in points")
        for i, p in enumerate(list_of_center_points):
            if utils.point_collide_circle(mousex_on_palette, mousey_on_palette, radius, p[0], p[1]):
                selected_tile = self._tileset_map[floordiv(i, self.palette_tiles_across)][i%self.palette_tiles_across]
                #print(selected_tile)
                self._tileset_primary = selected_tile
                self.draw_tile_palette_surface()
                offset_row_toggle = 0
                points = utils.hex_corners_vertical_scaled(p[0], p[1], self.palette_scaled_tile_width, self.palette_scaled_tile_height)
                for i in range(6):
                    j = i + 1
                    if j == len(points):
                        j = 0
                    pygame.draw.lines(self.palette_surface, utils.GRID_LINE_COLOR, False, (points[i], points[j]), width=4)
                    if offset_row_toggle == 0:
                        offset_row_toggle = 1
                    else:
                        offset_row_toggle = 0
                return
        self._tileset_primary = self._tileset_map[0][0]

    #draws all buttons of the visible UI to the _ui_surface
    def drawUI(self):
        self._ui_surface.fill(utils.GRAY_DARK)
        for thing in self._ui_panels[self._ui_visible_panel]:
            if thing.drawClicked:
                self._ui_surface.blit(thing.surface_clicked, thing.rect)
            else:
                self._ui_surface.blit(thing.surface, thing.rect)
            if thing.action == "?Palette?":
                x = thing.rect.left + 2
                y = thing.rect.top + 2
                self._ui_surface.blit(self.palette_surface, (x,y))

    #swaps the tileset
    def chooseTileset(self):
        #print("choosing tileset...")
        root = tk.Tk()
        root.withdraw()
        test = fd.askdirectory(title="Enter Tileset Folder", initialdir=os.path.join(os.path.dirname(__file__), "tilesets"))
        if isinstance(test, str):
            self.loadTileset(test)
            #print(self.tiles["V"])
            self.rebuild_UI()

    #this function imports an image as a pygame surface, for the intended
    #purpose of overlayign a grid onto the image and using it as a background for our map
    #not implemented yet.
    def import_image_as_background(self):
        root = tk.Tk()
        root.withdraw()
        test = fd.askopenfilename(title="Load Saved Hexmap")
        if len(test) > 0:
            self.map_surface_source = utils.loadImage(test, COLORKEY=False)
            self.map_surface_source_rect = self.map_surface_source.get_rect()

    def swapToBucket(self):
        self.current_tool = "BUCKET"

    def swapToPencil(self):
        self.current_tool = "PENCIL"

    #Sets the visible ui panel to the "NOTES" panel, saves current hex map to a folder where notes will be stored.
    def swapToNotesPanel(self):
        self._ui_visible_panel = "NOTES"
        self.drawUI()
        savePath = self._settings_default_save_location +  os.path.sep + str(self._map_name)
        if not os.path.isdir(savePath):
            os.mkdir(savePath)
        self._map_notes_save_path = savePath + os.path.sep
        utils.save_map_to_file(self._map, self._map_orientation, self._map_notes_save_path + str(self._map_name), self.current_tileset)
    #if no default editor is set, open a simple tk text window for inputting notes.
    def spawnEditor(self, tile_name):
        if self._settings_default_editor.strip() == "":
            self.NOTES_THREADS.append(threading.Thread(target=self.makeNote, args=(tile_name + ".txt",), daemon=True).start())
        else:
            os.system(self._settings_default_editor + " " + self._map_notes_save_path + tile_name + ".txt")

    #Simple tk text editor, notes are saved upon exiting the window.
    def makeNote(self, tile_name):
        root = tk.Tk()
        root.title(tile_name)
        data = tkinter.scrolledtext.ScrolledText(root, wrap = "word", undo = True)
        file_path = os.path.join(self._map_notes_save_path, tile_name)
        #print(file_path)
        if os.path.isfile(file_path):
            with open(file_path, "r") as f:
                lines = f.readlines()
                f.close()
            for line in lines:
                data.insert(tk.END, line)
        data.pack(side = tk.TOP, fill = "both", expand = "yes")

        def on_closing():
            endString = data.get("1.0", 'end-1c')#.split("\n")
            with open(file_path, "w") as f:
                f.write(endString)
                f.close()
            root.destroy()
            
        root.protocol("WM_DELETE_WINDOW", on_closing)
        data.focus_set()
        root.resizable(True, True)
        root.mainloop()            
           
    def swapToMappingPanel(self):
        self._ui_visible_panel = "MAPPING"
        self.drawUI()

    #Toggles the visible hex grid on or off
    def toggleGrid(self):
        self._settings_draw_grid ^= True
        if self._settings_IMAGE_IN_RAM_MODE:
            self.drawHexMap()

    #toggles the cell names (visible top left corner) of hexes.
    def toggleCellNames(self):
        self._settings_draw_cell_names ^= True
        if self._settings_IMAGE_IN_RAM_MODE:
            self.drawHexMap()

    #Generates new landmasses using cellular automata.
    def generateNewMap(self):
        self._map, self._map_name = self.genny.getNewWorldMap()
        self.drawHexMap()
        pygame.display.set_caption(f'{self.caption} -- {self._map_name}')        

    #Creates a new blank map of specified size.
    #Each tile on the new map will be the type of the selected palette tile.
    def newBlankMap(self):
        data = []
        self.newBlankMapDialog(data)
        #print(data)
        if len(data) > 0:
            self._map_height = data[0]
            self._map_width = data[1]
            self._map_orientation = data[2]        
            self.genny.resize(self._map_height, self._map_width, self._map_orientation)
            self._map, self._map_name = self.genny.getNewBlankMap(self._tileset_primary)
            self.makeMapSurface()
            self.drawHexMap()          
            pygame.display.set_caption(f'{self.caption} -- {self._map_name}')

    def newBlankMapDialog(self, data):
        #TODO ADD MAP SIZE WARNING
        root = tk.Tk()
        root.title("New Blank Map")
        newMapHeight = tk.StringVar(root)
        newMapWidth = tk.StringVar(root)
        newMapOrientation = tk.IntVar()
        orientations = ["H", "V"]
        labelHeight = tk.Label(root, text="Height of map in tiles: ").grid(row=1,column=0,sticky="w")
        labelWidth = tk.Label(root, text="Width of map in ties: ").grid(row=2,column=0,sticky="w")
        texHeight = tk.Entry(root, textvariable=newMapHeight).grid(row=1,column=1,sticky="w")
        texWidth = tk.Entry(root, textvariable=newMapWidth).grid(row=2,column=1,sticky="w")
        labelAlignment = tk.Label(root, text="Hexagon Alignment:").grid(row=3,sticky="w")
        radioHor = tk.Radiobutton(root, text="Horizontal", variable=newMapOrientation, value=0).grid(row=4,sticky="w")
        radioHor = tk.Radiobutton(root, text="Vertical", variable=newMapOrientation, value=1).grid(row=5,sticky="w")

        #would be nice to inclue a popup if the value entered isnt a number.
        def test():
            numHeight = newMapHeight.get()
            numWidth = newMapWidth.get()
            if (numHeight.isnumeric() and numWidth.isnumeric()):
                data.append(int(numHeight))
                data.append(int(numWidth))
                data.append(orientations[newMapOrientation.get()])
                root.destroy()
            else:
                pass

        def on_close():
            root.destroy()
            
        button_ok = tk.Button(root, text="Ok", command=test).grid(row=6,column=0,sticky="e")
        button_cancel = tk.Button(root, text="Cancel", command=on_close).grid(row=6,column=1,sticky="w")
        root.protocol("WM_DELETE_WINDOW", on_close)
        root.mainloop()        

    #Saves self._map to a file, specified by user.
    def saveMap(self):
        root = tk.Tk()
        root.withdraw()
        test = fd.asksaveasfilename(title="Save Hexmap As",initialdir=self._settings_default_save_location)
        if len(test) > 0:
            utils.save_map_to_file(self._map, self._map_orientation, test, self.current_tileset)

    #called upon quitting the main window.
    #yeah it looks ugly.
    def askToSaveMap(self):
        root = tk.Tk()
        def yes_save():
            test = fd.asksaveasfilename(title="Save Hexmap As",initialdir=self._settings_default_save_location)
            if len(test) > 0:
                utils.save_map_to_file(self._map, self._map_orientation, test, self.current_tileset)
                root.destroy()
                sys.exit()
            else:
                root.destroy()
                sys.exit() 
                return
        def no_quit():
            root.destroy()
            sys.exit() 
            return
        label_prompt_save = tk.Label(root, text="Save before quitting?").pack(side=tk.TOP)
        button_yes = tk.Button(root, text="Yes", command=yes_save).pack(side=tk.LEFT)
        button_no = tk.Button(root, text="No", command=no_quit).pack(side=tk.RIGHT)
        root.protocol("WM_DELETE_WINDOW", no_quit)
        root.mainloop()
    
    #Loads selected .hexmap file. Does not check that file has a .hexmap extension, but that shouldnt matter.
    def loadMap(self):
        root = tk.Tk()
        root.withdraw()
        test = fd.askopenfilename(title="Load Saved Hexmap",initialdir=self._settings_default_save_location)
        if len(test) > 0:
            path_to_top_level_dir = test.split(os.path.sep)
            #print(path_to_top_level_dir[-2])
            self._map_name = path_to_top_level_dir[-2]
            self._map_notes_save_path = self._settings_default_save_location +  os.path.sep + str(self._map_name) + os.path.sep
            self._map, self._map_orientation, self.current_tileset = utils.load_map_from_file(test)
            self.loadTileset(self.current_tileset)
            self.rebuild_UI()
            self._map_height = len(self._map)
            self._map_width = len(self._map[0])
            self.makeMapSurface()
            self.drawHexMap()
            pygame.display.set_caption(f'{self.caption} -- {self._map_name}')            

    #saves self.map_surface_source as a .png image.
    #in the future we can export massive maps in strips and stitch together with pyvips?
    def exportToPNG(self):
        root = tk.Tk()
        root.withdraw()
        test = fd.asksaveasfilename(title="Save Hexmap As",initialfile=self._map_name,initialdir=self._map_notes_save_path)
        if len(test) > 0:
            pygame.image.save(self.map_surface_source, os.path.join(test + ".png"))

    #Not implemented
    #this funcion will allow us to add rows/ columns to an existing hexmap.
    def growShrinkMap(self):
        data = [] #NUM_TO_ADD, TOP, LEFT, RIGHT, BOTTOM
        self.growShrinkDialog(data)
        if len(data) < 1:
            return
        else:
            numberToAdd = int(data[0])
            #print("Not yet implimented...")
            #print(data)
            #self.growMap(data)
        #yo this is actually trickier than I thought, I will leave this for later.
        #ok so I think this is acually not that bad, I will just need to
        #append/ delete the correct number of new rows, and add/remove tiles at the head or tail of the row list.
        #then I'll go into a makeWorldMap() type of function that updates each hextile to its proper grid location,
        #its coordinates, whether its offset row/col or not, and its new name.
        #we will leave the tileType as it is, and all new hextiles will get the _tileset_primary type.

    def growMap(self, specs):
        growth_amt = specs[0]
        add_to_top = specs[1]
        add_to_left = specs[2]
        add_to_right = specs[3]
        add_to_bottom = specs[4]
    
    #opens a tkinter gui to set how many and where we want the new/removed rows or cols.
    def growShrinkDialog(self, data_list):
        root = tk.Tk()
        root.title("Add/Remove Rows or Cols")
        addToTop = tk.BooleanVar()
        addToLeft = tk.BooleanVar()
        addToRight = tk.BooleanVar()
        addToBottom = tk.BooleanVar()
        amountToGrow = tk.StringVar(root)
        labelRows = tk.Label(root, text="Number of rows/cols to insert: ").grid(row=0,column=0,sticky="w")
        texRows = tk.Entry(root, textvariable=amountToGrow).grid(row=0,column=1,sticky="w")
        c1 = tk.Checkbutton(root, text="Top", variable=addToTop, onvalue=True, offvalue=False).grid(row=1,column=1,sticky="w")
        c2 = tk.Checkbutton(root, text="Left", variable=addToLeft, onvalue=True, offvalue=False).grid(row=2,column=1,sticky="w")
        c3 = tk.Checkbutton(root, text="Right", variable=addToRight, onvalue=True, offvalue=False).grid(row=3,column=1,sticky="w")
        c4 = tk.Checkbutton(root, text="Bottom", variable=addToBottom, onvalue=True, offvalue=False).grid(row=4,column=1,sticky="w")

        #would be nice to inclue a popup if the value entered isnt a number.
        def test():
            numstr = amountToGrow.get()
            numwithoutneg = ""
            if numstr[0] == "-":
                numwithoutneg = numstr[1:]
            if (amountToGrow.get().isnumeric() or numwithoutneg.isnumeric()):
                data_list.append(amountToGrow.get())
                data_list.append(addToTop.get())
                data_list.append(addToLeft.get())
                data_list.append(addToRight.get())
                data_list.append(addToBottom.get())
                root.destroy()
            else:
                pass

        def on_close():
            root.destroy()
            
        button_ok = tk.Button(root, text="Ok", command=test).grid(row=5,column=0,sticky="e")
        button_cancel = tk.Button(root, text="Cancel", command=on_close).grid(row=5,column=1,sticky="w")
        root.protocol("WM_DELETE_WINDOW", on_close)

        root.mainloop()
        
    #load all images in directory into a tileset dictionary, filename: surface.
    def loadTileset(self, directory):
        self.tiles["V"].clear()
        self.tiles["H"].clear()
        path = directory.split(os.path.sep)
        tileset_name = path[-1].split("x")
        #print(tileset_name)
        self.tile_size["H"] = (int(tileset_name[1]), int(tileset_name[2]))
        self.tile_size["V"] = (int(tileset_name[2]), int(tileset_name[1]))
        dirs = os.scandir(directory)
        for entry in dirs:
            if os.path.isfile(os.path.join(directory, entry.name)):
                self.tiles["H"][entry.name] = utils.loadImage(os.path.join(directory, entry.name))
                self.tiles["V"][entry.name] = pygame.transform.rotate(self.tiles["H"][entry.name], 90)
        self.current_tileset = directory
        #print(self.tiles)


    #We create a surface large enough to fit our hexmap, then blit our tiles from self.tiles to the surface.
    def makeMapSurface(self):
        if self._map_orientation == "H":
            self.map_surface_source = pygame.Surface((utils.HEX_TILE_WIDTH * len(self._map[0]) + (utils.HEX_TILE_WIDTH/2) + 2, len(self._map) * (3*utils.HEX_TILE_HEIGHT/4) + (utils.HEX_TILE_HEIGHT/4) + 2))
        else:
            self.map_surface_source = pygame.Surface((len(self._map[0]) * (3*utils.HEX_TILE_HEIGHT/4) + (utils.HEX_TILE_HEIGHT/4), utils.HEX_TILE_WIDTH * len(self._map) + (utils.HEX_TILE_WIDTH/2)))

        self.map_surface_source_rect = self.map_surface_source.get_rect()
        self.map_surface_source.fill(utils.BLACK)
        self.drawHexMap()
        self.setVisibleSurface(self.map_surface_source)
        
    #We create a rect large enough to fit our hexmap, and use its dimensions for drawing while _settings_IMAGE_IN_RAM_MODE == False.
    def makeMapRect(self):
        if self._map_orientation == "H":
            self.map_surface_rect = pygame.Rect((0,0), (utils.HEX_TILE_WIDTH * len(self._map[0]) + (utils.HEX_TILE_WIDTH/2) + 2, len(self._map) * (3*utils.HEX_TILE_HEIGHT/4) + (utils.HEX_TILE_HEIGHT/4) + 2))
        else:
            self.map_surface_rect = pygame.Rect((0,0), (len(self._map[0]) * (3*utils.HEX_TILE_HEIGHT/4) + (utils.HEX_TILE_HEIGHT/4), utils.HEX_TILE_WIDTH * len(self._map) + (utils.HEX_TILE_WIDTH/2)))
            
    #construct a 2d list of dimensions self._map_height by self._map_width
    def makeWorldMap(self, orientation):
        cur_col = 0
        char_max = 25
        char_lap_count = 0
        row_count = 0
        offset_row_toggle = 0
        m = []
        if orientation == "H":
            for row in range(self._map_height):
                row_count += 1
                r = []
                cur_col = 0
                char_lap_count = 0
                char_prefix = ""
                for col in range(self._map_width):
                    hname = char_prefix + utils.STRING_ASCII_UPPERCASE[cur_col] + str(row_count)
                    #hname = (utils.STRING_ASCII_UPPERCASE[cur_col] + (utils.STRING_ASCII_UPPERCASE[cur_col] * char_lap_count))+ str(row_count)
                    #print(hname)
                    h = hextile.HexTile(col, row, offset_row_toggle, hname, "grass.png", "H")
                    r.append(h)
                    cur_col += 1
                    if cur_col > char_max:
                        cur_col = 0
                        char_prefix += utils.STRING_ASCII_UPPERCASE[char_lap_count]
                        char_lap_count += 1
                
                if offset_row_toggle == 0:
                    offset_row_toggle = 1
                else:
                    offset_row_toggle = 0
                
                m.append(r)
        else:
            for row in range(self._map_height):
                row_count += 1
                r = []
                cur_col = 0
                char_lap_count = 0
                char_prefix = ""
                offset_row_toggle = 0
                for col in range(self._map_width):
                    hname = char_prefix + utils.STRING_ASCII_UPPERCASE[cur_col] + str(row_count)
                    #hname = (utils.STRING_ASCII_UPPERCASE[cur_col] + (utils.STRING_ASCII_UPPERCASE[cur_col] * char_lap_count))+ str(row_count)
                    #print(hname)
                    h = hextile.HexTile(col, row, offset_row_toggle, hname, "grass.png", "V")
                    r.append(h)
                    cur_col += 1
                    if cur_col > char_max:
                        cur_col = 0
                        char_prefix += utils.STRING_ASCII_UPPERCASE[char_lap_count]
                        char_lap_count += 1
                
                    if offset_row_toggle == 0:
                        offset_row_toggle = 1
                    else:
                        offset_row_toggle = 0
                        
                m.append(r)
        return m
        #print(self._map)      


    #this calculates how much of our map we can see based on the distance from our CAMERA to the surface and the CAMERA's field of view. 
    #we then scale what the CAMERA rect covers to fit into our SCREEN_WIDTH, SCREEN_HEIGHT window
    def setVisibleSurface(self, surf):
        surf_rect = surf.get_rect()

        old_width = self.CAMERA.width
        old_height = self.CAMERA.height
        
        vis_width = (math.tan(math.radians(30)) * self.VIEW_DISTANCE) * 2
        vis_height = vis_width * (self.SCREEN_ASPECT_RATIO[1] / self.SCREEN_ASPECT_RATIO[0])
        
        max_width = surf_rect.width
        max_height = surf_rect.height

        #ooook so this gets the world coord under our MOUSE, changes our CAMERA rect size to new width/height, then  moves our CAMERA center to the world coord that WAS under our MOUSE.
        #Next we find the new world coord under our MOUSE (since our CAMERA has moved, and is looking at new shit) and moves the CAMERA center by the difference between the old and new world coords
        if self.ZOOM_IN:
            #the map point we want under the MOUSE
            mouse_x, mouse_y = self.MOUSE_X, self.MOUSE_Y
            focus_x, focus_y = self.screenToWorld(mouse_x, mouse_y)
            #print("FOCUS POINT: " + str(focus_x) + ", " + str(focus_y))
            
            self.CAMERA.width = vis_width
            self.CAMERA.height = vis_height
            self.CAMERA.center = (focus_x, focus_y)   
            newx, newy = self.screenToWorld(mouse_x, mouse_y)
            self.CAMERA.center = (focus_x + (focus_x - newx), focus_y + (focus_y - newy))
            
            self.ZOOM_IN = False
        else:
            oldCamCenter = self.CAMERA.center
            self.CAMERA.width = vis_width
            self.CAMERA.height = vis_height
            self.CAMERA.center = oldCamCenter

        MIN_CAMERA_X = 0
        MAX_CAMERA_X = surf_rect.width
        MIN_CAMERA_Y = 0
        MAX_CAMERA_Y = surf_rect.height
        if self.CAMERA.centerx < MIN_CAMERA_X:
            self.CAMERA.centerx = MIN_CAMERA_X
        elif self.CAMERA.centerx > MAX_CAMERA_X:
            self.CAMERA.centerx = MAX_CAMERA_X
        if self.CAMERA.centery < MIN_CAMERA_Y:
            self.CAMERA.centery = MIN_CAMERA_Y
        elif self.CAMERA.centery > MAX_CAMERA_Y:
            self.CAMERA.centery = MAX_CAMERA_Y
        
        if   self.CAMERA.centerx - ( self.CAMERA.width / 2) < 0 or ( self.CAMERA.centerx + ( self.CAMERA.width / 2) ) > surf_rect.width or ( self.CAMERA.centery - ( self.CAMERA.height / 2) ) < 0 or ( self.CAMERA.centery + ( self.CAMERA.height / 2) ) > surf_rect.height:
            x_adjustment = 0
            y_adjustment = 0
            if ( self.CAMERA.centerx - ( self.CAMERA.width / 2) ) < 0:
                x_adjustment = -1 * self.CAMERA.left
            if ( self.CAMERA.centery - ( self.CAMERA.height / 2) ) < 0:
                y_adjustment = -1 * self.CAMERA.top
            
            scaling_factor = self.SCREEN_WIDTH / self.CAMERA.width
            
            newRect = self.CAMERA.clip(surf_rect)
            newSurface = pygame.transform.scale(surf.subsurface(newRect), (int(newRect.width*scaling_factor), int(newRect.height*scaling_factor)))
            self.visible_surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            self.visible_surface.fill(utils.BLACK)
            self.visible_surface.blit(newSurface, (x_adjustment*scaling_factor,y_adjustment*scaling_factor))
            self.visible_surface_rect = self.visible_surface.get_rect()

        else:
            self.visible_surface = pygame.transform.scale(surf.subsurface(self.CAMERA), (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            self.visible_surface_rect = self.visible_surface.get_rect()

    #calls drawHexMap passing it the list of tiles to update.
    #clears our list of changed tiles
    def update_changed_tiles(self):
        tiles = self._map_tiles_to_update.copy()
        self._map_tiles_to_update = []
        self.drawHexMap(False, tiles)
    
    #blits the correct tile from self.tiles tileset for each hex, also draws the hex grid if self._settings_draw_grid is True
    def drawHexMap(self, REDRAW_ALL=True, REDRAW_LIST=[]):
        offset_row_toggle = 0

        if REDRAW_ALL:
            for row in range(len(self._map)):
                #print(offset_row_toggle)
                for col in range(len(self._map[0])):
                    t = self._map[row][col]
                    img_rect = self.tiles[self._map_orientation][t.tileType].get_rect()
                    img_offset = [t.worldX - (img_rect.width/2), t.worldY - (img_rect.height/2)]
                    self.map_surface_source.blit(self.tiles[self._map_orientation][t.tileType], (img_offset[0], img_offset[1]))
                    
                    if self._settings_draw_grid:
                        points = self._map[row][col].points
                        for i in range(6):
                            j = i + 1
                            if j == len(points):
                                j = 0
                            pygame.draw.lines(self.map_surface_source, utils.GRID_LINE_COLOR, False, (points[i], points[j]), width=3)
                            if offset_row_toggle == 0:
                                offset_row_toggle = 1
                            else:
                                offset_row_toggle = 0
                                
                    if self._settings_draw_cell_names:
                        text = self._ui_button_font.render(t.cell_name, True, utils.HEX_LABEL_COLOR)     
                        self.map_surface_source.blit(text, (t.points[-2][0] + self._ui_padding_amt, t.points[-2][1] + self._ui_padding_amt))

        else:
            for t in REDRAW_LIST:
                img_rect = self.tiles[self._map_orientation][t.tileType].get_rect()
                img_offset = [t.worldX - (img_rect.width/2), t.worldY - (img_rect.height/2)]
                self.map_surface_source.blit(self.tiles[self._map_orientation][t.tileType], (img_offset[0], img_offset[1]))
                if self._settings_draw_grid:
                    points = t.points
                    for i in range(6):
                        j = i + 1
                        if j == len(points):
                            j = 0
                        pygame.draw.lines(self.map_surface_source, utils.GRID_LINE_COLOR, False, (points[i], points[j]), width=3)
                        if offset_row_toggle == 0:
                            offset_row_toggle = 1
                        else:
                            offset_row_toggle = 0
                if self._settings_draw_cell_names:
                    text = self._ui_button_font.render(t.cell_name, True, utils.HEX_LABEL_COLOR)     
                    self.map_surface_source.blit(text, (t.points[-2][0] + self._ui_padding_amt, t.points[-2][1] + self._ui_padding_amt))
        
    #tracks current window size, updates the necessary surfaces/rects when window size is changed.(
    def resizeWindow(self, new_size):
        self.SCREEN_WIDTH = new_size[0]
        self.SCREEN_HEIGHT = new_size[1]
        self.SCREEN_ASPECT_RATIO = [self.SCREEN_WIDTH, self.SCREEN_HEIGHT]
        self.BACKGROUND = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT)).convert()
        self.BACKGROUND.fill(utils.CREAM)
        self._ui_toolbar_vertical_size = self.SCREEN_HEIGHT
        self._ui_rect = pygame.Rect(0,0,self._ui_toolbar_horizontal_size, self._ui_toolbar_vertical_size)
        self._ui_surface = pygame.Surface((self._ui_rect.width, self._ui_rect.height)).convert()        
        self._ui_surface.fill(utils.GRAY_DARK)
        self.rebuild_UI()
        #TODO, update UI size here, recreate the UI panels, and redraw them.

    #returns the coordinates of a point on the map based on a position on screen.
    def screenToWorld(self, x, y):
        wr = self.CAMERA.width / self.SCREEN_WIDTH
        wh = self.CAMERA.height / self.SCREEN_HEIGHT
        cx, cy = self.CAMERA.topleft
        newx = (x * wr) + cx
        newy = (y * wh) + cy
        return (newx, newy)
    
    #takes a point on our map and tells us where it is on the screen
    def worldToScreen(self, x, y):
        cx, cy = self.CAMERA.topleft
        pcx = x - cx
        pcy = y - cy
        newx = ( pcx * self.SCREEN_WIDTH ) / self.CAMERA.width
        newy = ( pcy * self.SCREEN_HEIGHT ) / self.CAMERA.height
        return (newx, newy)
    
    #handles the CAMERA movement, smooth movement is done though copius elifs
    #Gotta be a better way but it works great for now so :shrug:
    def handleMovementInput(self, up, down, left, right, deltaT):
        dx, dy = 0, 0
        moveSpeed = 5*(self.VIEW_DISTANCE / self.MIN_VIEW_DISTANCE) #* deltaT
        tempHeading = 0
        if (up and down and left and not right):
            tempHeading = 180
        elif (up and down and not left and right):
            tempHeading = 0
        elif (up and down and not left and not right):
            return (dx, dy)
        elif (up and not down and not left and not right):
            tempHeading = 90
        elif (up and not down and left and not right):
            tempHeading = 135
        elif (up and not down and not left and right):
            tempHeading = 45
        elif (not up and down and not left and not right):
            tempHeading = 270
        elif (not up and down and left and right):
            tempHeading = 270
        elif (not up and down and left and not right):
            tempHeading = 225
        elif (not up and down and not left and right):
            tempHeading = 315
        elif (not up and not down and left and right):
            return (dx, dy)
        elif (up and not down and left and right):
            tempHeading = 90
        elif (not up and not down and left and not right):
            tempHeading = 180
        elif (not up and not down and not left and right):
            tempHeading = 0          
        else:
            if (up and down and left and right):
                moveSpeed = 0
            elif (not up and not down and not left and not right):
                moveSpeed = 0
        dx = math.cos(math.radians(tempHeading))*(moveSpeed)
        dy = math.sin(math.radians(tempHeading))*(moveSpeed)*-1
        self.moveCamera(dx,dy)
        
    #handles the mouse input, mouse buttons held down, etc.
    def handleMouseInput(self, left):
        if left:
            if self._ui_rect.collidepoint(self.MOUSE_X, self.MOUSE_Y):
                for b in self._ui_panels[self._ui_visible_panel]:
                    if b.rect.collidepoint(self.MOUSE_X, self.MOUSE_Y):
                        #print(b.action)
                        b.clicked(True)
                    else:
                        b.clicked(False)
            else:
                x, y = 0, 0
                tx, ty = 0, 0
                if self._map_orientation == "H":
                    x, y = self.screenToWorld(self.MOUSE_X, self.MOUSE_Y)
                    tx, ty = utils.coordToTileHorizontal(x, y)
                else:
                    x, y = self.screenToWorld(self.MOUSE_X, self.MOUSE_Y)
                    tx, ty = utils.coordToTileVertical(x, y)
                if (tx < 0 or tx > len(self._map[0]) - 1) or (ty < 0 or ty > len(self._map) - 1):
                    pass
                else:
                    if self._ui_visible_panel == "MAPPING":
                        if self.current_tool == "PENCIL":
                            self.pencilDraw(tx, ty, self._tileset_primary)
                    else:
                        pass    

    #handles mouse button RELEASES specifically. clicking buttons, filling tiles, etc.
    def handleMouseRelease(self, left):
        if left:
            if self._ui_rect.collidepoint(self.MOUSE_X, self.MOUSE_Y):
                #print("Clicking on UI!!!!!")
                for b in self._ui_panels[self._ui_visible_panel]:
                    if b.rect.collidepoint(self.MOUSE_X, self.MOUSE_Y):
                        #print(b.action)
                        self._ui_action_dict[b.action]()
                        b.clicked(False) 
            else:
                x, y = 0, 0
                tx, ty = 0, 0
                if self._map_orientation == "H":
                    x, y = self.screenToWorld(self.MOUSE_X, self.MOUSE_Y)
                    tx, ty = utils.coordToTileHorizontal(x, y)
                else:
                    x, y = self.screenToWorld(self.MOUSE_X, self.MOUSE_Y)
                    tx, ty = utils.coordToTileVertical(x, y)
                if (tx < 0 or tx > len(self._map[0]) - 1) or (ty < 0 or ty > len(self._map) - 1):
                    pass
                else:
                    if self._ui_visible_panel == "MAPPING":
                        if self.current_tool == "BUCKET":
                            self.bucketFillSimilarTiles(tx, ty, self._tileset_primary)
                        elif self.current_tool == "PENCIL":
                            self.pencilDraw(tx, ty, self._tileset_primary)
                    else:
                        self.spawnEditor(self._map[ty][tx].cell_name)
        
    #moves the CAMERA rect by dx,dy
    def moveCamera(self, dx, dy):
        self.CAMERA.centerx += dx
        self.CAMERA.centery += dy

    #sets tile to the selected tile type
    #radius exists so in the future we can change the pencil size to edit multiple tiles at once.
    def pencilDraw(self, tx, ty, color, radius=1):
        if self._map[ty][tx].tileType != color:
            self._map[ty][tx].tileType = color
            self._map_tiles_to_update.append(self._map[ty][tx])
    
    #flood fills tiles until neighbors are not similar
    def bucketFillSimilarTiles(self, tx, ty, color):
        matches = self.getIdenticalNeighbors(tx, ty)
        for m in matches:
            #TODO make sure this fills all connected like tiles of clicked type, not of _tileset_primary type.
            m.tileType = color
            self._map_tiles_to_update.append(m)

    #returns a list of all tiles of the same type that are connected to tile tx, ty
    def getIdenticalNeighbors(self, tx, ty):
        matches = []
        
        curTile = self._map[ty][tx]
        frontier = []
        closed = []
        
        frontier.append(curTile)
        
        while len(frontier) > 0:
            curTile = frontier.pop(0)
            neighborList = []
            if self._map_orientation == "H":
                neighborList = utils.HEX_NEIGHBORS_HORIZONTAL
            else:
                neighborList = utils.HEX_NEIGHBORS_VERTICAL
            
            for n in neighborList[curTile.IS_OFFSET_ROW]:
                #print("looping")
                if curTile.xTile + n[0] < 0 or curTile.xTile + n[0] > len(self._map[0]) - 1:
                    continue
                if curTile.yTile + n[1] < 0 or curTile.yTile + n[1] > len(self._map) - 1:
                    continue
                neigh = self._map[curTile.yTile + n[1]][curTile.xTile + n[0]]
                if neigh not in closed and neigh not in frontier:
                    #print(curTile.tileType + " : " + neigh.tileType)
                    if curTile.tileType == neigh.tileType:
                        frontier.append(neigh)
                    else:
                        closed.append(neigh)
            matches.append(curTile)
            closed.append(curTile)
        return matches
    
    #from our CAMERA coorinates get the tiles that the corners of the CAMERA are on.
    #returns a tuple of the top left and bottom right visible tiles (+1 on each side so we dont see any popping of tiles)
    def getVisibleTileIndices(self):
        topTile = 0
        rightTile = 0
        leftTile = 0
        bottomTile = 0
        if self._map_orientation == "H":
            tx,ty = utils.coordToTileHorizontal(self.CAMERA.left, self.CAMERA.top)
            topTile = ty
            leftTile = tx
            tx, ty = utils.coordToTileHorizontal(self.CAMERA.right, self.CAMERA.bottom)
            rightTile = tx
            bottomTile = ty
        else:
            tx,ty = utils.coordToTileVertical(self.CAMERA.left, self.CAMERA.top)
            topTile = ty
            leftTile = tx
            tx, ty = utils.coordToTileVertical(self.CAMERA.right, self.CAMERA.bottom)
            rightTile = tx
            bottomTile = ty            
        return ((leftTile-1, topTile-1), (rightTile+1, bottomTile+1))
    
    #keybindings and shit
    def checkEvents(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT: 
                self.onQuit()
                
            if e.type == VIDEORESIZE:
                #print("resized")
                new_size = e.dict["size"]
                #print(new_size)
                self.resizeWindow(new_size)

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_w:
                    self.KEY_STATES["CAM_UP"] ^= True
                if e.key == pygame.K_s:
                    if e.mod & pygame.KMOD_LCTRL:
                        #print("Saving")
                        self.saveMap()
                        if e.mod & pygame.KMOD_LSHIFT:
                            self.exportToPNG()
                            #print("Saved Image to world folder")
                    self.KEY_STATES["CAM_DOWN"] ^= True
                if e.key == pygame.K_a:
                    self.KEY_STATES["CAM_LEFT"] ^= True
                if e.key == pygame.K_d:
                    self.KEY_STATES["CAM_RIGHT"] ^= True
                if e.key == pygame.K_l:
                    if e.mod & pygame.KMOD_LCTRL:
                        #print("Loading")
                        self.loadMap()
                if e.key == pygame.K_ESCAPE:
                    self.onQuit()
                        
            if e.type == pygame.KEYUP:
                if e.key == pygame.K_w:
                    self.KEY_STATES["CAM_UP"] ^= True
                if e.key == pygame.K_s:
                    self.KEY_STATES["CAM_DOWN"] ^= True
                if e.key == pygame.K_a:
                    self.KEY_STATES["CAM_LEFT"] ^= True
                if e.key == pygame.K_d:
                    self.KEY_STATES["CAM_RIGHT"] ^= True
                
            if e.type == pygame.MOUSEBUTTONDOWN:
                #print("Mouse DOWN: " + str(e.button))
                if e.button == 1: #left mouse
                    self.MOUSE_STATES["LEFT"] ^= True
                    self.MOUSE_CLICK_X, self.MOUSE_CLICK_Y = self.screenToWorld(self.MOUSE_X, self.MOUSE_Y)
                if e.button == 3: #right mouse
                    self.MOUSE_STATES["RIGHT"] ^= True
                        
                if self.ZOOM_ENABLED:
                    if e.button == 4: #scroll up
                        self.LAST_VIEW_DISTANCE = self.VIEW_DISTANCE
                        self.VIEW_DISTANCE -= 50
                        if self.VIEW_DISTANCE < self.MIN_VIEW_DISTANCE:
                            self.VIEW_DISTANCE = self.MIN_VIEW_DISTANCE
                        else:
                            self.ZOOM_IN = True
                    if e.button == 5:
                        self.LAST_VIEW_DISTANCE = self.VIEW_DISTANCE
                        self.VIEW_DISTANCE += 50
                        if self.VIEW_DISTANCE > self.MAX_VIEW_DISTANCE:
                            self.VIEW_DISTANCE = self.MAX_VIEW_DISTANCE
                        else: 
                            self.ZOOM_IN = True
                   
            if e.type == pygame.MOUSEBUTTONUP:
                #print("Mouse UP: " + str(e.button))
                if e.button == 1: #left mouse
                    self.MOUSE_STATES["LEFT"] ^= True
                    self.handleMouseRelease(True)
                if e.button == 3: #right
                    self.MOUSE_STATES["RIGHT"] ^= True

    #should be obvious.
    def onQuit(self):
        self.askToSaveMap()
#        print(len(self.NOTES_THREADS))
        sys.exit()               

    #this is our main function
    #updates changed tiles, draws visible surfaces, checks for input, handles input, repeats.
    def run(self): 
        DEBUG = False
        while True:
            deltaT = self.CLOCK.get_time()/utils.FPS

            self.update_changed_tiles()
            
            self.drawUI()
            self.SCREEN.blit(self.BACKGROUND, (0,0))
            self.setVisibleSurface(self.map_surface_source)
            self.SCREEN.blit(self.visible_surface, (0,0))
            self.SCREEN.blit(self._ui_surface, (0,0))
            pygame.display.flip()
            
            self.LAST_MOUSE_X = self.MOUSE_X
            self.LAST_MOUSE_Y = self.MOUSE_Y
            self.MOUSE_X, self.MOUSE_Y = pygame.mouse.get_pos()
            
            self.checkEvents()
            
            self.handleMovementInput(self.KEY_STATES["CAM_UP"], self.KEY_STATES["CAM_DOWN"], self.KEY_STATES["CAM_LEFT"], self.KEY_STATES["CAM_RIGHT"], deltaT)
            
            self.handleMouseInput(self.MOUSE_STATES["LEFT"])
            
            self.CLOCK.tick(utils.FPS)

        
if __name__ == "__main__":
    hexmappy = Main()
    hexmappy.run()
