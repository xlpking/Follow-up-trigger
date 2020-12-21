# -*- coding: utf-8 -*-
import numpy as np
import psycopg2
import matplotlib.pyplot as plt
import requests
from datetime import datetime, timedelta
import time
import math
import logging
from FollowUp import FollowUp
import os,sys
#sys.path.append(‘/Volumes/Data/Documents/GitHub/Follow-up-trigger’) 
from xreadpara import xplot, xfindgaiadr2


#nohup python getOTImgsAll.py > /dev/null 2>&1 &
class GWACAutoFollowup:
    
    webServerIP1 = '172.28.8.28:8080'
    webServerIP2 = '10.0.10.236:9995'
    
    connParam={
        "host": "190.168.1.27",
        "port": "5432",
        "dbname": "gwac2",
        "user": "gwac",
        "password": "gdb%980"
        }
    # 2 xinglong server
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
    # 4 beijing sever
    connParam4={
        "host": "10.0.10.236",
        "port": "5432",
        "dbname": "gwac2",
        "user": "gwac",
        "password": "gdb%980"
        }
    
    QSciObj = "SELECT so_id, name, obj_ra, obj_dec, mag, status, trigger_status, " \
        "found_usno_r2, found_usno_b2, discovery_time_utc, auto_loop_slow, type " \
        "from science_object where auto_observation=true and status>=1" 
    QFupObj = "SELECT fuo.fuo_id, fuo.fuo_name, fuoType.fuo_type_name " \
        "from follow_up_object fuo " \
        "inner join follow_up_object_type fuoType on fuo.fuo_type_id=fuoType.fuo_type_id " \
        "where fuo.ot_id=%d"
    QFupRec = "SELECT fupObs.auto_loop, fupRec.mag_cal_usno, fupRec.date_utc " \
        "from follow_up_record fupRec " \
        "inner join follow_up_observation fupObs on fupObs.fo_id=fupRec.fo_id "  \
        "where fupRec.filter='R' and fupRec.fuo_id=%d " \
        "order by fupRec.date_utc asc"
    QFupObs = "select limit_mag, expose_duration, auto_loop, process_result from follow_up_observation " \
        "where filter='R' and ot_id=%d and auto_loop=%d ORDER BY fo_id asc "
    QOT2 = "SELECT ot_id, mag, found_time_utc from ot_level2 where name='%s'"
    
    maxExpTime = 150
    #maxExpTime = 100
    maxExpTimeFilter = 80
    maxExpTimeFilter2 = 110
    #maxMonitorTime = 100 #minute, max is 5 hours
    maxMonitorTime = 180 #180 #minute, max is 5 hours
    BjtimeStart = 8
    BjtimeEnd = 15
    
    stage2TriggerDelay = 2.0 #minute  #2
    stage2TriggerDelay1 = 2.0 #minute  #2
    stage3TriggerDelay1 = 1.5 #minute  #2
    stage3TriggerDelay2 = 3 #minute
    stageNTriggerDelay1 = 3 #minute
    stageNTriggerDelay2 = 3 #minute
    #stageNTriggerDelay3 = 3 #minute
    
    #defined stageNTriggerDelay4 in the inner code
    #stageNTriggerDelay4 = (1+self.deltaT) * (fupRecordTime - ot2time).total_seconds()/60.0
    
    stage1MagDiff = 1.2    #no vilid
    stage2MagDiff = 0.2  #0.3
    stageNMagDiff1 = 0.1  #0.2
    stageNMagDiff2 = 0.3
    deltaMagDiffTotal = 0.4
    
    
    deltaT = 2.0
    
    nexttmsghour = 0
    nexttmsgminutes = 0
    Talertmsg = 60.0
    #delayTime_max = 40
    delayTime_max = 100
    
    dirHRDImage = "/home/gwac/software/"
    #dirHRDImage = "/Volumes/Data/Documents/GitHub/Follow-up-trigger"
    
    def __init__(self):
        
        self.conn = False
        self.conn2 = False
        
        self.verbose = True
        self.log = logging.getLogger() #create logger
        self.log.setLevel(logging.DEBUG) #set level of logger
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s") #set format of logger
        logging.Formatter.converter = time.gmtime #convert time in logger to UCT
        filehandler = logging.FileHandler("otFollowup.log", 'w+')
        filehandler.setFormatter(formatter) #add format to log file
        self.log.addHandler(filehandler) #link log file to logger
        if self.verbose:
            streamhandler = logging.StreamHandler() #create print to screen logging
            streamhandler.setFormatter(formatter) #add format to screen logging
            self.log.addHandler(streamhandler) #link logger to screen logging
        
    def connDb(self):
        
        self.conn = psycopg2.connect(**self.connParam4)
        self.dataVersion = ()
        
    def closeDb(self):
        self.conn.close()
        
    def initSciObj(self, ot2Name):
    
        tsql = "update science_object set status=1, trigger_status=1, auto_observation=true where name='%s'"%(ot2Name)
        #self.log.debug(tsql)
        
        try:
            self.connDb()
    
            cur = self.conn.cursor()
            cur.execute(tsql)
            self.conn.commit()
            cur.close()
            self.closeDb()
        except Exception as err:
            self.log.error(" init science_object status error ")
            print(err)
            
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
            self.log.error(" query data error ")
            self.log.error(err)
            
        return rows

    def updateAutoObservationsTrue(self):
        
        tsql = "update science_object set auto_observation=true"
        #self.log.debug(tsql)
        
        try:
            self.connDb()
    
            cur = self.conn.cursor()
            cur.execute(tsql)
            self.conn.commit()
            cur.close()
            self.closeDb()
        except Exception as err:
            self.log.error(" update science_object status error ")
            print(err)

    def updateSciObjStatus(self, soId, status):
        
        tsql = "update science_object set status=%d where so_id=%d"%(status, soId)
        #self.log.debug(tsql)
        
        try:
            self.connDb()
    
            cur = self.conn.cursor()
            cur.execute(tsql)
            self.conn.commit()
            cur.close()
            self.closeDb()
        except Exception as err:
            self.log.error(" update science_object status error ")
            print(err)
            
    def updateSciObjTriggerStatus(self, soId, triggerStatus):
        
        tsql = "update science_object set trigger_status=%d where so_id=%d"%(triggerStatus, soId)
        #self.log.debug(tsql)
        
        try:
            self.connDb()
    
            cur = self.conn.cursor()
            cur.execute(tsql)
            self.conn.commit()
            cur.close()
            self.closeDb()
        except Exception as err:
            self.log.error(" update science_object trigger_status error ")
            self.log.error(err)
            
    def updateSciObjAutoLoopSlow(self, soId, autoLoop):
        
        tsql = "update science_object set auto_loop_slow=%d where so_id=%d"%(autoLoop, soId)
        #self.log.debug(tsql)
        
        try:
            self.connDb()
    
            cur = self.conn.cursor()
            cur.execute(tsql)
            self.conn.commit()
            cur.close()
            self.closeDb()
        except Exception as err:
            self.log.error(" update science_object trigger_status error ")
            self.log.error(err)
            
    def closeSciObjAutoObservation(self, soId):
        
        tsql = "update science_object set auto_observation=false where so_id=%d"%(soId)
        #self.log.debug(tsql)
        
        try:
            self.connDb()
    
            cur = self.conn.cursor()
            cur.execute(tsql)
            self.conn.commit()
            cur.close()
            self.closeDb()
        except Exception as err:
            self.log.error(" update science_object auto_observation error ")
            self.log.error(err)
            
    #fast transient channal for the plot        
    def sendImage007(self, imgPath, imgName):
        print(imgPath)
        try:
            msgURL = "http://%s/gwebend/sendTrigger2WChart.action"%(self.webServerIP2)
            
            fullPath = "%s/%s"%(imgPath, imgName)
            msgSession = requests.Session()
            #mediaType:image,voice,video,file
            data = {'chatId':'gwac007','mediaType':'image'}
            files = {"fileUpload" : (imgName, open(fullPath, "rb"), "image/jpeg")}
            r=msgSession.post(msgURL, data, files=files)
            
            #self.log.debug(r.text)
            msgSession.close()
        except Exception as e:
            self.log.error("send trigger msg error ")
            self.log.error(str(e))                
            
    #usage: self.sendImage('/data/path/of/img','imgPath.png')
    def sendImage(self, imgPath, imgName):
        print(imgPath)
        try:
            msgURL = "http://%s/gwebend/sendTrigger2WChart.action"%(self.webServerIP2)
            
            fullPath = "%s/%s"%(imgPath, imgName)
            msgSession = requests.Session()
            #mediaType:image,voice,video,file
            data = {'chatId':'gwac003','mediaType':'image'}
            files = {"fileUpload" : (imgName, open(fullPath, "rb"), "image/jpeg")}
            r=msgSession.post(msgURL, data, files=files)
            
            #self.log.debug(r.text)
            msgSession.close()
        except Exception as e:
            self.log.error("send trigger msg error ")
            self.log.error(str(e))        

 
    # fast transient 
    def sendTriggerMsg007(self, tmsg):  

        #fast transient channal
        try:
            
            #sendTime = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
            #tmsg = "%s: %s"%(sendTime, tmsg)
            msgURL = "http://%s/gwebend/sendTrigger2WChart.action?chatId=gwac007&triggerMsg="%(self.webServerIP2)
            #msgURL = "http://%s/gwebend/sendTrigger2WChart.action?chatId=gwac003&triggerMsg="%(self.webServerIP2)
            turl = "%s%s"%(msgURL,tmsg)
            #self.log.debug(turl)
            
            msgSession = requests.Session()
            msgSession.get(turl, timeout=10, verify=False)
            
        except Exception as e:
            self.log.error(" send trigger msg error ")
            self.log.error(str(e))

    

 #  follow-up info 
    def sendTriggerMsg005(self, tmsg):

        try:
            
            #sendTime = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
            #tmsg = "%s: %s"%(sendTime, tmsg)
            msgURL = "http://%s/gwebend/sendTrigger2WChart.action?chatId=gwac005&triggerMsg="%(self.webServerIP2)
            #msgURL = "http://%s/gwebend/sendTrigger2WChart.action?chatId=gwac003&triggerMsg="%(self.webServerIP2)
            turl = "%s%s"%(msgURL,tmsg)
            #self.log.debug(turl)
            
            msgSession = requests.Session()
            msgSession.get(turl, timeout=10, verify=False)
            
        except Exception as e:
            self.log.error(" send trigger msg error ")
            self.log.error(str(e))

    
    def sendTriggerMsg(self, tmsg):

        try:
            
            #sendTime = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
            #tmsg = "%s: %s"%(sendTime, tmsg)
            #msgURL = "http://%s/gwebend/sendTrigger2WChart.action?chatId=gwac005&triggerMsg="%(self.webServerIP2)
            msgURL = "http://%s/gwebend/sendTrigger2WChart.action?chatId=gwac003&triggerMsg="%(self.webServerIP2)
            turl = "%s%s"%(msgURL,tmsg)
            #self.log.debug(turl)
            
            msgSession = requests.Session()
            msgSession.get(turl, timeout=10, verify=False)
            
        except Exception as e:
            self.log.error(" send trigger msg error ")
            self.log.error(str(e))
    
    #tobs=[{'filter':['R','B'],'expTime':40,'frameCount':1},{'filter':['R'],'expTime':40,'frameCount':2}]
    def sendObservationCommand(self, sciObj, observes=[],autoLoop=1,lastExpTime=-1, magdiff=0, telescope=1, priority=41):

        try:
            self.log.debug(observes)
            print("observer=%s"%(observes))
            otName = sciObj[1]
            ra = sciObj[2]
            dec = sciObj[3]
            status = sciObj[5]
            for tobs in observes:
                #print(tobs)
                tfilters = tobs['filter']
                print("tfilters=%s"%(tfilters))
                if lastExpTime>0 and magdiff>=0:
                    if lastExpTime<self.maxExpTime:
                        expTime = int(lastExpTime * math.exp(0.4*magdiff))
                        if expTime>self.maxExpTime:
                            expTime = self.maxExpTime

                    else: # if expTime exceed maxExpTime, return false and stop observation   #is it volid? xlp
                        return True
                elif lastExpTime == self.maxExpTime and magdiff == -1:
                    return True
                else:
                    expTime = tobs['expTime']
                    
                if expTime>self.maxExpTimeFilter and magdiff< 0.2:
                    tfilters = ['R']
                
                if expTime>self.maxExpTimeFilter2:
                    tfilters = ['R']
                
                frameCount = tobs['frameCount']
                print("again tfilters=%s"%(tfilters))
                for tf in tfilters:
                    tfilter = tf    #xlp only B no R？
                    print("tfilter=%s"%(tfilter))
                    idxFC = 0
                    while idxFC < frameCount:
                        #fup = FollowUp(ra,dec,expTime,tfilter,frameCount,otName, telescope, priority)
                        frameCountSingle = 1
                        fup = FollowUp(ra,dec,expTime,tfilter,frameCountSingle,otName, telescope, priority)
                        self.log.debug(fup.getFollowUpString())
                        fup.uploadFollowUpCommond(autoLoop)   #to send the request of follow-up
                        tmsg="Followup request: status=%d RA=%.5f DEC=%.5f exptime=%d " \
                        "filter=%s frameCount=%d OTname=%s, telescope=%d, priority=%d\n"%(status, ra,dec,expTime,tfilter,frameCountSingle,otName, telescope, priority)
                        print(tmsg)
                        self.sendTriggerMsg005(tmsg)
                        #tmsg="debug infor: status=%d RA=%.5f DEC=%.5f lastExpTime=%d " \
                        #"filter=%s frameCount=%d OTname=%s, magDiff=%.5f, priority=%d\n"%(status, ra,dec,lastExpTime,tfilter,frameCount,otName, magdiff, priority)
                        #print(tmsg)                
                        #self.sendTriggerMsg005(tmsg)
                        idxFC = idxFC + 1
                    
        except Exception as e:
            self.log.error("sendObservationCommand error")
            self.log.error(e)
            
        return False


    def ra2hour(self, RAD):
        # convert the RA DEC in degree to hour format
        #==================================
        hh = RAD//15
        mmss = RAD/15 - hh
        mmss1 = mmss * 60
        mm = math.floor(mmss1)
        ss = (mmss1 - mm) * 60
        RA_Hour="%.2d:%.2d:%.3f"%(hh,mm,ss)
        print("RA=%s"%(RA_Hour))
        return RA_Hour
    
    
    def dec2hour(self, DEC):
        dd = math.floor(DEC)
        MMSS = (DEC - dd) * 60
        MM = math.floor(MMSS)
        SS = (MMSS - MM) * 60
        DEC_Hour="%.2d:%.2d:%.3f"%(dd,MM,SS)
        print("DEC=%s"%(DEC_Hour))
        return DEC_Hour
            #==================================


    
    #debug, info, warn, error
    def autoFollowUp(self):

        bjtimehour = int(time.strftime('%H',time.localtime(time.time())))
        bjtimeminute = int(time.strftime('%M',time.localtime(time.time())))  
        print("Beijing hour is %d, Beijng minutes is %d"%(bjtimehour,  bjtimeminute))
       
        delayMinutes = math.fabs((bjtimehour + bjtimeminute/60 - self.nexttmsghour - self.nexttmsgminutes/60)*60.0)
        print("%.2f"%(delayMinutes))  
        
        if bjtimehour>=self.BjtimeStart  and bjtimehour<self.BjtimeEnd:  
            if delayMinutes  >= self.Talertmsg:  
                if bjtimeminute < 10:
                    tmsg="Beijing time is %d:0%d:00, day time, will sleep for %d min, and then try again"%(bjtimehour,bjtimeminute, self.Talertmsg)
                else: 
                    tmsg="Beijing time is %d:%d:00, day time, will sleep for %d min, and then try again"%(bjtimehour,bjtimeminute, self.Talertmsg)
                print(tmsg)
                self.sendTriggerMsg005(tmsg)
                self.nexttmsgminutes = bjtimeminute
                self.nexttmsghour = bjtimehour
            return
        elif bjtimehour != self.nexttmsghour:
                tmsg="Beijing time (hour) is %d, working time,  next alive msg will be one hour later"%(bjtimehour)
                print(tmsg)
                self.sendTriggerMsg005(tmsg)
                self.nexttmsghour = bjtimehour 
        else:
            print("=====working time===")
            
        #so_id, name, point_ra, point_dec, mag, status, trigger_status, 
        #found_usno_r2, found_usno_b2, discovery_time_utc, auto_loop_slow, type
        sciObjs = self.getDataFromDB(self.QSciObj)
        self.log.debug("found %d sciObjs"%(len(sciObjs)))
        print("!!!!!!!!!!   1")
        print(sciObjs)
        print("~~~~~~~~~~  2 ")
        for sciObj in sciObjs:
            print("=======")
            print(sciObj)
            a0 = sciObj[0] #line
            a1 = sciObj[1] #OT name
            RAD = sciObj[2] # RA deg
            DEC = sciObj[3] # DEC deg 
            a4 = sciObj[4] # R mag
            a11 = sciObj[11]
            a9 = sciObj[9]
            print(a0)
            print(a1)
            print(RAD)
            print(DEC)
            print(a4)
            print(a11)
            print(a11[0:3])
            if a11[0:3] ==  "CAT":     
                OTFlag = "Transient Candidate"
                Fdiffmag = sciObj[4] - sciObj[7]
            else:
                OTFlag = "OT Candidate"
                Fdiffmag = sciObj[4] - 19   #19 is the limit mag for USNO B1.0
                
            print("OTFlag=%s"%(OTFlag))
            print("Fdiffmag=%.2f"%(Fdiffmag))
            print("obstime=%s"%(a9))
            print("hahahhahahha sdfasdfasfd")
            print("=======")
            status = sciObj[5] #status=1
            triggerStatus = sciObj[6] #trigger_status=1
            
            
            RA_Hour = self.ra2hour(RAD)
            DEC_Hour = self.dec2hour(DEC)
            
            
            foundTime = sciObj[9]
            curDateTime = datetime.utcnow()
            diffMinutes = (curDateTime - foundTime).total_seconds()/60.0 
            ot2Name = sciObj[1]
            if diffMinutes > self.maxMonitorTime:
                print("Time is out")
                self.closeSciObjAutoObservation(sciObj[0])
                self.log.warning("%s, %.2f exceed max monitor time(%dminutes), close monitor."%(ot2Name, diffMinutes, self.maxMonitorTime))
            
            
            print("hahahhahahha")
            tsql = self.QOT2%(ot2Name)
            ot2s = self.getDataFromDB(tsql)
            if len(ot2s)==0:
                print("hahahhahahha sdfasdfasfd")
                self.log.debug("cannot find ot2 %s"%(ot2Name))
                #self.closeSciObjAutoObservation(sciObj[0])
                continue 
           
            ot2=ot2s[0]
            
            self.log.debug("ot2: %s, status: %d, triggerStatus: %d"%(ot2Name, status, triggerStatus))
            
            
            foundTime = sciObj[9]
            print(foundTime)
            #time.sleep(5)
            #curDateTime = datetime.now()
            curDateTime = datetime.utcnow()
            print("   1 curDatetime=%s"%(curDateTime))
            #curDateTime.replace(hour=curDateTime.hour-8)
            print("curDatetime=%s"%(curDateTime))
            diffMinutes = (curDateTime - foundTime).total_seconds()/60.0
            print("diffMinutes= %f"%(diffMinutes))
            
            fadingslope= math.fabs( sciObj[4] - ot2[1] )/diffMinutes
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$4-----1")
            print("GWAC discovery time %s in UT "%(ot2[2]))
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$4-----2")
            #The diffMinutes shall be calculated by FoundTime and observed time for the first time of follow-ups
            print("fadingslope=%.2f calculated by the GWAC mag %.2f and 60cm mag %.2f "%(fadingslope, ot2[1], sciObj[4]))
                
            if status == 1:
                
                if diffMinutes < self.maxMonitorTime:
                    print("The delay is accepted")
                    if triggerStatus == 1:
                        tmsg = "New Auto Trigger 60CM Telescope:\n" \
                           "%s %s Stage1.\n" \
                           " \n"\
                           "gwacDiscoveryTime: %s UT\n"\
                           "60cmfirstobsTime: %s UT\n"\
                           "\n"\
                           "gwacMag: %.2f\n"\
                           "60cmfirstObsMag: %.2f\n" \
                           " \n"\
                           "usno R2 : %.2f\n"\
                           "usno B-R: %.2f\n" \
                           " \n"\
                           "RA(deg): %f \n"\
                           "DEC(deg): %f \n"\
                           "RA(J2000): %s \n"\
                           "DEC(J2000): %s \n"\
                           " \n"\
                           "The amplitude is more than %.2f  relative to USNO \n" \
                           "This is one %s"\
                           " \n"\
                           "The link is  http://www.gwac.top/gwac/gwac/pgwac-ot-detail2.action?otName=%s"%(sciObj[1],sciObj[11], ot2[2], sciObj[9], ot2[1], sciObj[4],sciObj[7],sciObj[8]-sciObj[7], RAD, DEC, RA_Hour, DEC_Hour, Fdiffmag, OTFlag, sciObj[1])
                        self.log.debug(tmsg)
                        self.sendTriggerMsg(tmsg)
                        self.updateSciObjTriggerStatus(sciObj[0], status+1)
                        tmsg = "The delay time for the next request of follow-up is %s minutes"%(self.stage2TriggerDelay)
                        self.sendTriggerMsg005(tmsg)
                        if fadingslope > 2:
                            tmsg = "It is possible a fake transient for %s with the fading slope of %.2f mag per minutes \n" \
                            "estimated by GWAC mag of %.2f and the mag of %.2f by 60cm first obs.\n"\
                            "during the time between %s and %s "%(sciObj[1], fadingslope, ot2[1],sciObj[4], foundTime, curDateTime)
                            self.sendTriggerMsg005(tmsg)
                            #self.closeSciObjAutoObservation(sciObj[0])


       

                        fileout="%s_newtemp.txt"%(sciObj[1])
                        pngfilename="%s_HRD.png"%(sciObj[1])
                        print("To find xfindgaiadr2")
                        print("RA=%s, DEC=%s, name=%s\n"%(RAD,DEC, sciObj[1]))
                        xfindgaiadr2(RAD, DEC, sciObj[1])
                        print("To find xfindgaiadr2------------over----")
                        if os.access(fileout, os.F_OK):
                            print("Given file path %s is exist"%(fileout))
                            pngfile=xplot(sciObj[1])
                            #time.sleep(5)
                            if pngfile:
                                self.sendImage(self.dirHRDImage, pngfilename)
                                print("will send the figure %s to the wechat"%(pngfilename))
                            else:
                                print("there is not %s"%(pngfilename))
                                tmsg="Have read the data from Gaia dr2, however, there is no %s"%(pngfilename)
                                self.sendTriggerMsg(tmsg)
                        else:
                            print("%s is not exist"%(fileout))
                            tmsg="Can not get the data from Gaia dr2, %s is not exist"%(fileout)
                            self.sendTriggerMsg(tmsg)
                            
                        dwarfnovaFlag="%s_DwarfnovaFlag.txt"%(sciObj[1])
                        print("============%s=========="%(dwarfnovaFlag))
                        if os.access(dwarfnovaFlag, os.F_OK):
                            print("Dwarfnova file is exist for status = 1")
                            ffdw=open(dwarfnovaFlag, 'r')
                            newdataalldw=ffdw.readlines()
                            for f1dw in newdataalldw:
                                f1t = f1dw.split()
                                xDwarfnovaValue = f1t[0]                     
                                if xDwarfnovaValue == "YES":
                                    OTFlag = "DN candidate"
                                else:
                                    OTFlag  = "Variable candiate"
                            tmsg="%s is a %s"%(sciObj[1], OTFlag)
                            self.sendTriggerMsg(tmsg)
                        else:
                            print("%s is not exist for status=1"%(dwarfnovaFlag))
                            tmsg="Can not tell the classification, %s is not exist for status=1"%(dwarfnovaFlag)
                            self.sendTriggerMsg(tmsg)
                    
                    if diffMinutes>self.stage2TriggerDelay:
                        print("diffMinutes=%s"%(diffMinutes))
                        tobs=[{'filter':['B','R'],'expTime':30,'frameCount':1}]
                        #print("tobs=%s"%(tobs))
                        #time.sleep(5)
                        
                        isExceedMaxTime = self.sendObservationCommand(sciObj, tobs, autoLoop=2)
                        
                        #if isExceedMaxTime:
                        #    self.closeSciObjAutoObservation(sciObj[0])
                        #    self.sendTriggerMsg("%s expTime exceed %d seconds, stop observation."%(ot2Name, self.maxExpTime))
                        self.updateSciObjStatus(sciObj[0], 2)
                        #if a11[0:3] ==  "CAT":
                        #file2 = open('/home/gwac/software/GWAC_OT3.txt', 'w') 
                        #writeline = "%s %f %f\n"%(sciObj[1], RAD, DEC)
                        #file2.write(writeline)
                        #file2.close()
                else: # exceed max monitor time, do not monitor this sciobj anymore
                    print("Time is out")
                    self.closeSciObjAutoObservation(sciObj[0])
                    self.log.warning("%s, %.2f exceed max monitor time(%dminutes), close monitor."%(ot2Name, diffMinutes, self.maxMonitorTime))
                    
            elif status > 1:

                dwarfnovaFlag="%s_DwarfnovaFlag.txt"%(sciObj[1])
                if os.access(dwarfnovaFlag, os.F_OK):
                    print("Dwarfnova file is exist for status >1 ")
                    ffdw=open(dwarfnovaFlag, 'r')
                    newdataalldw=ffdw.readlines()
                    for f1dw in newdataalldw:
                        f1t = f1dw.split()
                        xDwarfnovaValue = f1t[0]                     
                        if xDwarfnovaValue == "YES ":
                            OTFlag = "DN candidate"
                        else:
                            OTFlag  = "Variable candiate"
                    print("TOFlag=%s for status >2 "%(OTFlag))        
                else:
                    print("%s is not exist for status >1"%(dwarfnovaFlag))
                    OTFlag = "Transient candidate"
                    #tmsg="Can not tell the classification, %s is not exist for status >1"%(dwarfnovaFlag)
                    #self.sendTriggerMsg(tmsg)

                                
                ot2Id = ot2[0]
                        
                tsql = self.QFupObs%(ot2Id, status)
                #tsql = self.QFupObs%(ot2Id)
                #limit_mag
                fupObserves = self.getDataFromDB(tsql)
                if len(fupObserves)==0:
                    self.log.debug("cannot find fupObserves %s"%(ot2Name))
                    continue
                print(fupObserves)
                lastLimitMag = fupObserves[0][0]
                processResult = fupObserves[0][3]
                print("lastLimitmag=%s, processResult=%s"%(lastLimitMag, processResult))                 
                if lastLimitMag is None or processResult==0:     # no limit obtained from follow-up in the DB, "None is not a srting", 
                    #processResult is the flag of the results, 0 menas that DB have not got the results of the data processing
                    lastLimitMag = 18.0
                    #continue
                
                lastExpTime = fupObserves[0][1]
                #print("===========xinliping============")
                print("lastLimitMag = %.2f\n"%(lastLimitMag))
                
                tsql = self.QFupObj%(ot2Id)
                #fuo_id, fuo_name, fuo_type_name
                fupObjs = self.getDataFromDB(tsql)
                print(fupObjs)
                
                for fupObj in fupObjs:
                    print("check,mini,catas")
                    #print(fupObj)
                    print("fupObj[1]=%s, sciObj11=%s"%(fupObj[1],sciObj[11]))
                    if fupObj[1] != sciObj[11]:   #sciObj[11] is the object whose brightness is changed by more then 1.2 mag or it is a miniOT for twice.
                        continue
                    fuoId = fupObj[0]
                    tsql = self.QFupRec%(fuoId)
                    print(tsql)
                    #auto_loop, mag_cal_usno, date_utc
                    fupRecords = self.getDataFromDB(tsql)
                    print(fupRecords)
                    fupRecords = np.array(fupRecords)
                    print(" to print funRecords ")
                    print(fupRecords)
                    print(fupRecords.shape)
                    print(fupRecords[:5])
                    #break
                #    status = 2
                    fupRecordN = fupRecords[fupRecords[:,0]==status]
                    fupRecordN1 = fupRecords[fupRecords[:,0]==(status-1)]             
                    
                    print("To print fupRecordN")
                    print(fupRecordN)
                    print("To print fupRecordN1")
                    print(fupRecordN1)
                    print("============over====")
                    print(fupRecordN.shape[0])  
                    print(fupRecordN1.shape[0])
                    print("============over1====")
                    #if find object in Nth folllow
                    if fupRecordN.shape[0]>0 and fupRecordN1.shape[0]>0:
                        print("TSESFDE")
                        fupRecordN = fupRecordN[0]
                        fupRecordN1 = fupRecordN1[0]
                        
                        magDiff = math.fabs(fupRecordN[1]-fupRecordN1[1])
                        #magDiffTotalslope  = math.fabs(fupRecordN[1]-sciObj[4])/status
                        Diff_all = math.fabs(fupRecordN[1]-sciObj[4])
                        observeTime = fupRecordN[2]
                        foundTime = sciObj[9]
                        #curDateTime = datetime.now()
                        curDateTime = datetime.utcnow()
                        #curDateTime.replace(hour=curDateTime.hour-8)
                        #diffMinutes = (curDateTime - foundTime).total_seconds()/60.0
                        diffMinutes = (curDateTime - observeTime).total_seconds()/60.0
                        
                        print("3 diffMinutes=%.2f"%(diffMinutes))
                        if diffMinutes < self.maxMonitorTime:         
                            if status == 2:
                                if magDiff>=self.stage2MagDiff:
                                    priority = 41
                                    if triggerStatus == status:
                                        tmsg = "Auto Trigger 60CM Telescope:\n" \
                                           "The %s :\n"\
                                            "%s %s Stage%d.\n" \
                                            " \n" \
                                           "gwacDiscoveryTime: %s UT\n"\
                                           "60cmfirstobsTime: %s  UT\n"\
                                           "\n"\
                                           "gwacMag: %.2f\n"\
                                           "60cmfirstObsMag: %.2f\n60cmlastObsMag: %.2f\n" \
                                           " \n" \
                                           "usno R2:  %.2f\n"\
                                           "usno B-R: %.2f\n" \
                                           " \n"\
                                           "RA(deg): %f \n"\
                                           "DEC(deg): %f \n"\
                                           "RA(J2000): %s \n"\
                                           "DEC(J2000): %s \n"\
                                           " \n" \
                                           "DeltaMag during the whole obs by %.2f\n"\
                                           "DeltaMag during the last two epochs is %.2f\n"\
                                           "\n"\
                                           "The link is  http://www.gwac.top/gwac/gwac/pgwac-ot-detail2.action?otName=%s"\
                                           %(OTFlag,sciObj[1],sciObj[11],status, ot2[2], sciObj[9], ot2[1], sciObj[4], fupRecordN[1], sciObj[7], sciObj[8]-sciObj[7], RAD, DEC, RA_Hour, DEC_Hour,  fupRecordN[1] - sciObj[4], magDiff,sciObj[1])
                                        self.sendTriggerMsg(tmsg)
                                        self.updateSciObjTriggerStatus(sciObj[0], status+1)
                                        self.sendTriggerMsg007(tmsg)
                                        

                                        pngfilename="%s_HRD.png"%(sciObj[1])
                                        if pngfilename:
                                            self.sendImage007(self.dirHRDImage, pngfilename)
                                            print("will send the figure %s to the wechat"%(pngfilename))
                                        else:
                                            print("there is not %s"%(pngfilename))
                                            tmsg="Have read the data from Gaia dr2, however, there is no %s"%(pngfilename)
                                            self.sendTriggerMsg(tmsg)
  
                                        tmsg = "The delay time for the next request of follow-up is %s minutes"%(self.stage3TriggerDelay1)
                                        self.sendTriggerMsg005(tmsg)
                                            
                                   # if diffMinutes>self.stage3TriggerDelay1:
                                    if diffMinutes > 0:
                                        tobs=[{'filter':['B'],'expTime':40,'frameCount':1},
                                               {'filter':['R'],'expTime':40,'frameCount':3}   
                                               ]
                                        isExceedMaxTime = self.sendObservationCommand(sciObj, tobs, status+1, lastExpTime, magDiff, 1, priority)
                                       # if isExceedMaxTime:
                                       #     self.closeSciObjAutoObservation(sciObj[0])   
                                       #     self.sendTriggerMsg("%s expTime exceed %d seconds, stop observation."%(ot2Name, self.maxExpTime))
                                       #     break
                                        self.updateSciObjStatus(sciObj[0], status+1)
                                    break
                                else:
                                    priority = 40
                                    coloraccess = sciObj[8]-sciObj[7]
                                    #if coloraccess > 2:
                                    #    OTFlag = "Variable candidate"
                                    #if coloraccess < 0.5:
                                    #    OTFlag = "DN candidate"    
                                    if triggerStatus == status:
                                        self.sendTriggerMsg("The %s %s %s Stage%d, magDiff: %.2f, obtained by %.2f and %.2f during the last two epochs"%(OTFlag, sciObj[1],sciObj[11],status, magDiff, fupRecordN[1],fupRecordN1[1]))
                                        self.updateSciObjTriggerStatus(sciObj[0], status+1)
                                    if diffMinutes>self.stage3TriggerDelay2:
                                        tobs=[{'filter':['B','R'],'expTime':30,'frameCount':1}]
                                        isExceedMaxTime = self.sendObservationCommand(sciObj, tobs, status+1, lastExpTime, magDiff, 1, priority)
                                        #if isExceedMaxTime:
                                        #    self.closeSciObjAutoObservation(sciObj[0])
                                        #    self.sendTriggerMsg("%s expTime exceed %d seconds, stop observation."%(ot2Name, self.maxExpTime))
                                        #    break
                                        self.updateSciObjStatus(sciObj[0], status+1)
                                        self.updateSciObjAutoLoopSlow(sciObj[0], status-1)
                                        #self.updateSciObjTriggerStatus(sciObj[0], status+1)
                                    break
                            elif status > 2:
                                print("status >2")
                                #if magDiff>=self.stageNMagDiff1 and magDiffTotalslope >=self.deltaMagDiffTotal:
                                if magDiff>=self.stageNMagDiff1 and Diff_all >=self.deltaMagDiffTotal:     
                                    priority = 41
                                    if triggerStatus == status:
                                        tmsg = "Auto Trigger 60CM Telescope:\n" \
                                           "The %s :\n" \
                                           "%s %s Stage%d.\n" \
                                           " \n" \
                                           "gwacDiscoveryTime: %s UT\n"\
                                           "60cmfirstobsTime: %s UT\n"\
                                           "\n"\
                                           "gwacMag: %.2f\n"\
                                           "60cmfirstObsMag: %.2f\n60cmlastObsMag: %.2f\n" \
                                           " \n" \
                                           "usno R2:  %.2f\n"\
                                           "usno B-R: %.2f\n" \
                                           " \n"\
                                           "RA(deg): %f \n"\
                                           "DEC(deg): %f \n"\
                                           "RA(J2000): %s \n"\
                                           "DEC(J2000): %s \n"\
                                           " \n" \
                                           "DeltaMag during the whole obs by %.2f\n"\
                                           "DeltaMag during the last two epochs is %.2f\n"%(OTFlag,  sciObj[1],sciObj[11],status, ot2[2], sciObj[9], ot2[1], sciObj[4], fupRecordN[1], sciObj[7], sciObj[8]-sciObj[7], RAD, DEC, RA_Hour, DEC_Hour, fupRecordN[1] - sciObj[4], magDiff)
                                        self.sendTriggerMsg(tmsg)
                                        self.updateSciObjTriggerStatus(sciObj[0], status+1)
                                        self.sendTriggerMsg007(tmsg)
                                    #if diffMinutes>self.stageNTriggerDelay1:
                                    if diffMinutes>0:
                                        tobs=[{'filter':['B'],'expTime':40,'frameCount':1},
                                               {'filter':['R'],'expTime':40,'frameCount':6}
                                               ]
                                        isExceedMaxTime = self.sendObservationCommand(sciObj, tobs, status+1, lastExpTime, magDiff, 1, priority)
                                        #if isExceedMaxTime:
                                        #    self.closeSciObjAutoObservation(sciObj[0])
                                        #    self.sendTriggerMsg("%s expTime exceed %d seconds, stop observation."%(ot2Name, self.maxExpTime))
                                        #    break
                                        self.updateSciObjStatus(sciObj[0], status+1)
                                    break
                                else:
                                    priority = 40
                                    print("magDiff is small")
                                    autoLoopIdx = sciObj[10]
                                    print(autoLoopIdx)
                                    print("AAAAAAAAAA")
                                    
                                    fupRecordNk = fupRecords[fupRecords[:,0]==autoLoopIdx]
                                    print(fupRecordNk)
                                    #fupRecordNk = fupRecordNk[1]  #whiat is the fupRecordNk[1] and fupRecordNk[2]
                                    print("BBB")
                                    print(fupRecordNk[0][1])
                                    #print(fupRecordNk[0,1])
                                    magDiffK = math.fabs(fupRecordN[1]-fupRecordNk[0][1])
                                    print("magDiffK=%.2f"%(magDiffK))
                                    #self.sendTriggerMsg005("%s %.2f\n"%(sciObj[1],magDiffK))
                                    #if magDiffK>=self.stageNMagDiff2 and magDiffTotalslope>=self.deltaMagDiffTotal:
                                    if magDiffK>=self.stageNMagDiff2:
                                        priority = 41
                                        if triggerStatus == status:
                                            tmsg = "Auto Trigger 60CM Telescope:\n" \
                                               "The %s :\n"\
                                               "%s %s Stage%d.\n" \
                                               " \n" \
                                               "gwacDiscoveryTime: %s UT\n"\
                                               "60cmfirstobsTime: %s UT\n"\
                                               "\n"\
                                               "gwacMag:  %.2f\n"\
                                               "60cmfirstObsMag: %.2f\n60cmlastObsMag: %.2f\n" \
                                               " \n" \
                                               "usno R2: %.2f\n"\
                                               "usno B-R: %.2f\n" \
                                               " \n" \
                                               "RA(deg): %f \n"\
                                               "DEC(deg): %f \n"\
                                               "RA(J2000): %s \n"\
                                               "DEC(J2000): %s \n"\
                                               " \n"\
                                               "DeltaMag during the whole obs by %.2f\n"\
                                               "DeltaMag during the loop is %.2f\n"%(OTFlag, sciObj[1],sciObj[11],status, ot2[2], sciObj[9], ot2[1], sciObj[4], fupRecordN[1], sciObj[7], sciObj[8]-sciObj[7], RAD, DEC, RA_Hour, DEC_Hour, fupRecordN[1] - sciObj[4], magDiffK)
                                            self.sendTriggerMsg(tmsg)
                                            self.updateSciObjTriggerStatus(sciObj[0], status+1)
                                            self.sendTriggerMsg007(tmsg)
                                        if diffMinutes>self.stageNTriggerDelay2:
                                        #if diffMinutes>0:  
                                            #tobs=[{'filter':['B','R'],'expTime':30,'frameCount':2}]
                                            tobs=[{'filter':['B'],'expTime':40,'frameCount':1},
                                               {'filter':['R'],'expTime':40,'frameCount':6}
                                               ]
                                            isExceedMaxTime = self.sendObservationCommand(sciObj, tobs, status+1, lastExpTime, magDiffK, 1, priority)
                                          #  if isExceedMaxTime:
                                          #      self.closeSciObjAutoObservation(sciObj[0])
                                          #      self.sendTriggerMsg("%s expTime exceed %d seconds, stop observation."%(ot2Name, self.maxExpTime))
                                          #      break
                                            self.updateSciObjStatus(sciObj[0], status+1)
                                            self.updateSciObjAutoLoopSlow(sciObj[0], status)
                                        break
                                    else:
                                        coloraccess = sciObj[8]-sciObj[7]
                                        Diff_all = fupRecordN[1] - sciObj[4]
                                        deltamag2R2 = fupRecordN[1] - sciObj[7]
                                        priority = 40
                                        print("magDiffk is small")
                                        print("fupRecordNk=%s"%(fupRecordNk))
                                        fupRecordTime  =  fupRecordN[2]
                                        fupRecordTimeNk = fupRecordNk[0][2]
                                        print("fupRecordTimeNk=%s"%(fupRecordTimeNk))
                                        #fupRecordTimeN1 = fupRecordN1[2]
                                        #ot2time = ot2[2]
                                        #stageNTriggerDelay4 = (1+self.deltaT) * (fupRecordTime - ot2time).total_seconds()/60.0
                                 
                                        if Diff_all > 0.6:
                                            if deltamag2R2 > 1.0:
                                                deltaT = 0.2
                                                stageNTriggerDelay4 = (1+deltaT) * ((fupRecordTime - fupRecordTimeNk).total_seconds()/60.0)
                                            else:
                                                deltaT = 0.3
                                                stageNTriggerDelay4 = (1 + deltaT) * ((fupRecordTime - fupRecordTimeNk).total_seconds() / 60.0)
                                        else:                                            
                                            stageNTriggerDelay4 = (1+self.deltaT) * ((fupRecordTime - fupRecordTimeNk).total_seconds()/60.0)
                                        
                                        #stageNTriggerDelay4 = (1+self.deltaT) * ((fupRecordTime - fupRecordTimeN1).total_seconds()/60.0)
                                        if stageNTriggerDelay4>=self.delayTime_max:
                                            stageNTriggerDelay4 = self.delayTime_max    #max delay time is self.delayTime_max
                                        if triggerStatus == status:
                                            self.sendTriggerMsg005("The %s %s %s Stage%d, magDiff: %.2f during the last two epochs \n"\
                                                                "The delay time is %.2f, estimated by %s and %s \n"%(OTFlag, sciObj[1],sciObj[11],status, magDiffK,stageNTriggerDelay4,fupRecordTime, fupRecordTimeNk ))
                                            self.updateSciObjTriggerStatus(sciObj[0], status+1)  
                                       

                                        if status == 5 and coloraccess > 2.0  and Diff_all < self.stage2MagDiff:
                                            print("The %s is larger, and the status is %d "%(coloraccess, status))
                                            self.closeSciObjAutoObservation(sciObj[0])   # on any response for the last request of the follow-up observations. give up.
                                            self.sendTriggerMsg005("stop observation for %s, for its larger B-R of %5.2f , and the small brightness changing of %5.2f in the whole observations. "%(ot2Name, coloraccess, fupRecordN[1]-sciObj[4]))
                                            self.log.warning("%s, %.2f exceed max monitor time(%dminutes), close monitor."%(ot2Name, diffMinutes, self.maxMonitorTime))
                                            break 
                                        
                                        if diffMinutes>stageNTriggerDelay4:
                                            #tobs=[{'filter':['B','R'],'expTime':30,'frameCount':1}]
                                            tobs = [{'filter': ['R'], 'expTime': 30, 'frameCount': 1}]
                                            isExceedMaxTime = self.sendObservationCommand(sciObj, tobs, status+1, lastExpTime, magDiffK, 1, priority)
                                           # if isExceedMaxTime:
                                           #     self.closeSciObjAutoObservation(sciObj[0])
                                           #     self.sendTriggerMsg("%s expTime exceed %d seconds, stop observation."%(ot2Name, self.maxExpTime))
                                           #     break
                                            self.updateSciObjStatus(sciObj[0], status+1)
                                           # self.updateSciObjTriggerStatus(sciObj[0], status+1)
                                        break
                        
                        else:# exceed max monitor time, do not monitor this sciobj anymore
                            print("time is out")
                            self.closeSciObjAutoObservation(sciObj[0])   # on any response for the last request of the follow-up observations. give up.
                            self.log.warning("%s, %.2f exceed max monitor time(%dminutes), close monitor."%(ot2Name, diffMinutes, self.maxMonitorTime))
                            break
                        
                    elif fupRecordN.shape[0]==0 and fupRecordN1.shape[0]>0:  #shape[0] is number of rows, shape[1] is for column
                        
                        self.log.warning("cannot find fupRecord[n] mag, use limit mag")
                        print("limitmag")
                        fupRecordN1 = fupRecordN1[0]
                        priority = 41
                        print(fupObserves)
                        limitMag = fupObserves[0][0]
                        if limitMag is None:     # no limit obtained from follow-up in the DB, "None is not a srting", 
                            #processResult is the flag of the results, 0 menas that DB have not got the results of the data processing
                            limitMag = 18.0
                            #continue
                        magDiff = math.fabs(limitMag-fupRecordN1[1])
                        self.sendTriggerMsg("%s %s Stage%d \n " \
                                            "No detection, limitmag is %.2f \n" \
                                            "The magnitude in the last obs is %.2f\n " \
                                            "magDiff: %.2f"%(sciObj[1],sciObj[11],status, limitMag,  fupRecordN1[1],  magDiff))
                       
                        tobs=[{'filter':['R'],'expTime':30,'frameCount':2}]
                        isExceedMaxTime = self.sendObservationCommand(sciObj, tobs, status+1, lastExpTime, magDiff, 1, priority)
                        if isExceedMaxTime:
                            self.closeSciObjAutoObservation(sciObj[0])
                            self.sendTriggerMsg005("%s expTime exceed %d seconds, stop observation. The limit mag is %.2f in R-band "%(ot2Name, self.maxExpTime, limitMag))
                            break
                        self.updateSciObjTriggerStatus(sciObj[0], status+1)
                        self.updateSciObjStatus(sciObj[0], status+1)
                        break
                    
                    elif fupRecordN.shape[0]==0 and fupRecordN1.shape[0]==0:  #shape[0] is number of rows, shape[1] is for column
                        print("2limit")
                        self.log.warning("cannot find fupRecord[n] mag, use limit mag")
                        
                        #fupRecordN1 = fupRecordN1[0]
                        
                        #print(fupObserves)
                        #limitMag = fupObserves[0][0]
                        #magDiff = math.fabs(limitMag-fupRecordN1[1])
                        #self.sendTriggerMsg("%s %s Stage%d, magDiff: %.2f"%(sciObj[1],sciObj[11],status, magDiff))
                        priority = 40
                        limitMag = fupObserves[0][0]
                        if limitMag is None:     # no limit obtained from follow-up in the DB, "None is not a srting", 
                            #processResult is the flag of the results, 0 menas that DB have not got the results of the data processing
                            limitMag = 18.0
                            #continue
                        tobs=[{'filter':['R'],'expTime':150,'frameCount':1}]
                        isExceedMaxTime = self.sendObservationCommand(sciObj, tobs, status+1, lastExpTime, -1, 1, priority)
                        if isExceedMaxTime:
                            self.closeSciObjAutoObservation(sciObj[0])
                            self.sendTriggerMsg005("%s expTime exceed %d seconds, stop observation. The limit mag is %.2f in R-band "%(ot2Name, self.maxExpTime, limitMag))
                            break

                        self.updateSciObjStatus(sciObj[0], status+1)
                        self.updateSciObjTriggerStatus(sciObj[0], status+1)
                        break
                    else:  
                        limitMag = fupObserves[0][0]
                        if limitMag is None:     # no limit obtained from follow-up in the DB, "None is not a srting", 
                            #processResult is the flag of the results, 0 menas that DB have not got the results of the data processing
                            limitMag = 18.0
                        self.closeSciObjAutoObservation(sciObj[0])
                        self.log.warning("cannot find fupRecord[n-1] mag, stop obs")
                        self.sendTriggerMsg005("%s Stage%d cannot find fupRecord[n-1], stop observation. The limit mag is %.2f in R-band "%(ot2Name, status, limitMag))
                        break

    def start(self):
        
        #ot2Name = 'G200115_C10945'
        #self.initSciObj(ot2Name)
        #ot2Name = 'G200115_C09667'
        #self.initSciObj(ot2Name)
        #ot2Name = 'G200115_C02180'
        #self.initSciObj(ot2Name)
        #ot2Name = 'G200115_C10950'
        #self.initSciObj(ot2Name)
        #ot2Name = 'G181224_C06421'
        #self.initSciObj(ot2Name)
        #ot2Name = 'G190131_C06547'
        #self.initSciObj(ot2Name)        
        #ot2Name = 'G201217_C10436'
        #self.initSciObj(ot2Name)
    
        tmsg = "Restart the code"
        self.sendTriggerMsg(tmsg)
        
        
        #self.updateAutoObservationsTrue()
        
        aa="cd %s"%(self.dirHRDImage)
        os.system(aa)
        bb="pwd"
        os.system(bb)
        
        idx = 1
        try:
            while True:
                
                self.autoFollowUp()
                
                sleepTime = 10
                self.log.debug("\n\n*************%05d run, sleep %d seconds...\n"%(idx, sleepTime))
                #print("\n*************%05d run, sleep %d seconds...\n"%(idx, sleepTime))
                time.sleep(sleepTime)
                idx = idx + 1
                #if idx >2:
                #    break
             
        except Exception as err:
            self.log.error(" gwacAutoFollowUp error ")
            print(err)
            self.sendTriggerMsg(" The code for the auto follow-up observations is down")
            

if __name__ == '__main__':
    
    gwacAutoFollowUp = GWACAutoFollowup()
    gwacAutoFollowUp.start()
    

