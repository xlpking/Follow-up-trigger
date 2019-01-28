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
#from matplotlib import pyplot
#from amuse.plot import loglog, xlabel, ylabel

def xplot(filein):
    aa

def xgetcat(filein, fileout):
    
   ff=open("gaiaobjlist.txt","r")
   ftmp1=ff.readlines()
   ff.close()
   ff=open(tmpoutput,'w')
   for f0 in ftmp1:
       f0t = f0.strip()
       #id  = f0t[0:10]
       ra  = f0t[0:15]
       era = f0t[16:23]
       plxReal = f0t[67:78]
       Gmag = f0t[146:154]
       BPRP = f0t[237:247]
       Teff = f0t[260:269]
       if len(ra.strip())==0:
           ra=-1
       if len(plxReal.strip())==0:
           plxReal = 0.1
       if plxReal < 0:
           plxReal=0.1
       if len(Gmag.strip())==0:
           Gmag = 99
       if len(BPRP.strip())==0:
           BPRP = 99
       if len(Teff.strip())==0:
           Teff = 99
       print("%s,%s,%s,%s,%s,%s\n"%(ra,era,plxReal,Gmag,BPRP,Teff))
       aa="%s %s %s %s %s %s\n"%(ra,era,plxReal,Gmag,BPRP,Teff)
       ff.write(aa)
       ''' 
       dec = f0t[23:36]
       mag1 = f0t[36:43]
       magB = f0t[168:175]
       magV = f0t[175:182]
       gmag = f0t[182:189]
       rmag = f0t[189:196]
       imag = f0t[196:203]
       if len(imag.strip())==0:
           imag= 99
       sigi= f0t[227:233]
       if len(sigi.strip()) ==0:
          sigi = 99
       if len(magB.strip())==0:
          magB = 99
       if len(magV.strip())==0:
          magV = 99

       if len(gmag.strip())==0:
          gmag = 99

       if len(rmag.strip())==0:
          rmag = 99
       aa= "%11.6f %11.6f %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f % 5.2f\n" %(float(ra),float(dec),float(rmag),float(sigi),float(mag1),float(magB),float(magV),float(gmag),float(imag))
       ff.write(aa)
       '''
   ff.close()

def xfindgaiadr2(ra,dec):
    radecstr = "%s+%s"%(ra,dec)
    print(radecstr)

    aa="python find_gaia_dr2.py -r 2 \"%s\" >gaiaobjlist.txt"%(radecstr)  
    #os.system("mkdir -p %s"%(self.origPreViewDir))
    os.system(aa)
    '''
    print("it will print the line by line")
    idx = 1
    for line in gaia_dr2_out:
        print("%%%%%%%%%%%%")
        print("idx=%d\n"%(idx))
        print(line)
        idx = idx + 1

    print("print is over")
    idx = 1
    for f0 in gaia_dr2_out:
        if idx==66:
            print("the line 66 is %s\n"%(f0))
        idx = idx + 1
    
    objtable = gaia_dr2_out[65:]    #how to only read the 66 line?
    #print(objtable)
    '''
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
                ra=0
            if len(plxReal.strip())==0:
                plxReal = 0.1
            if plxReal < 0:
                plxReal=0.1
            if len(Gmag.strip())==0:
                Gmag = 99
            if len(BPRP.strip())==0:
                BPRP = 99
            if len(Teff.strip())==0:
                Teff = 99

            #AbsoMag = float(mmag) + 5 * log(plx,10)-10
            #aa="%11.6f 11.6f\n"%(float(ra),float(dec))
            aa= "%s %s %s %s %s %s"%(ra,dec,plxReal,Gmag,BPRP,Teff)
            bb= "ra=%s dec=%s plx=%s Gmag=%s bprp=%s teff=%s"%(ra,dec,plxReal,Gmag,BPRP,Teff)
            print(bb)
            ff=open("newtemp.txt", 'w')
            ff.write(aa)
            ff.close()
            ff=open("newtemp.txt", 'r')
            newdataall=ff.readlines()
            print("newdataall=%s"%(newdataall))
            print("@@@@@@@@")
            for f1 in newdataall:
              
                #f1t = f1.strip()
                #f2t=f1.strip()
                #print(f2t)
                f1t = f1.split()
                #f1t = f2t.strip()
                print(f1t)
                plx = f1t[2]
                Gmag = f1t[3]
                bprp = f1t[4]
                Teff = f1t[5]
                print(ra)
                print(dec)
                print(plx)
                print(Gmag)
                print(bprp)
                print(Teff)
                #print("ra=%f,dec=%f,plx=%f,Gmag=%f,bprp=%f,teff=%f"%(ra,dec,plx,Gmag,bprp,Teff))
                #print(f1t)
                '''
                ra = f1t[0]
                dec = f1t[1]
                plx = f1t[2]
                Gmag = f1t[3]
                bprp = f1t[4]
                Teff = f1t[5]
                print("&&&&&&&&&&&")
                print(ra,dec,plx,Gmag,bprp,Teff)
                print("&&&&&&&&&&&")
                print("ra=%f,dec=%f,plx=%f,Gmag=%f,bprp=%f,teff=%f"%(float(ra),dec,plx,Gmag,bprp,Teff))
                break
                '''
 
            break
    else:
        print("no any source for this candidate")
   
if __name__=='__main__':
    tmp = sys.argv[1]
    tmpoutput = sys.argv[2]
    raput = sys.argv[3]
    decput = sys.argv[4]
    xfindgaiadr2(raput,decput)
  #  xgetcat("gaiaobjlist.txt",tmpoutput)
    #xgetcat(tmp, tmpoutput)
   # xplot(tmpoutput)