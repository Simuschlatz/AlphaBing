"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/Simuschlatz> - All Rights Reserved. 
You may use, distribute and modify this code under the terms of the GNU General Public License
"""
import pygame
from core.Engine import Board, LegalMoveGenerator, Clock, UI, ZobristHashing
from core.Engine.AI import Dfs, Evaluation
from core.Utils import get_perft_result
from time import perf_counter



FPS = 45

pygame.display.set_caption("JOE MAMA")
# pygame.display.set_icon(PIECES_IMGS[7])
pygame.font.init()


INITIAL_FEN_BLACK_DOWN = "RHEAKAEHR/9/1C5C/P1P1P1P1P/9/9/p1p1p1p1p/1c5c/9/rheakaehr"
INITIAL_FEN_RED_DOWN = "rheakaehr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RHEAKAEHR"

def get_num_positions(depth, board):
    p_t = perf_counter()
    num_positions = get_perft_result(depth, board)
    time = perf_counter() - p_t
    print(f"depth: {depth} || nodes searched: {num_positions} || time: {round(time, 2)}")

    
def main():
    play_as_red = True
    red_moves_first = True
    fen = INITIAL_FEN_RED_DOWN if play_as_red else INITIAL_FEN_BLACK_DOWN 
    fen += (" w " if red_moves_first else " b ") + "- - 0 1"
    Clock.init(300, "MIKE", "OXLONG")
    # If you play as red, red pieces are gonna be at the bottom, else they're at the top
    ZobristHashing.init_table()
    board = Board(fen, play_as_red)

    LegalMoveGenerator.init_board(board)
    LegalMoveGenerator.load_moves()

    Evaluation.init(board)
    Dfs.init(board)

    ui = UI(board)

    # ------To run perft search------
    # iterative = False
    # depth = 4
    # depths = [depth]
    # if iterative:
    #     depths = range(1, depth + 1)
    # for d in depths:
    #     get_num_positions(d, board)
    # -------------------------------

    py_clock = pygame.time.Clock()
    run = True
    while run:   
        ui.update()
        py_clock.tick(FPS)

if __name__ == "__main__":
    main()
