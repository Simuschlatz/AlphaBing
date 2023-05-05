
def apply_config(config):
    from core.engine.ai.selfplay_rl import BaseConfig
    from core.engine.clock import Clock

    BaseConfig.max_processes = config.cores
    Clock.init(config.time * 60)

    if not config.no_ui:
        from core.utils import silence_function
        with silence_function():
            import pygame
            pygame.init()
        from core.engine.config import UIConfig
        UIConfig.piece_style_western = not config.chinese_style
        UIConfig.init_imgs()

def main():
    from manager import config
    # Not in manager.py so that ``python3 main.py -h`` terminates faster as all modules below aren't imported 
    apply_config(config) 

    from core.engine import Board, LegalMoveGenerator
    from core.engine.ai.selfplay_rl import Pipeline
    from core.utils.perft_utility import start_search
    from core.utils import BoardUtility
    if not config.no_ui:
        from core.engine.UI import UI
    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    # logger = logging.getLogger(__name__)

    
    fen = BoardUtility.get_inital_fen(not config.play_as_black, not config.move_second)
    # If you play as red, red pieces are gonna be at the bottom, else they're at the top
    board = Board(fen, not config.play_as_black)

    # Set up move generator
    LegalMoveGenerator.init_board(board)
    
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