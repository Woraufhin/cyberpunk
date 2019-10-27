from dataclasses import dataclass, field

import chess.settings as s
from chess.panels.panel import Panel


@dataclass(eq=False)
class Backdrop(Panel):
    color: tuple = s.BLACK
    alpha: int = 150

    def __post_init__(self):
        super().__post_init__()
