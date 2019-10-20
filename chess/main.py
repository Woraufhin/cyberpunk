import logging
import pygame as pg

import chess.settings as s
from chess.director import Director
from chess.states.intro import Intro
from chess.states.game import Game


# initialization
pg.init()
pg.display.set_caption(s.TITLE)
SCREEN = pg.display.set_mode((s.WIDTH, s.HEIGHT))
SCREEN_RECT = SCREEN.get_rect()


def main():
    logging.basicConfig(
        format='[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s',
        datefmt='%I:%M:%S %p',
        level=logging.INFO
    )
    director = Director(caption=s.TITLE)

    # states the game has / scenes
    state_dict = {
        'INTRO': Intro(),
        'GAME': Game()
    }
    director.setup_states(state_dict, "INTRO")
    director.main()


if __name__ == '__main__':
    main()
