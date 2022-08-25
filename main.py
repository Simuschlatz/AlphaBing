"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/SiiiMiii> 
- All Rights Reserved. You may use, distribute and modify this code
under the terms of the GNU General Public License
"""
import pygame
from core.Engine import Board, Piece, Legal_move_generator, Game_manager, Timer, UI
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
BG_COLOR = (100, 100, 100)

UNIT = 80
WIDTH = 1400
HEIGHT = 900
BOARD_WIDTH = 9 * UNIT
BOARD_HEIGHT = 10 * UNIT
OFFSET_X = (WIDTH - BOARD_WIDTH) / 2
OFFSET_Y = (HEIGHT - BOARD_HEIGHT) / 2
FONT_SIZE = 40
MOVE_MARKER_CIRCLE = UNIT / 7
CAPTURE_CIRCLE_D = UNIT * 1.1

piece_style_western = True
PIECES_IMGS, BOARD_IMG, BG_IMG = init_imgs(UNIT, WIDTH, HEIGHT, piece_style_western)

WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("JOE MAMA")
pygame.display.set_icon(PIECES_IMGS[7])
pygame.font.init()
pygame.mixer.init()

MOVE_SFX = pygame.mixer.Sound("assets/sfx/move.wav")
CAPTURE_SFX = pygame.mixer.Sound("assets/sfx/capture.wav")

DISPLAY_FONT = pygame.font.Font("freesansbold.ttf", FONT_SIZE)

INITIAL_FEN_BLACK_DOWN = "RHEAKAEHR/9/1C5C/P1P1P1P1P/9/9/p1p1p1p1p/1c5c/9/rheakaehr"
INITIAL_FEN_RED_DOWN = "rheakaehr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RHEAKAEHR"

# This board is created solely for UI purposes, so that the visual board can be modified
# without crating interdependencies with the inner board representation
board_ui = None

search = None
AI_SEARCH_DEPTH = 4

def get_num_positions(depth, board):
    p_t = perf_counter()
    num_positions = get_perft_result(depth, board)
    print(f"depth: {depth} || nodes searched: {num_positions} || time: {perf_counter() - p_t}")

def move_feedback():
    if selected_square != None:
        l_file = selected_square % 9
        l_rank = selected_square // 9
        l_x = OFFSET_X + (l_file + .5) * UNIT
        l_y = OFFSET_Y + (l_rank + .5) * UNIT
        # Small circle diameter
        scd = UNIT / 3
        pygame.draw.ellipse(WIN, (217, 255, 255), (l_x - scd / 2, l_y - scd / 2, scd, scd))
    if moved_to != None:
        c_file = moved_to % 9
        c_rank = moved_to // 9
        c_x = OFFSET_X + c_file * UNIT
        c_y = OFFSET_Y + c_rank * UNIT
        # Big circle diameter 
        bcd = UNIT * 1.1
        pygame.draw.ellipse(WIN, (217, 255, 255), (c_x - UNIT * 0.05, c_y - UNIT * 0.05, bcd, bcd))

selected_piece = None
moved_to = None
selected_square = None

def render_text(text: str, pos: tuple):
    surface = DISPLAY_FONT.render(text, False, (130, 130, 130))
    WIN.blit(surface, pos)

def draw(board, remainig_times, ui):

    WIN.fill(BG_COLOR)
    # WIN.blit(BG_IMG, (0, 0))
    WIN.blit(BOARD_IMG, (OFFSET_X, OFFSET_Y))
    ui.move_responsiveness()

    if Game_manager.checkmate:
        render_text("checkmate!", (OFFSET_X + UNIT * 9.5, HEIGHT / 2 - FONT_SIZE / 2))
    elif Game_manager.stalemate:
        render_text("stalemate!", (OFFSET_X + UNIT * 9.5, HEIGHT / 2 - FONT_SIZE / 2))
    else:
        # Drawing reamining time
        render_text(remainig_times[0], (OFFSET_X + UNIT * 9.5, HEIGHT / 2 - FONT_SIZE))
        render_text(remainig_times[1], (OFFSET_X + UNIT * 9.5, HEIGHT / 2))

    # Drawing the moves before displaying the pieces so that a big circle (indicating capture)
    # won't cover but outline the pieces
    if selected_piece:
        ui.mark_moves(board)

    # Drawing pieces
    for square, piece in enumerate(board_ui):
        if piece:
            file, rank = Board_utility.get_file_and_rank(square)
            is_red = Piece.is_color(piece, Piece.red)
            piece_type = Piece.get_type(piece)
            WIN.blit(PIECES_IMGS[is_red * 7 + Piece.get_type(piece)], (OFFSET_X + file * UNIT, OFFSET_Y + rank * UNIT))
    
    # Human selected a piece
    if ui.selected_piece:
        # Dragging the selected piece
        mouse_pos = pygame.mouse.get_pos()
        is_red = Piece.is_color(ui.selected_piece, Piece.red)
        piece_type = Piece.get_type(ui.selected_piece)
        WIN.blit(PIECES_IMGS[is_red * 7 + piece_type], (mouse_pos[0] - (UNIT // 2), (mouse_pos[1] - UNIT // 2)))
    
    pygame.display.update()

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
            board_ui = board.squares[:]
            moved_to, selected_square = None, None
            # This is just rudimentary, will make more efficient later
            Legal_move_generator.load_moves()

def main():
    global board_ui, search
    only_display_mode = False
    play_as_red = True
    fen = INITIAL_FEN_RED_DOWN if play_as_red else INITIAL_FEN_BLACK_DOWN

    clock = Timer(600, "Papa", "Mama")
    # If you play as red, red pieces are gonna be at the bottom, else they're at the top
    board = Board(fen, play_as_red, red_moves_first=True)
    print(board.moving_color, board.opponent_color)
    if not only_display_mode:
        Legal_move_generator.init_board(board)
        Legal_move_generator.load_moves()
    ui = UI(WIN, board, (OFFSET_X, OFFSET_Y), UNIT)
    # To run perft search
    # get_num_positions(4, board)
    Evaluation.init(board)
    search = Dfs(board)
    py_clock = pygame.time.Clock()
    run = True
    board_ui = board.squares[:]
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
        clock.run(board.moving_side)
        rendered_text = [f"{clock.r_min_tens[0]}{clock.r_min_ones[0]}:{clock.r_sec_tens[0]}{clock.r_sec_ones[0]}",
                        f"{clock.r_min_tens[1]}{clock.r_min_ones[1]}:{clock.r_sec_tens[1]}{clock.r_sec_ones[1]}"]            
        draw(board, rendered_text, ui)
        py_clock.tick(FPS)
        # r stands for remaining

if __name__ == "__main__":
    main()
