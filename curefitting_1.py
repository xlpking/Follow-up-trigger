#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 13:10:41 2019

@author: gwac
"""

import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np

def func(x,a,b,c):
    return a * np.exp( -b * x ) + c

def funcpowlaw3(x,w,a1,a2,a3,tb1,tb2,mb):
#def func(x,a1,a3,tb1,tb2,mb):
#    return a*np.exp(-b *x) + c
#    w = 3
#    a1 = 1.6
#    a2 = 0
#    a3 = 5.0
#    tb1 = 30
#    tb2 = 50
    w1 = 2.5 / w
   # mb = 19
    BB = (x/tb1)**(a1*w) +  (x/tb1)**(a2*w) + (tb2/tb1)**(a2*w) * (x/tb2)**(a3*w)
    AA = np.log10(BB)
    CC = mb + w1 * ( AA - np.log10(2) )
    return CC
    #return 2.5 * a * np.log10(x) + b

def funcpowlaw3piecewise(x,w,a1,a2,a3,tb1,tb2,mb):
#def func(x,a1,a3,tb1,tb2,mb):
#    return a*np.exp(-b *x) + c
#    w = 3
#    a1 = 1.6
#    a2 = 0
#    a3 = 5.0
#    tb1 = 30
#    tb2 = 50
    w1 = 2.5 / w
   # mb = 19
    BB = (x/tb1)**(a1*w) +  (x/tb1)**(a2*w) + (tb2/tb1)**(a2*w) * (x/tb2)**(a3*w)
    AA = np.log10(BB)
    CC = mb + w1 * ( AA - np.log10(2) )
    return CC
    #return 2.5 * a * np.log10(x) + b

def piecewise_powerlow3(x,a1,a2,a3,tb1,tb2,mb):
    return np.piecewise(x,[x < tb1, (tb1 <= x) & (x <= tb2), x>=tb2],[ mb + 2.5 * a1 * np.log10(x), 
                         mb - 2.5 * (a2 - a1) * np.log10(tb1) + 2.5 * a2 * np.log10(x), 
                        mb-2.5*(a2-a1)*np.log10(tb1)-2.5*(a3-a2)*np.log10(tb2)+2.5*a3*np.log10(x)])


#def funcpowlaw2(x,a1,a2,tb1,mb):
#def func(x,a1,a3,tb1,tb2,mb):
#    return a*np.exp(-b *x) + c
    # w = 3
#    a1 = 1.6
#    a2 = 0
#    a3 = 5.0
#    tb1 = 30
#    tb2 = 50
    #w1 = 2.5 / w
#    w = 3.
#    w1 = 2.5 / w
#   # mb = 19
#    BB = (x/tb1)**(a1*w) +  (x/tb1)**(a2*w)
#    AA = np.log10(BB)
#    CC = mb + w1 * (AA - np.log10(2))
#    return CC
    #return 2.5 * a * np.log10(x) + b


#b=np.loadtxt('GRB190530A.txt')
b=np.loadtxt('G181229_C02390lc.txt', dtype=np.float32)
print(b)
xdata = b[:,0]
ydata = b[:,1]
plt.gca().invert_yaxis()
#plt.plot(xdata, ydata)
#plt.semilogx(xdata, ydata)
#plt.xticks([1,2,3,4,5,6,7,8])
plt.grid()
#xdata = np.linspace(0, 4, 50)
#y = func(xdata, 2.5, 1.3, 0.5)
#np.random.seed(1729)
#y_noise = 0.2 * np.random.normal(size=xdata.size)
#ydata = y + y_noise


#plt.plot(xdata,ydata,'b-', logx=True, label='data')
plt.plot(xdata,ydata)
#popt, pcov = curve_fit(func, xdata, ydata)
#for powerlaw3
#popt, pcov = curve_fit(funcpowlaw3, xdata, ydata, bounds=([0, 1.6, 0.0, 4.0, 35.,45.,10.], [5, 2.0, 0.2, 6.0, 42., 55., 25.]))
#popt, pcov = curve_fit(piecewise_powerlow3, xdata, ydata, p0=[1.61, 0., 4.95, 30.,50.,19.0])
#print(popt)
#w = popt[0]
#a1 = popt[1]
#a2 = popt[2]
#a3 = popt[3]
#tb1 = popt[4]
#tb2 = popt[5]
#mb = popt[6]

# for powerlaw2 
#popt, pcov = curve_fit(funcpowlaw2, xdata, ydata,bounds=([0.0, 4.0, 45.,10.], [0.2, 6.0, 55., 100.]))
#print(popt)

param_bounds=([-np.inf,0],[np.inf,1])
popt, pcov = curve_fit(func, xdata, ydata, bounds=param_bounds)
print(popt)
plt.plot(xdata, func(xdata, *popt), 'r-',
         label='fit: a=%5.3f, b=%5.3f, c=%5.3f'% tuple(popt))
#plt.semilogx(xdata, func(xdata, *popt))
#plt.semilogx(xdata, funcpowlaw3(xdata,*popt))
#plt.legend("GRB190530A")
plt.title("G181229_C02390")
plt.xlabel('x')
plt.ylabel('y')
plt.show()
