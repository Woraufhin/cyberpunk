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

    def move(self, grid, pos=None):
        pass

    def promote(self, board, pawn, promotion_selector=None, pos=None):
        pass

class HumanPlayer(Player):
    type = 'human'

    def __init__(self, color):
        super().__init__(color)
        self.considering = None

    def move(self, grid, pos=None):
        move = False
        moves = grid.get_possible_moves(grid.grid, self.color)
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

    def promote(self, board, pawn, promotion_selector=None, pos=None):
        pick = promotion_selector.click(pos)
        board.handle_promotions(pawn, pick)
        return pick


class RandomAI(Player):
    type = 'machine'

    def __init__(self, color):
        super().__init__(color)

    def move(self, grid, pos=None):
        cho = choice(grid.get_possible_moves(grid.grid, self.color))
        grid.move(from_=cho[0], to=cho[1])
        return cho

    def promote(self, board, pawn, promotion_selector=None, pos=None):
        pick = choice(promotion_selector.promotions)
        board.handle_promotions(pawn, pick)
        return pick
