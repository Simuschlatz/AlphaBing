
def apply_config(config):
    from core.engine.ai.config import BaseConfig
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

    # fen =  "r1ea1a3/4kh3/2h1e4/pHp1p1p1p/4c4/6P2/P1P2R2P/1CcC5/9/2EAKAE2 w - - 0 1"
    # fen = "r1ea1a/4kh/2h1e/pHp1p1p1p/4c/6P/P1P2R2P/1CcC/4K/2EA1AE b - - 1 1"
    # fen = "r1eaka/5R/2h1e/pHp1p1p1p/4c/6P/P1P5P/1CcC/4K/2EA1AE b - - 3 2"
    # fen = " 5a3/3k5/3aR4/9/5r3/5h3/9/3A1A3/5K3/2EC2E2 w - - 0 1"
    # fen = "CRH1k1e2/3ca4/4ea3/9/2hr5/9/9/4E4/4A4/4KA3 w - - 0 1"
    # fen = "R1H1k1e2/9/3aea3/9/2hr5/2E6/9/4E4/4A4/4KA3 w - - 0 1"
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