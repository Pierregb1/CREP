def temp():
    T0, N, dt, c, h, S, T_lim = 100.0, 1000, 0.01, 1.0, 0.1, 10.0, 20.0
    T = [T0]
    for _ in range(1, N):
        T.append(T[-1] - dt * (T[-1] - T_lim) * h * S / c)
    return T
