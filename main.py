"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/Simuschlatz> - All Rights Reserved. 
You may use, distribute and modify this code under the terms of the GNU General Public License
"""
def main():
    play_as_red = True
    red_moves_first = True
    fen = INITIAL_FEN_RED_DOWN if play_as_red else INITIAL_FEN_BLACK_DOWN 
    fen += (" w " if red_moves_first else " b ") + "- - 0 1"
    Clock.init(600)
    # If you play as red, red pieces are gonna be at the bottom, else they're at the top

    board = Board(fen, play_as_red)
    agent = AlphaBetaZeroAgent(board)
    # print(agent.choose_action())
    LegalMoveGenerator.init_board(board)
    LegalMoveGenerator.load_moves()
    # print(sum(LegalMoveGenerator.bitvector_legal_moves()))
    ui = UI(board)
    m = CNN()
    m.load_checkpoint()
    # print(m.predict(board.piecelist_to_bitboard(adjust_perspective=True)))
    sp = SelfPlay(m, board)
    sp.train()
    # sp.parallel_training()
    # mcts = MCTS(m)
    # bb = board.piecelist_to_bitboard(adjust_perspective=True)
    # pi = mcts.get_probability_distribution(board, list(bb), tau=1)
    # print(pi)
    
    # ------To run perft search------
    # start_search(board)
    # -------------------------------

    py_clock = pygame.time.Clock()
    run = True
    while run:   
        ui.update()
        py_clock.tick(FPS)

if __name__ == "__main__":
    import pygame
    pygame.init()
    from core.Engine import Board, LegalMoveGenerator, Clock
    from core.Engine.UI import UI
    from core.Utils import start_search
    from core.Engine.AI.AlphaZero import CNN, MCTS, SelfPlay
    from core.Engine.AI.mixed_agent import AlphaBetaZeroAgent

    FPS = 45

    pygame.display.set_caption("JOE MAMA")
    # pygame.display.set_icon(PIECES_IMGS[7])
    pygame.font.init()


    INITIAL_FEN_BLACK_DOWN = "RHEAKAEHR/9/1C5C/P1P1P1P1P/9/9/p1p1p1p1p/1c5c/9/rheakaehr"
    INITIAL_FEN_RED_DOWN = "rheakaehr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RHEAKAEHR"
    main()
 