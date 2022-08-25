"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/SiiiMiii> 
- All Rights Reserved. You may use, distribute and modify this code
under the terms of the GNU General Public License
"""
import pygame
from core.Engine import Board, Legal_move_generator, Game_manager, Clock, UI
from core import init_imgs, get_perft_result
from core.Engine.AI import Dfs, Evaluation
from time import perf_counter

from core.Engine.board_utility import Board_utility

FPS = 45

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 200, 255)
BLUE_DARK = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
TURQUOISE = (64, 224, 208)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (200, 200, 200)

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
IMGS = init_imgs(UNIT, WIDTH, HEIGHT, piece_style_western)
PIECES_IMGS, BOARD_IMG, BG_IMG = IMGS

WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("JOE MAMA")
pygame.display.set_icon(PIECES_IMGS[7])
pygame.font.init()
pygame.mixer.init()

MOVE_SFX = pygame.mixer.Sound("assets/sfx/move.wav")
CAPTURE_SFX = pygame.mixer.Sound("assets/sfx/capture.wav")


INITIAL_FEN_BLACK_DOWN = "RHEAKAEHR/9/1C5C/P1P1P1P1P/9/9/p1p1p1p1p/1c5c/9/rheakaehr"
INITIAL_FEN_RED_DOWN = "rheakaehr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RHEAKAEHR"

search = None
AI_SEARCH_DEPTH = 4

def get_num_positions(depth, board):
    p_t = perf_counter()
    num_positions = get_perft_result(depth, board)
    print(f"depth: {depth} || nodes searched: {num_positions} || time: {perf_counter() - p_t}")

def play_sfx(is_capture):
    if is_capture:
        CAPTURE_SFX.play()
    else:
        MOVE_SFX.play()
        
def human_event_handler(event, board, ui):
    global board_ui, selected_piece, selected_square, moved_to, previous_targets
    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = pygame.mouse.get_pos()

        # Account for the offsets the board's (0,0) coordinate is replaced by on the window
        mouse_pos_on_board = (mouse_pos[0] - OFFSET_X, mouse_pos[1] - OFFSET_Y)
        file, rank = Board_utility.get_board_pos(mouse_pos_on_board, UNIT)

        current_square = Board_utility.get_square(file, rank)
        ui.select_square(current_square)
                
    if event.type == pygame.MOUSEBUTTONUP:
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos_on_board = (mouse_pos[0] - OFFSET_X, mouse_pos[1] - OFFSET_Y)
        file, rank = Board_utility.get_board_pos(mouse_pos_on_board, UNIT)
        target_square = rank * 9 + file
        # Check whether move is legal
        
        is_capture = ui.drop_piece(target_square)
        if is_capture == -1:
            return
        # Sound effects
        play_sfx(is_capture)
        print(board.load_fen_from_board())
        board_ui = board.squares[:]
        selected_piece = None
        # Load moves for next player
        moves = Legal_move_generator.load_moves() 
        if not len(moves):
            if Legal_move_generator.checks:
                Game_manager.checkmate = True
                return
            Game_manager.stalemate = True

        # move = search.traverse_tree(AI_SEARCH_DEPTH)
        # is_capture = board.make_move(move)
        # board_ui = board.squares[:]
        # play_sfx(is_capture)
        # print(f"traversed nodes: {search.searched_nodes}")

        # Load moves for next player
        moves = Legal_move_generator.load_moves() 
        if not len(moves):
            if Legal_move_generator.checks:
                Game_manager.checkmate = True
                return
            Game_manager.stalemate = True

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            Game_manager.reset_game_state()
            board.reverse_move()
            moved_to, selected_square = None, None
            # This is just rudimentary, will make more efficient later
            Legal_move_generator.load_moves()

def main():
    global search
    only_display_mode = False
    play_as_red = True
    fen = INITIAL_FEN_RED_DOWN if play_as_red else INITIAL_FEN_BLACK_DOWN

    Clock.init(600, "MIKE", "OXLONG")
    # If you play as red, red pieces are gonna be at the bottom, else they're at the top
    board = Board(fen, play_as_red, red_moves_first=True)
    print(board.moving_color, board.opponent_color)
    if not only_display_mode:
        Legal_move_generator.init_board(board)
        Legal_move_generator.load_moves()
    ui = UI(WIN, (WIDTH, HEIGHT), board, (OFFSET_X, OFFSET_Y), UNIT, IMGS)
    # To run perft search
    # get_num_positions(4, board)
    Evaluation.init(board)
    search = Dfs(board)
    py_clock = pygame.time.Clock()
    run = True
    while run:
        if only_display_mode:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                human_event_handler(event, board, ui)
        Clock.run(board.moving_side)           
        ui.render()
        py_clock.tick(FPS)

if __name__ == "__main__":
    main()
