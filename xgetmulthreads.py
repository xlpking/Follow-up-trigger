#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 10:20:24 2021

@author: xlp
"""
import os
#import paramiko
import time
import hashlib
import requests
from datetime import datetime, timedelta
import time
import traceback
import threading


def getIpList():
    
    ipPrefix   =  '172.28.2.'
    
    ips = []
    for i in range(2,5):
        for j in range(1,6):
            ip = "%s%d%d"%(ipPrefix, i,j)
            ips.append(ip)
    return ips
    

def backupDir_eachip(msgSession,tip):
    print(msgSession)
    print(tip)


def backupAllMachine(msgSession):
    
    ips = getIpList()
    threads = []
    for tip in ips:
        t1 = threading.Thread(target=backupDir_eachip, args=(msgSession,tip))
        threads.append(t1)
        
    for t in threads:
        t.setDaemon(True)
        t.start()
        
        
    for t in threads:
        t.join()
        
    
    print("over...")
    
    
 

if __name__ == '__main__':
    
    while True:
        try:
            curDateTime = datetime.now()
            tDateTime = datetime.now()
            startDateTime = tDateTime.replace(hour=9, minute=0, second=0)
            endDateTime = tDateTime.replace(hour=16, minute=0, second=0)
            remainSeconds1 = (startDateTime - curDateTime).total_seconds()
            remainSeconds2 = (endDateTime - curDateTime).total_seconds()
            if remainSeconds1<0 and remainSeconds2>0:
                msgSession = requests.Session()
                tstr = "start gwac fits backup"
                print(tstr)
                try:
                    #sendMsg(msgSession, tstr)
                    backupAllMachine(msgSession)
                except Exception as e:
                    print(e)
                    tstr = traceback.format_exc()
                    print(tstr)
                time.sleep(3600*1)
                tstr = "backup done"
                print(tstr)
                sendMsg(msgSession, tstr)
            else:
                time.sleep(600)
        except Exception as e:
            print(e)
            tstr = traceback.format_exc()
            print(tstr)
       
    
    
    
    
    