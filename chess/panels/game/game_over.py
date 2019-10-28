import logging
from pathlib import Path
from dataclasses import dataclass

import pygame as pg

import chess.settings as s
from chess.panels.panel import Panel
from chess.panels.backdrop import Backdrop
from chess.utils.typewriter import TypewriterConfig, Typewriter
from chess.panels.intro.button import Button

from chess.utils.coords import Coords


logger = logging.getLogger(Path(__file__).stem)


@dataclass(eq=False)
class GameOver(Panel):

    color: tuple = s.BLACK
    draw_px_art: bool = False
    go_config: 'TypewriterConfig' = TypewriterConfig(
        size=72,
        pos='center'
    )

    def __post_init__(self):
        self.backdrop = Backdrop(
            sprite_group=self.sprite_group,
            pos=Coords(x=0, y=0),
            size=Coords(x=s.GRIDWIDTH, y=s.GRIDHEIGHT)
        )
        self.tp = Typewriter(
            surface=self.backdrop.image,
            config=self.go_config
        )
        self.tp.type('Game over')
        #self.buttons = self.draw_buttons()
