import math
import random
import time
import pygame
from board import Board
from move_generator import Legal_move_generator
from data_init import init_imgs
from timer import Timer


RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 200, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
TURQUOISE = (64, 224, 208)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (200, 200, 200)
BG = (240, 210, 170)

UNIT = 80
WIDTH = 1500
HEIGHT = 1000
BOARD_WIDTH = 9 * UNIT
BOARD_HEIGHT = 10 * UNIT
FONT_SIZE = 50
CIRCLE_DIAMETER = 15

PIECES_IMGS, BOARD_IMG = init_imgs(UNIT, True)

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MOIN")
pygame.display.set_icon(PIECES_IMGS[1])
pygame.font.init()
pygame.mixer.init()

MOVE_SFX = pygame.mixer.Sound("assets/sfx/move.wav")
CAPTURE_SFX = pygame.mixer.Sound("assets/sfx/capture.wav")

DISPLAY_FONT = pygame.font.Font("freesansbold.ttf", FONT_SIZE)

INITIAL_FEN = "RHEAKAEHR/9/1C5C/P1P1P1P1P/9/9/p1p1p1p1p/1c5c/9/rheakaehr"

# This board is created solely for UI purposes, so that the visual board can be modified
# without crating interdependencies with the inner board representation
board_ui = None

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
        # If piece on target, it must be opponent's, otherwise it would've been removed
        if board.squares[index]:
            pygame.draw.ellipse(WIN, RED, (x - 4, y - 4, UNIT + 8, UNIT + 8))
        # Here, the -4 is just to correct for the unperfect aspect ratio of the board image
        pygame.draw.ellipse(WIN, RED, (x + UNIT / 2 - 4, y + UNIT / 2 - 4, CIRCLE_DIAMETER, CIRCLE_DIAMETER))

def draw(board, legal_target_squares, remainig_times):
    WIN.fill(BG)
    WIN.blit(BOARD_IMG, (OFFSET_X + UNIT / 2, OFFSET_Y + UNIT / 2))
    move_feedback()

    # Drawing reamining time
    WIN.blit(remainig_times[0], (OFFSET_X + UNIT * 9.5, HEIGHT / 2))
    WIN.blit(remainig_times[1], (OFFSET_X + UNIT * 9.5, HEIGHT / 2 - FONT_SIZE))

    # Check if there's selected piece
    # (not cheking if selected_square as it isn't reset before new moves are generated)
    if selected_piece:
        draw_moves(board, legal_target_squares[selected_square])
    
    # Drawing pieces
    for i, piece in enumerate(board_ui):
        if piece:
            file = i % 9
            rank = i // 9
            WIN.blit(PIECES_IMGS[piece[0] * 7 + piece[1]], (OFFSET_X + file * UNIT, OFFSET_Y + rank * UNIT))
    
    #Dragging the selected piece
    if selected_piece:
        mouse_pos = pygame.mouse.get_pos()
        WIN.blit(PIECES_IMGS[selected_piece[0] * 7 + selected_piece[1]], (mouse_pos[0] - (UNIT // 2), (mouse_pos[1] - UNIT // 2)))
    
    pygame.display.update()

def play_sfx(audiofile):
    audiofile.play()

def human_event_handler(event, board, m_g):
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
            if not board.is_friendly_square(current_square) or current_square not in m_g.target_squares:
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
        if target_square not in m_g.target_squares[selected_square]:
            board_ui[selected_square] = selected_piece
            selected_square = None
            selected_piece = None
            return

        # Sound effects
        if board.squares[target_square]:
            play_sfx(CAPTURE_SFX)
        else:
            play_sfx(MOVE_SFX)

        moved_to = target_square

        board.make_move(selected_square, target_square)
        board_ui = board.squares[:]
        selected_piece = None
        board.switch_player_to_move()

        previous_targets = m_g.target_squares
        # Load moves for next player
        m_g.load_moves()
        if not len(m_g.moves):
            print("CHECKMATE!")
            return
        board.make_move(*m_g.moves[math.floor(random.random() * len(m_g.moves))])
        board_ui = board.squares[:]
        board.switch_player_to_move()
        m_g.load_moves()

    if event.type == pygame.KEYDOWN and not selected_piece and moved_to:
        if event.key == pygame.K_SPACE and previous_targets:
            board.reverse_move()
            board_ui = board.squares[:]
            board.switch_player_to_move()
            m_g.target_squares = previous_targets
            moved_to, selected_square = None, None

def main():
    global board_ui
    game = Timer(600, "Papa", "Mama")
    board = Board(INITIAL_FEN, 1)
    board_ui = board.squares[:]
    m_g = Legal_move_generator(board)
    m_g.load_moves()
    clock = pygame.time.Clock()
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            human_event_handler(event, board, m_g)
        game.run(board.color_to_move)
        rendered_text = [DISPLAY_FONT.render(f"{game.r_min_tens[0]}{game.r_min_ones[0]}:{game.r_sec_tens[0]}{game.r_sec_ones[0]}", False, (130, 130, 130)),
                        DISPLAY_FONT.render(f"{game.r_min_tens[1]}{game.r_min_ones[1]}:{game.r_sec_tens[1]}{game.r_sec_ones[1]}", False, (130, 130, 130))]
        draw(board, m_g.target_squares, rendered_text)
        clock.tick(60)
        # r stands for remaining

if __name__ == "__main__":
    main()