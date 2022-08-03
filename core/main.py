import pygame
from Engine.board import Board
from Engine.piece import Piece
from Engine.move_generator import Legal_move_generator
from Engine.game_manager import Game_manager
from data_init import init_imgs
from Engine.timer import Timer
from Engine.AI.minimax import Dfs


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
BG_COLOR = (240, 210, 170)

UNIT = 80
WIDTH = 1500
HEIGHT = 1000
BOARD_WIDTH = 9 * UNIT
BOARD_HEIGHT = 10 * UNIT
FONT_SIZE = 40
CIRCLE_DIAMETER = 15

piece_style_western = True
PIECES_IMGS, BOARD_IMG, BG_IMG = init_imgs(UNIT, WIDTH, HEIGHT, piece_style_western)

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("JOE")
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

def move_feedback():
    if selected_square != None:
        l_file = selected_square % 9
        l_rank = selected_square // 9
        l_x = OFFSET_X + l_file * UNIT
        l_y = OFFSET_Y + l_rank * UNIT
        pygame.draw.ellipse(WIN, (217, 255, 255), (l_x + UNIT / 3, l_y + UNIT / 3, UNIT / 3, UNIT / 3))
    if moved_to != None:
        c_file = moved_to % 9
        c_rank = moved_to // 9
        c_x = OFFSET_X + c_file * UNIT
        c_y = OFFSET_Y + c_rank * UNIT
        pygame.draw.rect(WIN, (217, 255, 255), (c_x, c_y, UNIT, UNIT))

OFFSET_X = (WIDTH - BOARD_WIDTH) / 2
OFFSET_Y = (HEIGHT - BOARD_HEIGHT) / 2
selected_piece = None
moved_to = None
selected_square = None
previous_targets = {}

def draw_moves(board, target_indices):
    for index in target_indices:
        file = index % 9
        rank = index // 9
        x = OFFSET_X + file * UNIT
        y = OFFSET_Y + rank * UNIT
        # If piece on target, it must be opponent's,  otherwise it would've been removed
        if board.squares[index]:
            pygame.draw.ellipse(WIN, BLUE_DARK, (x - 4, y - 4, UNIT + 8, UNIT + 8))
        # Here, the -4 is just to correct for the unperfect aspect ratio of the board image
        pygame.draw.ellipse(WIN, BLUE_DARK, (x + UNIT / 2 - 4, y + UNIT / 2 - 4, CIRCLE_DIAMETER, CIRCLE_DIAMETER))

def render_text(text: str, pos: tuple):
    surface = DISPLAY_FONT.render(text, False, (130, 130, 130))
    WIN.blit(surface, pos)

def draw(board, remainig_times):

    # WIN.fill(BG_COLOR)
    WIN.blit(BG_IMG, (0, 0))
    WIN.blit(BOARD_IMG, (OFFSET_X + UNIT / 2, OFFSET_Y + UNIT / 2))
    move_feedback()

    if Game_manager.checkmate:
        render_text("CHECKMATE!", (OFFSET_X + UNIT * 9.5, HEIGHT / 2 - FONT_SIZE / 2))
    elif Game_manager.stalemate:
        render_text("STALEMATE!", (OFFSET_X + UNIT * 9.5, HEIGHT / 2 - FONT_SIZE / 2))
    else:
        # Drawing reamining time
        render_text(remainig_times[0], (OFFSET_X + UNIT * 9.5, HEIGHT / 2 - FONT_SIZE))
        render_text(remainig_times[1], (OFFSET_X + UNIT * 9.5, HEIGHT / 2))

    # Drawing the moves before displaying the pieces so that a big circle (indicating capture)
    # won't cover but outline the pieces
    if selected_piece:
        draw_moves(board, Legal_move_generator.target_squares[selected_square])

    # Drawing pieces
    for i, piece in enumerate(board_ui):
        if piece:
            file = i % 9
            rank = i // 9
            is_red = Piece.is_color(piece, Piece.red)
            piece_type = Piece.get_type(piece)
            WIN.blit(PIECES_IMGS[is_red * 7 + Piece.get_type(piece)], (OFFSET_X + file * UNIT, OFFSET_Y + rank * UNIT))
    
    # Human selected a piece
    if selected_piece:
        # Dragging the selected piece
        mouse_pos = pygame.mouse.get_pos()
        is_red = Piece.is_color(selected_piece, Piece.red)
        piece_type = Piece.get_type(selected_piece)
        WIN.blit(PIECES_IMGS[is_red * 7 + piece_type], (mouse_pos[0] - (UNIT // 2), (mouse_pos[1] - UNIT // 2)))
    
    pygame.display.update()

def play_sfx(is_capture):
    if is_capture:
        CAPTURE_SFX.play()
    else:
        MOVE_SFX.play()
        
def human_event_handler(event, board):
    global board_ui, selected_piece, selected_square, moved_to, previous_targets
    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = pygame.mouse.get_pos()

        # Account for the offsets the board's (0,0) coordinate is replaced by on the window
        mouse_pos_on_board = (mouse_pos[0] - OFFSET_X, mouse_pos[1] - OFFSET_Y)
        file, rank = Board.get_board_pos(mouse_pos_on_board, UNIT)

        current_square = rank * 9 + file
        # Check if selected square is not empty
        if board.squares[current_square]:
            
            # If not a friendly color or no moves possible return
            if current_square not in Legal_move_generator.target_squares:
                return
            selected_square = rank * 9 + file
            selected_piece = board.squares[selected_square]
            board_ui[selected_square] = 0
            # Reset previous target square
            if moved_to:
                moved_to = None
                
    if event.type == pygame.MOUSEBUTTONUP and selected_piece:
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos_on_board = (mouse_pos[0] - OFFSET_X, mouse_pos[1] - OFFSET_Y)
        file, rank = Board.get_board_pos(mouse_pos_on_board, UNIT)
        target_square = rank * 9 + file
        # Check whether move is legal
        if target_square not in Legal_move_generator.target_squares[selected_square]:
            board_ui[selected_square] = selected_piece
            selected_square = None
            selected_piece = None
            return


        moved_to = target_square
        move = (selected_square, target_square)

        print("move: ", board.get_move_notation(move))
        is_capture = board.make_move(move)
        # Sound effects
        play_sfx(is_capture)
        print(board.load_fen_from_board())
        board_ui = board.squares[:]
        selected_piece = None
        
        move = search.traverse_tree(3)
        is_capture = board.make_move(move)
        board_ui = board.squares[:]
        play_sfx(is_capture)

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
    play_as_red = True
    fen = INITIAL_FEN_RED_DOWN if play_as_red else INITIAL_FEN_BLACK_DOWN

    clock = Timer(600, "Papa", "Mama")
    # If you play as red, red pieces are gonna be at the bottom, else they're at the top
    board = Board(fen, play_as_red)
    Legal_move_generator.init_board(board)
    Legal_move_generator.load_moves()
    py_clock = pygame.time.Clock()
    search = Dfs(board)
    run = True
    board_ui = board.squares[:]

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            human_event_handler(event, board)
        clock.run(board.moving_side)
        rendered_text = [f"{clock.r_min_tens[0]}{clock.r_min_ones[0]}:{clock.r_sec_tens[0]}{clock.r_sec_ones[0]}",
                        f"{clock.r_min_tens[1]}{clock.r_min_ones[1]}:{clock.r_sec_tens[1]}{clock.r_sec_ones[1]}"]            
        draw(board, rendered_text)
        py_clock.tick(FPS)
        # r stands for remaining

if __name__ == "__main__":
    main()
