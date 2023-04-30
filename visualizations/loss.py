import matplotlib as mpl

import numpy as np
import matplotlib.pyplot as plt

mpl.style.use('bmh')


loss_1 = [
    5.72,
    3.657,
    2.412,
    1.6638,
    1.2027,
    .934,
    .8695,
    .7805,
    .7417,
    .71,
    .636,
    .567,
    .6,
    .538,
    .526,
]

loss_2 = [
    .5,
    .156,
    .0332,
    .0158,
    .012,
    .0087,
    .0064,
    .0058,
    .0048,
    .0043,
    .004,
    .0041,
    .0038,
    .0032,
    .0029,
]

loss = [
    6.8,
    4.4,
    3,
    2.3,
    1.8,
    1.57,
    1.5,
    1.41,
    1.37,
    1.34,
    1.27,
    1.2,
    1.24,
    1.17,
    1.159
]
epochs = range(1, 16)

fig = plt.figure(figsize=(6, 5))
plt.plot(epochs, loss_1, color ='#2CBDFE', label="policy head loss")
plt.plot(epochs, loss_2, color ='#F5B14C', label="value head loss")
plt.plot(epochs, loss, color='#9D2EC5', label="overall loss")
plt.xlabel("epochs")
plt.ylabel("loss")
plt.legend()
plt.show()
fig.savefig("assets/imgs/vis/loss.pdf")