import logging
from pathlib import Path
from dataclasses import dataclass, field
from collections import namedtuple

import pygame as pg

import chess.settings as s
from chess.utils.coords import Coords
from chess.utils.typewriter import Typewriter, TypewriterConfig
from chess.panels.intro.button import Button, SelectionButton
from chess.pieces import Color


logger = logging.getLogger(Path(__file__).stem)


@dataclass(eq=False)
class PlayerMenu:
    pos: 'Coords'
    size: 'Coords'
    surface: 'pg.Surface'
    current: 'Color' = Color.white
    selection: dict = field(default_factory=dict)
    pmenu_title: 'TypewriterConfig' = TypewriterConfig(
        pos='midtop',
        size=16,
        surface_color=s.BLACK,
        padding=5
    )

    def __post_init__(self):
        self.scaled_pos = self.pos * s.TILESIZE
        self.scaled_size = self.size * s.TILESIZE
        self.pmenu = self.draw_frame()
        self.title_printer = Typewriter(
            surface=self.pmenu,
            config=self.pmenu_title
        )
        self.selection_buttons = {
            Color.white: self._draw_buttons(),
            Color.black: self._draw_buttons() + self._back_button()
        }

    def draw(self):
        self.pmenu.fill(s.BLACK)
        self.draw_player()
        for button in self.selection_buttons[self.current]:
            button.new()
        return self.selection_buttons[self.current]

    def draw_player(self):
        player = f'{self.current.name}'
        p_size = self.title_printer.get_text_size(player)
        self.title_printer.type(player)
        pad = self.title_printer.config.padding
        pg.draw.line(
            self.pmenu, s.GREEN,
            (0, p_size[1] + pad),
            (self.pmenu.get_width(), p_size[1] + pad), 1
        )

    def click(self, button):
        action = button.on_click()
        if action == 'back':
            self.current = Color.white
        else:
            self.selection[self.current] = action
            for button in self.selection_buttons[self.current]:
                if button.text != self.selection[self.current]:
                    button.selected = False
                else:
                    button.selected = True
            Player = namedtuple('Player', ['player', 'color'])
            p = Player(action, self.current)
            self.current = Color.black
            return p

    def _draw_buttons(self):
        size = Coords(x=6, y=1)
        return [
            SelectionButton(
                surface=self.surface,
                pos=Coords(x=8, y=2),
                size=size,
                text='human',
                desc="""A typical human scum. Tends to have 4 legs and a gender of her choice.

They love to watch the fire burn and have Vietnam flashbacks."""
            ),
            SelectionButton(
                surface=self.surface,
                pos=Coords(x=8, y=3),
                size=size,
                text='random AI',
                desc="""Cute AI that shoots bullets in the dark.
I\'m actually going to tell you what it does:

   import random as r
   r.choice(possible_moves)
"""
            )
        ]

    def _back_button(self):
        size = Coords(x=6, y=1)
        return [
            Button(
                surface=self.surface,
                pos=Coords(x=8, y=4),
                size=size,
                text='back',
                config=TypewriterConfig(
                    size=16,
                    color=s.GREEN,
                    pos='midleft'
                )
            )
        ]

    def draw_frame(self):
        subsurface = pg.Rect(
            self.scaled_pos.x, self.scaled_pos.y,
            self.scaled_size.x, self.scaled_size.y
        )
        frame = self.surface.subsurface(subsurface)
        frame.fill(s.BLACK)
        return frame
