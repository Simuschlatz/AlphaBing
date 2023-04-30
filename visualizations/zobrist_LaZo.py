


import matplotlib as mpl

import numpy as np
import matplotlib.pyplot as plt

mpl.style.use('bmh')
best_case = (32 * 64, 130)
worst_case = (32 * 64 + 1, 194)
 
# set width of bar
barWidth = 0.25
fig = plt.figure(figsize=(6, 5))
 
 
# Set position of bar on X axis
br1 = np.arange(2)
br2 = [x + barWidth for x in br1]
 
# Make the plot
plt.bar(br1, worst_case, color='#F5B14C', width=barWidth, label='Obergrenze')
plt.bar(br2, best_case, color='#2CBDFE', width=barWidth, label='Untergrenze')

 
# Adding Xticks
plt.xlabel('Methode', fontweight='bold')
plt.ylabel('Anzahl XOR-Operationen für jeden Zug', fontweight='bold')
plt.xticks([r + barWidth / 2 for r in range(2)],
        ["Zobrist Hashing", "LaZo"])
 
plt.legend()
plt.show()

fig.savefig("assets/imgs/vis/zobristComp.pdf")

