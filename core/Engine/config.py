import pygame
from core.engine.data_init import init_imgs

class UIConfig:
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

    FPS = 45
    # Style of piece images
    piece_style_western = True

    IMGS = init_imgs(UNIT, 
                    (WIDTH, HEIGHT), 
                    (BOARD_WIDTH, BOARD_HEIGHT), 
                    BUTTON_DIMS, 
                    piece_style_western)

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
    SMALL_CIRCLE_D = UNIT // 6