
import math
import numpy as np
import matplotlib.pyplot as plt


def planck_black_body(Lambda, T):
    """
    Lambda - radiation wavelength in nanometers
    T - temperature in Kelvins"""
    # Note: lambda is a keyword in Python so we need to capitalize it
    # Convert to meters
    l = Lambda*10e-9
    h = 6.626e-34
    k = 1.38e-23
    prefactor = 8 * math.pi * h * c / l**5
    hc_over_kT = h * c / k / T
    exponential = np.exp(hc_over_kT/ l)
    rho = prefactor / (exponential-1)
    return rho
c = 3e8
ghz = 1.0e9
T1 = 0.01    # In Kelvins
T2 = 0.1
lambdas = np.arange(1000000, 100000000., 100000.)
mu = c/(lambdas*10e-9)/ghz
fig = plt.plot(figsize = (12,8))
# plt.clf()
plt.plot(mu, planck_black_body(lambdas, T1)/planck_black_body(lambdas, T1).max(),label = 'temperature: '+str(T1)+' K')
plt.plot(mu, planck_black_body(lambdas, T2)/planck_black_body(lambdas, T2).max(),label = 'temperature: '+str(T2)+' K')
#plt.axis([0, 10000, 0, 2])
plt.ylabel("Normalized Energy density",fontsize = 24)
plt.xlabel("Wavelength / GHz",fontsize = 24)
plt.legend(fontsize = 20)
plt.show()