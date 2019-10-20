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

    def move(self, grid, pos):
        pass

    def get_possible_moves(self, grid):
        pos_moves = []
        for p in grid.get_pieces_for_color(self.color):
            for move in p.possible_moves(grid.grid):
                pos_moves.append((p.pos, move))
        return pos_moves


class HumanPlayer(Player):
    type = 'human'

    def __init__(self, color):
        super().__init__(color)
        self.considering = None

    def move(self, grid, pos):
        move = False
        moves = self.get_possible_moves(grid)
        sel = grid.select(pos, self.color)
        if sel is not None and self.considering is None:
            self.considering = sel
        elif (self.considering, sel) in moves:
            move = (self.considering, sel)
            grid.move(from_=move[0], to=move[1])
            self.considering = None
        else:
            logger.debug('Player did not click on a possible square')
            self.considering = None
        return move


class RandomAI(Player):
    type = 'machine'

    def __init__(self, color):
        super().__init__(color)

    def move(self, grid, pos):
        cho = choice(self.get_possible_moves(grid))
        grid.move(from_=cho[0], to=cho[1])
        return cho
