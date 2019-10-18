from pathlib import PurePath


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
LIGHTBLUE = (142,229,238)

# game settings
WIDTH = 1024   # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 768  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 20
TITLE = "Cyberpunk chess"
BGCOLOR = BLACK

TILESIZE = 32
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE
