import os
import sys
root = os.environ.get("CHEAPCHESS")
sys.path.append(root)
from core.engine.AI.ABMM import PieceSquareTable
import numpy as np
import seaborn as sns
sns.set_theme(style="ticks")
import matplotlib.pyplot as plt

def normalize(pst):
    pst *= np.argmax(pst)
    return pst
    
def plot_pst(pst, ax, title):
    pst = np.reshape(pst, (10, 9))
    sns.heatmap(pst, ax=ax, cmap="crest", cbar=False, square=True)
    ax.set_title(title, fontweight="bold")

def plot_psts():
    psts = PieceSquareTable.piece_square_tables[1:]
    piece_names = [
        "Elefant",
        "Wache",
        "Kannone ",
        "Bauer",
        "Turm",
        "Pferd"
        ]
    n_cols = 3
    fig, ax = plt.subplots(2, n_cols, figsize=(11, 8))
    # fig.subplots_adjust(hspace=0.3)
    print(ax)
    for i, pst in enumerate(psts):
        pst = normalize(np.array(pst))
        row, col = divmod(i, n_cols)
        plot_pst(pst, ax[row][col], piece_names[i])

    fig.savefig("assets/imgs/vis/pst.pdf")
    plt.show()

plot_psts()