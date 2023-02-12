"""
Copyright (C) 2022-2023 Simon Ma <https://github.com/Simuschlatz> - All Rights Reserved. 
You may use, distribute and modify this code under the terms of the GNU General Public License
"""
import os
import sys
import shutil
from collections import deque
from concurrent.futures import ProcessPoolExecutor, wait
from datetime import datetime
from logging import getLogger
from multiprocessing import Manager
from threading import Thread
from time import time, sleep
from collections import defaultdict
from multiprocessing import Lock
from random import random, randint
import numpy as np

logger = getLogger(__name__)

# 0 ~ 999: K = 30; 1000 ~ 1999: K = 15; 2000 ~ 2999: K = 10; 3000 ~ : K = 5
K_TABLE = [30, 15, 10, 5]   

R_PRI = 40

def compute_elo(r0, r1, w):
    '''
    Compute the elo rating with method from https://www.xqbase.com/protocol/elostat.htm
    :param r0: red player's elo rating
    :param r1: black player's elo rating
    :param w: game result: 1 = red win, 0.5 = draw, 0 = black win
    '''
    relative_elo = r1 - r0 - R_PRI
    we = 1 / (1 + 10 ** (relative_elo / 400))
    k0 = K_TABLE[min(r0, 3000) // 1000] # Limit highest coefficient K to 5
    k1 = K_TABLE[min(r1, 3000) // 1000]
    rn0 = int(r0 + k0 * (w - we))
    rn1 = int(r1 + k1 * (we - w))
    rn0 = max(rn0, 0) # Can't get rating below 0
    rn1 = max(rn1, 0)
    return rn0, rn1

def compute_elo():
    pass
