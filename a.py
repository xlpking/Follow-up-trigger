#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 10:37:11 2019

@author: gwac
"""

import os,sys,time,glob
import numpy as np
import linecache
from math import log
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def pl2(x,a,b):
    return a*x+b+4

def pl1(x,a,b):
#def func(x,a1,a3,tb1,tb2,mb):
#    return a*np.exp(-b *x) + c
#    w = 3
#    a1 = 1.6
#    a2 = 0
#    a3 = 5.0
#    tb1 = 30
#    tb2 = 50
     return a*x+b


dataset = np.loadtxt("/home/gwac/software/gaia_dr2_hrd.cat")
plt.figure(figsize=(8,8))
plt.ylim(18,-5)
plt.xlim(-2,6)
plt.grid(True)
plt.xlabel('bp-rp')
plt.ylabel('Absolute G mag')

#plt.plot( x , y)

plt.plot(dataset[:,4], dataset[:,7], 'ro', markersize=0.5)
xdata = dataset[:,4]
ydata = dataset[:,7]
popt, pcov = curve_fit(pl1, xdata, ydata)
print(popt)
plt.plot(xdata, pl2(xdata, *popt), 'b-',
         label='fit: a=%5.3f, b=%5.3f'% tuple(popt)) 

plt.savefig("dwarfnova.png", dpi=100)

