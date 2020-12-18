# -*- coding: utf-8 -*-

import sys
from astropy.io import fits

#EXTEND=F
def saveSubImg(spath, sname, dpath, dname, boundary):

    CCDSEC="[%d:%d,%d:%d]" % boundary
    BIASSEC="[%d:%d,%d:%d]" % (1,boundary[1]-boundary[0]+1, 1, boundary[3]-boundary[2]+1)
    TRIMSEC=CCDSEC

    hdulist  = fits.open(spath+sname)
    hdu = hdulist[0]
    hdu.data=hdu.data[boundary[2]:boundary[3], boundary[0]:boundary[1]]
    phdr = hdu.header
    phdr.set('CCDSEC',CCDSEC)
    phdr.set('BIASSEC',BIASSEC)
    phdr.set('TRIMSEC',TRIMSEC)
    phdr.set('IMWHOLE',sname)
    phdr.set('EXTEND',False)
    '''
    phdr.set('WCSDIM',2)
    phdr.set('LTM1_1',1)
    phdr.set('LTM2_2',1)
    phdr.set('WAT0_001','system=physical')
    phdr.set('WAT1_001','wtype=linear')
    phdr.set('WAT2_001','wtype=linear')
    phdr.set('XIM',(boundary[2]+boundary[3])/2+500)
    phdr.set('YIM',(boundary[0]+boundary[1])/2+300)
    '''
    #print(phdr)
    hdu.writeto(dpath+dname)
    hdulist.close() 
  
#sys.argv[1]
#spath, sname, dpath, dname, xmin, xmax, ymin, ymax
#!python get_sub_fits.py F:\gwac_data\GWAC\G004_016_170523\ G016_objt_170523T13230377.fit E:\work\program\python\OTRecognition\ G016_objt_170523T13230377_sub.fit  0 400.5 0 100  
if __name__ == '__main__':
    
    if len(sys.argv)!=9:
        print("input should be: python get_sub_fits.py spath, sname, dpath, dname, xmin, xmax, ymin, ymax")
    else:
        #boundary=(2048-100,2048+100,2048-100,2048+100)
        #spath='F:\\gwac_data\\GWAC\\G004_016_170523\\'
        #sname='G016_objt_170523T13230377.fit'
        #dpath='E:\\work\\program\\python\\OTRecognition\\'
        #dname='G016_objt_170523T13230377_sub.fit'
    
        spath=str(sys.argv[1])
        sname=str(sys.argv[2])
        dpath=str(sys.argv[3])
        dname=str(sys.argv[4])
        boundary=(int(float(sys.argv[5])),int(float(sys.argv[6])),int(float(sys.argv[7])),int(float(sys.argv[8])) )
        
        saveSubImg(spath, sname, dpath, dname, boundary)

    
    
    