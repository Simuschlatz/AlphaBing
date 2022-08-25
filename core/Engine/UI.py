import pygame
from core.Engine import Board_utility, Piece, Legal_move_generator, Game_manager, Clock

class UI:
    MOVE_RESPONSE_COLOR = (217, 255, 255)
    MOVE_HIGHLIGHT_COLOR = (248, 241, 174)
    BG_COLOR = (100, 100, 100)
    def __init__(self, window, dimensions, board, offsets, unit, imgs):
        self.window = window
        self.WIDTH, self.HEIGHT = dimensions
        self.internal_board = board
        # This board is created solely for UI purposes, so that the visual board can be modified
        # without crating interdependencies with the internal board representation
        self.ui_board = board.squares[:]

        self.offsets = offsets
        self.off_x, self.off_y = offsets
        self.unit = unit

        self.FONT_SIZE = unit // 2
        self.DISPLAY_FONT = pygame.font.Font("freesansbold.ttf", self.FONT_SIZE)
        self.TEXT_X = self.off_x + unit * 9.5
        
        self.BIG_CIRCLE_D = unit * 1.1
        self.SMALL_CIRCLE_D = unit // 7

        self.PIECES_IMGS, self.BOARD_IMG, self.BG_IMG = imgs 
        
        self.move_from = None
        self.selected_piece = None
        self.move_to = None
        self.legal_targets = []

    def draw_piece(self, is_red, piece_type, coords):
        self.window.blit(self.PIECES_IMGS[is_red * 7 + piece_type], coords)

    def get_circle_center(self, rect_coord, factor=1):
        return [pos + factor * self.unit // 2 for pos in rect_coord]

    def render_circle(self, upper_left_corner_pos, diameter, color):
        centered_coords = self.get_circle_center(upper_left_corner_pos)
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

    def render_text(self, text: str, pos: tuple):
        surface = self.DISPLAY_FONT.render(text, False, (130, 130, 130))
        self.window.blit(surface, pos)

    def render_remaining_time(self, player):
        y = self.HEIGHT / 2 - (1 - player) * self.FONT_SIZE
        rendered_text = f"{Clock.r_min_tens[player]}{Clock.r_min_ones[player]}:{Clock.r_sec_tens[player]}{Clock.r_sec_ones[player]}"
        self.render_text(rendered_text, (self.TEXT_X, y))

    def is_selection_valid(self, piece):
        return Piece.is_color(piece, self.internal_board.moving_color)

    def is_target_valid(self, target):
        return target in self.legal_targets

    def reset_values(self):
        self.ui_board = self.internal_board.squares[:]
        self.move_from = None
        self.selected_piece = None
        self.move_to = None
        self.legal_targets = []

    def select_square(self, square):
        piece = self.internal_board.squares[square]
        if not self.is_selection_valid(piece):
            return
        self.ui_board[square] = 0
        self.move_to = None
        self.legal_targets = Legal_move_generator.get_legal_targets(square)
        self.move_from = square
        self.selected_piece = piece

    def drop_piece(self, square):
        if not self.selected_piece:
            return
        if not self.is_target_valid(square):
            self.reset_values()
            return -1
        self.move_to = square
        move = (self.move_from, self.move_to)
        is_capture = self.internal_board.make_move(move)
        self.reset_values()
        return is_capture

    def drag_piece(self):
        mouse_pos = pygame.mouse.get_pos()
        piece_pos = self.get_circle_center(mouse_pos, factor=-1)
        is_red = Piece.is_color(self.selected_piece, Piece.red)
        piece_type = Piece.get_type(self.selected_piece)
        self.draw_piece(is_red, piece_type, piece_pos)

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
            if self.internal_board.squares[square]:
                self.highlight_large(square, self.MOVE_HIGHLIGHT_COLOR)
            self.highlight_small(square, self.MOVE_HIGHLIGHT_COLOR)
    
    def render(self):

        self.window.fill(self.BG_COLOR)
        # self.window.blit(BG_IMG, (0, 0))
        self.window.blit(self.BOARD_IMG, self.offsets)
        self.move_responsiveness()

        if Game_manager.checkmate:
            self.render_text("checkmate!", (self.TEXT_X, self.HEIGHT / 2 - self.FONT_SIZE / 2))
        elif Game_manager.stalemate:
            self.render_text("stalemate!", (self.TEXT_X, self.HEIGHT / 2 - self.FONT_SIZE / 2))
        else:
            for player in range(2):
                self.render_remaining_time(player)
        
        if self.selected_piece:
            self.mark_moves()

        # Draself.windowg pieces
        for square, piece in enumerate(self.ui_board):
            if piece:
                file, rank = Board_utility.get_file_and_rank(square)
                pos = Board_utility.get_display_coords(file, rank, self.unit, *self.offsets)
                is_red = Piece.is_color(piece, Piece.red)
                piece_type = Piece.get_type(piece)
                self.draw_piece(is_red, piece_type, pos)
        
        # Human selected a piece
        if self.selected_piece:
            self.drag_piece()

        pygame.display.update()



