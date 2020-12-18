# -*- coding: utf-8 -*-

from astropy.io import fits
import numpy as np
import sys

def getBkg(imgData):
    
    bgimg = imgData.copy()
    samples = bgimg.flatten()
    samples.sort()
    chop_size = int(0.1*len(samples))
    maxThr = samples[-chop_size]
    minThr = samples[chop_size]
    bkgSubset = samples[:-chop_size]
    bkg = np.median(bkgSubset)
    bgimg[bgimg>maxThr] = bkg
    rms = np.std(bgimg)
    return bgimg, bkg, rms

def addStar(img, srcPos=(20, 20), dstPos=(20, 20), hssize = 8, scale=1.0):
    
    minX = srcPos[0]-hssize-1
    maxX = srcPos[0]+hssize
    minY = srcPos[1]-hssize-1
    maxY = srcPos[1]+hssize
    
    minX2 = dstPos[0]-hssize-1
    maxX2 = dstPos[0]+hssize
    minY2 = dstPos[1]-hssize-1
    maxY2 = dstPos[1]+hssize
    
    bgimg, bkg, rms = getBkg(img)
    
    target = img[minY:maxY, minX:maxX]-bkg
    
    img[minY2:maxY2, minX2:maxX2] = img[minY2:maxY2, minX2:maxX2] + target*scale
    
    return img

def saveImg(spath, sname, dpath, dname, srcPos, dstPos, hssize, scale):

    hdulist  = fits.open(spath+"/"+sname)
    hdu = hdulist[0]
    timg=addStar(hdu.data, srcPos, dstPos, hssize, scale)
    phdr = hdu.header
    
    new_hdu = fits.PrimaryHDU(timg)
    new_hdu.header=phdr
    
    new_hdu.writeto(dpath+"/"+dname, overwrite=True)
    hdulist.close()
    
if __name__ == '__main__':

    if len(sys.argv)!=11:
        print("input should be: python addStar.py spath sname dpath dname srcX srcY dstX dstY halfWidth fluxScale")
        print("eg: /home/gwac/img_diff_xy/anaconda3/envs/imgdiff3/bin/python addStar.py gwacImage G024_Mon_objt_191203T16220564_align_0100.fit gwacImage abc.fit 41 68 50 20 8 1.5")
    else:
        spath=str(sys.argv[1])
        sname=str(sys.argv[2])
        dpath=str(sys.argv[3])
        dname=str(sys.argv[4])
        srcPos=(int(sys.argv[5]),int(sys.argv[6]))
        dstPos=(int(sys.argv[7]),int(sys.argv[8]))
        hssize=int(sys.argv[9])
        scale=float(sys.argv[10])
        
        saveImg(spath, sname, dpath, dname, srcPos, dstPos, hssize, scale)