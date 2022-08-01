import pygame
import os

def init_imgs(unit, width, height, is_western_style: bool) -> list:

    pieces_file_names = ["general.png",
                        "elephant.png",
                        "advisor.png",
                        "cannon.png",
                        "soldier.png",
                        "rook.png",
                        "horse.png"]

    # Loads all pieces' sprite sheets in a 4:1 aspect ratio, containing four sprites,
    # one of traditional and western style for the two colors each
    _pieces_imgs = [pygame.image.load(os.path.join("assets/imgs/Pieces", file_name))
                    for file_name in pieces_file_names]
    size_img = _pieces_imgs[0].get_size()
    piece_width, piece_height = size_img[0] / 4, size_img[1]

    # This gets us the individual images of every piece-color and -type of the chosen style
    pieces_imgs = [img.subsurface((color * piece_width * 2 + is_western_style * piece_width, 0,
                                    piece_width, piece_height)) 
                    for color in [1, 0] for img in _pieces_imgs]

    pieces_imgs = [pygame.transform.scale(img, (unit, unit)) for img in pieces_imgs]
    board_img = pygame.image.load(os.path.join("assets/imgs", "board.png"))
    board_img = pygame.transform.scale(board_img, (unit * 8, unit * 9))

    bg = pygame.image.load(os.path.join("assets/imgs", "bg_light.jpg"))
    bg = pygame.transform.scale(bg, (width, height))

    return pieces_imgs, board_img, bg