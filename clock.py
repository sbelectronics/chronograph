import datetime
import threading
import time
import traceback
from smbpi.max6921 import Max6921

class ClockThread(threading.Thread):
    def __init__(self, pi):
        threading.Thread.__init__(self)
        self.pi = pi
        self.vfd = Max6921(pi=pi)
        self.vfd.setDP(0,True)
        self.vfd.setDP(2,True)
        self.vfd.setDP(4,True)
        self.vfd.setDP(6,True)
        self.daemon = True

    def runOnce(self):
        now = datetime.datetime.now()
        timeStr = now.strftime("%H%M%S") + ("%d" % (now.microsecond / 100000))
        self.vfd.displayString(timeStr)


    def run(self):
        while True:
            try:
                self.runOnce()
            except:
                traceback.print_exc()
            time.sleep(0.01)
