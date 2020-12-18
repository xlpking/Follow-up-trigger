#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 15:45:38 2019

@author: xlp
"""
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def func(x, a, b, c):
  #return a * np.exp(-b * x) + c
  return a * np.log(b * x) + c

x = np.linspace(1,5,50)   # changed boundary conditions to avoid division by 0
y = func(x, 2.5, 1.3, 0.5)
yn = y + 0.2*np.random.normal(size=len(x))

popt, pcov = curve_fit(func, x, yn)

plt.figure()
plt.plot(x, yn, 'ko', label="Original Noised Data")
plt.plot(x, func(x, *popt), 'r-', label="Fitted Curve")
plt.legend()
plt.show()
"""
import mpfit
import Numeric
x = Numeric.arange(100, Numeric.float)
p0 = [5.7, 2.2, 500., 1.5, 2000.]
y = ( p[0] + p[1]*[x] + p[2]*[x**2] + p[3]*Numeric.sqrt(x) +
     p[4]*Numeric.log(x))
fa = {'x':x, 'y':y, 'err':err}
m = mpfit('myfunct', p0, functkw=fa)
print 'status = ', m.status
if (m.status <= 0): print 'error message = ', m.errmsg
print 'parameters = ', m.params