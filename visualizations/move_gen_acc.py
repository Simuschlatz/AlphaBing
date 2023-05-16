import matplotlib as mpl

import numpy as np
import matplotlib.pyplot as plt

mpl.style.use('bmh')
d1 = (100, 100, 100, 100, 100)
d5 = (100, 100, 100, 100, 99)
 
# set width of bar
barWidth = 0.12
fig = plt.figure(figsize=(8, 6))
 
 
# Set position of bar on X axis
br1 = np.arange(5)
br2 = [x + barWidth for x in br1]
br3 = [x + barWidth for x in br2]
br4 = [x + barWidth for x in br3]
br5 = [x + barWidth for x in br4]

# Make the plot
plt.bar(br1, d1, color="#ff4805", width=barWidth, label='Tiefe 1')
plt.bar(br2, d1, color="#ff5805", width=barWidth, label='Tiefe 2')
plt.bar(br3, d1, color="#ff7105", width=barWidth, label='Tiefe 3')
plt.bar(br4, d1, color="#ff8f05", width=barWidth, label='Tiefe 4')
plt.bar(br5, d5, color="#F5B14C", width=barWidth, label='Tiefe 5')

 
# Adding Xticks
plt.xlabel('Position')
plt.ylabel('Genauigkeit in %')
plt.xticks([r + barWidth * 2 for r in range(5)],
        range(1, 6))
 
plt.legend()
plt.show()

fig.savefig("assets/imgs/vis/accuracy.pdf")