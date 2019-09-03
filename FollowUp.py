# -*- coding: utf-8 -*-
import requests
import time

def fail_retry(times, ret_vals=(True,), exception=Exception):
    if not isinstance(ret_vals, (list, tuple)):
        ret_vals = (ret_vals, )

    def inner(func):
        def _inner(*args, **kwargs):
            for i in range(times):
                if i:
                    print('run %s retry times %d', func.__name__, i)
                try:
                    ret = func(*args, **kwargs)
                    if ret in ret_vals:
                        return ret
                    sleepTime = i*0.1 + 5
                    print('request %d error, sleep %fs' % ( i, sleepTime))
                    time.sleep(sleepTime)
                except exception as e:
                    print('exception: %s', e)
                    pass
            #raise Exception('run %s times > %d' % (func.__name__, times))

        return _inner

    return inner
    
class FollowUp:
    
    #followUpUrl = "http://127.0.0.1:8080/gwebend/otFollowUp.action"
    #followUpUrl = "http://172.28.8.8:8080/gwebend/otFollowUp.action"
    followUpUrl = "http://10.0.10.236:9995/gwebend/otFollowUp.action"
    
    def __init__(self,ra,dec,expTime,filter,frameCount,otName='',telescope='1',
                 priority=41,epoch="2000",imageType = "LIGHT", userName='gwac',
                 triggerType='0',begineTime='',endTime='',followName=''):
        
        self.userName = userName
        self.followName = followName
        self.otName = otName
        self.ra = ra
        self.dec = dec
        self.expTime = expTime
        self.frameCount = frameCount
        self.filter = filter
        self.priority = priority
        self.begineTime = begineTime
        self.endTime = endTime
        self.triggerType = triggerType
        self.epoch = epoch
        self.imageType = imageType
        self.telescope = telescope
        self.comment = ""
        
    def getFollowUpString(self):
        
        tstr = "append_plan %s %s\nappend_object %s %.6f %.6f %s %s %d %d %s %d %s %s %s\n"% \
            (self.userName,self.triggerType,self.otName,self.ra,self.dec,self.epoch, \
             self.imageType,self.expTime,self.frameCount,self.filter,self.priority, \
             self.begineTime,self.endTime,self.telescope)
        
        return tstr
        
    #@fail_retry(3, exception=requests.Timeout)
    def uploadFollowUpCommond(self, autoLoop=1):
        
        ''' '''
        ts = requests.Session()
        parameters = {'ot2fp.userName': self.userName, 
                      'ot2fp.otName': self.otName, 
                      'ot2fp.ra': self.ra, 
                      'ot2fp.dec': self.dec, 
                      'ot2fp.expTime': self.expTime, 
                      'ot2fp.frameCount': self.frameCount, 
                      'ot2fp.telescope': self.telescope, 
                      'ot2fp.filter': self.filter, 
                      'ot2fp.triggerType': self.triggerType,
                      'ot2fp.priority': self.priority,
                      'autoLoop': autoLoop}
        #print(parameters)
        r = ts.post(self.followUpUrl, data=parameters, timeout=10, verify=False)
        #print(r.encoding)
        resp = r.json()
        #print(resp)
        if resp[u'result'] == 'success!':
            print('upload follow up command success.')
        else:
            print(resp[u'result'])
        return r.status_code == 200
        

    def uploadFollowUpCommondtest(self, autoLoop=1):
        ''' '''
        print("To send the command")
        return True
        
if __name__ == '__main__':
    
    fup = FollowUp(10,20.1,31,'R|B',1,'G181214_C08444',1,41)
    print(fup.getFollowUpString())
    fup.uploadFollowUpCommond()
