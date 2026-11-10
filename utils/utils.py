import os
import sys
from .matrix import set_blocks, calculate_board
from .connection import rects_to_blocksDict
from . import themeManager
import pygame as pg


COLOR_1X1 = (245, 214, 59)
COLOR_1X2 = (66, 135, 245)
COLOR_2X2 = (252, 86, 43)
COLOR_1X1_HINT = (255, 234, 128)
COLOR_1X2_HINT = (122, 174, 255)
COLOR_2X2_HINT = (252, 124, 91)


class HintObject:
    def __init__(self, rect: pg.Rect | None, screenMultiplier: int):
        if rect is None:
            self._active = False
            return
        self._active = True
        self.rect = pg.Rect(rect)
        self.screenMultiplier = screenMultiplier
        self.startingPos = (rect.topleft)
        self.pos = (rect.topleft)
        self.width = rect.width
        self.height = rect.height
        self.color = set_color(rect, screenMultiplier, True)
        self.counter = 0
    
    def move(self, direction: str):
        if not getattr(self, '_active', False):
            print("Object is None")
            return
        if direction == "up":
            self.pos = (self.pos[0], self.pos[1] - 2)
        elif direction == "down":
            self.pos = (self.pos[0], self.pos[1] + 2)
        elif direction == "left":
            self.pos = (self.pos[0] - 2, self.pos[1])
        elif direction == "right":
            self.pos = (self.pos[0] + 2, self.pos[1])
        if self.counter > self.screenMultiplier:
            self.pos = self.startingPos
            self.counter = 0
        else:
            self.counter += 2
    
    def copy(self):
        return HintObject(self.rect.copy(), self.screenMultiplier)


class Label:
    def __init__(self, text: str, pos: tuple[int, int], fontSize: int = 40, color = (255, 255, 255)):
        self.text = text
        self.color = color
        self.font = pg.font.SysFont(None, fontSize)
        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect(center=pos)
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Button:
    def __init__(self, text: str, pos: tuple[int, int], role: str, buttonSize: tuple[int, int], fontSize: int = 40):
        self.text = text
        self.pos = pos
        self.role = role
        self.buttonSize = buttonSize
        self.font = pg.font.SysFont(None, fontSize)
        self.setup()

    def setup(self):
        self.buttonRect = pg.Rect((0, 0), self.buttonSize)
        self.buttonRect.center = self.pos

    def draw(self, screen: pg.Surface):
        theme = themeManager.activeTheme
        if self.role == "menu":
            buttonColor = theme.menu_button
            textColor = theme.menu_text
        elif self.role == "pause":
            buttonColor = theme.pause_button
            textColor = theme.pause_text
        else:
            buttonColor = theme.neutral_white
            textColor = theme.neutral_black
        
        textSurface = self.font.render(self.text, True, textColor, buttonColor)
        textRect = textSurface.get_rect(center=self.buttonRect.center)
        pg.draw.rect(screen, buttonColor, self.buttonRect)
        screen.blit(textSurface, textRect)
    
    def is_clicked(self, event: pg.event.Event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.buttonRect.collidepoint(event.pos):
                return True
        return False


class MenuUI:
    def __init__(self, screen: pg.Surface, size: tuple[int, int], role: str, buttons: dict[str, Button] = {}):
        self.screen = screen
        self.menuSurface = pg.Surface(size)
        self.menuSurfaceRect = self.menuSurface.get_rect(center=screen.get_rect().center)
        self.role = role
        self.buttons = buttons

    def get_button(self, button):
        return self.buttons[button]

    def draw(self):
        theme = themeManager.activeTheme
        if self.role == "menu":
            bgColor = theme.menu_bg
        elif self.role == "pause":
            bgColor = theme.pause_bg
        else:
            bgColor = theme.neutral_white
        alpha = theme.alpha
        
        self.menuSurface.fill(bgColor)
        self.menuSurface.set_alpha(alpha)
        self.screen.blit(self.menuSurface, self.menuSurfaceRect)
        for button in self.buttons.values():
            button.draw(self.screen)


# return corresponding color to given block
def set_color(rect: pg.Rect, screenMultiplier: int, isHint: bool = False):
    if isHint:
        if rect.height < screenMultiplier and rect.width < screenMultiplier:
            return COLOR_1X1_HINT
        elif (rect.height < 2 * screenMultiplier and rect.width < screenMultiplier) or (rect.height < screenMultiplier and rect.width < 2 * screenMultiplier):
            return COLOR_1X2_HINT
        elif rect.height < 2 * screenMultiplier and rect.width < 2 * screenMultiplier:
            return COLOR_2X2_HINT
    else:
        if rect.height < screenMultiplier and rect.width < screenMultiplier:
            return COLOR_1X1
        elif (rect.height < 2 * screenMultiplier and rect.width < screenMultiplier) or (rect.height < screenMultiplier and rect.width < 2 * screenMultiplier):
            return COLOR_1X2
        elif rect.height < 2 * screenMultiplier and rect.width < 2 * screenMultiplier:
            return COLOR_2X2
    return "black"


def solve_board(boardZeros, rects: list[pg.Rect], targetRect: pg.Rect | None, screenMuliplier: int, targetPos: tuple[int, int] = (0,0)) -> list[tuple[tuple[int, int], str]] | None:
    blocks = rects_to_blocksDict(rects, screenMuliplier, targetRect)
    board = set_blocks(boardZeros, blocks)
    return calculate_board(board, blocks, targetPos)


def get_resourcepath(relativePath: str) -> str:
    basePath = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(basePath, relativePath)