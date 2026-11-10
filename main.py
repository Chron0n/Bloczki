import sys
import pygame as pg
from math import ceil, floor
import utils


BOARD_HEIGHT = 5
BOARD_WIDTH = 4
SCREEN_MULTIPLIER = 200
SPACING = ceil(SCREEN_MULTIPLIER / 40)

SCREEN_HEIGHT = BOARD_HEIGHT * SCREEN_MULTIPLIER
SCREEN_WIDTH = BOARD_WIDTH  * SCREEN_MULTIPLIER
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

DIRECTIONS = {
    pg.K_UP: ((0, -SCREEN_MULTIPLIER), "up"),
    pg.K_DOWN: ((0, SCREEN_MULTIPLIER), "down"),
    pg.K_LEFT: ((-SCREEN_MULTIPLIER, 0), "left"),
    pg.K_RIGHT: ((SCREEN_MULTIPLIER, 0), "right")
}


class Game:
    menuUI: utils.MenuUI
    pauseUI: utils.MenuUI

    solutionMovesCopy: list[tuple[tuple[int, int], str]]
    rectsListCopy: list[pg.Rect]
    targetRectCopy: pg.Rect
    hintBlockCopy: utils.HintObject
    def __init__(self):
        pg.init()
        pg.display.set_icon(pg.image.load(utils.get_resourcepath("assets/icon.png")))
        pg.display.set_caption("Bloczki")
        self.screen = pg.display.set_mode(SCREEN_SIZE)
        self.clock = pg.time.Clock()

        self.gameState = "MENU"

        self.blockTypesList = [(2, 2, 1), (1, 2, 5), (1, 1, 4)]
        self.targetBlock = (2, 2)
        self.targetPos = (3, 1)
        self.boardZeros = utils.create_board(BOARD_HEIGHT, BOARD_WIDTH)

        self.solutionMoves = None
        self.rectsList = []
        self.targetRect = None
        self.hintBlock = None

        self.selectedBlock = None
        self.isHintActive = False
        self.mx, self.my = 0, 0
        self.isMouseMode = False

        self.frame = pg.Rect(SPACING, SPACING, SCREEN_MULTIPLIER - 2 * SPACING, SCREEN_MULTIPLIER - 2 * SPACING)

        self.setup()


    def setup(self):
        menuButtons = {
            "play" : utils.Button("Play", (SCREEN_WIDTH // 2, floor(SCREEN_HEIGHT * 0.3)), "menu", (2 * SCREEN_MULTIPLIER, SCREEN_MULTIPLIER // 2), SCREEN_MULTIPLIER // 2),
            "settings" : utils.Button("Settings", (SCREEN_WIDTH // 2, floor(SCREEN_HEIGHT * 0.5)), "menu", (2 * SCREEN_MULTIPLIER, SCREEN_MULTIPLIER // 2), SCREEN_MULTIPLIER // 2),
            "exit" : utils.Button("Exit", (SCREEN_WIDTH // 2, floor(SCREEN_HEIGHT * 0.7)), "menu", (2 * SCREEN_MULTIPLIER, SCREEN_MULTIPLIER // 2), SCREEN_MULTIPLIER // 2)
            }
        self.menuUI = utils.MenuUI(self.screen, SCREEN_SIZE, "menu", menuButtons)

        settingsButtons = {
            "darkMode": utils.Button("Dark Mode", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), "menu", (2 * SCREEN_MULTIPLIER, SCREEN_MULTIPLIER // 2), SCREEN_MULTIPLIER // 2),
            "back": utils.Button("Back", (SCREEN_MULTIPLIER // 2, SCREEN_MULTIPLIER // 4), "menu", (SCREEN_MULTIPLIER, SCREEN_MULTIPLIER // 2), SCREEN_MULTIPLIER // 2)
        }
        self.settingsUI = utils.MenuUI(self.screen, SCREEN_SIZE, "menu", settingsButtons)

        pauseButtons = {
            "resume" : utils.Button("Resume", (SCREEN_WIDTH // 2, SCREEN_MULTIPLIER), "pause", (2 * SCREEN_MULTIPLIER, SCREEN_MULTIPLIER // 2), SCREEN_MULTIPLIER // 2),
            "restart" : utils.Button("Restart", (SCREEN_WIDTH // 2, 2 * SCREEN_MULTIPLIER), "pause", (2 * SCREEN_MULTIPLIER, SCREEN_MULTIPLIER // 2), SCREEN_MULTIPLIER // 2),
            "newLevel" : utils.Button("New Level",(SCREEN_WIDTH // 2, 3 * SCREEN_MULTIPLIER), "pause", (2 * SCREEN_MULTIPLIER, SCREEN_MULTIPLIER // 2), SCREEN_MULTIPLIER // 2),
            "menu" : utils.Button("Menu", (SCREEN_WIDTH // 2, 4 * SCREEN_MULTIPLIER), "pause", (2 * SCREEN_MULTIPLIER, SCREEN_MULTIPLIER // 2), SCREEN_MULTIPLIER // 2)
        }
        pauseScreenSize = (floor(SCREEN_WIDTH * 0.7), floor(SCREEN_HEIGHT * 0.8))
        self.pauseUI = utils.MenuUI(self.screen, pauseScreenSize, "pause", pauseButtons)


    def generate_level(self):
        self.solutionMoves = None

        while self.solutionMoves is None or len(self.solutionMoves) == 0:
            blocksDict, board = utils.blocks_randomly_to_blocksDict(self.boardZeros, self.blockTypesList, self.targetBlock)
            self.solutionMoves = utils.calculate_board(board, blocksDict, self.targetPos)
        
        self.rectsList, self.targetRect = utils.blocksDict_to_rects(blocksDict, SCREEN_MULTIPLIER, SPACING)
        self.hintBlock = utils.HintObject(utils.find_rect_of_matrix_pos(self.rectsList, self.solutionMoves[0][0], SCREEN_MULTIPLIER, SPACING), SCREEN_MULTIPLIER)

        self.solutionMovesCopy = self.solutionMoves.copy()
        self.rectsListCopy = [rect.copy() for rect in self.rectsList]
        self.targetIndex = self.rectsList.index(self.targetRect)
        self.hintBlockCopy = self.hintBlock.copy()


    def clear_level(self):
        self.solutionMoves = None
        self.rectsList = []
        self.targetRect = None
        self.hintBlock = None
        
        self.selectedBlock = None
        self.isHintActive = False
        self.mx, self.my = 0, 0

        self.frame.x = SPACING
        self.frame.y = SPACING


    def restart_level(self):
        self.clear_level()
        self.solutionMoves = self.solutionMovesCopy.copy()
        self.rectsList = [rect.copy() for rect in self.rectsListCopy]
        self.targetRect = self.rectsList[self.targetIndex]
        self.hintBlock = self.hintBlockCopy.copy()


    def handle_events_menu(self, event):
        if self.menuUI.buttons["play"].is_clicked(event):
            self.generate_level()
            self.gameState = "GAME"
        elif self.menuUI.buttons["settings"].is_clicked(event):
            self.gameState = "SETTINGS"
        elif self.menuUI.buttons["exit"].is_clicked(event):
            pg.quit()
            sys.exit()


    def handle_events_settings(self, event):
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.gameState = "MENU"
        elif self.settingsUI.buttons["back"].is_clicked(event):
            self.gameState = "MENU"
        elif self.settingsUI.buttons["darkMode"].is_clicked(event):
            utils.themeManager.toggle_dark_mode()


    def handle_events_game(self, event):
        if self.solutionMoves is None:
            self.clear_level
            self.gameState = "MENU"
            return
        
        if event.type == pg.KEYDOWN:
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.gameState = "PAUSE"
            
            elif event.key in DIRECTIONS:
                self.isMouseMode = False
                objectToMove = self.selectedBlock if self.selectedBlock is not None else self.frame
                dx, dy = DIRECTIONS[event.key][0]
                direction = DIRECTIONS[event.key][1]
                
                can_move = (
                    dy < 0 and objectToMove.top > SCREEN_MULTIPLIER or
                    dy > 0 and objectToMove.bottom < SCREEN_HEIGHT - SCREEN_MULTIPLIER or
                    dx < 0 and objectToMove.left > SCREEN_MULTIPLIER or
                    dx > 0 and objectToMove.right < SCREEN_WIDTH - SCREEN_MULTIPLIER
                )
                if can_move:   # Checking if object won't expand over the board
                    isHintBlock = objectToMove.topleft == self.hintBlock.startingPos if self.hintBlock is not None else False
                    objectToMove.move_ip(dx, dy)
                    if self.selectedBlock is not None:      # Logic for blocks only
                        other_blocks = [b for b in self.rectsList if b is not self.selectedBlock]
                        if self.selectedBlock.collideobjects(other_blocks) is None:      # Checking if there is no collision with any other block
                            self.frame.move_ip(dx, dy)   # Moving a frame to block
                            self.isHintActive = False
                            if isHintBlock and direction == self.solutionMoves[0][1] and len(self.solutionMoves) > 1:
                                self.solutionMoves.pop(0)
                                self.hintBlock = utils.HintObject(utils.find_rect_of_matrix_pos(self.rectsList, self.solutionMoves[0][0], SCREEN_MULTIPLIER, SPACING), SCREEN_MULTIPLIER)
                            else:
                                self.solutionMoves = []
                                self.hintBlock = None
                        else:
                            self.selectedBlock.move_ip(-dx, -dy) # Moving a block back
            
            elif event.key == pg.K_SPACE:
                self.isMouseMode = False
                if self.selectedBlock is not None:
                    self.selectedBlock = None
                else:
                    self.selectedBlock = self.frame.collideobjects(self.rectsList)
            
            elif event.key == pg.K_c:
                if not self.solutionMoves:
                    self.solutionMoves = utils.solve_board(self.boardZeros, self.rectsList, self.targetRect, SCREEN_MULTIPLIER, self.targetPos)
                    if self.solutionMoves is None:
                        self.clear_level()
                        self.gameState = "MENU"
                        return
                print(self.solutionMoves)
            
            elif event.key == pg.K_h:
                if not self.isHintActive:
                    if not self.solutionMoves:
                        self.solutionMoves = utils.solve_board(self.boardZeros, self.rectsList, self.targetRect, SCREEN_MULTIPLIER, self.targetPos)
                        if self.solutionMoves is None:
                            self.clear_level()
                            self.gameState = "MENU"
                            return
                    if self.solutionMoves:
                        print(self.solutionMoves[0])
                        self.hintBlock = utils.HintObject(utils.find_rect_of_matrix_pos(self.rectsList, self.solutionMoves[0][0], SCREEN_MULTIPLIER, SPACING), SCREEN_MULTIPLIER)
                    else:
                        self.hintBlock = None
                    self.isHintActive = True
                else:
                    self.isHintActive = False
        
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.isMouseMode = True
            cursorRect = pg.Rect(event.pos[0], event.pos[1], 1, 1)
            self.selectedBlock = cursorRect.collideobjects(self.rectsList)
            pg.mouse.get_rel()
        
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.selectedBlock = None
            self.mx, self.my = 0, 0
        
        elif event.type == pg.MOUSEMOTION:
            if pg.mouse.get_pressed()[0] and self.selectedBlock is not None:
                mouse = pg.mouse.get_rel()
                self.mx += mouse[0]
                self.my += mouse[1]
                dx, dy = 0, 0
                direction = ""
                if self.my < -SCREEN_MULTIPLIER:
                    direction = "up"
                    dx, dy = (0, -SCREEN_MULTIPLIER)
                    self.my += SCREEN_MULTIPLIER
                elif self.my > SCREEN_MULTIPLIER:
                    direction = "down"
                    dx, dy = (0, SCREEN_MULTIPLIER)
                    self.my -= SCREEN_MULTIPLIER
                elif self.mx < -SCREEN_MULTIPLIER:
                    direction = "left"
                    dx, dy = (-SCREEN_MULTIPLIER, 0)
                    self.mx += SCREEN_MULTIPLIER
                elif self.mx > SCREEN_MULTIPLIER:
                    direction = "right"
                    dx, dy = (SCREEN_MULTIPLIER, 0)
                    self.mx -= SCREEN_MULTIPLIER
                
                if dx != 0 or dy != 0:
                    can_move = (
                        dy < 0 and self.selectedBlock.top > SCREEN_MULTIPLIER or
                        dy > 0 and self.selectedBlock.bottom < SCREEN_HEIGHT - SCREEN_MULTIPLIER or
                        dx < 0 and self.selectedBlock.left > SCREEN_MULTIPLIER or
                        dx > 0 and self.selectedBlock.right < SCREEN_WIDTH - SCREEN_MULTIPLIER
                    )
                    if can_move:
                        isHintBlock = self.selectedBlock.topleft == self.hintBlock.startingPos if self.hintBlock is not None else False
                        self.selectedBlock.move_ip(dx, dy)
                        other_blocks = [b for b in self.rectsList if b is not self.selectedBlock]
                        if self.selectedBlock.collideobjects(other_blocks) is None:
                            self.isHintActive = False
                            if isHintBlock and direction == self.solutionMoves[0][1] and len(self.solutionMoves) > 1:
                                self.solutionMoves.pop(0)
                                self.hintBlock = utils.HintObject(utils.find_rect_of_matrix_pos(self.rectsList, self.solutionMoves[0][0], SCREEN_MULTIPLIER, SPACING), SCREEN_MULTIPLIER)
                            else:
                                self.solutionMoves = []
                                self.hintBlock = None
                        else:
                            self.selectedBlock.move_ip(-dx, -dy)


    def handle_events_pause(self, event):
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.gameState = "GAME"
        elif self.pauseUI.buttons["resume"].is_clicked(event):
            self.gameState = "GAME"
        elif self.pauseUI.buttons["restart"].is_clicked(event):
            self.restart_level()
            self.gameState = "GAME"
        elif self.pauseUI.buttons["newLevel"].is_clicked(event):
            self.clear_level()
            self.generate_level()
            self.gameState = "GAME"
        elif self.pauseUI.buttons["menu"].is_clicked(event):
            self.clear_level()
            self.gameState = "MENU"


    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            
            if self.gameState == "MENU":
                self.handle_events_menu(event)
            elif self.gameState == "SETTINGS":
                self.handle_events_settings(event)
            elif self.gameState == "GAME":
                self.handle_events_game(event)
            elif self.gameState == "PAUSE":
                self.handle_events_pause(event)


    def upadate(self):
        if self.isHintActive and self.hintBlock is not None and self.solutionMoves is not None:
            self.hintBlock.move(self.solutionMoves[0][1])


    def draw_game(self):
        theme = utils.themeManager.activeTheme
        self.screen.fill(theme.game_bg)

        # Drawing an animated hint block
        if self.isHintActive and self.hintBlock is not None:
            pg.draw.rect(self.screen, self.hintBlock.color, pg.Rect(self.hintBlock.pos[0], self.hintBlock.pos[1], self.hintBlock.width, self.hintBlock.height))

        # Drawing all blocks
        for rect in self.rectsList:
            pg.draw.rect(self.screen, utils.set_color(rect, SCREEN_MULTIPLIER), rect)

        # Drawing a frame
        if not self.isMouseMode:
            if self.selectedBlock is not None:
                pg.draw.lines(self.screen, theme.frame_selected, True, [self.selectedBlock.topleft, self.selectedBlock.topright, self.selectedBlock.bottomright, self.selectedBlock.bottomleft], floor(SCREEN_MULTIPLIER / 25))
            else:
                pg.draw.lines(self.screen, theme.frame_notselected, True, [self.frame.topleft, self.frame.topright, self.frame.bottomright, self.frame.bottomleft], floor(SCREEN_MULTIPLIER / 25))


    def draw(self):
        if self.gameState == "MENU":
            self.menuUI.draw()
        elif self.gameState == "SETTINGS":
            self.settingsUI.draw()
        elif self.gameState == "GAME":
            self.draw_game()
        elif self.gameState == "PAUSE":
            self.draw_game()
            self.pauseUI.draw()
        
        pg.display.flip()


    def run(self):
        while True:
            self.handle_events()
            self.upadate()
            self.draw()
            self.clock.tick(60)



def main():
        game = Game()
        game.run()


if __name__ == "__main__":
    main()