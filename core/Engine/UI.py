"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/Simuschlatz> - All Rights Reserved. 
You may use, distribute and modify this code under the terms of the GNU General Public License
"""
import pygame
from core.Engine import Piece, LegalMoveGenerator, GameManager, Clock, GameManager, Board
from core.Engine.AI import AIPlayer, TrainingDataCollector
from core.Utils import init_imgs, BoardUtility

class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.top_left = (x, y)
        self.rect.topleft = self.top_left

    def render(self, window):
        window.blit(self.image, (self.rect.x, self.rect.y))

    def check_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            return True
        return False

    def change_image(self, new_image):
        self.image = new_image
        self.rect = self.image.get_rect()
        self.rect.topleft = self.top_left


class UI:
    BG_COLOR = (100, 100, 100)
    RED = (190, 63, 64)
    BLUE = (26, 57, 185)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREY = (40, 40, 40)
    MOVE_RESPONSE_COLOR = (217, 255, 255)
    MOVE_HIGHLIGHT_COLORS = ((100, 100, 240), RED)

    WIDTH = 1200
    HEIGHT = 800
    UNIT = HEIGHT // 11
    BOARD_WIDTH = 9 * UNIT
    BOARD_HEIGHT = 10 * UNIT
    BUTTON_DIMS = (UNIT * 2.2, UNIT * .83)
    OFFSET_X = (WIDTH - BOARD_WIDTH) // 2
    OFFSET_Y = (HEIGHT - BOARD_HEIGHT) // 2
    OFFSETS = (OFFSET_X, OFFSET_Y)

    # Style of piece images
    piece_style_western = True
    pygame.mixer.init()
    IMGS = init_imgs(UNIT, (WIDTH, HEIGHT), (BOARD_WIDTH, BOARD_HEIGHT), BUTTON_DIMS, piece_style_western)
    # SFX
    MOVE_SFX = pygame.mixer.Sound("assets/sfx/move.wav")
    CAPTURE_SFX = pygame.mixer.Sound("assets/sfx/capture.wav")
    # Font stuff
    FONT_SIZE_LARGE = UNIT // 2
    FONT_SIZE_SMALL = UNIT // 3
    FONT_WIDTH_SMALL = FONT_SIZE_SMALL * 0.55

    def __init__(self, board:Board):
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
        self.board = board
        # This board is created solely for UI purposes, so that the visual board can be modified
        # without crating interdependencies with the internal board representation
        self.ui_board = board.squares[:]


        self.LARGE_FONT = pygame.font.Font("freesansbold.ttf", self.FONT_SIZE_LARGE)
        self.SMALL_FONT = pygame.font.Font("freesansbold.ttf", self.FONT_SIZE_SMALL)
        self.TIMER_TEXT_X, self.TIMER_TEXT_Y = self.OFFSET_X + self.UNIT * 9.5, [self.HEIGHT / 2 - (1 - side) * self.FONT_SIZE_LARGE for side in range(2)]
        self.MOVE_STR_POS = (self.WIDTH // 20, self.WIDTH // 20)
        
        # Circle diameters to mark moves and captures
        self.BIG_CIRCLE_D = self.UNIT * 1.1
        self.SMALL_CIRCLE_D = self.UNIT // 6

        # All the images
        self.PIECES_IMGS, self.BOARD_IMG, self.BG_IMG, self.BTN_ACTIVATE_IMG, self.BTN_DEACTIVATE_IMG = self.IMGS 

        # Move logics
        self.move_from = None
        self.selected_piece = None
        self.move_to = None
        self.legal_targets = []

        # Activate AI option
        self.AI_BUTTON_HEIGHT = self.BTN_ACTIVATE_IMG.get_height()
        self.AI_BUTTON = Button(20, self.HEIGHT // 2 - self.AI_BUTTON_HEIGHT // 2, self.BTN_ACTIVATE_IMG)
        self.activate_ai = False

        self.ai_vs_ai = False

        # Analytics
        self.fen = board.load_fen_from_board()
        self.zobrist_off = (self.WIDTH - len(bin(self.board.zobrist_key)) * self.FONT_WIDTH_SMALL) / 2
        self.move_str = ""

        # Data collector for Self-Learning-Evaluation-Function (SLEF)
        self.training_data_generator = TrainingDataCollector(board)

    def render_piece(self, color, piece_type, coords):
        self.window.blit(self.PIECES_IMGS[color * 7 + piece_type], coords)
    
    def render_pieces(self):
        for square, piece in enumerate(self.ui_board):
            if not piece:
                continue
            file, rank = self.board.get_file_and_rank(square)
            pos = BoardUtility.get_display_coords(file, rank, self.UNIT, *self.OFFSETS)
            color, piece_type = piece
            self.render_piece(color, piece_type, pos)

    def get_circle_center(self, rect_coord, diameter, factor=1):
        """
        centers a rectangle coordinate to the circle center
        :param factor: -1 or 1 => subtract or add half of diameter
        """
        return [pos + factor * diameter // 2 for pos in rect_coord]

    def render_circle(self, upper_left_corner_pos, diameter, color):
        centered_coords = self.get_circle_center(upper_left_corner_pos, self.UNIT)
        x, y = (pos - diameter // 2 for pos in centered_coords)
        pygame.draw.ellipse(self.window, color, (x, y, diameter, diameter))
    
    def highlight_move(self, square, color, large: bool):
        file, rank = self.board.get_file_and_rank(square)
        coordinates = BoardUtility.get_display_coords(file, rank, self.UNIT, *self.OFFSETS)
        d = self.BIG_CIRCLE_D if large else self.SMALL_CIRCLE_D
        self.render_circle(coordinates, d, color)

    def render_text(self, text: str, color: tuple, pos: tuple, large_font):
        if large_font:
            surface = self.LARGE_FONT.render(text, False, color)
        else:
            surface = self.SMALL_FONT.render(text, False, color)
        self.window.blit(surface, pos)

    def render_remaining_time(self, player):
        rendered_text = Clock.ftime[player]
        self.render_text(rendered_text, self.BLACK, (self.TIMER_TEXT_X, self.TIMER_TEXT_Y[player]), True)
    
    def render_game_state(self):
        if GameManager.checkmate:
            self.render_text("checkmate!", self.GREY, (self.TIMER_TEXT_X, self.HEIGHT // 2 - self.FONT_SIZE_LARGE // 2), True)
        elif GameManager.stalemate:
            self.render_text("stalemate!", self.GREY, (self.TIMER_TEXT_X, self.HEIGHT // 2 - self.FONT_SIZE_LARGE // 2), True)
        else:
            for player in range(2):
                self.render_remaining_time(player)

    def render_move_str(self):
        self.render_text(self.move_str, self.GREY, self.MOVE_STR_POS, True)

    def render_zobrist(self):
        for i, char in enumerate(bin(self.board.zobrist_key)):  
            if not char.isdigit():
                self.render_text(char, self.BLUE, (self.zobrist_off + i * self.FONT_WIDTH_SMALL, 10), False)
                continue
            # 1 is blue
            if int(char):
                self.render_text(char, self.BLUE, (self.zobrist_off + i * self.FONT_WIDTH_SMALL, 10), False)
                continue
            # 0 is red
            self.render_text(char, self.RED, (self.zobrist_off + i * self.FONT_WIDTH_SMALL, 10), False)

    def is_selection_valid(self, piece):
        return Piece.is_color(piece, self.board.moving_color)

    def is_target_valid(self, target):
        return target in self.legal_targets

    def update_ui_board(self):
        self.ui_board = self.board.squares[:]

    def reset_move_data(self):
        self.move_from = None
        self.move_to = None
    
    def drop_reset(self):
        self.selected_piece = None
        self.legal_targets = []
        self.update_ui_board()

    def reset_values(self):
        self.reset_move_data()
        self.drop_reset()

    def update_info(self):
        self.fen = self.board.load_fen_from_board()
        print(self.fen)
        self.zobrist_off = (self.WIDTH - len(bin(self.board.zobrist_key)) * self.FONT_WIDTH_SMALL) / 2

    def drop_update(self):
        self.update_info()

    def update_move_str(self, move):
        self.move_str = self.board.get_move_notation(move)
        
    def select_square(self, square):
        piece = self.board.squares[square]
        if not self.is_selection_valid(piece):
            print("Can't pick up opponent's piece")
            return
        self.reset_move_data()
        self.ui_board[square] = 0
        LegalMoveGenerator.load_moves()
        self.legal_targets = LegalMoveGenerator.get_legal_targets(square)
        self.move_from = square
        self.selected_piece = piece

    def drop_piece(self, square): 
        if not self.selected_piece:
            return - 1
        if not self.is_target_valid(square):
            self.reset_values()
            return -1
        self.move_to = square
        move = (self.move_from, self.move_to)
        self.update_move_str(move)
        is_capture = self.board.make_move(move)
        self.drop_update()
        self.drop_reset()
        return is_capture

    def drag_piece(self):
        if not self.selected_piece:
            return
        mouse_pos = pygame.mouse.get_pos()
        piece_pos = self.get_circle_center(mouse_pos, self.UNIT, factor=-1)
        color, piece_type = self.selected_piece
        self.render_piece(color, piece_type, piece_pos)

    def move_responsiveness(self):
        if self.move_from == None:
            return
        self.highlight_move(self.move_from, self.MOVE_RESPONSE_COLOR, False)
        if self.move_to == None:
            return
        self.highlight_move(self.move_to, self.MOVE_RESPONSE_COLOR, True)

    def mark_moves(self):
        if not self.selected_piece:
            return
        piece_color = Piece.get_color_no_check(self.selected_piece)
        for square in self.legal_targets:
            # If piece on target, it must be opponent's, otherwise it would either be invalid or empty
            if self.board.squares[square]:
                # outline red pieces with blue and black pieces with red
                self.highlight_move(square, self.MOVE_HIGHLIGHT_COLORS[piece_color], True)
                continue
            # draw black's moves in red and red's moves in blue
            self.highlight_move(square, self.MOVE_HIGHLIGHT_COLORS[1-piece_color], False)
    
    @staticmethod
    def audio_player(audiofile):
        """
        :param audiofile: pygame.mixer.Sound object
        """
        audiofile.play()

    def play_sfx(self, is_capture):
        if is_capture:
            self.audio_player(self.CAPTURE_SFX)
        else:
            self.audio_player(self.MOVE_SFX)

    def selection(self, mouse_pos):
        # Account for the OFFSETS the board's (0,0) coordinate is replaced by on the window
        file, rank = BoardUtility.get_board_pos(mouse_pos, self.UNIT, *self.OFFSETS)
        current_square = self.board.get_square(file, rank)
        self.select_square(current_square)

    def make_human_move(self):
        mouse_pos = pygame.mouse.get_pos()
        file, rank = BoardUtility.get_board_pos(mouse_pos, self.UNIT, *self.OFFSETS)
        target_square = rank * 9 + file

        is_capture = self.drop_piece(target_square)
        if is_capture == -1:
            return False
        # Sound effects
        self.play_sfx(is_capture)
        # See if there is a mate or stalemate
        LegalMoveGenerator.load_moves()
        GameManager.check_game_state()
        return True
    
    def unmake_move(self):
        if not self.board.game_history:
            return
        GameManager.reset_mate()
        self.board.reverse_move()
        self.reset_values()
        self.update_info()
        LegalMoveGenerator.load_moves()

    def make_AI_move(self):
        AI_move = AIPlayer.load_move()
        if AI_move == None:
            return
        self.update_move_str(AI_move)
        is_capture = self.board.make_move(AI_move)
        self.move_from, self.move_to = AI_move
        self.drop_update()
        self.update_ui_board()
        # Sound effects
        self.play_sfx(is_capture)
        # See if there is a mate or stalemate
        LegalMoveGenerator.load_moves()
        GameManager.check_game_state()
    
    def get_button_img(self):
        return self.BTN_DEACTIVATE_IMG if self.activate_ai else self.BTN_ACTIVATE_IMG

    def ai_button_response(self):
        self.activate_ai = not self.activate_ai
        self.AI_BUTTON.change_image(self.get_button_img())

    def event_handler(self):
        """
        Handles Human events
        mousebuttondown: select and drag a piece
        mousebuttonup: drop a piece
        space: reverse the last move
        enter: save board config and evaluation in csv file
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            
            if self.ai_vs_ai:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.ai_vs_ai = not self.ai_vs_ai
                continue

            # Piece selection
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                is_btn_clicked = self.AI_BUTTON.check_click(mouse_pos)
                if is_btn_clicked:
                    self.ai_button_response()
                else:
                    self.selection(mouse_pos)
  
            # Piece placement
            if event.type == pygame.MOUSEBUTTONUP:
                move_succes = self.make_human_move()
                if not move_succes or not self.activate_ai:
                    continue
                self.make_AI_move()

            if event.type == pygame.KEYDOWN:
                # Move reverse
                if event.key == pygame.K_SPACE:
                    self.unmake_move()
                if event.key == pygame.K_a:
                    self.ai_vs_ai = not self.ai_vs_ai
                if event.key == pygame.K_RETURN:
                    print("ENTER")
                    self.training_data_generator.store_training_data()
                    

    def render(self):
        """
        Does all the rendering work on the window
        """
        self.window.fill(self.BG_COLOR)
        self.window.blit(self.BOARD_IMG, self.OFFSETS)

        self.move_responsiveness()

        self.render_game_state()
        self.render_move_str

        self.AI_BUTTON.render(self.window)
        self.render_zobrist()

        self.mark_moves()

        self.render_pieces()
        
        # Human selected a piece
        self.drag_piece()

        pygame.display.update()

    def update(self):
        Clock.run(self.board.moving_color)  
        self.render()
        self.event_handler()
        if GameManager.gameover:
            return
        if self.ai_vs_ai:
            self.make_AI_move()
            self.training_data_generator.store_training_data()