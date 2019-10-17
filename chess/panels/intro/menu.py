import logging
from pathlib import Path
from dataclasses import dataclass, field
from collections import defaultdict
from functools import partial
from typing import Type, Union

import pygame as pg

import chess.settings as s
from chess.utils.coords import Coords
from chess.panels.intro.button import Button
from chess.panels.intro.player import PlayerMenu


logger = logging.getLogger(Path(__file__).stem)


@dataclass(eq=False)
class Menu(pg.sprite.Sprite):
    sprite_group: Type['pg.sprite.Group']
    pos: 'Coords'
    size: 'Coords'
    console: Union[None, Type['chess.panels.console.Console']] = None
    config: dict = field(default_factory=partial(defaultdict, dict))

    def __post_init__(self):
        super().__init__(self.sprite_group)
        self.image = pg.Surface((
            s.TILESIZE * self.size.x,
            s.TILESIZE * self.size.y
        ))
        self.image.fill(s.DARKGREY)
        self.rect = self.image.get_rect()
        self.x = self.pos.x
        self.y = self.pos.y
        self.rect = self.image.get_rect(
            midtop=(self.x * s.TILESIZE, self.y * s.TILESIZE)
        )
        self.buttons = self.draw_buttons()
        self.player_menu = PlayerMenu(
            surface=self.image,
            pos=Coords(x=8, y=1),
            size=Coords(x=6, y=6)
        )
        self.sel_buttons = self.player_menu.draw()
        self.draw_pixel_art()

    def scale_mouse(self, mpos):
        mpos = Coords(x=mpos[0], y=mpos[1])
        offset = Coords(x=self.rect.x, y=self.rect.y)
        return mpos - offset

    def click(self, mpos):
        action = None
        sel_action = None
        mpos = self.scale_mouse(mpos)
        for button in self.buttons:
            if button.rect.collidepoint(mpos):
                action = button.on_click()
        for button in self.sel_buttons:
            if button.rect.collidepoint(mpos):
                sel_action = self.player_menu.click(button)
        if sel_action:
            self.console.log(f'[INFO] {sel_action.color}: {sel_action.player}')
            self.config['player'][sel_action.color] = sel_action.player
        if action:
            return action

    def update(self):
        self.sel_buttons = self.player_menu.draw()
        mpos = self.scale_mouse(pg.mouse.get_pos())
        buttons = self.buttons + self.sel_buttons
        for button in buttons:
            if button.rect.collidepoint(mpos):
                button.hovering = True
            else:
                button.hovering = False
            button.update()

    def draw_buttons(self):
        size = Coords(x=6, y=6)
        return [
            Button(
                surface=self.image,
                pos=Coords(x=1, y=1),
                size=size,
                text='PLAY'
            ),
            Button(
                surface=self.image,
                pos=Coords(x=1, y=8),
                size=size,
                text='CONFIG'
            ),
            Button(
                surface=self.image,
                pos=Coords(x=8,y=8),
                size=size,
                text='CREDITS'
            ),
            Button(
                surface=self.image,
                pos=Coords(x=15, y=8),
                size=size,
                text='QUIT'
            )
        ]

    def draw_pixel_art(self):
        px = s.TILESIZE / 4
        pg.draw.rect(self.image, s.BLACK, (0, 0, px, px))
        pg.draw.rect(self.image, s.BLACK, (0, self.image.get_height() - px, px, px))
        pg.draw.rect(self.image, s.BLACK, (self.image.get_width() - px, self.image.get_height() - px, px, px))
        pg.draw.rect(self.image, s.BLACK, (self.image.get_width() - px, 0, px, px))

    def set_console(self, console):
        self.console = console
