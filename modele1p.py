import numpy as np
def temp(T0=100.0, N=1000, dt=0.01, c=1.0, h=0.1, S=10.0, T_lim=20.0):
    T = [T0]
    for _ in range(1, N):
        T.append(T[-1] - dt * (T[-1] - T_lim) * h * S / c)
    return T
