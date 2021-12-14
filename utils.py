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

import os
import math
import random
from operator import floordiv

import pygame
import hextile

#COLORS
GRAY_LIGHT = (100,100,100)
GRAY_LIGHTEST = (150,150,150)
GRAY_DARK = (80,80,80)
GRAY_DARKEST = (30,30,30)
BLACK = (0,0,0)
WHITE = (255,255,255)
CREAM = (115, 115, 90)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
MISSING_TEXTURE_PURPLE = (255,0,255)

GRID_LINE_COLOR = (0,0,0)
HEX_LABEL_COLOR = (0,0,0)

#MISC
FPS = 144

STRING_ASCII_UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


#Hex area

HEX_NEIGHBORS_HORIZONTAL = {    True: [[0,-1], [1,-1],
                                [-1,0],          [1,0],
                                    [0,1],  [1,1]],
                            False:  [[-1,-1], [0,-1],
                                [-1,0],          [1,0],
                                    [-1,1],  [0,1]]
                        }

HEX_NEIGHBORS_VERTICAL = { True: [[0,-1],
                                  [-1,0],     [1,0],
                                  [-1,1],     [1,1],
                                  [0,1]],
                           False: [[0,-1],
                                  [-1,-1],     [1,-1],
                                  [-1,0],     [1,0],
                                  [0,1]]
                           }
#THE SIZES ARE IN TERMS OF HORIZONTALLY STACKING HEXAGONS.
HEX_TILE_SIZE = 200
HEX_TILE_HEIGHT = 200
HEX_TILE_WIDTH = 175
HEX_TILE_PADDING = 200

SLOPE_OF_HEX_DIAGONALS = 50/86 #0.57735
SLOPE_OF_HEX_DIAGONALS_VERTICAL = 86/50

def hex_corners_horizontal(worldCenterX, worldCenterY):
    pts = []
    for i in range(6):
        angle_deg = 60 * i - 30
        angle_rad = math.radians(angle_deg)
        #angle_rad = math.pi  / 180 * angle_deg
        pts.append([worldCenterX + (HEX_TILE_SIZE/2) * math.cos(angle_rad), worldCenterY + (HEX_TILE_SIZE/2) * math.sin(angle_rad)])
    #print(pts)
    return pts

def hex_corners_vertical(worldCenterX, worldCenterY):
    pts = []
    for i in range(6):
        angle_deg = 60 * i
        angle_rad = math.radians(angle_deg)
        pts.append([worldCenterX + (HEX_TILE_SIZE/2) * math.cos(angle_rad), worldCenterY + (HEX_TILE_SIZE/2) * math.sin(angle_rad)])
    return pts

#yeah I got lazy
def hex_corners_vertical_scaled(worldCenterX, worldCenterY, width, height):
    pts = []
    for i in range(6):
        angle_deg = 60 * i
        angle_rad = math.radians(angle_deg)
        pts.append([worldCenterX + (height/2) * math.cos(angle_rad), worldCenterY + (height/2) * math.sin(angle_rad)])
    return pts

def coordToTileHorizontal(x,y):
    rw = (HEX_TILE_WIDTH / 2)
    rh = (3*HEX_TILE_HEIGHT / 4)
    
    gx = floordiv(x, rw)
    gy = floordiv(y + (HEX_TILE_HEIGHT/4), rh)
    
    xt = 0
    yt = 0
    
    if gy == 0:
        xt = math.ceil((gx-1)/2)
        return (int(xt), 0)
    if gx == 0:
        if gy % 2 != 0:
            return (0, int(gy-1))
        else:
            return (0, int(gy))
    #if we are in an odd column, only the yTile could change.
    if gx % 2 != 0:
        xt = math.ceil((gx-1)/2)
        
        newcoordsxStart = gx*rw 
        newcoordsxEnd = (gx+1)*rw
        newcoordsWidth = newcoordsxEnd - newcoordsxStart
        #our x coord scaled to the new coord system width
        newPOSx = newcoordsxEnd - x
        #this is the x Value we multiply by SLOPE_OF_HEX_DIAGONALS
        newPOSx = newPOSx - (newcoordsWidth / 2)
        newPOSx *= -1
        newcoordsyStart = gy*rh
        newcoordsyEnd = (gy+1)*rh
        newcoordsHeight = newcoordsyEnd - newcoordsyStart
        #our x coord scaled to the new coord system width
        newPOSy = newcoordsyEnd - y
        #this is the x Value we multiply by SLOPE_OF_HEX_DIAGONALS
        newPOSy = (newPOSy - (HEX_TILE_HEIGHT/4)) - (newcoordsHeight / 2)

        if (gy % 2 != 0):
            point_line = SLOPE_OF_HEX_DIAGONALS * newPOSx
            if  newPOSy >= point_line:
                return (int(xt), int(gy - 1))
            elif newPOSy < point_line:
                return (int(xt), int(gy))
        else:
            point_line = SLOPE_OF_HEX_DIAGONALS * -1 * newPOSx
            if newPOSy >= point_line:
                return (int(xt), int(gy -1))
            if newPOSy < point_line:
                return (int(xt), int(gy))
            
    else:
        newcoordsxStart = gx*rw 
        newcoordsxEnd = (gx+1)*rw
        newcoordsWidth = newcoordsxEnd - newcoordsxStart
        #our x coord scaled to the new coord system width
        newPOSx = newcoordsxEnd - x
        #this is the x Value we multiply by SLOPE_OF_HEX_DIAGONALS
        newPOSx = newPOSx - (newcoordsWidth / 2)
        newPOSx *= -1
        newcoordsyStart = gy*rh
        newcoordsyEnd = (gy+1)*rh
        newcoordsHeight = newcoordsyEnd - newcoordsyStart
        #our x coord scaled to the new coord system width
        newPOSy = newcoordsyEnd - y
        #this is the x Value we multiply by SLOPE_OF_HEX_DIAGONALS
        newPOSy = (newPOSy - (HEX_TILE_HEIGHT/4)) - (newcoordsHeight / 2)
        
        if (gy % 2 != 0):
            point_line = SLOPE_OF_HEX_DIAGONALS * -1 * newPOSx
            if  newPOSy >= point_line:
                xt = math.ceil((gx-1)/2)
                return (int(xt), int(gy - 1))
            elif newPOSy < point_line:
                xt = math.ceil((gx-2)/2)
                return (int(xt), int(gy))
        else:
            point_line = SLOPE_OF_HEX_DIAGONALS * newPOSx
            if newPOSy >= point_line:
                xt = math.ceil((gx-2)/2)
                return (int(xt), int(gy -1))
            if newPOSy < point_line:
                xt = math.ceil((gx-1)/2)
                return (int(xt), int(gy))
    return (int(gx),int(gy))


def coordToTileVertical(x,y):
    sw = (3*HEX_TILE_HEIGHT/4)
    sh = (HEX_TILE_WIDTH/2)

    gx = floordiv(x, sw)
    gy = floordiv(y, sh)
    #print(str(gx) + ", " + (str(gy)))

    xt = 0
    yt = 0

    if gx == 0:
        yt = int(floordiv(gy,2))
        return (xt, yt)
    
    #for odd rows
    if gy % 2 != 0:
        yt = int(floordiv(gy-1, 2))

        originx = ((3*HEX_TILE_HEIGHT/4) * gx) + (HEX_TILE_HEIGHT/8)
        originy = ((HEX_TILE_WIDTH/2) * gy) + (HEX_TILE_WIDTH/4)
        relativex_to_origin = x - originx
        relativey_to_origin = y - originy
        #print(str(relativex_to_origin) + ", " + str(relativey_to_origin))

        #negative slope for even columns
        if gx % 2 == 0:
            y_on_line = SLOPE_OF_HEX_DIAGONALS_VERTICAL * -1 * relativex_to_origin
            if y_on_line >= (-1 * relativey_to_origin):
                xt = int(gx - 1)
                return (xt, yt)
            else:
                xt = int(gx)
                return (xt, yt)
        #positive slope for odd columns
        else:
            y_on_line = SLOPE_OF_HEX_DIAGONALS_VERTICAL * relativex_to_origin
            #we invert the y value because for the math Y axis is up, for graphics Y axis is down.
            if y_on_line >= (-1 * relativey_to_origin):
                xt = int(gx)
                return (xt, yt)
            else:
                xt = int(gx - 1)
                return (xt, yt)
            
    #for even rows
    else:
        originx = ((3*HEX_TILE_HEIGHT/4) * gx) + (HEX_TILE_HEIGHT/8)
        originy = ((HEX_TILE_WIDTH/2) * gy) + (HEX_TILE_WIDTH/4)
        relativex_to_origin = x - originx
        relativey_to_origin = y - originy        
        #for even columns, slope is positive
        if gx % 2 == 0:
            y_on_line = SLOPE_OF_HEX_DIAGONALS_VERTICAL * relativex_to_origin
            if y_on_line >= (-1 * relativey_to_origin):
                xt = int(gx)
                yt = int(math.ceil((gy - 1) / 2))
                return (xt, yt)
            else:
                xt = int(gx - 1)
                yt = int(floordiv(gy - 1, 2))
                return (xt, yt)
        #for odd columns slope is negative
        else:
            y_on_line = SLOPE_OF_HEX_DIAGONALS_VERTICAL * -1 *  relativex_to_origin
            if y_on_line >= (-1 * relativey_to_origin):
                xt = int(gx - 1)
                yt = int(math.ceil((gy - 1)/2))
                return (xt, yt)
            else:
                xt = int(gx)
                yt = int(floordiv(gy - 1,2))
                return (xt, yt)
    #IF WE ARE IN AN ODD ROW, the TILE ROW STAYS THE SAME

    #returns the center point of a hex tile based on the tile x,y and whether the row it is in is an offset row or not

    #returns the coords of the center of the tile passed

def tileToCoordHorizontal(tx, ty, is_offset_row):
    x_val = 0
    if is_offset_row:
        x_val =  (HEX_TILE_WIDTH/2) + (tx * (HEX_TILE_WIDTH)) + (HEX_TILE_WIDTH/2)
    else:
        x_val =  (HEX_TILE_WIDTH/2) + (tx * (HEX_TILE_WIDTH))
    y_val = (HEX_TILE_PADDING/2) + (ty * (3*HEX_TILE_HEIGHT / 4))
    
    return (x_val, y_val)

def tileToCoordVertical(tx, ty, is_offset_row):
    x_val = (HEX_TILE_HEIGHT/2) + (tx * (3*HEX_TILE_HEIGHT / 4))
    y_val = 0
    if is_offset_row:
        y_val = (HEX_TILE_WIDTH) + (ty * (HEX_TILE_WIDTH))
    else:
        y_val = (HEX_TILE_WIDTH/2) + (ty * (HEX_TILE_WIDTH))

    return (x_val, y_val)
        
def get_uniqueID():
    return random.getrandbits(32)

def loadImage(image, COLORKEY=True):
    try:
        tmp = pygame.image.load(image)
        tmp = tmp.convert()
        if COLORKEY:
            colorkey = tmp.get_at((0,0))
            tmp.set_colorkey(colorkey, pygame.RLEACCEL)
        return tmp
    except pygame.error as message:
        print('Cannot load image:', path)
        raise SystemExit(message)

def get_neighbors(self, tx, ty, radius):
    matches = []
    
    curTile = self._map[int(ty)][int(tx)]
    
    matches.append(curTile)
        
    for i in range(radius):
        for n in utils.HEX_NEIGHBORS[curTile.IS_OFFSET_ROW]:
            #print("looping")
            if curTile.xTile + n[0] * (i+1) < 0 or curTile.xTile + n[0]  * (i+1) > len(self._map[0]) - 1:
                continue
            if curTile.yTile + n[1]  * (i+1) < 0 or curTile.yTile + n[1]  * (i+1) > len(self._map) - 1:
                continue
            neigh = self._map[curTile.yTile + (n[1] * (i+1))][curTile.xTile + (n[0] * (i+1))]
            matches.append(neigh)

        matches.append(curTile)
        
    return matches

def save_map_to_file(hexmap, mapOrientation, directory, tileset):
    path_to_file = directory
    if ".hexmap" not in directory:
        path_to_file = os.path.join(directory + ".hexmap")
    #print(path_to_file)
    with open(path_to_file, "w") as savefile:
        savefile.write(f'{len(hexmap)},{len(hexmap[0])},{mapOrientation},{tileset}\n')
        for row in range(len(hexmap)):
            for col in range(len(hexmap[0])):
                t = hexmap[row][col]
                savefile.write(f'{t.xTile},{t.yTile},{t.IS_OFFSET_ROW},{t.cell_name},{t.tileType}\n')

def load_map_from_file(filename):
    hexmap = []
    with open(filename) as loadfile:
        line = loadfile.readline().strip()
        data = line.split(",")
        orientation = data[2]
        tileset = data[3]
        for row in range(int(data[0])):
            r = []
            for col in range(int(data[1])):
                hexdata = loadfile.readline().strip().split(",")
                r.append(hextile.HexTile(int(hexdata[0]), int(hexdata[1]), str_to_bool(hexdata[2]), hexdata[3], hexdata[4], orientation))
            hexmap.append(r)
    return (hexmap, orientation, tileset)
                                     
def str_to_bool(string):
    if string == "True":
        return True
    elif string == "False":
        return False
    else:
        return False
    
def point_collide_circle(x1, y1, r, x2, y2):
    if ( pow((x1-x2),2) + pow((y1-y2), 2) <= pow(r,2)):
        return True
    else:
        return False
