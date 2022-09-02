"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/SiiiMiii> 
- All Rights Reserved. You may use, distribute and modify this code
under the terms of the GNU General Public License
"""
import pygame
from core.Engine import Board, Legal_move_generator, Clock, UI, Zobrist_hashing
from core.Engine.AI import Dfs, Evaluation
from core import init_imgs, get_perft_result
from time import perf_counter

FPS = 45
UNIT = 80
WIDTH = 1400
HEIGHT = 900
BOARD_WIDTH = 9 * UNIT
BOARD_HEIGHT = 10 * UNIT
OFFSET_X = (WIDTH - BOARD_WIDTH) / 2
OFFSET_Y = (HEIGHT - BOARD_HEIGHT) / 2

MOVE_MARKER_CIRCLE = UNIT / 7
CAPTURE_CIRCLE_D = UNIT * 1.1

piece_style_western = True
IMGS = init_imgs(UNIT, WIDTH, HEIGHT, BOARD_WIDTH, BOARD_HEIGHT, piece_style_western)
PIECES_IMGS, BOARD_IMG, BG_IMG = IMGS

WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("JOE MAMA")
pygame.display.set_icon(PIECES_IMGS[7])
pygame.font.init()


INITIAL_FEN_BLACK_DOWN = "RHEAKAEHR/9/1C5C/P1P1P1P1P/9/9/p1p1p1p1p/1c5c/9/rheakaehr"
INITIAL_FEN_RED_DOWN = "rheakaehr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RHEAKAEHR"

search = None
AI_SEARCH_DEPTH = 4

def get_num_positions(depth, board):
    p_t = perf_counter()
    num_positions = get_perft_result(depth, board)
    print(f"depth: {depth} || nodes searched: {num_positions} || time: {perf_counter() - p_t}")

    
def main():
    only_display_mode = False
    play_as_red = True
    fen = INITIAL_FEN_RED_DOWN if play_as_red else INITIAL_FEN_BLACK_DOWN

    Clock.init(600, "MIKE", "OXLONG")
    # If you play as red, red pieces are gonna be at the bottom, else they're at the top
    board = Board(fen, play_as_red, red_moves_first=False)
    if not only_display_mode:
        Legal_move_generator.init_board(board)
        Legal_move_generator.load_moves()

    Zobrist_hashing.init_table()
    Evaluation.init(board)
    Dfs.init(board)

    ui = UI(WIN, (WIDTH, HEIGHT), board, (OFFSET_X, OFFSET_Y), UNIT, IMGS)
    # To run perft search
    get_num_positions(4, board)

    py_clock = pygame.time.Clock()
    run = True
    while run:
        if only_display_mode:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
        else:
            ui.event_handler()
            
        Clock.run(board.moving_side)           
        ui.render()
        py_clock.tick(FPS)

if __name__ == "__main__":
    main()
