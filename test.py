try:

except Exception as err:
        self.log.error(" gwacAutoFollowUp error ")
        print(err)
        self.sendTriggerMsg(" The code for the auto follow-up observations is down")