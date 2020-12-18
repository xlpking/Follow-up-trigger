#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 15:38:47 2019

@author: xlp
"""

import numpy as np
X=[ 1 ,2  ,3 ,4 ,5 ,6]
Y=[ 2.5 ,3.51 ,4.45 ,5.52 ,6.47 ,7.51]
z1 = np.polyfit(X, Y, 1)  #一次多项式拟合，相当于线性拟合
p1 = np.poly1d(z1)
print z1  #[ 1.          1.49333333]
print p1  # 1 x + 1.493