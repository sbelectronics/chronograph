from __future__ import print_function
import datetime
import threading
import time
import traceback
from smbpi.max6921 import Max6921

class ClockThread(threading.Thread):
    def __init__(self, pi):
        threading.Thread.__init__(self)
        self.pi = pi
        self.gpsSynced = 0
        self.lastSecond = 0
        self.vfd = Max6921(pi=pi)
        self.vfd.setDP(0, True)
        self.vfd.setDP(2, True)
        self.vfd.setDP(4, True)
        self.vfd.setDP(6, True)
        self.daemon = True

    def indicateGPSSynced(self):
        self.gpsSynced = 5

    def runOnce(self):
        now = datetime.datetime.now()
        timeStr = now.strftime("%H%M%S") + ("%d" % (now.microsecond / 100000))
        self.vfd.setLeader(top=(self.gpsSynced > 0))
        self.vfd.displayString(timeStr)

        # update the synced indicator, keep it lit for up to 5 seconds after
        # the last time we received a gps time packet
        if (self.lastSecond != now.second):
            self.lastSecond = now.second
            if self.gpsSynced > 0:
                self.gpsSynced = self.gpsSynced - 1

    def run(self):
        while True:
            try:
                self.runOnce()
            except:
                traceback.print_exc()
                time.sleep(10)

            time.sleep(0.01)
