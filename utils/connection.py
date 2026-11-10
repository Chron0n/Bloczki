from math import floor, ceil
from pygame import Rect


# Create a dictionary from given rectangles list: key >= 2, val = (hight, width, row, column, isTarget)
def rects_to_blocksDict(rects: list[Rect], screenMultiplier: int, targetRect: Rect | None) -> dict[int, tuple[int, int, int, int, bool]]:
    if targetRect is None:
        targetRect = rects[0] 
    blocksDict = {}
    key = 2
    for rect in rects:
        isTarget = (rect is targetRect)
        blocksDict[key] = (
            ceil(rect.height / screenMultiplier),
            ceil(rect.width / screenMultiplier),
            floor(rect.y / screenMultiplier),
            floor(rect.x / screenMultiplier),
            isTarget
            )
        key += 1
    return blocksDict


# Create a list of rectangles from given dictionary
# Also create a target block based on dictionary
def blocksDict_to_rects(blocksDict: dict[int, tuple[int, int, int, int, bool]], screeMultiplier: int, spacing: int) -> tuple[list[Rect], Rect]:
    rects = []
    for block in blocksDict.values():
        rect = Rect(block[3] * screeMultiplier + spacing,
                    block[2] * screeMultiplier + spacing,
                    block[1] * screeMultiplier - 2 * spacing,
                    block[0] * screeMultiplier - 2 * spacing)
        rects.append(rect)
        if block[4]:
            targetBlock = rect
    return rects, targetBlock


# Return first found rectangle on given matrix posistion (y, x)
def find_rect_of_matrix_pos(rectsList : list[Rect], pos: tuple[int, int], screenMultiplier: int, spacing: int) -> Rect | None:
    for rect in rectsList:
        if rect.collidepoint(pos[1] * screenMultiplier + spacing + 1, pos[0] * screenMultiplier + spacing + 1):
            return rect
    return None


# Create a rectangle of given height, width and position(row, column)
# NOTE: height and width are inversed to those in matrix and also values in position
def create_rect(pos: tuple[int, int], height: int, width: int, screenMultiplier: int, spacing: int) -> Rect:
    return Rect(pos[1] * screenMultiplier + spacing, pos[0] * screenMultiplier + spacing, width * screenMultiplier - 2 * spacing, height * screenMultiplier - 2 * spacing)