import matplotlib.pyplot as plt

T0 = 100.0  # Initial temperature
t0 = 0.0    # Initial time 

N = 1000    # Number of time steps
dt = 0.01   # Time step size
c = 1.0    # Heat capacity
h = 0.1    # Heat transfer coefficient
S = 10.0   # Surface area
T_lim = 20.0  # Limiting temperature

def Temp(T0,t0,N,dt,c,h,S,T_lim):
    T = [T0]
    t = [t0]
    for i in range(1, N):
        t.append(t[i-1] + dt)
        T.append(T[i-1] - dt * (T[i-1] - T_lim)*h *S/c)
    return (t, T)

y = Temp(T0, t0, N, dt, c, h, S, T_lim)[1]

x = Temp(T0, t0, N, dt, c, h, S, T_lim)[0]

plt.plot(x, y)
plt.xlabel('Time (s)')
plt.ylabel('Temperature (C)')
plt.title('Temperature en fonction du temps')
plt.grid()
plt.show()