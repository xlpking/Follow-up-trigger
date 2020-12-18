#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 16:20:28 2019

@author: xlp
"""

#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
import os,sys,time,glob
import numpy as np
import linecache
from math import log
import matplotlib.pyplot as plt

dateset = np.loadtxt("/Volumes/Data/data/30cmtest/matched.txt")
OTnametitle = "Astrometry error"
plt.figure(figsize=(8,8))
#plt.title(OTnametitle, fontsize=12)
plt.ylim(0,4000)
plt.xlim(0,4000)
plt.grid(True)
plt.xlabel('X')
plt.ylabel('Y')
    #plt.annotate(OTpara, (-1.8, 1))
   
    #plt.plot( x , y)
    #print(bprp)
    #print(AbsoMag)
   #plt.plot(bprp, AbsoMag,'go',markersize=10)
plt.plot(dateset[:,1], dateset[:,2], 'ro', markersize=1)
    
#plt.scatter(dataset[:,1], dataset[:,5], 'ro', s=10)
fig, ax = plt.subplots()
X=dateset[:,1]
Y=dateset[:,2]
U=dateset[:,3]- dateset[:,1]
V=dateset[:,4]- dateset[:,2]
q = ax.quiver(X, Y,U,V,angles="uv")  
#ax.quiverkey(q, X=0.3, Y=1.1, U=10,
#             label='Quiver key, length = 10', labelpos='E')
#plt.show()
plt.savefig('f30cm.png', format='png', dpi=1000)


#X = np.arange(-10, 10, 1)
#Y = np.arange(-10, 10, 1)
#U, V = np.meshgrid(X, Y)

#fig, ax = plt.subplots()
#q = ax.quiver(X, Y, U, V)
#ax.quiverkey(q, X=0.3, Y=1.1, U=10,
#             label='Quiver key, length = 10', labelpos='E')

#plt.show()