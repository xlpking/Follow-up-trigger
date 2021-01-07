#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  7 12:15:11 2021

@author: xlp
"""
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
#from PS1_Getimg1 import xgetps1
#from PS1_Getimg2 import xgetps10arcmin
from PS1_Getimg import xgetps1, xgetps10arcmin


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

    def connDb(self):
        
        self.conn = psycopg2.connect(**self.connParam4)
        self.dataVersion = ()
        


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
            self.log.error(" query data error ")
            self.log.error(err)
            
        return rows
    
   
    
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
            

    def closeSciObjAutoObservation(self, soId):
        
        tsql = "update science_object set auto_observation=false where name='%s'"%(soId)
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
            
            
 
    def start(self, OTname):
        try:
            self.closeSciObjAutoObservation(OTname)             
        except Exception as err:
            self.log.error(" gwacAutoFollowUp error ")
            print(err)
            self.sendTriggerMsg(" The code for the auto follow-up observations is down")
                                   

if __name__ == '__main__':
    OTname = sys.argv[1]
    #OTname = "G210106_C07825"
    print("%s\n"%(OTname))
    
    gwacAutoFollowUp = GWACAutoFollowup()
    gwacAutoFollowUp.start(OTname)    
    #self.closeSciObjAutoObservation(OTname)