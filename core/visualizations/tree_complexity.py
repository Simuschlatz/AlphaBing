import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
mpl.style.use('bmh')

leaf_nodes = [
    44,
    1_920,
    79_666,
    3_290_240,
    133_312_995,
    5_392_831_844,
    217_154_523_878
]

plt.figure(figsize=(7, 5))
plt.plot(leaf_nodes)
plt.xlabel("Tiefe")
plt.ylabel("Erreichbare Positionen")
plt.title("Suchbaumgröße relativ zur Suchtiefe")
plt.savefig("assets/imgs/vis/searchtree.pdf")
plt.show()