
def apply_config(config):
    from core.engine.ai.selfplay_rl import BaseConfig
    from core.engine.config import UIConfig
    from core.engine.clock import Clock
    BaseConfig.max_processes = config.cores
    UIConfig.piece_style_western = not config.chinese_style
    Clock.init(config.time * 60)

def main():
    from core.utils import silence_function
    with silence_function():
        import pygame
        pygame.init()

    from manager import config
    apply_config(config) # Not in manager.py so that ``python3 main.py -h`` terminates faster

    from core.engine import Board, LegalMoveGenerator
    from core.engine.UI import UI
    from core.engine.ai.selfplay_rl import CNN, MCTS, Pipeline
    from core.utils.perft_utility import start_search

    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    # logger = logging.getLogger(__name__)
    

    INITIAL_FEN_BLACK_DOWN = "RHEAKAEHR/9/1C5C/P1P1P1P1P/9/9/p1p1p1p1p/1c5c/9/rheakaehr"
    INITIAL_FEN_RED_DOWN = "rheakaehr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RHEAKAEHR"
    play_as_red = True
    red_moves_first = True
    fen = INITIAL_FEN_RED_DOWN if play_as_red else INITIAL_FEN_BLACK_DOWN 
    fen += (" w " if red_moves_first else " b ") + "- - 0 1"
    # If you play as red, red pieces are gonna be at the bottom, else they're at the top
    # "r1ea1kehr/4a/1ch/p1p1p1p1p/c/1C/P1P1P1P1P/E1H3HC/4A/R3KAE1R w - - 10 6"
    board = Board(fen, play_as_red)

    # Set up move generator
    LegalMoveGenerator.init_board(board)
    LegalMoveGenerator.load_moves()
    
    if config.run_perft:
        start_search(board)

    if config.run_pipeline:
        pl = Pipeline(board)
        pl.start_pipeline()

    if config.no_ui:
        return
    ui = UI(board, agent=config.agent)
    ui.run()

if __name__ == "__main__":
    main()
