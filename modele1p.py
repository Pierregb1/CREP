
import numpy as np

def temp():
    x = np.linspace(0, 24, 1000)
    T = 273 + 10 * np.exp(-x / 5)
    return T.tolist()
