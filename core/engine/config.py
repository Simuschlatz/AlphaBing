import pygame
pygame.font.init()
pygame.mixer.init()
from core.engine.data_init import init_imgs

class UIConfig:
    BG_COLOR = (200, 200, 200)
    # BG_COLOR = (215, 186, 137)
    RED = (190, 63, 64)
    BLUE = (26, 57, 185)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREY = (40, 40, 40)
    MOVE_RESPONSE_COLOR = (217, 255, 255)
    MOVE_HIGHLIGHT_COLORS = ((100, 100, 240), (255, 0, 0))
    ARROW_CAPTURE = RED
    ARROW_MOVE = [
        pygame.Color("#03fcf4"),
        pygame.Color("#03e3fc"),
        pygame.Color("#03cefc"),
        pygame.Color("#03c2fc"),
    ]
    ARROW_PSEUDO_LEGAL = [
        pygame.Color("#ff4805"),
        pygame.Color("#ff4c05"),
        pygame.Color("#ff7105"),
        pygame.Color("#ff8f05"),
    ]
    ARROW_COLORS = (ARROW_PSEUDO_LEGAL, ARROW_MOVE, ARROW_CAPTURE)

    WIDTH = 1200
    HEIGHT = 800
    UNIT = HEIGHT // 11
    BOARD_WIDTH = 9 * UNIT
    BOARD_HEIGHT = 10 * UNIT
    BUTTON_DIMS = (UNIT * 2.2, UNIT * .83)
    OFFSET_X = (WIDTH - BOARD_WIDTH) // 2
    OFFSET_Y = (HEIGHT - BOARD_HEIGHT) // 2
    OFFSETS = (OFFSET_X, OFFSET_Y)
    # BOARD_OFFSETS = (OFFSET_X + UNIT / 2, OFFSET_Y + UNIT / 2)
    BOARD_OFFSETS = OFFSETS

    FPS = 45
    # Style of piece images
    piece_style_western = True

    # Font stuff
    FONT_SIZE_LARGE = UNIT // 2
    FONT_SIZE_SMALL = UNIT // 3
    FONT_WIDTH_SMALL = FONT_SIZE_SMALL * 0.55
    FONT_WIDTH_LARGE = FONT_SIZE_LARGE * 0.55

    LARGE_FONT = pygame.font.Font("freesansbold.ttf", FONT_SIZE_LARGE)
    SMALL_FONT = pygame.font.Font("freesansbold.ttf", FONT_SIZE_SMALL)
    TIMER_TEXT_X = OFFSET_X + UNIT * 9.5
    TIMER_TEXT_Y = [HEIGHT / 2 - FONT_SIZE_LARGE, HEIGHT / 2]
    MOVE_STR_POS = (WIDTH // 20) * 2
    
    # SFX
    MOVE_SFX = pygame.mixer.Sound("assets/sfx/move.wav")
    CAPTURE_SFX = pygame.mixer.Sound("assets/sfx/capture.wav")


    BIG_CIRCLE_D = UNIT * 1.1
    SMALL_CIRCLE_D = UNIT // 5

    @classmethod
    def init_imgs(cls):
        cls.IMGS = init_imgs(cls.UNIT, 
                            (cls.WIDTH, cls.HEIGHT), 
                            (cls.BOARD_WIDTH, cls.BOARD_HEIGHT), 
                            cls.BUTTON_DIMS, 
                            cls.piece_style_western)