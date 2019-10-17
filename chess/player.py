import logging
from random import choice
from pathlib import Path


logger = logging.getLogger(Path(__file__).stem)


class PlayerFactory:
    @staticmethod
    def make(name):
        return {
            'human': HumanPlayer,
            'random AI': RandomAI
        }[name]


class Player:
    type = None
    def __init__(self, color):
        self.color = color

    def move(self):
        pass


class HumanPlayer(Player):
    type = 'human'

    def __init__(self, color):
        super().__init__(color)
        self.considering = []

    def move(self, pos, grid):
        move = False
        sel = grid.select(pos, self.color)
        if sel is not None:
            logger.info('Selecting: %r', sel)
            self.considering.append(sel)
        if len(self.considering) == 2:
            if grid.move(*self.considering, self.color):
                move = self.considering
            self.considering = []
        return move


class RandomAI(Player):
    type = 'machine'

    def __init__(self, color):
        super().__init__(color)

    def move(self, grid):
        move = False
        pos_moves = []
        for p in grid.get_pieces_for_color(self.color):
            for move in p.possible_moves(grid.grid):
                pos_moves.append((p.pos, move))
        cho = choice(pos_moves)
        logger.info('AI choosing: %r', cho)
        if grid.move(*cho, self.color):
            move = cho
        return move
