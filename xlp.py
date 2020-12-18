#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 20:56:20 2020

@author: gwac
"""

import matplotlib.pyplot as plt
import numpy as np
x=np.linspace(-3,3,50)
y1=2*x+1
y2=x**2

plt.figure()
fig1, = plt.plot(x,y1,label='y1')
fig2, = plt.plot(x,y2,label='y2',color='red',linewidth=1.0,linestyle='--')
plt.xlim((-1,2))
plt.ylim((-2,3))
plt.xlabel("I am X")
plt.ylabel("I am Y")

new_ticks = np.linspace(-1,2,4)
print(new_ticks)
plt.xticks(new_ticks)

plt.yticks([-2,-1,0,-1.5,3],
           [r'$really\ bad$',r'$bad\ \alpha$',r'$normal$','good','really good'])


#ax = plt.gca()
#ax.spines['right'].set_color('none')
#ax.spines['top'].set_color('none')
#ax.xaxis.set_ticks_position('bottom')
#ax.yaxis.set_ticks_position('left')


#ax.spines['bottom'].set_position(('data',0))  #outward, axes
#ax.spines['left'].set_position(('data',0))

plt.legend(handles=[fig1,fig2,],labels=['ccc','ddd'],loc='best')/

plt.show()