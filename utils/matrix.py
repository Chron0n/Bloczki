import numpy as np
from collections import deque
import random


# Create a matrix of given height and width filled with 0s
def create_board(height, width):
    return np.zeros((height, width))


# Set blocks from given dictionary in matrix
def set_blocks(board, blocksDict):
    newBoard = board.copy() # Board filled with 0s
    for key in blocksDict:
        block = blocksDict[key]
        newBoard[block[2]:block[2]+block[0], block[3]:block[3]+block[1]] = 1 # Filling all cells of block with 1
        newBoard[block[2], block[3]] = key   # Filling top-left cell with block key
    return newBoard


# Create a dictionary from given blocks list of format [(height, width, amount), ...]
# Also return a setted board
def blocks_randomly_to_blocksDict(board, blockTypesList, targetBlock=(0, 0)):
    newBoard = board.copy()
    blocksDict = {}
    key = 2

    for blockType in blockTypesList:
        leftSquares = np.argwhere(newBoard == 0).tolist()   # Take all squares with 0 and randomly shuffle
        random.shuffle(leftSquares)

        blocksCounter = blockType[2]
        i = 0
        
        while blocksCounter > 0:
            if i >= len(leftSquares):   # Checking if there is no space left to place current block
                print("No space left, skipping the rest of blocks")
                return blocksDict, newBoard
            
            y, x = leftSquares[i]
            i += 1

            dim1, dim2 = blockType[0], blockType[1]
            if dim1 == dim2:
                orientations = [(dim1, dim2)]
            else:
                orientations = [(dim1, dim2), (dim2, dim1)]
                random.shuffle(orientations)    # Shuffle 2 directions of non-squared block
                
            for height, width in orientations:
                if y + height > newBoard.shape[0] or x + width > newBoard.shape[1]: # Checking if block does not expand over the board
                    continue

                boardSlice = newBoard[y : y + height, x : x + width]    # Take fragment of board where block is to be placed
                if (boardSlice != 0).any():     # Checking if block does not overlap other blocks
                    continue

                newBoard[y : y + height, x : x + width] = 1
                newBoard[y, x] = key    # Placing block on the board

                isTarget = (height, width) == targetBlock
                blocksDict[key] = (height, width, y, x, isTarget)   # Write block in the dictionary

                key += 1
                blocksCounter -= 1
                break       # End loop if block has been placed or repeate once more with other direction if there is one
    return blocksDict, newBoard


# Finding the shortest way to solve given board
def calculate_board(board, blocksDict, targetPos=(0,0)):
    queue = deque([(board, [])])

    calculationBlocksDict = {key: (val[0], val[1], val[4]) for key, val in blocksDict.items()}  # Create blocks dictionary without positions
    usedBoards = set()

    while queue:
        currentBoard, currentMoves = queue.popleft()

        boardState = get_board_state(currentBoard, calculationBlocksDict)
        if boardState in usedBoards:
            continue                    # Continue if the same board was already analysed
        usedBoards.add(boardState)

        elemInTargetPos = currentBoard[targetPos[0], targetPos[1]]
        if elemInTargetPos != 0 and elemInTargetPos != 1:
            if calculationBlocksDict[elemInTargetPos][2]:
                return currentMoves                     # End if board is solved
        
        for (row, column), elem in np.ndenumerate(currentBoard):
            if elem != 0 and elem != 1:
                directions = ["up", "down", "left", "right"]
                block = calculationBlocksDict[elem]
                pos = (row, column)
                for direction in directions:
                    if is_valid_move(currentBoard, block, pos, direction):
                        newBoard = move_block(currentBoard, block, elem, pos, direction)
                        newMoves = currentMoves + [(pos, direction)]
                        queue.append((newBoard, newMoves))
    return None # No solutions


def move_block(board, block, blockID, pos, direction):
    newBoard = board.copy()
    height = block[0]
    width = block[1]
    if direction == "up":
        newBoard[pos[0], pos[1]] = 1                                # Filling old block position with 1
        newBoard[pos[0] + height - 1, pos[1] : pos[1] + width] = 0  # Filling old row/column with 0
        newBoard[pos[0] - 1, pos[1] : pos[1] + width] = 1           # Filling new row/column with 1
        newBoard[pos[0] - 1, pos[1]] = blockID                      # Filling new block position with blockID
    elif direction == "down":
        newBoard[pos[0], pos[1]] = 1
        newBoard[pos[0], pos[1] : pos[1] + width] = 0
        newBoard[pos[0] +height, pos[1] : pos[1] + width] = 1
        newBoard[pos[0] + 1, pos[1]] = blockID
    elif direction == "left":
        newBoard[pos[0], pos[1]] = 1
        newBoard[pos[0] : pos[0] + height, pos[1] + width - 1] = 0
        newBoard[pos[0] : pos[0] + height, pos[1] - 1] = 1
        newBoard[pos[0], pos[1] - 1] = blockID
    elif direction == "right":
        newBoard[pos[0], pos[1]] = 1
        newBoard[pos[0] : pos[0] + height, pos[1]] = 0
        newBoard[pos[0] : pos[0] + height, pos[1] + width] = 1
        newBoard[pos[0], pos[1] + 1] = blockID
    return newBoard


def is_valid_move(board, block, pos, direction):
    if direction == "up":
        if pos[0] - 1 < 0:  # Checking if block won't be moved out of the board
            return False
        for i in range(block[1]):   # Checking collision with other blocks
            if board[pos[0] - 1, pos[1] + i] != 0:
                return False
    elif direction == "down":
        if pos[0] + block[0] >= board.shape[0]:
            return False
        for i in range(block[1]):
            if board[pos[0] + block[0], pos[1] + i] != 0:
                return False
    elif direction == "left":
        if pos[1] - 1 < 0:
            return False
        for i in range(block[0]):
            if board[pos[0] + i, pos[1] - 1] != 0:
                return False
    elif direction == "right":
        if pos[1] + block[1] >= board.shape[1]:
            return False
        for i in range(block[0]):
            if board[pos[0] + i, pos[1] + block[1]] != 0:
                return False
    return True


# Return state of the board - a tuple of values of each cell in matrix
def get_board_state(board, blocksDict):
    state = []
    for row in board:
        row_state = []
        for cell in row:
            if cell == 0 or cell == 1:
                row_state.append(cell)
            else:       # Create an unique value for each block (same value for the same block type)
                row_state.append(f"B_{blocksDict[cell][0]}x{blocksDict[cell][1]}_{blocksDict[cell][2]}")
        state.append(tuple(row_state))
    return tuple(state)