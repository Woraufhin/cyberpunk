import logging
import pygame as pg

from pathlib import PurePath

from chess.director import Director
from chess.states.intro import Intro
from chess.states.game import Game


# PYGAME OPTIONS
FONT_PATH = str(PurePath('assets', 'fonts', 'redalert_inet.ttf'))
SPRITE_FOLDER = str(PurePath('assets', 'sprites'))

# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (102, 255, 102)
LIGHTGREEN = (51, 255, 51)
DARKGREEN = (0, 128, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# game settings
WIDTH = 1024   # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 768  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Cyberpunk chess"
BGCOLOR = BLACK

TILESIZE = 32
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

#Initialization
pg.init()
pg.display.set_caption(TITLE)
SCREEN = pg.display.set_mode((WIDTH, HEIGHT))
SCREEN_RECT = SCREEN.get_rect()


def main():
    logging.basicConfig(
        format='[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s',
        datefmt='%I:%M:%S %p',
        level=logging.DEBUG
    )
    """Add states to control here."""
    director = Director(TITLE)
    state_dict = {
        'INTRO': Intro(),
        'GAME': Game()
    }
    director.setup_states(state_dict, "INTRO")
    director.main()

main()
