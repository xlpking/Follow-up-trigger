#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 12 02:27:22 2019

@author: xlp
"""
import os,sys,time,glob
import numpy as np
import linecache
from math import log
import matplotlib.pyplot as plt
#import pylab as pl


#from matplotlib import pyplot
#from amuse.plot import loglog, xlabel, ylabel
#X, Y = [], []



def xplot(OTname):
    datafile="%s_newtemp.txt"%(OTname)
    ff=open(datafile, 'r')
    newdataall=ff.readlines()
    print("newdataall=%s"%(newdataall))
    print("To read the para for the plot")
    for f1 in newdataall:
        #f1t = f1.strip()
        #f2t=f1.strip()
        #print(f2t)
        f1t = f1.split()
        #f1t = f2t.strip()
        print(f1t)
        ra = f1t[0]
        dec = f1t[1]
        plx = f1t[2]
        Gmag = f1t[3]
        bprp = f1t[4]
        Teff = f1t[5]
        ra = float(ra)
        dec = float(dec)
        plx = float(plx)
        Gmag = float(Gmag)
        bprp = float(bprp)
        Teff = float(Teff)
        plx = float(plx)
        Realplx = plx
        if plx < 0:
            plx = 0.1
        print(ra)
        print(dec)
        print("plx=%f"%(plx))
        print(Gmag)
        print(bprp)
        print(Teff)
        AbsoMag = Gmag + 5 * log( plx, 10 ) - 10
            #AbsoMag = 18 + 5 * log(30,10) - 10
        print(AbsoMag)
        OTpara = "ra=%9.5f deg\n"\
                "dec=%9.5f deg\n"\
                "Realplx=%f mas\n"\
                "plx=%f mas\n"\
                "Gmag=%f \n"\
                "bprp=%f\n"\
                "teff=%f k\n"\
                "AbsoMag=%f\n"%(ra,dec,Realplx, plx,Gmag,bprp,Teff,AbsoMag)   
        #print("ra=%f,dec=%f,plx=%f,Gmag=%f,bprp=%f,teff=%f"%(ra,dec,plx,Gmag,bprp,Teff))
            #print(f1t)
    

    dataset = np.loadtxt("/home/gwac/software/gaia_dr2_hrd.cat")
    pngfilename="%s_HRD.png"%(OTname)
    OTnametitle = "Hertzsprung-Russell diagram for %s"%(OTname)
    plt.figure(figsize=(8,8))
    plt.title(OTnametitle, fontsize=12)
    plt.ylim(18,-5)
    plt.xlim(-2,6)
    plt.grid(True)
    plt.xlabel('bp-rp')
    plt.ylabel('Absolute G mag')
    plt.annotate(OTpara, (-1.8, 1))
   
    #plt.plot( x , y)
    print(bprp)
    print(AbsoMag)
    
    plt.plot(dataset[:,4], dataset[:,7], 'ro', markersize=0.5)
    plt.plot(bprp, AbsoMag,'bo',markersize=10)
    
    #plt.scatter(dataset[:,4], dataset[:,7], 'ro', s=10)
  

    #plt.show()
    #plt.savefig(pngfilename, format='png', dpi=100)
    plt.savefig(pngfilename, dpi=100)
    return pngfilename

 

def xfindgaiadr2(ra,dec, OTname):
    dec = float(dec)
    ra	= float(ra)
    if dec < 0:
    	radecstr = "%s%s"%(ra,dec)
    else:
    	radecstr = "%s+%s"%(ra,dec)
    print("radecstr=%s"%(radecstr))
    fileout="%s_newtemp.txt"%(OTname)
    aa="/home/gwac/anaconda3/bin/python ~/software/find_gaia_dr2.py -r 2 \"%s\" >gaiaobjlist.txt"%(radecstr)  
    #os.system("mkdir -p %s"%(self.origPreViewDir))
    os.system(aa)
    ff=open("gaiaobjlist.txt",'r')
    objtableall=ff.readlines()
    ff.close()
    #print(np.shape(objtableall))
    #if np.shape(objtableall) > 30:
        #print("have source for the obj")
    objtable65 = objtableall[65:]
    print(objtable65)
    if len(objtable65)>0:
        print("have source for the obj")
        for f0 in objtable65:
            f0t = f0.strip()
            print("@@@@@@@@@")
            print(f0t)
            print("@@@@@@@@@")
            #id  = f0t[0:10]
            ra  = f0t[0:15]
            #era = f0t[16:23]
            dec = f0t[24:36]
            plxReal = f0t[67:78]
            Gmag = f0t[146:154]
            BPRP = f0t[240:247]
            Teff = f0t[262:269]

            if len(ra.strip())==0:
                ra = 0.0
            if len(dec.strip()) == 0:
                dec = 0.0
            if len(plxReal.strip())==0:
                plxReal = 0.1
            #if plxReal < 0:
            #    plxReal=0.1
            if len(Gmag.strip())==0:
                Gmag = 99
            if len(BPRP.strip())==0:
                BPRP = 99
            if len(Teff.strip())==0:
                Teff = 99

            
            aa= "%s %s %s %s %s %s"%(ra,dec,plxReal,Gmag,BPRP,Teff)
            print(aa)
            bb= "ra=%f dec=%f plx=%f Gmag=%f bprp=%f teff=%f"%(float(ra),float(dec),float(plxReal),float(Gmag),float(BPRP),float(Teff))
            print(bb)
            fileout="%s_newtemp.txt"%(OTname)
            #ff=open("newtemp.txt", 'w')
            ff=open(fileout, 'w')
            ff.write(aa)
            ff.close()
            

            break
       #xplot() 
    else:
        print("no any source for this candidate")

   
if __name__=='__main__':
    raput = sys.argv[1]
    decput = sys.argv[2]
    OTname = sys.argv[3]
    print("%s,%s,%s\n"%(raput,decput,OTname))
    xfindgaiadr2(raput,decput, OTname)
    xplot(OTname)
    
