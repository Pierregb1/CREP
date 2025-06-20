
import numpy as np

def temp(zoomX):
    x = np.linspace(0, 24 / zoomX, 1000)
    return 273 + 10 * np.exp(-x / 5)
