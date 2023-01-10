"""
Copyright (C) 2021-2022 Simon Ma <https://github.com/Simuschlatz> - All Rights Reserved. 
You may use, distribute and modify this code under the terms of the GNU General Public License
"""
def main():
    Clock.init(600)
    board = Board()
    agent = AlphaBetaZeroAgent(board)
    # print(agent.choose_action())
    LegalMoveGenerator.init_board(board)
    LegalMoveGenerator.load_moves()
    # print(sum(LegalMoveGenerator.bitvector_legal_moves()))
    ui = UI(board)
    m = CNN()
    m.load_checkpoint()
    # print(m.predict(board.piecelist_to_bitboard(adjust_perspective=True)))
    # sp = SelfPlay(m, board)
    # sp.train()
    # sp.parallel_training()
    # mcts = MCTS(m)
    # bb = board.piecelist_to_bitboard(adjust_perspective=True)
    # pi = mcts.get_probability_distribution(board, list(bb), tau=1)
    # print(pi)
    
    # ------To run perft search------
    # start_search(board)
    # -------------------------------

    ui.run()

if __name__ == "__main__":
    import pygame
    pygame.init()
    from core.Engine import Board, LegalMoveGenerator, Clock
    from core.Engine.UI import UI
    from core.Utils import start_search
    from core.Engine.AI.AlphaZero import CNN, MCTS, SelfPlay
    from core.Engine.AI.mixed_agent import AlphaBetaZeroAgent

    main()
 