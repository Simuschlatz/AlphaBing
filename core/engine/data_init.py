import pygame
import os

def init_imgs(unit, window_dims, board_dims, button_dims, is_western_style: bool, images_folder="./assets/imgs") -> list:

    pieces_file_names = ["general.png",
                        "elephant.png",
                        "advisor.png",
                        "cannon.png",
                        "soldier.png",
                        "rook.png",
                        "horse.png"]

    # Loads all pieces' sprite sheets in a 4:1 aspect ratio, containing four sprites,
    # one of traditional and western style for the two colors each
    _pieces_imgs = [pygame.image.load(os.path.join(images_folder, "Pieces", file_name))
                    for file_name in pieces_file_names]
    size_img = _pieces_imgs[0].get_size()
    piece_width, piece_height = size_img[0] / 4, size_img[1]

    # This gets us the individual images of every piece-color and -type of the chosen style
    pieces_imgs = [img.subsurface((color * piece_width * 2 + is_western_style * piece_width, 0,
                                    piece_width, piece_height)) 
                    for color in [1, 0] for img in _pieces_imgs]

    pieces_imgs = [pygame.transform.scale(img, (unit, unit)) for img in pieces_imgs]
    board_img = pygame.image.load(os.path.join(images_folder, "board_light.svg"))
    board_img = pygame.transform.scale(board_img, board_dims)
    # board_img = pygame.image.load(os.path.join(images_folder, "board_transparent.png"))

    board_img = pygame.transform.scale(board_img, board_dims)

    # bg = pygame.image.load(os.path.join(images_folder, "bg_light.jpg"))
    # bg = pygame.transform.scale(bg, window_dims)

    ai_button_activate = pygame.image.load(os.path.join(images_folder, "Buttons/button_activate-ai_black.png"))
    ai_button_deactivate = pygame.image.load(os.path.join(images_folder, "Buttons/button_deactivate-ai_black.png"))
    btns = (ai_button_activate, ai_button_deactivate)
    btn_dims = ai_button_activate.get_size()
    btn_dims = [btn_dims[axis] * 1 for axis in range(2)]
    btns = [pygame.transform.scale(btns[i], btn_dims) for i in range(len(btns))]
    return pieces_imgs, board_img, *btns