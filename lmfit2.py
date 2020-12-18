# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 09:08:43 2019

@author: gwac
"""

from numpy import exp, linspace, random

def gaussian(x,amp,cen,wid):
    return amp * exp(-(x-cen)**2 / wid)

from scipy.optimize import curve_fit

x = linspace(-10, 10, 101)
y = gaussian(x, 2.33, 0.21, 1.51) + random.normal(0, 0.2, len(x))

init_vals = [1,0,1]
best_vals, covar = curve_fit(gaussian, x, y, p0=init_vals)

print(best_vals)

from lmfit import Model
gmodel = Model(gaussian)
gmodel.param_names
