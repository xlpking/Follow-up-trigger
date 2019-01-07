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
    
    QSciObj = "SELECT so_id, name, point_ra, point_dec, mag, status, trigger_status, " \
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
    QFupObs = "select limit_mag, expose_duration, auto_loop from follow_up_observation " \
        "where ot_id=%d and auto_loop=%d ORDER BY fo_id asc "
    QOT2 = "SELECT ot_id, mag, found_time_utc from ot_level2 where name='%s'"
    
    maxExpTime = 200
    maxMonitorTime = 300 #minute 60  max is 5 hours
    
    stage2TriggerDelay = 0.5 #minute  #2
    stage3TriggerDelay1 = 1.5 #minute  #2
    stage3TriggerDelay2 = 3 #minute
    stageNTriggerDelay1 = 3 #minute
    stageNTriggerDelay2 = 3 #minute
    stageNTriggerDelay3 = 3 #minute
    
    #defined stageNTriggerDelay4 in the inner code
    #stageNTriggerDelay4 = (1+self.deltaT) * (fupRecordTime - ot2time).total_seconds()/60.0
    
    stage1MagDiff = 1.2    #no vilid
    stage2MagDiff = 0.1  #0.3
    stageNMagDiff1 = 0.2
    stageNMagDiff2 = 0.2
    
    deltaT = 0.3 
    
    nexttmsghour = 0
    nexttmsgminutes = 0
    Talertmsg = 60.0
    
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
    def sendObservationCommand(self, sciObj, observes=[],autoLoop=1,lastExpTime=-1, magdiff=0):

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
                if lastExpTime>0 and magdiff>0:
                    if lastExpTime<self.maxExpTime:
                        expTime = int(lastExpTime * math.exp(0.4*magdiff))
                        if expTime>self.maxExpTime:
                            expTime = self.maxExpTime
                    else: # if expTime exceed maxExpTime, return false and stop observation   #is it volid? xlp
                        return True
                else:
                    expTime = tobs['expTime']
                frameCount = tobs['frameCount']
                print("again tfilters=%s"%(tfilters))
                for tf in tfilters:
                    tfilter = tf    #xlp only B no R？
                    print("tfilter=%s"%(tfilter))
                    fup = FollowUp(ra,dec,expTime,tfilter,frameCount,otName)
                    self.log.debug(fup.getFollowUpString())
                    fup.uploadFollowUpCommond(autoLoop)   #to send the request of follow-up
                    tmsg="Followup request: status=%d RA=%.5f DEC=%.5f exptime=%d " \
                    "filter=%s frameCount=%d OTname=%s"%(status, ra,dec,expTime,tfilter,frameCount,otName)
                    print(tmsg)
                    self.sendTriggerMsg005(tmsg)
        except Exception as e:
            self.log.error("sendObservationCommand error")
            self.log.error(e)
            
        return False
    
    #debug, info, warn, error
    def autoFollowUp(self):

        bjtimehour = int(time.strftime('%H',time.localtime(time.time())))
        bjtimeminute = int(time.strftime('%M',time.localtime(time.time())))  
        print("Beijing hour is %d, Beijng minutes is %d"%(bjtimehour,  bjtimeminute))
       
        delayMinutes = math.fabs((bjtimehour + bjtimeminute/60 - self.nexttmsghour - self.nexttmsgminutes/60)*60.0)
        print("%.2f"%(delayMinutes))  
        
        if bjtimehour>=8 and bjtimehour<17:  
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
            a2 = sciObj[2] # RA deg
            a3 = sciObj[3] # DEC deg 
            a4 = sciObj[4] # R mag
            a11 = sciObj[11]
            print(a0)
            print(a1)
            print(a2)
            print(a3)
            print(a4)
            print(a11)
            print(a11[0:3])
            if a11[0:3] ==  "CAT":     
                OTFlag = "Flaring Candidate"
                Fdiffmag = sciObj[4] - sciObj[7]
            else:
                OTFlag = "OT Candidate"
                Fdiffmag = sciObj[4] - 19   #19 is the limit mag for USNO B1.0
                
            print("OTFlag=%s"%(OTFlag))
            print("Fdiffmag=%.2f"%(Fdiffmag))
            print("=======")
            status = sciObj[5] #status=1
            triggerStatus = sciObj[6] #trigger_status=1
            
            ot2Name = sciObj[1]
            tsql = self.QOT2%(ot2Name)
            ot2s = self.getDataFromDB(tsql)
            if len(ot2s)==0:
                self.log.debug("cannot find ot2 %s"%(ot2Name))
                #self.closeSciObjAutoObservation(sciObj[0])
                return
            ot2=ot2s[0]
            
            self.log.debug("ot2: %s, status: %d, triggerStatus: %d"%(ot2Name, status, triggerStatus))
                
            if status == 1:
                
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
                if diffMinutes < self.maxMonitorTime:
                    print("The delay is accepted")
                    if triggerStatus == 1:
                        tmsg = "New Auto Trigger 60CM Telescope:\n" \
                           "%s %s Stage1.\n" \
                           "gwacMag:%.2f\nfirstObsMag_60cm:%.2f\n" \
                           "usnoRMag:%.2f\nusnoBMag:%.2f\n" \
                           "The amplitude is more than %.2f  relative to USNO \n" \
                           "This is one %s"%(sciObj[1],sciObj[11],ot2[1], sciObj[4],sciObj[7],sciObj[8], Fdiffmag, OTFlag)
                        self.log.debug(tmsg)
                        self.sendTriggerMsg(tmsg)
                        self.updateSciObjTriggerStatus(sciObj[0], 2)
                        
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
                        
                else: # exceed max monitor time, do not monitor this sciobj anymore
                    print("Time is out")
                    self.closeSciObjAutoObservation(sciObj[0])
                    self.log.warning("%s, %.2f exceed max monitor time(%dminutes), close monitor."%(ot2Name, diffMinutes, self.maxMonitorTime))
                    
            elif status > 1:
                                
                ot2Id = ot2[0]
                        
                tsql = self.QFupObs%(ot2Id, status)
                #tsql = self.QFupObs%(ot2Id)
                #limit_mag
                fupObserves = self.getDataFromDB(tsql)
                if len(fupObserves)==0:
                    self.log.debug("cannot find fupObserves %s"%(ot2Name))
                    return
                print(fupObserves)
                lastLimitMag = fupObserves[0][0]
                print("lastLimitmag=%s"%(lastLimitMag))
                if lastLimitMag is None:     # no limit obtained from follow-up in the DB, "None is not a srting"
                   # self.closeSciObjAutoObservation(sciObj[0])
                    continue
                
                lastExpTime = fupObserves[0][1]
                
                tsql = self.QFupObj%(ot2Id)
                #fuo_id, fuo_name, fuo_type_name
                fupObjs = self.getDataFromDB(tsql)
                print(fupObjs)
                
                for fupObj in fupObjs:
                    print("check,mini,catas")
                    print(fupObj)
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
                    status = 2
                    fupRecordN = fupRecords[fupRecords[:,0]==status]
                    fupRecordN1 = fupRecords[fupRecords[:,0]==(status-1)]             
                    
                    print("To print fupRecordN")
                    print(fupRecordN)
                    print("To print fupRecordN1")
                    print(fupRecordN1)
                    print("============over====")
                                        
                    #if find object in Nth folllow
                    if fupRecordN.shape[0]>0 and fupRecordN1.shape[0]>0:
                        fupRecordN = fupRecordN[0]
                        fupRecordN1 = fupRecordN1[0]
                        
                        magDiff = math.fabs(fupRecordN[1]-fupRecordN1[1])
                        
                        observeTime = fupRecordN[2]
                        #curDateTime = datetime.now()
                        curDateTime = datetime.utcnow()
                        #curDateTime.replace(hour=curDateTime.hour-8)
                        diffMinutes = (curDateTime - observeTime).total_seconds()/60.0
                        print("3 diffMinutes=%.2f"%(diffMinutes))
                        if diffMinutes < self.maxMonitorTime:         
                            if status == 2:
                                if magDiff>=self.stage2MagDiff:
                                    if triggerStatus == status:
                                        tmsg = "Auto Trigger 60CM Telescope:\n" \
                                           "The %s :\n"\
                                            "%s %s Stage%d.\n" \
                                           "gwacMag:%.2f\nfirstObsMag:%.2f\nlastObsMag:%.2f\n" \
                                           "usnoRMag:%.2f\nusnoBMag:%.2f\n" \
                                           "DeltaMag during the whole obs by %.2f\n"\
                                           "DeltaMag during the last two epochs is %.2f\n"%(OTFlag, sciObj[1],sciObj[11],status, ot2[1], sciObj[4], fupRecordN[1], sciObj[7], sciObj[8],  fupRecordN[1] - sciObj[4], magDiff)
                                        self.sendTriggerMsg(tmsg)
                                        self.updateSciObjTriggerStatus(sciObj[0], status+1)
                                    if diffMinutes>self.stage3TriggerDelay1:
                                        tobs=[{'filter':['B'],'expTime':40,'frameCount':1},
                                               {'filter':['R'],'expTime':40,'frameCount':2}]
                                        isExceedMaxTime = self.sendObservationCommand(sciObj, tobs, status+1, lastExpTime, magDiff)
                                       # if isExceedMaxTime:
                                       #     self.closeSciObjAutoObservation(sciObj[0])   
                                       #     self.sendTriggerMsg("%s expTime exceed %d seconds, stop observation."%(ot2Name, self.maxExpTime))
                                       #     break
                                        self.updateSciObjStatus(sciObj[0], status+1)
                                    break
                                else:
                                    self.sendTriggerMsg("The %s %s %s Stage%d, magDiff: %.2f, obtained by %.2f and %.2f during the last two epochs"%(OTFlag, sciObj[1],sciObj[11],status, magDiff, fupRecordN[1],fupRecordN1[1]))
                                    if diffMinutes>self.stage3TriggerDelay2:
                                        tobs=[{'filter':['B','R'],'expTime':30,'frameCount':1}]
                                        isExceedMaxTime = self.sendObservationCommand(sciObj, tobs, status+1, lastExpTime, magDiff)
                                        #if isExceedMaxTime:
                                        #    self.closeSciObjAutoObservation(sciObj[0])
                                        #    self.sendTriggerMsg("%s expTime exceed %d seconds, stop observation."%(ot2Name, self.maxExpTime))
                                        #    break
                                        self.updateSciObjStatus(sciObj[0], status+1)
                                        self.updateSciObjAutoLoopSlow(sciObj[0], status-1)
                                        self.updateSciObjTriggerStatus(sciObj[0], status+1)
                                    break
                            elif status > 2:
                                if magDiff>=self.stageNMagDiff1:
                                    if triggerStatus == status:
                                        tmsg = "Auto Trigger 60CM Telescope:\n" \
                                           "The %s :\n" \
                                           "%s %s Stage%d.\n" \
                                           "gwacMag:%.2f\nfirstObsMag:%.2f\nlastObsMag:%.2f\n" \
                                           "usnoRMag:%.2f\nusnoBMag:%.2f\n" \
                                           "DeltaMag during the whole obs by %.2f\n"\
                                           "DeltaMag during the last two epochs is %.2f\n"%(OTFlag, sciObj[1],sciObj[11],status, ot2[1], sciObj[4], fupRecordN[1], sciObj[7], sciObj[8],  fupRecordN[1] - sciObj[4], magDiff)
                                        self.sendTriggerMsg(tmsg)
                                        self.updateSciObjTriggerStatus(sciObj[0], status+1)
                                    if diffMinutes>self.stageNTriggerDelay1:
                                        tobs=[{'filter':['B'],'expTime':40,'frameCount':1},
                                               {'filter':['R'],'expTime':40,'frameCount':1}]
                                        isExceedMaxTime = self.sendObservationCommand(sciObj, tobs, status+1, lastExpTime, magDiff)
                                        #if isExceedMaxTime:
                                        #    self.closeSciObjAutoObservation(sciObj[0])
                                        #    self.sendTriggerMsg("%s expTime exceed %d seconds, stop observation."%(ot2Name, self.maxExpTime))
                                        #    break
                                        self.updateSciObjStatus(sciObj[0], status+1)
                                    break
                                else:
                                    autoLoopIdx = sciObj[10]
                                    #print(autoLoopIdx)
                                    #print(fupRecords)
                                    fupRecordNk = fupRecords[fupRecords[:,0]==autoLoopIdx]
                                    fupRecordNk = fupRecordNk[0]
                                    #print(fupRecordNk)
                                    magDiffK = math.fabs(fupRecordN[1]-fupRecordNk[1])
                                    if magDiffK>=self.stageNMagDiff2:
                                        if triggerStatus == status:
                                            tmsg = "Auto Trigger 60CM Telescope:\n" \
                                               "The %s :\n"\
                                               "%s %s Stage%d.\n" \
                                               "gwacMag:%.2f\nfirstObsMag:%.2f\nlastObsMag:%.2f\n" \
                                               "usnoRMag:%.2f\nusnoBMag:%.2f\n" \
                                               "DeltaMag during the whole obs by %.2f\n"\
                                               "DeltaMag during the last two epochs is %.2f\n"%(OTFlag, sciObj[1],sciObj[11],status, ot2[1], sciObj[4], fupRecordN[1], sciObj[7], sciObj[8],  fupRecordN[1] - sciObj[4], magDiffK)
                                            self.sendTriggerMsg(tmsg)
                                            self.updateSciObjTriggerStatus(sciObj[0], status+1)
                                        if diffMinutes>self.stageNTriggerDelay2:
                                            tobs=[{'filter':['B','R'],'expTime':30,'frameCount':1}]
                                            isExceedMaxTime = self.sendObservationCommand(sciObj, tobs, status+1, lastExpTime, magDiff)
                                          #  if isExceedMaxTime:
                                          #      self.closeSciObjAutoObservation(sciObj[0])
                                          #      self.sendTriggerMsg("%s expTime exceed %d seconds, stop observation."%(ot2Name, self.maxExpTime))
                                          #      break
                                            self.updateSciObjStatus(sciObj[0], status+1)
                                            self.updateSciObjAutoLoopSlow(sciObj[0], status)
                                        break
                                    else:
                                        self.sendTriggerMsg("The %s %s %s Stage%d, magDiff: %.2f during the last two epochs"%(OTFlag, sciObj[1],sciObj[11],status, magDiffK))
                                        fupRecordTime  =  fupRecordN[2]
                                        ot2time = ot2[2]
                                        stageNTriggerDelay4 = (1+self.deltaT) * (fupRecordTime - ot2time).total_seconds()/60.0
                                        if diffMinutes>stageNTriggerDelay4:
                                            tobs=[{'filter':['B','R'],'expTime':30,'frameCount':1}]
                                            isExceedMaxTime = self.sendObservationCommand(sciObj, tobs, status+1, lastExpTime, magDiffK)
                                           # if isExceedMaxTime:
                                           #     self.closeSciObjAutoObservation(sciObj[0])
                                           #     self.sendTriggerMsg("%s expTime exceed %d seconds, stop observation."%(ot2Name, self.maxExpTime))
                                           #     break
                                            self.updateSciObjStatus(sciObj[0], status+1)
                                            self.updateSciObjTriggerStatus(sciObj[0], status+1)
                                        break
                        
                        else:# exceed max monitor time, do not monitor this sciobj anymore
                            self.closeSciObjAutoObservation(sciObj[0])   # on any response for the last request of the follow-up observations. give up.
                            self.log.warning("%s, %.2f exceed max monitor time(%dminutes), close monitor."%(ot2Name, diffMinutes, self.maxMonitorTime))
                            break
                        
                    elif fupRecordN.shape[0]==0 and fupRecordN1.shape[0]>0:  #shape[0] is number of rows, shape[1] is for column
                        
                        self.log.warning("cannot find fupRecord[n] mag, use limit mag")
                        
                        fupRecordN1 = fupRecordN1[0]
                        
                        print(fupObserves)
                        limitMag = fupObserves[0][0]
                        magDiff = math.fabs(limitMag-fupRecordN1[1])
                        self.sendTriggerMsg("%s %s Stage%d \n " \
                                            "No detection, limitmag is %.2f \n" \
                                            "The magnitude in the last obs is %.2f\n " \
                                            "magDiff: %.2f"%(sciObj[1],sciObj[11],status, limitMag,  fupRecordN1[1],  magDiff))
                        
                        tobs=[{'filter':['B','R'],'expTime':30,'frameCount':1}]
                        isExceedMaxTime = self.sendObservationCommand(sciObj, tobs, status+1, lastExpTime, magDiff)
                        if isExceedMaxTime:
                            self.closeSciObjAutoObservation(sciObj[0])
                            self.sendTriggerMsg("%s expTime exceed %d seconds, stop observation. The limit mag is %.2f in R-band "%(ot2Name, self.maxExpTime, limitMag))
                            break

                        self.updateSciObjStatus(sciObj[0], status+1)
                        self.updateSciObjTriggerStatus(sciObj[0], status+1)
                        break
                    
                    elif fupRecordN.shape[0]==0 and fupRecordN1.shape[0]==0:  #shape[0] is number of rows, shape[1] is for column
                        
                        self.log.warning("cannot find fupRecord[n] mag, use limit mag")
                        
                        #fupRecordN1 = fupRecordN1[0]
                        
                        #print(fupObserves)
                        #limitMag = fupObserves[0][0]
                        #magDiff = math.fabs(limitMag-fupRecordN1[1])
                        #self.sendTriggerMsg("%s %s Stage%d, magDiff: %.2f"%(sciObj[1],sciObj[11],status, magDiff))
                        
                        tobs=[{'filter':['B','R'],'expTime':200,'frameCount':1}]
                        isExceedMaxTime = self.sendObservationCommand(sciObj, tobs, status+1, lastExpTime, -1)
                        if isExceedMaxTime:
                            self.closeSciObjAutoObservation(sciObj[0])
                            self.sendTriggerMsg("%s expTime exceed %d seconds, stop observation. The limit mag is %.2f in R-band "%(ot2Name, self.maxExpTime, limitMag))
                            break

                        self.updateSciObjStatus(sciObj[0], status+1)
                        self.updateSciObjTriggerStatus(sciObj[0], status+1)
                        break
                    else:  
                        limitMag = fupObserves[0][0]
                        self.closeSciObjAutoObservation(sciObj[0])
                        self.log.warning("cannot find fupRecord[n-1] mag, stop obs")
                        self.sendTriggerMsg("%s Stage%d cannot find fupRecord[n-1], stop observation. The limit mag is %.2f in R-band "%(ot2Name, status, limitMag))
                        break

    def start(self):
        
        #ot2Name = 'G181224_C01823'
        #self.initSciObj(ot2Name)
        
        #ot2Name = 'G181218_C00304'
        #self.initSciObj(ot2Name)
    

        
        idx = 1
        try:
            while True:
                
                self.autoFollowUp()
                
                sleepTime = 10
                self.log.debug("\n\n*************%05d run, sleep %d seconds...\n"%(idx, sleepTime))
                #print("\n*************%05d run, sleep %d seconds...\n"%(idx, sleepTime))
                time.sleep(sleepTime)
                idx = idx + 1
                if idx >2:
                    break
             
        except Exception as err:
            self.log.error(" gwacAutoFollowUp error ")
            print(err)
            self.sendTriggerMsg(" The code for the auto follow-up observations is down")
            

if __name__ == '__main__':

    gwacAutoFollowUp = GWACAutoFollowup()
    gwacAutoFollowUp.start()
    

