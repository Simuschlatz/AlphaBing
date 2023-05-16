import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.style.use('bmh')

import seaborn as sns


evaluated_nodes = [1281157, 173628, 109786, 66932, 250]
algorithms = ['Minimax', 'Alpha-Beta', 'Zugsortierung 1', 'Zugsortierung 2', 'MCTS']


colors = sns.color_palette("Blues_r")
c = colors[:]
colors = [c[i-1] for i in range(len(colors))]
# colors = sns.color_palette("ch:start=.2,rot=-.3")
sorted_evaluated = sorted(evaluated_nodes)
print(sorted_evaluated)
colors = [colors[sorted_evaluated.index(n)] for n in evaluated_nodes]

fig = plt.figure(figsize=(8, 6))
plt.ticklabel_format(style='scientific', axis='x', scilimits=(0,0))
plt.bar(algorithms, evaluated_nodes, width=.8, color=colors)
# plt.title("Vergleich der Performance unterschiedlicher Suchalgorithmen", fontweight="bold")
# plt.xlabel('Algorithmus')
plt.ylabel('Evaluierte Positionen')
plt.show()
fig.savefig("assets/imgs/vis/algComparison.pdf")