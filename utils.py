import pygame as pg

import settings as s


def draw_text(surf, text, size, pos, color=s.GREEN):
    font = pg.font.Font(s.FONT_PATH, size)
    font.set_bold(2)
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect()
    text_rect.topleft = (pos.x, pos.y)
    surf.blit(text_surf, text_rect)
