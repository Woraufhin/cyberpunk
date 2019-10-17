import logging
from pathlib import Path
from dataclasses import dataclass, field, replace
from typing import Dict

import pygame as pg

import chess.settings as s
from chess.panels.panel import Panel
from chess.utils.typewriter import Typewriter, TypewriterConfig, LogType


logger = logging.getLogger(Path(__file__).stem)


@dataclass(eq=False)
class Console(Panel):

    title: str = 'CONSOLE'
    history: list = field(default_factory=list)
    config: 'TypewriterConfig' = TypewriterConfig(
        surface_color=s.BLACK,
        padding=5
    )
    level_configs: Dict['LogType', 'TypewriterConfig'] = field(default_factory=dict)
    margin: int = 12
    frame_offset: int = s.TILESIZE * 2

    def __post_init__(self):
        super().__post_init__()
        self.console = self.draw_frame()
        self.level_configs = self.get_level_configs()
        self.tp = Typewriter(
            surface=self.console,
            config=self.config
        )

    def draw_frame(self):
        subsurface = pg.Rect(
            self.margin,
            self.frame_offset,
            self.image.get_width() - self.margin * 2,
            self.image.get_height() - self.margin - self.frame_offset
        )
        frame = self.image.subsurface(subsurface)
        frame.fill(s.BLACK)
        return frame

    def get_level_configs(self):
        return {
            LogType.INFO: replace(self.config, color=s.GREEN),
            LogType.WARNING: replace(self.config, color=s.YELLOW),
            LogType.ERROR: replace(self.config, color=s.RED),
            LogType.DEBUG: replace(self.config, color=s.LIGHTBLUE),
            LogType.CUSTOM: self.config
        }

    def log(self, text, level=LogType.INFO):
        self.history.append((level, text))
        self.tp.log(self.history, configs=self.level_configs)

    def type(self, text):
        self.tp.log(
            text=[(LogType.CUSTOM, text)],
            top_down=True,
            configs=self.level_configs
        )
