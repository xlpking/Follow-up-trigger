# -*- coding: utf-8 -*-
import os
import paramiko
import time
import hashlib
import requests
from datetime import datetime, timedelta
import time
import traceback
from GeneratePreImage2 import genOneDate


def sendMsg(msgSession, tmsg):
    
    try:
        sendTime = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
        tmsg = "%s: %s"%(sendTime, tmsg)
        msgURL = "http://172.28.8.8:8080/gwebend/sendTrigger2WChart.action?chatId=gwac004&triggerMsg="
        turl = "%s%s"%(msgURL,tmsg)
        msgSession.get(turl, timeout=10, verify=False)
    except Exception as e:
        print(str(e))

def file_as_bytes(file):
    with file:
        return file.read()

#limit: require the file at least have two lines
def getLastLine(fname):
    f = open(fname, 'rb')
    last = ""
    try:
        f.seek(0, os.SEEK_END)
        if f.tell()>1:
            f.seek(-1, os.SEEK_END)     # Jump to the second last byte.
            tdata = f.read(1)
            #jump the last empty line, to the last line with content
            while tdata == b"\n" or tdata == b"\r":
                if f.tell()<=1:
                    break
                f.seek(-2, os.SEEK_CUR) 
                tdata = f.read(1)
            #search to the head of last line
            while tdata != b"\n" and tdata != b"\r":
                f.seek(-2, os.SEEK_CUR)
                tdata = f.read(1)
            last = f.readline().decode()         # Read last line.
            #last = f.readlines()[-1].decode()
    finally:
        f.close()
    return last.strip()

def getIpList():
    
    ipPrefix   =  '172.28.2.'
    
    ips = []
    for i in range(2,5):
        for j in range(1,6):
            ip = "%s%d%d"%(ipPrefix, i,j)
            ips.append(ip)
    return ips
    
def backupDir(spath, dpath, logpath, ssh, ftp, ip, msgSession, stopDateStr):
    
    fpackEXE = '/home/gwac/img_diff_xy/image_diff/tools/cfitsio/fpack'
    tempDirName = "G004_019_170617"
    tempFitsName = "G041_mon_objt_180210T10480999.fit.fz"
    stopDateNumber = int(stopDateStr)
    
    print("backup %s: %s"%(ip, spath))  
    ftp.chdir(spath)
    tdirs = ftp.listdir()
    tdirs.sort()
    dataDirs = []
    for tdir in tdirs:
        if len(tdir)!=len(tempDirName):
            tstr = "No new data needed to backup"
            sendMsg(msgSession, tstr)
            continue
	    
        if tdir[0]==tempDirName[0] and tdir[4]==tempDirName[4] and tdir[8]==tempDirName[8] and len(tdir)==len(tempDirName):
            tdateStr = tdir[-6:]
            tdateNumber = int(tdateStr)
            if tdateNumber<stopDateNumber and tdateNumber> 190623: #备份今天之前的所有数据，不备份今天的数据
                dataDirs.append(tdir)

    if len(dataDirs)==0:
        tstr = "No data in this disk"
        sendMsg(msgSession, tstr)
        return
    print("%s: %s total has %d dirs, lastDir is %s"%(ip, spath, len(dataDirs), dataDirs[-1]))  
    dataDirs.sort()
    
    continueFileName = ""
    continueFlag = False
    logfName0 = '%s/%s_%s.log'%(logpath, ip, os.path.basename(spath))
    ''''''
    if os.path.exists(logfName0) and os.stat(logfName0).st_size > 0:
        tlastLine = getLastLine(logfName0)
        if len(tlastLine)>2:
            continueFileName=tlastLine.strip()
    
    tstr = "%s, last backup dir is %s, latest dir is %s"%(spath, continueFileName, dataDirs[-1])
    print(tstr)
    sendMsg(msgSession, tstr)
    
    logfile0 = open(logfName0, 'a')
    #logfile0.write("190623\n\n")
    
    for tdir in dataDirs:
        
        #G002_023_171208
        dateStr = tdir[-6:]
        ccdStr = tdir[:8]
        
        if len(dateStr)==len(continueFileName) and dateStr>continueFileName:
            #tstr = "%s, %s start backup %s"%(spath, ccdStr, dateStr)
            #print(tstr)
            #sendMsg(msgSession, tstr)
            
            #break
            #logfile0.write("%s\n"%(tdir))

            
            spath2 = "%s/%s"%(spath, tdir)
            #dpath2 = "%s/%s"%(dpath, tdir)
            dpath2 = "%s/%s/%s"%(dpath, dateStr, ccdStr)
            if not os.path.exists(dpath2):
                os.makedirs(dpath2)
            
            tstr = "backup %s ..."%(spath2)
            print(tstr)
            sendMsg(msgSession, tstr)
            
            startTime = datetime.now()
            try:
                tcmd = "%s -Y -D %s/G*.fit"%(fpackEXE, spath2)
                print(tcmd)
                stdin, stdout, stderr = ssh.exec_command(tcmd, get_pty=True)
                for line in iter(stdout.readline, ""):
                    print(line)
            except Exception as e:
                tstr = "compress %s error: %s"%(spath2, str(e))
                print(tstr)
                sendMsg(msgSession, tstr)
                tstr = traceback.format_exc()
                print(tstr)
            
            endTime = datetime.now()
            remainSeconds =(endTime - startTime).total_seconds()
            tstr = "fpack compress %s, use %d seconds"%(spath2, remainSeconds)
            print(tstr)
            sendMsg(msgSession, tstr)
            
            startTime = datetime.now()
            try:
                tcmd = "cd %s ; tar -c *.fit.fz | ssh gwac@172.28.8.8 'tar -xvf - -C %s'"%(spath2,dpath2)
                print(tcmd)
                stdin, stdout, stderr = ssh.exec_command(tcmd, get_pty=True)
                for line in iter(stdout.readline, ""):
                    print(line)
            except Exception as e:
                tstr = "backup %s error: %s"%(spath2, str(e))
                print(tstr)
                sendMsg(msgSession, tstr)
                tstr = traceback.format_exc()
                print(tstr)
            
            ftp.chdir(spath2)
            tfiles = ftp.listdir()
            tfiles.sort()
            imgfiles = []
            for tfile in tfiles:
                if tfile[-6:]==tempFitsName[-6:]:
                    imgfiles.append(tfile)
                            
            ii = 0
            for timgName in imgfiles:
                localpath   = '%s/%s'%(dpath2, timgName)        
                if os.path.exists(localpath):
                    ii = ii + 1
             
            endTime = datetime.now()
            remainSeconds =(endTime - startTime).total_seconds()
            tstr = "%s total has %d files, success copyed %d files, use %d seconds, %.2fMB/s"%(tdir, len(imgfiles), ii, remainSeconds, ii*16.0/remainSeconds)
            print(tstr)
            sendMsg(msgSession, tstr)
            
            logfile0.write("%s\n"%(dateStr))
            logfile0.flush()
            
    logfile0.close()
        
def backupWcsDir(spath, dpath, logpath, ssh, ftp, ip, msgSession, stopDateStr):
    
    tempDirName = "G004_019_170617"
    tempFitsName = "G041_mon_objt_180210T10480999.fit.fz"
    stopDateNumber = int(stopDateStr)
    
    ftp.chdir(spath)
    tdirs = ftp.listdir()
    tdirs.sort()
    dataDirs = []
    for tdir in tdirs:
        if tdir[0]==tempDirName[0] and tdir[4]==tempDirName[4] and tdir[8]==tempDirName[8] and len(tdir)==len(tempDirName):
            tdateStr = tdir[-6:]
            tdateNumber = int(tdateStr)
            if tdateNumber<stopDateNumber and tdateNumber> 190623: #备份今天之前的所有数据，不备份今天的数据
                dataDirs.append(tdir)

    if len(dataDirs)==0:
        return
    #print("%s total has %d dirs"%(spath, len(dataDirs)))  
    dataDirs.sort()
    
    continueFileName = ""
    continueFlag = False
    logfName0 = '%s/%s_%s.log'%(logpath, ip, os.path.basename(spath))
    ''''''
    if os.path.exists(logfName0) and os.stat(logfName0).st_size > 0:
        tlastLine = getLastLine(logfName0)
        if len(tlastLine)>2:
            continueFileName=tlastLine.strip()
    
    #tstr = "%s, last backup dir is %s, latest dir is %s"%(spath, continueFileName, dataDirs[-1])
    #print(tstr)
    #sendMsg(msgSession, tstr)
    
    logfile0 = open(logfName0, 'a')
    #logfile0.write("190623\n\n")
    
    for tdir in dataDirs:
        
        #G002_023_171208
        dateStr = tdir[-6:]
        ccdStr = tdir[:8]
        ''' '''
        #if (not continueFlag)  and len(tdir)==len(continueFileName):
        if (not continueFlag)  and len(dateStr)==len(continueFileName):
            if dateStr!=continueFileName:
                continue
            else:
                continueFlag = True
                tstr = "%s, %s last line is: %s, restart from next dir"%(spath, ccdStr, continueFileName)
                print(tstr)
                sendMsg(msgSession, tstr)
                continue
        
        #break
        #logfile0.write("%s\n"%(tdir))
        #logfile0.write("%s\n"%(dateStr))
        #logfile0.flush()
        
        spath2 = "%s/%s"%(spath, tdir)
        #dpath2 = "%s/%s"%(dpath, tdir)
        dpath2 = "%s/%s/%s"%(dpath, dateStr, ccdStr)
        if not os.path.exists(dpath2):
            os.makedirs(dpath2)
        
        tstr = "backup wcs: %s ..."%(spath2)
        print(tstr)
        sendMsg(msgSession, tstr)
                
        startTime = datetime.now()
        try:
            tcmd = "cd %s ; tar -c *.acc | ssh gwac@172.28.8.8 'tar -xvf - -C %s'"%(spath2,dpath2)
            print(tcmd)
            stdin, stdout, stderr = ssh.exec_command(tcmd, get_pty=True)
            for line in iter(stdout.readline, ""):
                print(line)
        except Exception as e:
            tstr = "backup %s error: %s"%(spath2, str(e))
            print(tstr)
            sendMsg(msgSession, tstr)
            tstr = traceback.format_exc()
            print(tstr)
        
        ftp.chdir(spath2)
        tfiles = ftp.listdir()
        tfiles.sort()
        imgfiles = []
        for tfile in tfiles:
            if tfile[-6:]==tempFitsName[-6:]:
                imgfiles.append(tfile)
                        
        ii = 0
        for timgName in imgfiles:
            localpath   = '%s/%s'%(dpath2, timgName)        
            if os.path.exists(localpath):
                ii = ii + 1
         
        endTime = datetime.now()
        remainSeconds =(endTime - startTime).total_seconds()
        tstr = "backup wcs: %s total has %d files, success copyed %d files, use %d seconds, %.2fMB/s"%(tdir, len(imgfiles), ii, remainSeconds, ii*16.0/remainSeconds)
        print(tstr)
        sendMsg(msgSession, tstr)
        
        logfile0.write("%s\n"%(dateStr))
        logfile0.flush()
            
    logfile0.close()
        
def backupAllMachine(msgSession):
    
    spath1 = '/data1'
    spath2 = '/data2'
    spath3 = '/data3'
    dpath = '/data/gwac_data/gwac_orig_fits'
    logpath = '/data/gwac_data/gwac_backup_log'
    
    spathWcs = '/data/GWAC/wcs/wcsfile'
    dpathWcs = '/data/gwac_data/gwac_orig_fits_wcs'
    
    curDateTime = datetime.now()
    curDateTime = curDateTime - timedelta(days=1)
    curDateStr = datetime.strftime(curDateTime, "%Y%m%d")
    curDateStr = curDateStr[2:]
    
    #sftpUser  =  'gwac'
    sftpUser  =  'gwac'
    sftpPass  =  'gwac1234'
    #sftpUser  =  'root'
    #sftpPass  =  'gwac1234'
    ips = getIpList()
            
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
        
    for tip in ips:
        
        tstr = "start backup %s"%(tip)
        print(tstr)
        sendMsg(msgSession, tstr)
        try:
            ssh.connect(tip, username=sftpUser, password=sftpPass)        
            ftp = ssh.open_sftp()
            backupDir(spath1, dpath, logpath, ssh, ftp, tip, msgSession, curDateStr)
            backupDir(spath2, dpath, logpath, ssh, ftp, tip, msgSession, curDateStr)
            backupDir(spath3, dpath, logpath, ssh, ftp, tip, msgSession, curDateStr)
            
            backupWcsDir(spathWcs, dpathWcs, logpath, ssh, ftp, tip, msgSession, curDateStr)
        except paramiko.AuthenticationException:
            print("Authentication Failed!")
            tstr = traceback.format_exc()
            print(tstr)
            sendMsg(msgSession,tstr)
        except paramiko.SSHException:
            print("Issues with SSH service!")
            tstr = traceback.format_exc()
            print(tstr)
            sendMsg(msgSession,tstr)
        except Exception as e:
            print(str(e))
            tstr = traceback.format_exc()
            print(tstr)
            sendMsg(msgSession,tstr)
        
        try:
            time.sleep(1)
            ftp.close()
            ssh.close()
        except Exception as e:
            print(str(e))
            tstr = traceback.format_exc()
            print(tstr)
            sendMsg(msgSession,tstr)
        #break
    
    curDateTime = datetime.now()
    curDateTime = curDateTime - timedelta(days=2)
    curDateStr = datetime.strftime(curDateTime, "%Y%m%d")
    tdateStr = curDateStr[2:]
    tnum = genOneDate(tdateStr)
    if tnum:
        tstr = "total generate %d preImage"%(tnum)
        print(tstr)
        sendMsg(msgSession, tstr)
    

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
                    sendMsg(msgSession, tstr)
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
    
    
