import os
import sys
root = os.environ.get("CHEAPCHESS")
sys.path.append(root)
from core.engine import Board
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style="ticks")

def plot_floatboard(floatboard, ax, title=""):
    floatboard = np.reshape(floatboard, (10, 9))
    sns.heatmap(floatboard, square=True, cmap="rocket_r", ax=ax)
    ax.set_xlabel("Spalte")
    ax.set_ylabel("Reihe")
    ax.set_title(title)


def bitboards_to_floatboard(bitboards):
    """
    Convert one set of bitboards into a single array of 90 floats, where each piece has
    its own value.
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
    # Initialize the floatboards
    floatboards = [bitboards_to_floatboard(bitboards), bitboards_to_floatboard(adj_bitboards)]

    fig, ax = plt.subplots(2, 2, figsize=(10, 10))
    titles = ["Zusammengeführte Bitboards", "Nach Perspektivischer Anpassung"]
    for side in range(2):
        for mode, mode_name in enumerate(titles):
            title = mode_name if not side else ""
            plot_floatboard(floatboards[mode][side], ax[side][mode], title=title)

    plt.show()

if __name__ == '__main__':
    fen = "rheakaehr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RHEAKAEHR w - - 0 1"
    board = Board(fen)
    bbs = board.piecelist_to_bitboard(adjust_perspective=False)
    # Adjusted bitboards
    adj_bbs = board.piecelist_to_bitboard()
    plot_bitboards(bbs, adj_bbs)