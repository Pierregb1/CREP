import numpy as np
def temp():
    x = np.linspace(0, 24, 1000)
    return (273 + 10 * np.exp(-x / 5)).tolist()