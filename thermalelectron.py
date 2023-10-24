import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
from scipy.integrate import cumtrapz
from scipy.integrate import cumulative_trapezoid
'''
equations follow this paper: J. Phys. Chem. A (2014) 118, 8067−8073 
'''


def returns_dEdt(E, t):
    dEdt = -E/tau + sigma0 * np.exp(-(t-1)**2/(tau1**2))
    return dEdt
def rate(E):
    ke = A0 * np.exp(-phi/(np.sqrt(4.0*E*Ef/(np.pi**2*N))-kB*T0))
    return ke
def te(E):
    teme = np.sqrt(4.0*E*Ef/(np.pi**2*N))-kB*T0
    return teme

# initial condition
E0 = 0
# consider the unit, i will try SI unit

# values of time
fs = 1.0e-15
t = np.arange(0, 10, 0.001)
t = t*fs
eV = 1.6e-19
tau = 100.0*fs
tau1 = 20.0*fs
sigma0 = 1.0
t0 = 50.0*fs
A0 = 2.7e-15
N = 240
phi = 7.6*eV
Ef = 20.0*eV
kB = 1.38e-23
T0 = 0.5*eV


kin = np.arange(0, 10, 0.001)
# solving ODE
E = odeint(returns_dEdt, E0, t)
profile = np.exp(-(t-1)**2/(tau1**2))
ke = rate(E)
temperatureelectron = te(E)
temax = temperatureelectron.max()
kemax = ke.max()
profilemax = profile.max()
scale = E.max()
intrate = cumulative_trapezoid(ke[:,0], t)
# intrate = np.trapz(ke[:,0], t)
# print(intrate)
intratemax = intrate.max()
# print(np.shape(intrate))
# print(np.shape(ke))
y = np.multiply(ke[1:,0],np.exp(-1.0*intrate/intratemax))
ymax = y.max()
# print(np.multiply(y,ke[1:,0]))

pes = np.multiply(np.divide(y,temperatureelectron[1:]),np.exp(-kin[1:]/temperatureelectron[1:]))
# print(np.shape(y))
print(np.shape(pes))
# print(np.shape(ke[:,0]),np.shape(t))
# plot results
fig = plt.figure(figsize=(12,8))
plt.plot(t, E/scale,label = 'inner energy')
plt.plot(t,1/profilemax*np.exp(-(t-1)**2/(tau1**2)),'--',label = 'laser profile')
plt.plot(t,ke/kemax,'-.',label = 'rate')
plt.plot(t,temperatureelectron/temax,'-.',label = 'electron temperature')
plt.plot(t[1:],intrate/intratemax,'-',label = 'interate')
# plt.plot(t[1:],np.exp(-intrate))
plt.plot(t[1:],y/ymax,'-',label = 'surviving')
plt.xlabel("Time")
plt.ylabel("Inner energy")
plt.legend()

fig2 = plt.figure(figsize=(12,8))
plt.plot(kin[1:],pes[-1,:],'-',label = 'surviving')
plt.plot(kin[1:],pes[2,:],'-',label = 'surviving')
plt.xlabel("kinetic energy")
plt.ylabel("ionization probability")
plt.show()

# x = np.linspace(-2, 2, num=20)
# y = x
# y_int = cumulative_trapezoid(y, x, initial=0)
# plt.plot(x, y_int, 'ro', x, y[0] + 0.5 * x**2, 'b-')
# plt.show()