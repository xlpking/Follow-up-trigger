#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 22:42:47 2020

@author: gwac
"""
from kapteyn import maputils
import numpy
from service import *

fignum = 19
fig = plt.figure(figsize=figsize)
frame = fig.add_axes(plotbox)
title = "Hammer Aitoff projection (AIT). (Cal. fig.23)"
header = {'NAXIS'  : 2, 'NAXIS1': 100, 'NAXIS2': 80,
          'CTYPE1' : 'RA---AIT',
          'CRVAL1' : 0.0, 'CRPIX1' : 50, 'CUNIT1' : 'deg', 'CDELT1' : -4.0,
          'CTYPE2' : 'DEC--AIT',
          'CRVAL2' : 0.0, 'CRPIX2' : 40, 'CUNIT2' : 'deg', 'CDELT2' : 4.0,
         }
X = cylrange()
Y = numpy.arange(-60,90,30.0)
f = maputils.FITSimage(externalheader=header)
annim = f.Annotatedimage(frame)
grat = annim.Graticule(axnum= (1,2), wylim=(-90,90.0), wxlim=(0,360),
                       startx=X, starty=Y)
grat.setp_lineswcs0(0, lw=2)
grat.setp_lineswcs1(0, lw=2)
lat_world = [-60,-30, 0, 30, 60]
# Remove the left 180 deg and print the right 180 deg instead
w1 = numpy.arange(0,151,30.0)
w2 = numpy.arange(210,360,30.0)
lon_world = numpy.concatenate((w1, w2))
labkwargs0 = {'color':'r', 'va':'bottom', 'ha':'right'}
labkwargs1 = {'color':'b', 'va':'bottom', 'ha':'right'}
doplot(frame, fignum, annim, grat, title,
       lon_world=lon_world, lat_world=lat_world,
       labkwargs0=labkwargs0, labkwargs1=labkwargs1,
       markerpos=markerpos)
