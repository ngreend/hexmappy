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

import pygame
import utils

class Button:
    def __init__(self, x, y, surface, surface_clicked, action):
        self.surface = surface
        self.surface_clicked = surface_clicked
        self.drawSurface = self.surface
        self.drawClicked = False
        self.rect = surface.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.action = action
        self.finalizeSurfaces()

    def clicked(self, isClicked):
        self.drawClicked = isClicked

    def updateSurf(self, newSurf, newSurfClicked):
        self.surface = newSurf
        self.surface_clicked = newSurfClicked
        oldx = self.rect.left
        oldy = self.rect.top
        self.rect = self.surface.get_rect()
        self.rect.left = oldx
        self.rect.top = oldy
        self.finalizeSurfaces()

    #this adds the light/dark gray lines on the border of our button surfaces
    def finalizeSurfaces(self):
        pygame.draw.line(self.surface, utils.GRAY_DARKEST, (0,0), (0,self.rect.height), 2)
        pygame.draw.line(self.surface, utils.GRAY_DARKEST, (0,self.rect.height-2), (self.rect.width-2, self.rect.height-2), 2)
        pygame.draw.line(self.surface, utils.GRAY_LIGHTEST, (0,0), (self.rect.width,0), 2)
        pygame.draw.line(self.surface, utils.GRAY_LIGHTEST, (self.rect.width-2,0), (self.rect.width-2, self.rect.height-2), 2)
        pygame.draw.line(self.surface_clicked, utils.GRAY_LIGHTEST, (0,0), (0,self.rect.height), 2)
        pygame.draw.line(self.surface_clicked, utils.GRAY_LIGHTEST, (0,self.rect.height-2), (self.rect.width-2, self.rect.height-2), 2)
        pygame.draw.line(self.surface_clicked, utils.GRAY_DARKEST, (0,0), (self.rect.width,0), 2)
        pygame.draw.line(self.surface_clicked, utils.GRAY_DARKEST, (self.rect.width-2,0), (self.rect.width-2, self.rect.height-2), 2)
