#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 21:53:34 2021

@author: xlp
"""
import math

def dec2hour(DEC):
    if DEC > 0:
        print("positive")
        dd = math.floor(DEC)
        print(dd)
        MMSS = (DEC - dd) * 60
        MM = math.floor(MMSS)
        SS = (MMSS - MM) * 60
    else:
        print("negtive")
        dd = math.ceil(DEC)
        print(dd)
        MMSS = (dd - DEC) * 60
        MM = math.floor(MMSS)
        SS = (MMSS - MM) * 60
    if SS < 10:
        print('SS<10')
        DEC_Hour="%.2d:%.2d:0%.3f"%(dd,MM,SS)
    else:
        print("SS>=10")
        DEC_Hour="%.2d:%.2d:%.3f"%(dd,MM,SS)
    print("DEC=%s"%(DEC_Hour))
    return DEC_Hour
    
  
decdeg=-0.345
aa=dec2hour(decdeg)
print(aa)