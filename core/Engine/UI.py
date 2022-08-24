import pygame
from core.Engine import Board_utility, Piece, Legal_move_generator

class UI:
    MOVE_RESPONSE_COLOR = (217, 255, 255)
    MOVE_HIGHLIGHT_COLOR = (248, 241, 174)
    def __init__(self, window, board, offsets, unit):
        self.window = window
        self.board = board
        self.off_x, self.off_y = offsets
        self.unit = unit
        self.BIG_CIRCLE_D = unit * 1.1
        self.SMALL_CIRCLE_D = unit // 7
        self.move_from = None
        self.selected_piece = None
        self.move_to = None
        self.legal_targets = []
    
    def highlight_large(self, square, color):
        file, rank = Board_utility.get_file_and_rank(square)
        coordinates = Board_utility.get_display_coords(file, rank, self.unit, self.off_x, self.off_y)
        x, y = (pos + self.unit // 2 - self.BIG_CIRCLE_D // 2 for pos in coordinates)
        pygame.draw.ellipse(self.window, color, (x, y, self.BIG_CIRCLE_D, self.BIG_CIRCLE_D))
    
    def highlight_small(self, square, color):
        file, rank = Board_utility.get_file_and_rank(square)
        coordinates = Board_utility.get_display_coords(file, rank, self.unit, self.off_x, self.off_y)
        x, y = (pos + self.unit // 2 - self.SMALL_CIRCLE_D // 2 for pos in coordinates)
        pygame.draw.ellipse(self.window, color, (x, y, self.SMALL_CIRCLE_D, self.SMALL_CIRCLE_D))

    def is_piece_valid(self, piece):
        return Piece.is_color(piece, self.board.moving_color)

    def select_square(self, square):
        piece = self.board.squares[square]
        if not self.is_piece_valid(piece):
            return
        self.move_to = None
        self.legal_targets = Legal_move_generator.get_legal_targets(square)
        self.move_from = square
        self.selected_piece = piece

    def move_responsiveness(self):
        if self.move_from == None:
            return
        self.highlight_small(self.move_from, self.MOVE_RESPONSE_COLOR)
        if self.move_to == None:
            return
        self.highlight_large(self.move_to, self.MOVE_RESPONSE_COLOR)

    def mark_moves(self, board):
        for square in self.legal_targets:
            # If piece on target, it must be opponent's,  otherwise it would've been removed
            if board.squares[square]:
                self.highlight_large(square, self.MOVE_HIGHLIGHT_COLOR)
            self.highlight_small(square, self.MOVE_HIGHLIGHT_COLOR)
    


    
    
