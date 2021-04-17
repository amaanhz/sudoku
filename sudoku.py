import pygame
import sys
import time
import random
import os
import copy
import numpy as np



def plusone(loc, history=None):
    """
    :param tuple loc: Location
    :param dict history: History dictionary (Default None)
    :return: The next grid square in history if it is provided, otherwise returns the next grid square in order.
    """
    if history is not None:
        keys = list(history.keys())
        keys.append(loc)
        keys.sort(key=lambda x : [x[0], x[1]])
        if len(keys) > 0:
            if keys[-1] != loc:
                return keys[-1]
        return None
    else:
        if loc[1] < 8:
            return loc[0], loc[1] + 1
        return loc[1] + 1, 0
class Square:
    def __init__(self, loc, val):
        self.loc = loc
        self.value = val

class Cell:
    def __init__(self, rect):
        self.rect = rect
        self.state = False
    def toggleselect(self):
        self.state = True if not self.state else False

class SquareStack:
    def __init__(self):
        self.stack = []
        self.histories = {}
    def append(self, loc, val):
        self.stack.append(Square(loc, val))
    def pop(self):
        lastSquare = self.stack.pop()
        # remove the history of the next square, as it no longer applies
        self.histories.pop(plusone(lastSquare.loc, self.histories), None)
        if lastSquare.loc not in self.histories:
            self.histories[lastSquare.loc] = []
        self.histories[lastSquare.loc].append(lastSquare.value)
        return lastSquare
    def history(self, loc):
        return self.histories[loc] if loc in self.histories else []

class Sudoku:
    def __init__(self, override=False, dim=9, clues=32):
        self.dimensions = dim
        self.clues = set()
        self.board = []
        self.quadrants = []
        # Initialize board - col, row
        if override:
            self.board = [[3, 7, None, None, None, 6, None, 1, None],
                          [None, 4, 2, 3, None, None, None, 5, None],
                          [None, None, None, None, 8, None, 2, None, None],
                          [2, None, None, 7, None, None, None, None, 9],
                          [None, None, 6, 4, None, 9, 8, None, None],
                          [1, None, None, None, None, 2, None, None, 3],
                          [None, None, 5, None, 9, None, None, None, None],
                          [None, 1, None, None, None, 5, 4, 9, None],
                          [None, 9, None, 1, None, None, None, 7, 2]]
        else:
            for i in range(self.dimensions):
                col = []
                for j in range(self.dimensions):
                    col.append(None)
                self.board.append(col)
            self.solve()
            self.set_clues(clues)
            self.original = copy.deepcopy(self.board)

    def write(self, loc, val):
        i, j = loc
        self.board[i][j] = val

    def randfilledsquare(self):
        x, y = -1, -1
        while x < 0 or y < 0:
            x, y = random.randint(0, 8), random.randint(0, 8)
            if self.board[x][y] is None:
                x, y = -1, -1
        return x, y

    def print(self):
        grid = ""
        for row in range(self.dimensions):
            line = "|"
            for col in self.board:
                char = " " if col[row] is None else col[row]
                line = line + f"{str(char)}|"
            grid = grid + line + "\n"
        print(grid)

    def solve2(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] is None:
                    for n in range(1, 10):
                        if n in self.possible_numbers((i, j)):
                            self.board[i][j] = n
                            self.solve2()
                            self.board[i][j] = None
                    return

    def set_clues(self, clues=35):
        stack = SquareStack()
        flat = list(np.concatenate(self.board).flat)
        while len([x for x in flat if isinstance(x, (int, np.integer))]) > clues:
            removal = None
            while removal is None or removal in stack.histories:
                removal = self.randfilledsquare()
            i, j = removal
            stack.append(removal, self.board[i][j])
            self.board[i][j] = None
            removed = copy.deepcopy(self.board)
            if self.solve():
                first = copy.deepcopy(self.board)
                self.board = copy.deepcopy(removed)
                if self.solve(prevboard=first):
                    self.board = copy.deepcopy(removed)
                    previous = stack.pop()
                    self.board[previous.loc[0]][previous.loc[1]] = previous.value
            flat = list(np.concatenate(self.board).flat)

    def solve(self, prevboard=[]):
        stack = SquareStack()
        try:
            while any(None in col for col in self.board):
                brk = False
                for i in range(len(self.board)):
                    for j in range(len(self.board[i])):
                        if self.board[i][j] is None:
                            possible = [num for num in self.possible_numbers((i, j)) if num not in stack.history((i, j))]
                            if len(possible) > 0:
                                self.board[i][j] = random.choice(possible)
                                stack.append((i, j), self.board[i][j])
                                if self.board == prevboard:
                                    prevMove = stack.pop()
                                    x, y = prevMove.loc
                                    self.board[x][y] = None
                                    brk = True
                                    break
                            else:
                                prevMove = stack.pop()
                                x, y = prevMove.loc
                                self.board[x][y] = None
                                brk = True
                                break
                    if brk:
                        break
        except IndexError:
            return False
        return True

    def value(self, loc):
        i, j = loc
        return self.board[i][j]

    def get_row(self, loc, include_loc=True):
        """
        :param tuple loc: Location
        :param bool include_loc: Include the location provided when returning the row
        :return: The row belonging to the given grid location. (List)
        """
        i, j = loc
        row = []
        for col in self.board:
            if col[j] == loc[0] and not include_loc:
                continue
            else:
                row.append(col[j])
        return row

    def get_quad(self, loc, grid=False, include_loc=True):
        """
        Returns the quadrant of this grid coordinate unless grid is True, then returns
        the coordinates of said quadrant.
        """
        i, j = loc
        values = []
        try:
            temp = self.board[i][j]
        except IndexError:
            raise Exception
        if not grid:
            startingcol, startingrow = self.get_quad(loc, grid=True)[0] * 3, self.get_quad(loc, grid=True)[1] * 3
            for col in range(startingcol, startingcol + 3):
                for row in range(startingrow, startingrow + 3):
                    values.append(self.board[col][row])
        return (i // 3, j // 3) if grid else values

    def possible_numbers(self, loc):
        """
        Returns all the possible numbers according to column
         and row for this grid coordinate.
        """
        i, j = loc
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        numbers = [num for num in numbers if num not in self.board[i] and num not in self.get_row(loc)
                   and num not in self.get_quad(loc)]
        return numbers

game = Sudoku()

