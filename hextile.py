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
    along with Hexmappy.  If not, see <https://www.gnu.org/licenses/>.
"""

import utils
class HexTile():
    def __init__(self, xTile, yTile, offset_row_toggle, cell_name, tileType, orientation):
        self.cell_name = cell_name
        self.xTile = xTile
        self.yTile = yTile
        self.IS_OFFSET_ROW = bool(offset_row_toggle)
        worldX, worldY = 0, 0
        if orientation == "H":
            worldX, worldY = utils.tileToCoordHorizontal(self.xTile, self.yTile, self.IS_OFFSET_ROW)
        else:
            worldX, worldY = utils.tileToCoordVertical(self.xTile, self.yTile, self.IS_OFFSET_ROW)
        self.worldX = worldX
        self.worldY = worldY
        self.points = []
        if orientation == "H":
            self.points = utils.hex_corners_horizontal(self.worldX, self.worldY)
        else:
            self.points = utils.hex_corners_vertical(self.worldX, self.worldY)
        self.tileType = tileType

    def __repr__(self):
        #print(f'{self.xTile}, {self.yTile}, {self.IS_OFFSET_ROW}, {self.cell_name}, {self.tileType}, {self.symbol}')
        return f'{self.cell_name}, {self.tileType}'
