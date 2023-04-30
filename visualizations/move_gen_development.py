import matplotlib as mpl

import numpy as np
import matplotlib.pyplot as plt

mpl.style.use('bmh')

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
# plt.title("Performance-Vergleich der Versionen bei Suchtiefe 4", fontweight="bold")
plt.xlabel("Versionen", fontweight="bold")
plt.ylabel("Zeit in s", fontweight="bold")
ax.legend()
plt.show()
fig.savefig("assets/imgs/vis/moveGen.pdf")