
import sys
import os
root = os.environ.get("CHEAPCHESS")
sys.path.append(root)
print(sys.path)

import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.style.use('bmh')

import seaborn as sns


evaluated_nodes = [1281157, 173628, 109786, 66932]
algorithms = ['Minimax', 'Alpha-Beta', 'A-B-Zugsortierung\n(Koeffizient = 1)', 'A-B-Zugsortierung\n(Koeffizient = 250)']


colors = sns.color_palette("Blues_r")
# colors = sns.color_palette("ch:start=.2,rot=-.3")
sorted_evaluated = sorted(evaluated_nodes)
colors = [colors[sorted_evaluated.index(n)] for n in evaluated_nodes]

with sns.axes_style("darkgrid"):
    plt.figure(figsize=(10, 8))
    plt.ticklabel_format(style='scientific', axis='x', scilimits=(0,0))
    plt.bar(algorithms, evaluated_nodes, color=colors)
    plt.title("Vergleich der Performance unterschiedlicher Suchalgorithmen")
    plt.xlabel('Algorithmus')
    plt.ylabel('Evaluierte Positionen')
plt.show()