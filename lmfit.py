#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 08:54:18 2019

@author: gwac
"""
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import sympy as sym
import math

"""
Generate some data, let's imagine that you already have this. 
"""
x = np.linspace(0, 3, 50)
y = np.log10(x)

"""
Plot your data
"""
plt.plot(x, y, 'ro',label="Original Data")

"""
brutal force to avoid errors
"""    
x = np.array(x, dtype=float) #transform your data in a numpy array of floats 
y = np.array(y, dtype=float) #so the curve_fit can work

"""
create a function to fit with your data. a, b, c and d are the coefficients
that curve_fit will calculate for you. 
In this part you need to guess and/or use mathematical knowledge to find
a function that resembles your data
"""
#def func(x, a, b, c, d):
#    return a*x**3 + b*x**2 +c*x + d

def func(x,w,a1,a2,a3,mb,tb1,tb2):
    #w1 = 2.5 / w
    #AA = (x/tb1)**(a1*w) + (x/tb1)**(a2*w) + (tb2/tb1)**(a2*w)*(x/tb2)**(a3*w)
    return mb + (2.5/w)*np.log10((x/tb1)**(a1*w) + (x/tb1)**(a2*w) + (tb2/tb1)**(a2*w)*(x/tb2)**(a3*w))

"""
make the curve_fit
"""
popt, pcov = curve_fit(func, x, y)

print(popt)
"""
The result is:
popt[0] = a , popt[1] = b, popt[2] = c and popt[3] = d of the function,
so f(x) = popt[0]*x**3 + popt[1]*x**2 + popt[2]*x + popt[3].
"""
#print("a = %s , b = %s, c = %s, d = %s")%(popt[0], popt[1], popt[2], popt[3])

"""
Use sympy to generate the latex sintax of the function
"""
xs = sym.Symbol('\lambda')    
tex = sym.latex(func(xs,*popt)).replace('$', '')
plt.title(r'$f(\lambda)= %s$' %(tex),fontsize=16)

"""
Print the coefficients and plot the funcion.
"""

plt.plot(x, func(x, *popt), label="Fitted Curve") #same as line above \/
#plt.plot(x, popt[0]*x**3 + popt[1]*x**2 + popt[2]*x + popt[3], label="Fitted Curve") 

plt.legend(loc='upper left')
plt.show()