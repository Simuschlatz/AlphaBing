"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/Simuschlatz> 
- All Rights Reserved. You may use, distribute and modify this code
under the terms of the GNU General Public License
"""
import pygame
from core.Engine import Board,  Clock, UI, ZobristHashing
from core.Utils import init_imgs

FPS = 45
WIDTH = 1200
HEIGHT = 800
UNIT = HEIGHT // 11
BOARD_WIDTH = 9 * UNIT
BOARD_HEIGHT = 10 * UNIT
BUTTON_DIMS = (UNIT * 2.2, UNIT * .83)
OFFSET_X = (WIDTH - BOARD_WIDTH) // 2
OFFSET_Y = (HEIGHT - BOARD_HEIGHT) // 2

MOVE_MARKER_CIRCLE = UNIT / 7
CAPTURE_CIRCLE_D = UNIT * 1.1

# Style of piece images
piece_style_western = True

IMGS = init_imgs(UNIT, (WIDTH, HEIGHT), (BOARD_WIDTH, BOARD_HEIGHT), BUTTON_DIMS, piece_style_western)
# PIECES_IMGS, BOARD_IMG, BG_IMG, BUTTON_IMGS = IMGS

WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Display Mama")
# pygame.display.set_icon(PIECES_IMGS[7])
pygame.font.init()


INITIAL_FEN_BLACK_DOWN = "RHEAKAEHR/9/1C5C/P1P1P1P1P/9/9/p1p1p1p1p/1c5c/9/rheakaehr"
INITIAL_FEN_RED_DOWN = "rheakaehr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RHEAKAEHR"
    
def main():
    play_as_red = True
    fen = INITIAL_FEN_RED_DOWN if play_as_red else INITIAL_FEN_BLACK_DOWN
    Clock.init(600, "MIKE", "OXLONG")
    # If you play as red, red pieces are gonna be at the bottom, else they're at the top
    ZobristHashing.init_table()
    board = Board("4R/9/9/9/6R/9/9/4E/3K/9", play_as_red, red_moves_first=True)

    ui = UI(WIN, (WIDTH, HEIGHT), board, (OFFSET_X, OFFSET_Y), UNIT, IMGS)
    py_clock = pygame.time.Clock()
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        ui.render()
        py_clock.tick(FPS)

if __name__ == "__main__":
    main()
