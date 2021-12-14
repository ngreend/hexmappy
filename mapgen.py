"""
    This file is a part of Hexmappy.

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
    along with Hexmappy. It can be found in the root directory of this program
    under the name 'COPYING'.  If not, see <https://www.gnu.org/licenses/>.
"""

import random

import utils
import hextile

class MapGen():
    
    def __init__(self, width, height, orientation):
        self.width = width
        self.height = height
        self.orientation = orientation


    def resize(self, height, width, orientation):
        self.height = height
        self.width = width
        self.orientation = orientation
        
    def getNewBlankMap(self, tile):
        cur_col = 0
        char_max = 25
        char_lap_count = 0
        row_count = 0
        col_count = 0
        offset_row_toggle = 0
        m = []
        if self.orientation == "H":
            for row in range(self.height):
                row_count += 1
                r = []
                col_count = 0
                for col in range(self.width):
                    col_count += 1
                    hname = str(col_count) + "-" + str(row_count)
                    h = hextile.HexTile(col, row, offset_row_toggle, hname, tile, "H")
                    r.append(h)
                
                if offset_row_toggle == 0:
                    offset_row_toggle = 1
                else:
                    offset_row_toggle = 0
                
                m.append(r)
        else:
            row_count = 0
            col_count = 0
            for row in range(self.height):
                row_count += 1
                r = []
                col_count = 0
                offset_row_toggle = 0
                for col in range(self.width):
                    col_count += 1
                    hname = str(col_count) + "-" + str(row_count)
                    h = hextile.HexTile(col, row, offset_row_toggle, hname, tile, "V")
                    r.append(h)
                
                    if offset_row_toggle == 0:
                        offset_row_toggle = 1
                    else:
                        offset_row_toggle = 0
                
                m.append(r)
        return (m, utils.get_uniqueID())
        
    def getNewWorldMap(self):
        cur_col = 0
        char_max = 25
        char_lap_count = 0
        row_count = 0
        col_count = 0
        offset_row_toggle = 0
        m = []
        if self.orientation == "H":
            for row in range(self.height):
                row_count += 1
                r = []
                col_count = 0
                for col in range(self.width):
                    col_count += 1
                    hname = str(col_count) + "-" + str(row_count)

                    val = random.randint(0,1)
                    tile_name_noise = "void.png"
                    if val < 1:
                        tile_name_noise = "water.png"
                    else:
                        tile_name_noise = "grass.png"
                    
                    h = hextile.HexTile(col, row, offset_row_toggle, hname, tile_name_noise, "H")
                    r.append(h)
                
                if offset_row_toggle == 0:
                    offset_row_toggle = 1
                else:
                    offset_row_toggle = 0
                
                m.append(r)
        else:
            row_count = 0
            col_count = 0
            for row in range(self.height):
                row_count += 1
                r = []
                col_count = 0
                offset_row_toggle = 0
                for col in range(self.width):
                    col_count += 1
                    hname = str(col_count) + "-" + str(row_count)

                    val = random.randint(0, 1)
                    tile_name_noise = "void.png"
                    if val < 1:
                        tile_name_noise = "water.png"
                    else:
                        tile_name_noise = "grass.png"
                    
                    h = hextile.HexTile(col, row, offset_row_toggle, hname, tile_name_noise, "V")
                    r.append(h)
                
                    if offset_row_toggle == 0:
                        offset_row_toggle = 1
                    else:
                        offset_row_toggle = 0
                
                m.append(r)
                
        return (self.automatize(m), utils.get_uniqueID())

    #performs cellular automata on our hexmap
    def automatize(self, m, laps=4):
        if self.orientation == "H":
            for i in range(laps):
                copy_of_m = m.copy()
                for row in range(len(m)):
                    for col in range(len(m[0])):
                        matches = 0
                        curTile = m[row][col]
                        for n in utils.HEX_NEIGHBORS_HORIZONTAL[curTile.IS_OFFSET_ROW]:
                            #print("looping")
                            if curTile.xTile + n[0] < 0 or curTile.xTile + n[0] > len(m[0]) - 1:
                                continue
                            if curTile.yTile + n[1] < 0 or curTile.yTile + n[1] > len(m) - 1:
                                continue
                            if m[row + n[1]][col + n[0]].tileType == "grass.png":
                                matches += 1
                        if m[row][col].tileType == "grass.png":
                            if matches < 3: #2 change in conjunction with line ~605 for thinner landmasses
                                copy_of_m[row][col].tileType = "water.png"
                        #for smaller islands, change this to a 4
                        elif matches > 3: #4 change in conjunction with line ~605 for thinner landmasses
                            copy_of_m[row][col].tileType = "grass.png"
                m = copy_of_m.copy()
            return m
        else:
            for i in range(laps):
                copy_of_m = m.copy()
                for row in range(len(m)):
                    for col in range(len(m[0])):
                        matches = 0
                        curTile = m[row][col]
                        for n in utils.HEX_NEIGHBORS_VERTICAL[curTile.IS_OFFSET_ROW]:
                            #print("looping")
                            if curTile.xTile + n[0] < 0 or curTile.xTile + n[0] > len(m[0]) - 1:
                                continue
                            if curTile.yTile + n[1] < 0 or curTile.yTile + n[1] > len(m) - 1:
                                continue
                            if m[row + n[1]][col + n[0]].tileType == "grass.png":
                                matches += 1
                        if m[row][col].tileType == "grass.png":
                            if matches < 3: #2 change in conjunction with line ~605 for thinner landmasses
                                copy_of_m[row][col].tileType = "water.png"
                        #for smaller islands, change this to a 4
                        elif matches > 3: #4 change in conjunction with line ~605 for thinner landmasses
                            copy_of_m[row][col].tileType = "grass.png"
                m = copy_of_m.copy()
            return m         
        
