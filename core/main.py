import pygame
import os
from board import Board
from move_generator import Move_generator
from game import Game

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 200, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
TURQUOISE = (64, 224, 208)
PURPLE = (128, 0, 128)
PINK = (250, 0, 250)
BLACK = (0, 0, 0)
DARK_BLUE = (0, 0, 70)
WHITE = (255, 255, 255)
GREY = (200, 200, 200)

WIDTH = 1200
HEIGHT = 1000
FONT_SIZE = 50
CIRCLE_DIAMETER = 15

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Xiangqi")

pygame.font.init()
DISPLAY_FONT = pygame.font.Font("freesansbold.ttf", FONT_SIZE)

# sys.path.append("/Xiangqi/assets")
_pieces_img = pygame.image.load(os.path.join("assets/imgs", "high_res (1).png"))
pieces_img = [_pieces_img.subsurface(j * 77, i * 77, 75, 72) for i in range(2) for j in range(7)]
board_img = pygame.image.load(os.path.join("assets", "clean_board.png"))
pygame.display.set_icon(pieces_img[0])

INITIAL_FEN = "rheakaehr/9/1c5c/p1p1p1p1p/9/9/P1P1P1P1P/1C5C/9/RHEAKAEHR"

def move_feedback(board):
    if selected_square != None:
        l_file = selected_square % 9
        l_rank = selected_square // 9
        l_x = OFFSET_X + l_file * board.UNIT
        l_y = OFFSET_Y + l_rank * board.UNIT
        pygame.draw.ellipse(WIN, (220, 200, 140), (l_x + board.UNIT / 3, l_y + board.UNIT / 3, board.UNIT / 3, board.UNIT / 3))
    if moved_to != None:
        c_file = moved_to % 9
        c_rank = moved_to // 9
        c_x = OFFSET_X + c_file * board.UNIT
        c_y = OFFSET_Y + c_rank * board.UNIT
        pygame.draw.rect(WIN, (220, 200, 140), (c_x, c_y, board.UNIT, board.UNIT))

OFFSET_X = (WIDTH - Board.WIDTH) / 2
OFFSET_Y = (HEIGHT - Board.HEIGHT) / 2
selected_piece = None
moved_to = None
selected_square = None
start_squares = set()
target_squares = set()

def draw_moves(board, target_indices):
    for index in target_indices:
        file = index % 9
        rank = index // 9
        x = OFFSET_X + (file + 0.5) * board.UNIT - CIRCLE_DIAMETER / 2
        y = OFFSET_Y + (rank + 0.5) * board.UNIT - CIRCLE_DIAMETER / 2
        pygame.draw.ellipse(WIN, (0, 0, 250), (x, y, CIRCLE_DIAMETER, CIRCLE_DIAMETER))

def draw(board, legal_target_squares, remainig_times):
    WIN.fill((209, 188, 140))
    WIN.blit(board_img, (OFFSET_X, OFFSET_Y))
    move_feedback(board)

    # Drawing reamining time
    WIN.blit(remainig_times[0], (1000, HEIGHT / 2))
    WIN.blit(remainig_times[1], (1000, HEIGHT / 2 - FONT_SIZE))

    # Check if there's selected piece
    # (not cheking if selected_square as it isn't reset before new moves are generated)
    if selected_piece:
        draw_moves(board, legal_target_squares[selected_square])
    
    # Drawing pieces
    for i, piece in enumerate(board.squares):
        if piece:
            file = i % 9
            rank = i // 9
            WIN.blit(pieces_img[piece[0] * 7 + piece[1]], (OFFSET_X + file * board.UNIT, OFFSET_Y + rank * board.UNIT))
    
    #Dragging the selected piece
    if selected_piece:
        mouse_pos = pygame.mouse.get_pos()
        WIN.blit(pieces_img[selected_piece[0] * 7 + selected_piece[1]], (mouse_pos[0] - (board.UNIT // 2), (mouse_pos[1] - board.UNIT // 2)))
    
    pygame.display.update()

def human_event_handler(event, board, game, m_g):
    global selected_piece, selected_square, moved_to
    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = pygame.mouse.get_pos()

        # Account for the offsets the board's (0,0) coordinate is replaced by on the window
        mouse_pos_on_board = (mouse_pos[0] - OFFSET_X, mouse_pos[1] - OFFSET_Y)
        file, rank = Board.get_board_pos(mouse_pos_on_board, board.UNIT)

        # Check if selected square is not empty
        if board.squares[rank * 9 + file]:
            # If not a friendly color return
            if rank * 9 + file not in board.piece_square[game.color_to_move]:
                return
            selected_square = rank * 9 + file
            selected_piece = board.squares[selected_square]
            board.squares[selected_square] = 0
            # Reset previous target square
            if moved_to:
                moved_to = None
                
    if event.type == pygame.MOUSEBUTTONUP and selected_piece:
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos_on_board = (mouse_pos[0] - OFFSET_X, mouse_pos[1] - OFFSET_Y)
        file, rank = Board.get_board_pos(mouse_pos_on_board, board.UNIT)
        target_square = rank * 9 + file
        # Check whether move is legal
        if target_square not in m_g.target_squares[selected_square]:
            board.squares[selected_square] = selected_piece
            selected_piece = None
            return
        moved_to = target_square
        board.make_move(selected_square, target_square, game.color_to_move, is_human_move=True, piece=selected_piece)
        game.switch_player_to_move()
        # Load moves for next player
        m_g.load_moves(game.color_to_move)
        selected_piece= None

def main():
    board = Board(INITIAL_FEN)
    game = Game(True, 610, "Papa", "Mama")
    m_g = Move_generator(board)
    m_g.load_moves(game.color_to_move)
    run = True
    while run:
        game.run()
        rendered_text = [DISPLAY_FONT.render(f"{game.r_min_tens[0]}{game.r_min_ones[0]}:{game.r_sec_tens[0]}{game.r_sec_ones[0]}", False, (130, 130, 130)),
                        DISPLAY_FONT.render(f"{game.r_min_tens[1]}{game.r_min_ones[1]}:{game.r_sec_tens[1]}{game.r_sec_ones[1]}", False, (130, 130, 130))]
        draw(board, m_g.target_squares, rendered_text)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            human_event_handler(event, board, game, m_g)
        # r stands for remaining


if __name__ == "__main__":
    main()