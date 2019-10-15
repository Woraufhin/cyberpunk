import logging
from random import choice
from pathlib import Path

import pygame as pg


logger = logging.getLogger(Path(__file__).stem)


class Player:
    def __init__(self, color):
        self.color = color

    def move(self):
        pass


class HumanPlayer(Player):
    def __init__(self, color):
        super().__init__(color)
        self.considering = []

    def move(self, pos, grid):
        turn_over = False
        sel = grid.select(pos, self.color)
        if sel is not None:
            logger.info('Selecting: %r', sel)
            self.considering.append(sel)
        if len(self.considering) == 2:
            if grid.move(*self.considering, self.color):
                turn_over = True
            self.considering = []
        return turn_over


class RandomAI(Player):
    def __init__(self, color):
        super().__init__(color)

    def move(self, grid):
        turn_over = False
        pos_moves = []
        for p in grid.white_pieces:
            for move in p.possible_moves(grid.grid):
                pos_moves.append((p.pos, move))
        cho = choice(pos_moves)
        logger.info('AI choosing: %r', cho)
        if grid.move(*cho, self.color):
            turn_over = True
        return turn_over
