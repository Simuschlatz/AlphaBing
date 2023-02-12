"""
Copyright (C) 2022-2023 Simon Ma <https://github.com/Simuschlatz> - All Rights Reserved. 
You may use, distribute and modify this code under the terms of the GNU General Public License
"""

import matplotlib as mpl

import numpy as np
import matplotlib.pyplot as plt

# mpl.style.use('bmh')
# best_case = (32 * 64, 130)
# worst_case = (32 * 64 + 1, 194)
 
# # set width of bar
# barWidth = 0.25
# fig = plt.subplots(figsize =(6, 5))
 
 
# # Set position of bar on X axis
# br1 = np.arange(2)
# br2 = [x + barWidth for x in br1]
 
# # Make the plot
# plt.bar(br1, best_case, color ='#2CBDFE', width = barWidth, label ='Obergrenze')
# plt.bar(br2, worst_case, color ='#F5B14C', width = barWidth, label ='Untergrenze')

 
# # Adding Xticks
# plt.xlabel('Methode', fontweight ='bold')
# plt.ylabel('Anzahl bitweiser XOR Operationen', fontweight ='bold')
# plt.xticks([r + barWidth / 2 for r in range(2)],
#         ["Zobrist Hashing", "LaZo"])
 
# plt.legend()
# plt.show()


times = [
    7.8,
    4.9,
    4.4,
    4.1,
    3.9,
    3.17,
    3.11,
    3.07,
    3.05,
    2.98
    ]

iterations = range(1, len(times) + 1)

mpl.style.use('bmh')
fig, ax = plt.subplots(figsize=(7, 6))

ax.plot(iterations, times)
ax.fill_between(iterations, 0, times, alpha=.3)
ax.set_xlim(1, 10)
ax.set_ylim(2, 8)
plt.title("Performance-Vergleich der Versionen bei Suchtiefe 4", fontweight="bold")
plt.xlabel("Versionen", fontweight="bold")
plt.ylabel("Zeit in s", fontweight="bold")
ax.legend()
plt.show()

# mpl.style.use('bmh')
# loss_1 = [
#     5.72,
#     3.657,
#     2.412,
#     1.6638,
#     1.2027,
#     .934,
#     .8695,
#     .7805,
#     .7417,
#     .71,
#     .636,
#     .567,
#     .6,
#     .538,
#     .526,
# ]

# loss_2 = [
#     .5,
#     .156,
#     .0332,
#     .0158,
#     .012,
#     .0087,
#     .0064,
#     .0058,
#     .0048,
#     .0043,
#     .004,
#     .0041,
#     .0038,
#     .0032,
#     .0029,
# ]

# loss = [
#     6.8,
#     4.4,
#     3,
#     2.3,
#     1.8,
#     1.57,
#     1.5,
#     1.41,
#     1.37,
#     1.34,
#     1.27,
#     1.2,
#     1.24,
#     1.17,
#     1.159
# ]
# epochs = range(1, 16)

# plt.figure(figsize=(7, 5))
# plt.plot(epochs, loss_1, color ='#2CBDFE', label="policy head loss")
# plt.plot(epochs, loss_2, color ='#F5B14C', label="value head loss")
# plt.plot(epochs, loss, color='#9D2EC5', label="overall loss")
# plt.xlabel("epochs")
# plt.ylabel("loss")
# plt.legend()
# plt.show()