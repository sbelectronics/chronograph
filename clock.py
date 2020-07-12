from __future__ import print_function
import datetime
import threading
import time
import traceback
from smbpi.max6921 import Max6921

MODE_OFF = 1
MODE_DATE = 2
MODE_TIME = 3
MODE_TIME_TENTHS = 4


class ClockThread(threading.Thread):
    def __init__(self, pi, pilock=None):
        threading.Thread.__init__(self)
        self.pi = pi
        self.gpsSynced = 0
        self.lastSecond = 0
        self.vfd = Max6921(pi=pi, pilock=pilock)
        self.mode = MODE_TIME_TENTHS
        self.daemon = True

    def setMode(self, mode):
        self.mode = mode

    def incrementMode(self):
        if self.mode == MODE_OFF:
            self.mode = MODE_DATE
        elif self.mode == MODE_DATE:
            self.mode = MODE_TIME
        elif self.mode == MODE_TIME:
            self.mode = MODE_TIME_TENTHS
        else:
            self.mode = MODE_OFF

    def indicateGPSSynced(self):
        self.gpsSynced = 5

    def runOnce(self):
        now = datetime.datetime.now()

        if self.mode == MODE_OFF:
            timeStr = ""
            self.vfd.setDPList([])
        elif self.mode == MODE_DATE:
            timeStr = now.strftime("%y %m %d")
            self.vfd.setDPList([])
        elif self.mode == MODE_TIME:
            timeStr = now.strftime("%H %M %S")
            self.vfd.setDPList([])
        elif self.mode == MODE_TIME_TENTHS:
            timeStr = now.strftime("%H%M%S") + (" %d" % (now.microsecond / 100000))
            self.vfd.setDPList([4, 6])

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
