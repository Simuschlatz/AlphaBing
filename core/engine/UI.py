import pygame, os
from core.engine import Piece, PrecomputingMoves, LegalMoveGenerator, Board#, NLPCommandHandler
from core.engine.clock import Clock
from core.engine.game_manager import GameManager
from core.engine.ai.alphabeta import Dfs, AlphaBetaAgent
from core.engine.ai.selfplay_rl import AlphaZeroAgent
from core.engine.ai.mixed_agent import AlphaBetaZeroAgent
from core.engine.ai.slef import TrainingDataCollector
from core.utils import BoardUtility
from core.engine.config import UIConfig
from core.utils import time_benchmark
from datetime import datetime

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
    def __init__(self, board: Board, agent: str="ab"):
        self.window = pygame.display.set_mode((UIConfig.WIDTH, UIConfig.HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("JOE MAMA")
        self.board = board
        # This board is created solely for UI purposes, so that the visual board can be modified
        # without crating interdependencies with the internal board representation
        self.ui_board = board.squares[:]

        # All the images
        self.PIECES_IMGS, self.BOARD_IMG, self.BTN_ACTIVATE_IMG, self.BTN_DEACTIVATE_IMG = UIConfig.IMGS 

        # Move logics
        self.move_from = None
        self.selected_piece = None
        self.move_to = None
        self.legal_targets = []

        # Activate AI option
        self.AI_BUTTON_HEIGHT = self.BTN_ACTIVATE_IMG.get_height()
        self.AI_BUTTON = Button(20, UIConfig.HEIGHT // 2 - self.AI_BUTTON_HEIGHT // 2, self.BTN_ACTIVATE_IMG)
        self.activate_ai = False

        self.ai_vs_ai = False

        # Analytics
        self.fen = board.load_fen_from_board()
        self.zobrist_off = (UIConfig.WIDTH - len(bin(self.board.zobrist_key)) * UIConfig.FONT_WIDTH_SMALL) / 2
        self.move_str = ""

        # Data collector for Self-Learning-Evaluation-Function (SLEF)
        self.training_data_generator = TrainingDataCollector(board)

        # self.search = time_benchmark(Dfs.search)
        # self.agent = AlphaBetaZeroAgent()
        self.select_agent(agent)

    def select_agent(self, agent_str: str):
        assert agent_str, "Agent must be str"
        match agent_str.lower():
            case "ab": self.agent = AlphaBetaAgent()
            case "az": self.agent = AlphaZeroAgent()
            case "abz": self.agent = AlphaBetaZeroAgent()

    def render_piece(self, color: int, piece_type: int, coords):
        self.window.blit(self.PIECES_IMGS[color * 7 + piece_type], coords)
    
    def render_pieces(self):
        for square, piece in enumerate(self.ui_board):
            if not piece:
                continue
            file, rank = self.board.get_file_and_rank(square)
            pos = BoardUtility.get_display_coords(file, rank, UIConfig.UNIT, *UIConfig.OFFSETS)
            color, piece_type = piece
            self.render_piece(color, piece_type, pos)

    def get_circle_center(self, rect_coord, diameter: int, factor=1):
        """
        centers a rectangle coordinate to the circle center
        :param factor: -1 or 1 => subtract or add half of diameter
        """
        return [pos + factor * diameter // 2 for pos in rect_coord]

    def render_circle(self, upper_left_corner_pos, diameter: int, color):
        centered_coords = self.get_circle_center(upper_left_corner_pos, UIConfig.UNIT)
        x, y = (pos - diameter // 2 for pos in centered_coords)
        pygame.draw.ellipse(self.window, color, (x, y, diameter, diameter))
    
    def highlight_move(self, square, color, large: bool):
        file, rank = self.board.get_file_and_rank(square)
        coordinates = BoardUtility.get_display_coords(file, rank, UIConfig.UNIT, *UIConfig.OFFSETS)
        d = UIConfig.BIG_CIRCLE_D if large else UIConfig.SMALL_CIRCLE_D
        self.render_circle(coordinates, d, color)

    def render_text(self, text: str, color: tuple, pos: tuple, large_font):
        if large_font:
            surface =UIConfig.LARGE_FONT.render(text, False, color)
        else:
            surface = UIConfig.SMALL_FONT.render(text, False, color)
        self.window.blit(surface, pos)

    def render_remaining_time(self, player):
        rendered_text = Clock.ftime[player]
        self.render_text(rendered_text, UIConfig.BLACK, (UIConfig.TIMER_TEXT_X, UIConfig.TIMER_TEXT_Y[player]), True)
    
    def render_game_state(self):
        if GameManager.checkmate:
            self.render_text("checkmate!", UIConfig.GREY, (UIConfig.TIMER_TEXT_X, UIConfig.HEIGHT // 2 - UIConfig.FONT_SIZE_LARGE // 2), True)
        elif GameManager.stalemate:
            self.render_text("stalemate!", UIConfig.GREY, (UIConfig.TIMER_TEXT_X, UIConfig.HEIGHT // 2 - UIConfig.FONT_SIZE_LARGE // 2), True)
        else:
            for player in range(2):
                self.render_remaining_time(player)

    def render_move_str(self):
        self.render_text(self.move_str, UIConfig.GREY, UIConfig.MOVE_STR_POS, True)

    def render_zobrist(self):
        for i, char in enumerate(bin(self.board.zobrist_key)):  
            if not char.isdigit():
                self.render_text(char, UIConfig.BLUE, (self.zobrist_off + i * UIConfig.FONT_WIDTH_SMALL, 10), False)
                continue
            # 1 is blue
            if int(char):
                self.render_text(char, UIConfig.BLUE, (self.zobrist_off + i * UIConfig.FONT_WIDTH_SMALL, 10), False)
                continue
            # 0 is red
            self.render_text(char, UIConfig.RED, (self.zobrist_off + i * UIConfig.FONT_WIDTH_SMALL, 10), False)

    def show_square_ids(self):
        for i in range(9):
            for j in range(10):
                x = i * UIConfig.UNIT + UIConfig.OFFSET_X + UIConfig.UNIT // 2
                y = j * UIConfig.UNIT + UIConfig.OFFSET_Y + UIConfig.UNIT // 2
                square_id = str(j * 9 + i)
                self.render_text(square_id, UIConfig.RED, (x, y), False)

    def draw_arrow(
        self,
        start: pygame.Vector2,
        end: pygame.Vector2,
        color: pygame.Color,
        body_width: int = 10,
        head_width: int = 30,
        head_height: int = 20,
    ):
        """Draw an arrow between start and end with the arrow head at the end.

        Args:
            surface (pygame.Surface): The surface to draw on
            start (pygame.Vector2): Start position
            end (pygame.Vector2): End position
            color (pygame.Color): Color of the arrow
            body_width (int, optional): Defaults to 2.
            head_width (int, optional): Defaults to 4.
            head_height (float, optional): Defaults to 2.
        """
        arrow = start - end
        angle = arrow.angle_to(pygame.Vector2(0, -1))
        body_length = arrow.length() - head_height

        # Create the triangle head around the origin
        head_verts = [
            pygame.Vector2(0, head_height / 2),  # Center
            pygame.Vector2(head_width / 2, -head_height / 2),  # Bottomright
            pygame.Vector2(-head_width / 2, -head_height / 2),  # Bottomleft
        ]
        # Rotate and translate the head into place
        translation = pygame.Vector2(0, arrow.length() - (head_height / 2)).rotate(-angle)
        for i in range(len(head_verts)):
            head_verts[i].rotate_ip(-angle)
            head_verts[i] += translation
            head_verts[i] += start

        pygame.draw.polygon(self.window, color, head_verts)

        # Stop weird shapes when the arrow is shorter than arrow head
        if arrow.length() >= head_height:
            # Calculate the body rect, rotate and translate into place
            body_verts = [
                pygame.Vector2(-body_width / 2, body_length / 2),  # Topleft
                pygame.Vector2(body_width / 2, body_length / 2),  # Topright
                pygame.Vector2(body_width / 2, -body_length / 2),  # Bottomright
                pygame.Vector2(-body_width / 2, -body_length / 2),  # Bottomleft
            ]
            translation = pygame.Vector2(0, body_length / 2).rotate(-angle)
            for i in range(len(body_verts)):
                body_verts[i].rotate_ip(-angle)
                body_verts[i] += translation
                body_verts[i] += start

            pygame.draw.polygon(self.window, color, body_verts)

    def render_move_arrows(self, legals_only=True, captures_only=False):
        move_color = UIConfig.ARROW_COLORS[legals_only]
        if legals_only:
            get_targets = LegalMoveGenerator.get_legal_targets
        else: 
            get_targets = PrecomputingMoves.get_targets_for

        for piece_list in self.board.piece_lists[self.board.moving_color]:
            for square in piece_list:
                file, rank = self.board.get_file_and_rank(square)
                from_coords = BoardUtility.get_display_coords(
                                        file, 
                                        rank, 
                                        UIConfig.UNIT, 
                                        UIConfig.OFFSETS[0] + UIConfig.UNIT / 2,
                                        UIConfig.OFFSETS[1] + UIConfig.UNIT / 2
                                        )
                targets = get_targets(square, self.board)
                for i, target in enumerate(reversed(targets)):
                    is_capture = bool(self.board.squares[target])
                    if not is_capture and captures_only:
                        continue
                    i %= len(UIConfig.ARROW_MOVE)
                    file, rank = self.board.get_file_and_rank(target)

                    color = UIConfig.ARROW_CAPTURE if is_capture else move_color[i]
                    to_coords = BoardUtility.get_display_coords(
                                            file, 
                                            rank, 
                                            UIConfig.UNIT, 
                                            UIConfig.OFFSETS[0] + UIConfig.UNIT / 2,
                                            UIConfig.OFFSETS[1] + UIConfig.UNIT / 2
                                            )
                                            
                    self.draw_arrow(pygame.Vector2(from_coords), 
                                    pygame.Vector2(to_coords), 
                                    color)
                                    # UIConfig.ARROW_COLORS[is_capture])

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
        print(len(self.board.repetition_history))
        self.zobrist_off = (UIConfig.WIDTH - len(bin(self.board.zobrist_key)) * UIConfig.FONT_WIDTH_SMALL) / 2
        
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
        print(self.board.mirror_move(move))
        self.update_move_str(move)
        is_capture = self.board.make_move(move)
        self.drop_update()
        self.drop_reset()
        return is_capture

    def drag_piece(self):
        if not self.selected_piece:
            return
        mouse_pos = pygame.mouse.get_pos()
        piece_pos = self.get_circle_center(mouse_pos, UIConfig.UNIT, factor=-1)
        color, piece_type = self.selected_piece
        self.render_circle(piece_pos, UIConfig.BIG_CIRCLE_D, UIConfig.MOVE_HIGHLIGHT_COLORS[1-color])
        self.render_piece(color, piece_type, piece_pos)

    def move_responsiveness(self):
        if self.move_from == None:
            return
        self.highlight_move(self.move_from, UIConfig.MOVE_RESPONSE_COLOR, False)
        if self.move_to == None:
            return
        self.highlight_move(self.move_to, UIConfig.MOVE_RESPONSE_COLOR, True)

    def mark_moves(self):
        if not self.selected_piece:
            return
        piece_color = Piece.get_color_no_check(self.selected_piece)
        for square in self.legal_targets:
            # If piece on target, it must be opponent's, otherwise it would either be invalid or empty
            if self.board.squares[square]:
                # outline red pieces with blue and black pieces with red
                self.highlight_move(square, UIConfig.MOVE_HIGHLIGHT_COLORS[piece_color], True)
                continue
            # draw black's moves in red and red's moves in blue
            self.highlight_move(square, UIConfig.MOVE_HIGHLIGHT_COLORS[piece_color], False)
    
    @staticmethod
    def audio_player(audiofile):
        """
        :param audiofile: pygame.mixer.Sound object
        """
        audiofile.play()

    def play_sfx(self, is_capture):
        if is_capture:
            self.audio_player(UIConfig.CAPTURE_SFX)
        else:
            self.audio_player(UIConfig.MOVE_SFX)

    def selection(self, mouse_pos):
        # Account for the OFFSETS the board's (0,0) coordinate is replaced by on the window
        file, rank = BoardUtility.get_board_pos(mouse_pos, UIConfig.UNIT, *UIConfig.OFFSETS)
        current_square = self.board.get_square(file, rank)
        self.select_square(current_square)

    def make_human_move(self):
        mouse_pos = pygame.mouse.get_pos()
        file, rank = BoardUtility.get_board_pos(mouse_pos, UIConfig.UNIT, *UIConfig.OFFSETS)
        target_square = rank * 9 + file

        is_capture = self.drop_piece(target_square)
        if is_capture == -1:
            return False
        # Sound effects
        self.play_sfx(is_capture)
        # See if there is a mate or stalemate
        LegalMoveGenerator.load_moves()
        # print(self.board.piecelist_to_bitboard()[:2, 0])
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
        # AI_move = self.search(self.board, 250)
        AI_move = self.agent.choose_action(self.board)
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

    # def command_response(self):
    #     """
    #     Handles response to verbal commands
    #     """
    #     start_search = NLPCommandHandler.listen_for_activation()
    #     if start_search:
    #         self.activate_ai = True
    #         self.make_AI_move()
    #         self.activate_ai = False
    
    def screenshot(self, x=0, y=0, w=UIConfig.WIDTH, h=UIConfig.HEIGHT, filepath="assets/imgs/screenshots"):
        """
        Takes a screenshot of the window and saves it to ``filepath``.
        """
        if not os.path.exists(filepath):
            os.mkdir(filepath)
        rect = pygame.Rect(x, y, w, h)
        sub = self.window.subsurface(rect)
        pygame.image.save(sub, filepath + f"/in-game_at_{datetime.now()}.png")

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
                if GameManager.gameover:
                    continue
                self.make_AI_move()

            if event.type == pygame.KEYDOWN:
                # Move reverse
                key = event.key
                if key == pygame.K_SPACE:
                    print("Pressed Space-key")
                    self.unmake_move()
                if key == pygame.K_a:
                    print("Pressed A-key")
                    self.ai_vs_ai = not self.ai_vs_ai
                if key == pygame.K_s:
                    print("pressed S-key")
                    self.screenshot(UIConfig.OFFSET_X, 
                                    UIConfig.OFFSET_Y, 
                                    UIConfig.BOARD_WIDTH, 
                                    UIConfig.BOARD_HEIGHT)
                # if key == pygame.K_c:
                #     print("Pressed C-key")
                #     self.command_response()
                if key == pygame.K_RETURN:
                    print("ENTER")
                    self.training_data_generator.store_training_data()
                    

    def render(self):
        """
        Does all the rendering work on the window
        """
        self.window.fill(UIConfig.BG_COLOR)

        self.window.blit(self.BOARD_IMG, UIConfig.BOARD_OFFSETS)
        # self.show_square_ids()
        self.move_responsiveness()

        self.render_game_state()
        self.render_move_str

        self.AI_BUTTON.render(self.window)
        self.render_zobrist()

        self.mark_moves()

        
        # self.render_move_arrows(legals_only=True)
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
            # self.training_data_generator.store_training_data()
        
    def run(self):
        if not LegalMoveGenerator.moves:
            LegalMoveGenerator.load_moves()
        py_clock = pygame.time.Clock()
        run = True
        while run:   
            self.update()
            py_clock.tick(UIConfig.FPS)    