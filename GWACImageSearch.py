# -*- coding: utf-8 -*-
import numpy as np
import psycopg2
import time
import logging
import os
import math
from astropy.wcs import WCS
from datetime import datetime
import traceback
import sys
#import matplotlib.pyplot as plt
import warnings
from astropy.modeling import models, fitting

#nohup python getOTImgsAll.py > /dev/null 2>&1 &
class GWACWCSIndex:
    
    orgImgRoot = '/data/gwac_data/gwac_orig_fits'
    wcsIdxRoot = '/data/gwac_data/gwac_wcs_idx'
    webServerIP1 = '172.28.8.28:8080'
    webServerIP2 = '10.0.10.236:9995'
    
    connParam={
        "host": "190.168.1.27",
        "port": "5432",
        "dbname": "gwac2",
        "user": "gwac",
        "password": "gdb%980"
        }
    connParam2={
        "host": "172.28.8.28",
        "port": "5432",
        "dbname": "gwac2",
        "user": "gwac",
        "password": "gdb%980"
        }
    connParam3={
        "host": "10.0.3.62",
        "port": "5433",
        "dbname": "gwac2",
        "user": "gwac",
        "password": "gdb%980"
        }
    
    
    def __init__(self):
        
        self.conn = False
        
        self.imgSize = (4136, 4096)
        self.templateImg = 'ti.fit'
        self.tmpRoot="/dev/shm/gwacWCS"
        self.templateDir="%s/tmpl"%(self.tmpRoot)
        if not os.path.exists(self.templateDir):
            os.system("mkdir -p %s"%(self.templateDir))
         
    
    def connDb(self):
        
        self.conn = psycopg2.connect(**self.connParam)
        
    def closeDb(self):
        self.conn.close()
        
    def getDataFromDB(self, sql):
                
        tsql = sql
        #self.log.debug(tsql)
        
        try:
            self.connDb()
    
            cur = self.conn.cursor()
            cur.execute(tsql)
            rows = cur.fetchall()
            cur.close()
            self.closeDb()
        except Exception as err:
            rows = []
            print(" query data error ")
            print(err)
            
        return np.array(rows)
    
    def queryObs(self, cRa, cDec, radius,startDate, endDate):
        
        startDate = startDate.replace('T', ' ')
        endDate = endDate.replace('T', ' ')
        
        halfSearchBox = 13.0/2;
        minDec = cDec-halfSearchBox-radius;
        maxDec = cDec+halfSearchBox+radius;
    
        tsql = "select center_ra, center_dec, left_top_ra, left_top_dec, left_bottom_ra, left_bottom_dec, "\
                "right_top_ra, right_top_dec, right_bottom_ra, right_bottom_dec, ors_id "\
                "from observation_record_statistic "\
                "where has_wcs= true and center_dec>=%f and center_dec<=%f " \
                  "and (( start_obs_time>='%s' and start_obs_time<='%s')  " \
                  "or ( end_obs_time>='%s' and end_obs_time<='%s') " \
                  "or ( start_obs_time<='%s' and end_obs_time>='%s') ) order by date_str desc, cam_id, sky_id" \
                  %(minDec, maxDec, startDate, endDate, startDate, endDate, startDate, endDate);
        #print(tsql)
        return self.getDataFromDB(tsql)
    
    def queryObs2(self, cRa, cDec, radius, maxRecSize=20):
        
        halfSearchBox = 13.0/2
        minDec = cDec-halfSearchBox-radius
        maxDec = cDec+halfSearchBox+radius
    
        tsql = "select center_ra, center_dec, left_top_ra, left_top_dec, left_bottom_ra, left_bottom_dec, "\
                "right_top_ra, right_top_dec, right_bottom_ra, right_bottom_dec, ors_id "\
                "from observation_record_statistic "\
                "where has_wcs= true and center_dec>=%f and center_dec<=%f " \
                  "order by date_str desc, cam_id, sky_id limit %d" \
                  %(minDec, maxDec, maxRecSize)
        #print(tsql)
        return self.getDataFromDB(tsql)
    
    def getImgList(self, orsId, his='_his'):
        
        tsql = "select ff2.img_path "\
            "from fits_file2%s ff2 "\
            "INNER JOIN observation_record_statistic ors on ors.cam_id=ff2.cam_id and  "\
            "ors.sky_id=ff2.sky_id and ors.date_str=to_char(ff2.gen_time, 'YYMMDD') "\
            "WHERE ors.ors_id=%d "\
            "ORDER BY ff2.ff_id"%(his, orsId)
            
        #print(tsql)
        return self.getDataFromDB(tsql)
    
    def getImgList2(self, orsIds):
        
        tstr = ""
        for orsId in orsIds:
            if len(tstr)==0:
                tstr = "%d"%(orsId)
            else:
                tstr = "%s,%d"%(tstr, orsId)
        
        tsql = "select ff2.img_path "\
            "from fits_file2_his ff2 "\
            "INNER JOIN observation_record_statistic ors on ors.cam_id=ff2.cam_id and  "\
            "ors.sky_id=ff2.sky_id and ors.date_str=to_char(ff2.gen_time, 'YYMMDD') "\
            "WHERE ors.ors_id in (%s) "\
            "ORDER BY ff2.ff_id"%(tstr)
            
        #print(tsql)
        return self.getDataFromDB(tsql)
    
    def getObsListDetail(self, orsId, his='_his'):
                
        tsql = "select ors.date_str, osky.sky_name, cam.name, ors.start_obs_time, ors.end_obs_time, ors.real_img_num, ff2.img_name  "\
            "from  observation_record_statistic ors  "\
            "INNER JOIN observation_sky osky on ors.sky_id = osky.sky_id  "\
            "INNER JOIN camera cam on cam.camera_id=ors.cam_id  "\
            "INNER JOIN observation_record_statistic_wcs orsWcs on orsWcs.ors_id=ors.ors_id  "\
            "INNER JOIN fits_file2%s ff2 on ff2.ff_id=orsWcs.ff_id  "\
            "WHERE ors.ors_id=%d  "\
            "ORDER BY ors.ors_id desc"%(his, orsId)
            
        #print(tsql)
        return self.getDataFromDB(tsql)
    
    def getObsListDetail2(self, orsIds, his='_his'):
        
        tstr = ""
        for orsId in orsIds:
            if len(tstr)==0:
                tstr = "%d"%(orsId)
            else:
                tstr = "%s,%d"%(tstr, orsId)
        
        tsql = "select ors.date_str, osky.sky_name, cam.name, ors.start_obs_time, ors.end_obs_time, ors.real_img_num, ff2.img_name  "\
            "from  observation_record_statistic ors  "\
            "INNER JOIN observation_sky osky on ors.sky_id = osky.sky_id  "\
            "INNER JOIN camera cam on cam.camera_id=ors.cam_id  "\
            "INNER JOIN observation_record_statistic_wcs orsWcs on orsWcs.ors_id=ors.ors_id  "\
            "INNER JOIN fits_file2%s ff2 on ff2.ff_id=orsWcs.ff_id  "\
            "WHERE ors.ors_id in (%s)  "\
            "ORDER BY ors.ors_id desc"%(his, tstr)
            
        #print(tsql)
        return self.getDataFromDB(tsql)

def wcs2plane(raD,decD, raD0, decD0):
    
    D2R = math.pi/180.0
    ra0 =  raD0*D2R
    dec0 = decD0*D2R
    ra =  raD*D2R
    dec = decD*D2R
    
    j = 0
    tiny = 1e-6;

    sdec0 = math.sin(dec0);
    sdec = math.sin(dec);
    cdec0 = math.cos(dec0);
    cdec = math.cos(dec);
    radif = ra - ra0;
    sradif = math.sin(radif);
    cradif = math.cos(radif);

    denom = sdec * sdec0 + cdec * cdec0*cradif;

    if denom > tiny:
        j = 0
    elif denom >= 0.0:
        j = 1
        denom = tiny
    elif denom > -tiny:
        j = 2
        denom = -tiny;
    else:
        j = 3

    xi = cdec * sradif / denom;
    eta = (sdec * cdec0 - cdec * sdec0 * cradif) / denom;

    return xi, eta, j
            
def polynomialFit(dataOi, dataTi, degree=3):
        
    oix = dataOi[:,0]
    oiy = dataOi[:,1]
    tix = dataTi[:,0]
    tiy = dataTi[:,1]
    
    p_init = models.Polynomial2D(degree)
    fit_p = fitting.LevMarLSQFitter()
    
    with warnings.catch_warnings():
        # Ignore model linearity warning from the fitter
        warnings.simplefilter('ignore')
        tixp = fit_p(p_init, oix, oiy, tix)
        tiyp = fit_p(p_init, oix, oiy, tiy)
        
    return tixp, tiyp

def getGreatCircleDistance(ra1, dec1, ra2, dec2):
    rst = 57.295779513 * math.acos(math.sin(0.017453293 * dec1) * math.sin(0.017453293 * dec2)
            + math.cos(0.017453293 * dec1) * math.cos(0.017453293 * dec2) * math.cos(0.017453293 * (math.fabs(ra1 - ra2))));
    return rst


def planProject(cRa, cDec, radius, startDate='', endDate='', getImgs='false', getSkys='true'):
    
    maxSearchBox = 12.5 * 1.414 / 2;
    
    width = 4096
    height = 4136
    imgXY = []
    imgXY.append((width/2,height/2))
    imgXY.append((0,0))
    imgXY.append((0,height-1))
    imgXY.append((width-1,height-1))
    imgXY.append((width-1,0))
    imgXY = np.array(imgXY)
    
    wcsIdx = GWACWCSIndex()
    if len(startDate)>5 and len(endDate)>5:
        tdatas = wcsIdx.queryObs(cRa, cDec, radius, startDate, endDate)
    else:
        tdatas = wcsIdx.queryObs2(cRa, cDec, radius)
        
    #print("query database, get %d records"%(tdatas.shape[0]))
    
    searchList = []
    for td in tdatas:
        
        ctrDis = getGreatCircleDistance(cRa, cDec, td[0],td[1])
        #print("cra1=%f,cdec1=%f,ra2=%f,dec2=%f,dist=%f, max=%f"%(cRa, cDec, td[0],td[1], ctrDis, maxSearchBox))
        if ctrDis<=maxSearchBox:
            transXY = []
            #xi, eta, j = wcs2plane(td[0],td[1], td[0],td[1])
            transXY.append((0,0))
            xi, eta, j = wcs2plane(td[2],td[3], td[0],td[1])
            transXY.append((xi,eta))
            xi, eta, j = wcs2plane(td[4],td[5], td[0],td[1])
            transXY.append((xi,eta))
            xi, eta, j = wcs2plane(td[6],td[7], td[0],td[1])
            transXY.append((xi,eta))
            xi, eta, j = wcs2plane(td[8],td[9], td[0],td[1])
            
            transXY.append((xi,eta))
            transXY=np.array(transXY)
            tixp, tiyp = polynomialFit(transXY, imgXY, 1)
            
            txi00, teta00, j = wcs2plane(cRa, cDec, td[0],td[1])
            #convexHull
            timgX = tixp(txi00, teta00)
            timgY = tiyp(txi00, teta00)
            #print("matchSky: ra=%f, dec=%f, projection: j=%d, imgx=%f, imgy=%f"%(cRa, cDec, j, timgX, timgY))
            
            if timgX>=0 and timgX<=width and timgY>=0 and timgY<=height:
                timgX = timgX+20
                searchList.append([td[10], timgX, timgY])
     
    print("total match %d skys"%(len(searchList)))
    #print(searchList)
    imgList = []
    if len(searchList)>0:
        
        if getImgs=='true':
            theader = '#imgPath, imgX, imgY\n'
            savePath = "imgList_%.5f_%.5f.txt"%(cRa, cDec)
            tfile = open(savePath, 'w')
            tfile.write(theader)
            tnum =0
            for tl in searchList:
                orId = int(tl[0])
                imgX = tl[1]
                imgY = tl[2]
                imgList = wcsIdx.getImgList(orId, '')
                for timg in imgList:
                    tfile.write("%s,%.1f,%.1f\n"%(timg[0], imgX, imgY))
                    tnum = tnum+1
                imgList = wcsIdx.getImgList(orId)
                for timg in imgList:
                    tfile.write("%s,%.1f,%.1f\n"%(timg[0], imgX, imgY))
                    tnum = tnum+1
            tfile.close()
            print("save image list to %s, total %d images."%(savePath, tnum))
        
        if getSkys=='true':
            theader = '#dateStr, skyName, camName, startObsTime, endObsTime, imgNum, templateName, imgX, imgY\n'
            savePath = "obsList_%.5f_%.5f.txt"%(cRa, cDec)
            tfile = open(savePath, 'w')
            tfile.write(theader)
            
            tnum =0
            for tl in searchList:
                orId = int(tl[0])
                imgX = tl[1]
                imgY = tl[2]
                obsList = wcsIdx.getObsListDetail(orId, '')
                for obs in obsList:
                    tfile.write("%s,%s,G%s,%s,%s,%s,%s,%.1f,%.1f\n"%(obs[0],obs[1],obs[2],obs[3],obs[4],obs[5],obs[6],imgX, imgY))
                    tnum = tnum+1
                obsList = wcsIdx.getObsListDetail(orId)
                for obs in obsList:
                    tfile.write("%s,%s,G%s,%s,%s,%s,%s,%.1f,%.1f\n"%(obs[0],obs[1],obs[2],obs[3],obs[4],obs[5],obs[6],imgX, imgY))
                    tnum = tnum+1
            tfile.close()
            print("save observation list to %s, total %d observations."%(savePath, tnum))

#GWACImageSearch.py 72.33214 -8.366754 0.1 2019-10-29T18:02:48 2019-10-31T18:02:48 false true
if __name__ == '__main__':
    
    #cRa = 72.33214
    #cDec = -8.366754
    #radius = 0.1
    #startDate='2019-10-29T18:02:48'
    #endDate='2019-10-31T18:02:48'
    #startDate='2019-10-30T18:01:48'
    #endDate='2019-10-30T18:10:48'
    
    if len(sys.argv)==6:
        cRa = float(sys.argv[1])
        cDec = float(sys.argv[2])
        radius = float(sys.argv[3])
        isGetImgs = sys.argv[4]
        isGetSkys = sys.argv[5]
        startDate=' '
        endDate=' '
        planProject(cRa, cDec, radius, startDate, endDate, isGetImgs, isGetSkys)
    elif len(sys.argv)==8:
        cRa = float(sys.argv[1])
        cDec = float(sys.argv[2])
        radius = float(sys.argv[3])
        startDate= sys.argv[4]
        endDate= sys.argv[5]
        isGetImgs = sys.argv[6]
        isGetSkys = sys.argv[7]
        planProject(cRa, cDec, radius, startDate, endDate, isGetImgs, isGetSkys)
    else:
        print("Notice, only 2 types of parameters are accepted:")
        print("1, GWACImageSearch.py centerRa(degree), centerDec(degree), radius(degree), isGetImgs(true|false), isGetSkys(true|false)")
        print("2, GWACImageSearch.py centerRa(degree), centerDec(degree), radius(degree), startDate(2019-10-31T18:02:48), endDate(2019-10-31T18:02:48), isGetImgs(true|false), isGetSkys(true|false)")
        print("3, In GWAC Data process machine, query G191030_C14687 as an example: /home/gwac/img_diff_xy/anaconda3/envs/imgdiff3/bin/python GWACImageSearch.py 72.33214 -8.366754 0.1 2019-10-29T18:02:48 2019-10-31T18:02:48 false true")
        print("4, Default, this tools can only use in GWAC dome. If you want use this tools in Beijing, change the connParam in function connDb to connParam3.")