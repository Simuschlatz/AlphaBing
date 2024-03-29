import os
import sys
root = os.environ.get("CHEAPCHESS")
sys.path.append(root)
from core.engine import Board, Piece
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style="ticks")

def plot_floatboard(floatboard, ax, title="", style="rocket_r", cbar=False, cbar_kws=None):
    """
    Plots the floatboard on a Seaborn heatmap
    """
    floatboard = np.reshape(floatboard, (10, 9))
    sns.heatmap(floatboard, square=True, cmap=style, ax=ax, cbar=cbar, cbar_kws=cbar_kws)
    ax.set_xlabel("Spalte")
    ax.set_ylabel("Reihe")
    ax.set_title(title, fontweight="bold")


def bitboards_to_floatboard(bitboards):
    """
    Convert one set of bitboards into a single array of 90 floats, where each piece has
    its own value.
    :return: a dict of form {piece: value on floatboard} used for color bar
    """
    # print(f"{bitboards.shape=}")
    floatboard = np.zeros((2, 90))

    for color, bbs in enumerate(bitboards):
        for piece, bb in enumerate(bbs):
            bb *= (piece + 1) / 7
            floatboard[color] += bb

    return floatboard

def plot_bitboards(bitboards, adj_bitboards):
    """
    Converts the bitboards into floatboars and plots them on a single figure.
    """
    # piece_value_dict = {Piece.letters[7 + piece]: (piece + 1) / 7 for piece in range(7)}
    # print(piece_value_dict)
    # Initialize the floatboards
    floatboards = [bitboards_to_floatboard(bitboards), bitboards_to_floatboard(adj_bitboards)]

    fig, ax = plt.subplots(2, 3, figsize=(12, 8))
    fig.subplots_adjust(hspace=0.125, wspace=0.5)
    print(ax)
    titles = ["Zusammengeführte Bitboards", "Nach perspektivischer Anpassung", "Wenn rot am Zug ist"]

    for side in range(2):
        for mode, mode_name in enumerate(titles):
            flip_order = mode == 2
            title = mode_name if not side else ""
            red_up = side - flip_order
            # Limit mode to 2 as floatboard of mode 2 and 3 are the same in the starting position
            # The bitboards are already adjusted so that the moving side's bitboards are at index 0
            # but it makes no difference in the symmetrical initial state of each game.
            floatboard_mode = min(mode, 1)
            style = "rocket_r" if red_up else "mako_r"
            plot_floatboard(floatboards[floatboard_mode][side], 
                            ax[side][mode], 
                            title=title, 
                            style=style, 
                            # cbar=flip_order,
                            # cbar_kws=piece_value_dict
                            )
    fig.savefig("assets/imgs/vis/adj.pdf")
    plt.show()

if __name__ == '__main__':
    fen = "rheakaehr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RHEAKAEHR w - - 0 1"
    board = Board(fen)
    bbs = board.piecelist_to_bitboard(adjust_perspective=False)
    # Adjusted bitboards
    adj_bbs = board.piecelist_to_bitboard()
    plot_bitboards(bbs, adj_bbs)