"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/Simuschlatz> 
- All Rights Reserved. You may use, distribute and modify this code
under the terms of the GNU General Public License
"""
import pygame
from core.Engine import Board_utility, Piece, Legal_move_generator, Game_manager, Clock, Zobrist_hashing
from core.Engine.AI import AI_player
from core.Utils import Data_generator

class UI:
    MOVE_RESPONSE_COLOR = (217, 255, 255)
    MOVE_HIGHLIGHT_COLOR = (100, 100, 240)
    BG_COLOR = (100, 100, 100)
    RED = (190, 63, 64)
    BLUE = (26, 57, 185)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREY = (40, 40, 40)

    pygame.mixer.init()
    MOVE_SFX = pygame.mixer.Sound("assets/sfx/move.wav")
    CAPTURE_SFX = pygame.mixer.Sound("assets/sfx/capture.wav")

    def __init__(self, window, dimensions, board, offsets, unit, imgs):
        self.window = window
        self.WIDTH, self.HEIGHT = dimensions
        self.board = board
        # This board is created solely for UI purposes, so that the visual board can be modified
        # without crating interdependencies with the internal board representation
        self.ui_board = board.squares[:]

        self.offsets = offsets
        self.off_x, self.off_y = offsets
        self.unit = unit

        self.FONT_SIZE_LARGE = unit // 2
        self.FONT_SIZE_SMALL = unit // 3
        self.FONT_WIDTH_SMALL = self.FONT_SIZE_SMALL * 0.55
        self.GAME_STATE_FONT = pygame.font.Font("freesansbold.ttf", self.FONT_SIZE_LARGE)
        self.DISPLAY_FONT = pygame.font.Font("freesansbold.ttf", self.FONT_SIZE_SMALL)
        self.TEXT_X = self.off_x + unit * 9.5
        
        self.BIG_CIRCLE_D = unit * 1.1
        self.SMALL_CIRCLE_D = unit // 7

        self.PIECES_IMGS, self.BOARD_IMG, self.BG_IMG = imgs 
        
        self.move_from = None
        self.selected_piece = None
        self.move_to = None
        self.legal_targets = []

        self.fen = board.load_fen_from_board()
        self.zobrist_off = (self.WIDTH - len(bin(self.board.zobrist_key)) * self.FONT_WIDTH_SMALL) / 2
        self.move_str = ""

        self.data_generator = Data_generator(board)

    def draw_piece(self, color, piece_type, coords):
        self.window.blit(self.PIECES_IMGS[color * 7 + piece_type], coords)

    def get_circle_center(self, rect_coord, diameter, factor=1):
        """
        centers a rectangle coordinate to the circle center
        :param factor: subtract or add half of diameter
        """
        return [pos + factor * self.unit // 2 for pos in rect_coord]

    def render_circle(self, upper_left_corner_pos, diameter, color):
        centered_coords = self.get_circle_center(upper_left_corner_pos, self.unit)
        x, y = (pos - diameter // 2 for pos in centered_coords)
        pygame.draw.ellipse(self.window, color, (x, y, diameter, diameter))
    
    def highlight_large(self, square, color):
        file, rank = Board_utility.get_file_and_rank(square)
        coordinates = Board_utility.get_display_coords(file, rank, self.unit, *self.offsets)
        self.render_circle(coordinates, self.BIG_CIRCLE_D, color)
    
    def highlight_small(self, square, color):
        file, rank = Board_utility.get_file_and_rank(square)
        coordinates = Board_utility.get_display_coords(file, rank, self.unit, *self.offsets)
        self.render_circle(coordinates, self.SMALL_CIRCLE_D, color)

    def render_text(self, text: str, color: tuple, pos: tuple, large_font):
        if large_font:
            surface = self.GAME_STATE_FONT.render(text, False, color)
        else:
            surface = self.DISPLAY_FONT.render(text, False, color)
        self.window.blit(surface, pos)

    def render_remaining_time(self, player):
        y = self.HEIGHT / 2 - (1 - player) * self.FONT_SIZE_LARGE
        rendered_text = f"{Clock.r_min_tens[player]}{Clock.r_min_ones[player]}:{Clock.r_sec_tens[player]}{Clock.r_sec_ones[player]}"
        self.render_text(rendered_text, self.GREY, (self.TEXT_X, y), True)

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
            print("Can't pick up this piece")
            return
        self.reset_move_data()
        self.ui_board[square] = 0
        Legal_move_generator.load_moves()
        self.legal_targets = Legal_move_generator.get_legal_targets(square)
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
        mouse_pos = pygame.mouse.get_pos()
        piece_pos = self.get_circle_center(mouse_pos, self.unit, factor=-1)
        color, piece_type = self.selected_piece
        self.draw_piece(color, piece_type, piece_pos)

    def move_responsiveness(self):
        if self.move_from == None:
            return
        self.highlight_small(self.move_from, self.MOVE_RESPONSE_COLOR)
        if self.move_to == None:
            return
        self.highlight_large(self.move_to, self.MOVE_RESPONSE_COLOR)

    def mark_moves(self):
        for square in self.legal_targets:
            # If piece on target, it must be opponent's,  otherwise it would've been removed
            if self.board.squares[square]:
                self.highlight_large(square, self.MOVE_HIGHLIGHT_COLOR)
            self.highlight_small(square, self.MOVE_HIGHLIGHT_COLOR)
    
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

    def selection(self):
        mouse_pos = pygame.mouse.get_pos()
        # Account for the offsets the board's (0,0) coordinate is replaced by on the window
        file, rank = Board_utility.get_board_pos(mouse_pos, self.unit, *self.offsets)
        current_square = Board_utility.get_square(file, rank)
        self.select_square(current_square)

    def make_human_move(self):
        mouse_pos = pygame.mouse.get_pos()
        file, rank = Board_utility.get_board_pos(mouse_pos, self.unit, *self.offsets)
        target_square = rank * 9 + file

        is_capture = self.drop_piece(target_square)
        if is_capture == -1:
            return False
        # Sound effects
        self.play_sfx(is_capture)
        # See if there is a mate or stalemate
        Legal_move_generator.load_moves()
        Game_manager.check_game_state()
        return True
    
    def unmake_move(self):
        if not self.board.game_history:
            return
        Game_manager.reset_mate()
        self.board.reverse_move()
        self.reset_values()
        self.update_info()
        Legal_move_generator.load_moves()

    def make_AI_move(self):
        AI_move = AI_player.load_move()
        self.update_move_str(AI_move)
        is_capture = self.board.make_move(AI_move)
        self.move_from, self.move_to = AI_move
        self.drop_update()
        self.update_ui_board()
        # Sound effects
        self.play_sfx(is_capture)
        # See if there is a mate or stalemate
        Legal_move_generator.load_moves()
        Game_manager.check_game_state()
        
    def event_handler(self):
        """
        Handles Human events
        mousebuttondown: select and drag a piece
        mousebuttonup: drop a piece
        space: reverse the last move
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            
            # Piece selection
            if event.type == pygame.MOUSEBUTTONDOWN:
               self.selection()
  
            # Piece placement
            if event.type == pygame.MOUSEBUTTONUP:
                move_succes = self.make_human_move()
                if not move_succes:
                    continue
                self.make_AI_move()

            if event.type == pygame.KEYDOWN:
                # Move reverse
                if event.key == pygame.K_SPACE:
                    self.unmake_move()
                if event.key == pygame.K_RETURN:
                    print("ENTER")
                    self.data_generator.store_training_data()
                    

    def render(self):
        """
        Does all the rendering work on the window
        """
        self.window.fill(self.BG_COLOR)
        # self.window.blit(BG_IMG, (0, 0))
        self.window.blit(self.BOARD_IMG, self.offsets)
        self.move_responsiveness()

        if Game_manager.checkmate:
            self.render_text("checkmate!", self.GREY, (self.TEXT_X, self.HEIGHT // 2 - self.FONT_SIZE_LARGE // 2), True)
        elif Game_manager.stalemate:
            self.render_text("stalemate!", self.GREY, (self.TEXT_X, self.HEIGHT // 2 - self.FONT_SIZE_LARGE // 2), True)
        else:
            for player in range(2):
                self.render_remaining_time(player)
        
        # self.render_text(self.fen, self.GREY, (self.off_x, 5), False)
        self.render_text(self.move_str, self.GREY, (self.WIDTH // 10, self.HEIGHT // 2 - self.FONT_SIZE_LARGE // 2), True)

        for i, char in enumerate(bin(self.board.zobrist_key)):  
            if not char.isdigit():
                self.render_text(char, self.BLUE, (self.zobrist_off + i * self.FONT_WIDTH_SMALL, 10), False)
                continue
            if int(char):
                self.render_text(char, self.BLUE, (self.zobrist_off + i * self.FONT_WIDTH_SMALL, 10), False)
                continue
            self.render_text(char, self.RED, (self.zobrist_off + i * self.FONT_WIDTH_SMALL, 10), False)

        if self.selected_piece:
            self.mark_moves()

        # Draw pieces
        for square, piece in enumerate(self.ui_board):
            if piece:
                file, rank = Board_utility.get_file_and_rank(square)
                pos = Board_utility.get_display_coords(file, rank, self.unit, *self.offsets)
                color, piece_type = piece
                self.draw_piece(color, piece_type, pos)
        
        # Human selected a piece
        if self.selected_piece:
            self.drag_piece()

        pygame.display.update()

