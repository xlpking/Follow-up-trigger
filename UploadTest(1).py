# -*- coding: utf-8 -*-
import numpy as np
import os
import cv2
import requests
import traceback
from datetime import datetime
import scipy.ndimage
from PIL import Image

def crossTaskCreate(taskName, crossMethod, serverIP):
    
    mergedR = 0.0167
    mergedMag = 20     
    cvsR = 0.0167  
    cvsMag = 20   
    rc3R = 0.03333  
    rc3MaxMag = 20   
    rc3MinMag = -20  
    minorPlanetR = 0.05  #3arcmin
    minorPlanetMag = 16
    ot2HisR = 0.01
    ot2HisMag = 20
    usnoR1 = 0.016667
    usnoMag1 = 15.5  
    usnoR2 = 0.041667   #degree
    usnoMag2 = 8   #<8mag
    
    try:
        turl = "http://%s:8080/gwebend/crossTaskCreate.action"%(serverIP)
        
        values = {'taskName': taskName, 
                  'mergedR': mergedR, 
                  'mergedMag': mergedMag, 
                  'cvsR': cvsR, 
                  'cvsMag': cvsMag, 
                  'rc3R': rc3R, 
                  'rc3MaxMag': rc3MaxMag, 
                  'rc3MinMag': rc3MinMag, 
                  'minorPlanetR': minorPlanetR, 
                  'minorPlanetMag': minorPlanetMag, 
                  'ot2HisR': ot2HisR, 
                  'ot2HisMag': ot2HisMag, 
                  'usnoR1': usnoR1, 
                  'usnoMag1': usnoMag1, 
                  'usnoR2': usnoR2, 
                  'usnoMag2': usnoMag2, 
                  'crossMethod': crossMethod}
        
        msgSession = requests.Session()
        r = msgSession.post(turl, data=values)
        
        print(r.text)
    except Exception as e:
        tstr = traceback.format_exc()
        print(tstr)
        
def crossTaskUpload(taskName, ftype, path, fnames, serverIP):
    
    try:
        turl = "http://%s:8080/gwebend/crossTaskUpload.action"%(serverIP)
        
        sendTime = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")
        values = {'taskName': taskName, 
                  'fileType': ftype, 
                  'sendTime': sendTime}
        files = []
        
        for tfname in fnames:
            tpath = "%s/%s"%(path, tfname)
            files.append(('fileUpload', (tfname,  open(tpath,'rb'), 'text/plain')))
        
        msgSession = requests.Session()
        r = msgSession.post(turl, files=files, data=values)
        
        print(r.text)
    except Exception as e:
        tstr = traceback.format_exc()
        print(tstr)

def crossTaskUploadTest():
    
    serverIP = '10.36.1.77'
    taskName = '20190425_G21_combine25_1'
    crossMethod = '2'
    
    crossTaskCreate(taskName, crossMethod, serverIP)
     
    ''' '''
    ftype = 'crossOTList'
    path = 'data'
    fnames = ['G021_mon_objt_190421T11580477.cat']
    crossTaskUpload(taskName, ftype, path, fnames, serverIP)
    crossTaskUpload(taskName, ftype, path, fnames, serverIP)
    
    ftype = 'crossOTStamp'
    path = 'data'
    fnames = ['G024_tom_objt_190413T19200211_2_c_c_00005.jpg']
    crossTaskUpload(taskName, ftype, path, fnames, serverIP)
    
        
if __name__ == "__main__":
    
    crossTaskUploadTest()