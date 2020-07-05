from __future__ import print_function
import datetime
import pigpio
import sys
import threading
import time
from clock import MODE_OFF, MODE_DATE, MODE_TIME, MODE_TIME_TENTHS

DEFAULT_PIN_TX = 24
DEFAULT_PIN_RX = 23
DEFAULT_BAUD = 1200

RESULT_OKAY = "0"
RESULT_SYNTAX_ERROR = "8"
RESULT_WRITE_PROTECT = "9"


class HayesHandlerThread(threading.Thread):
    def __init__(self, pi, tx=DEFAULT_PIN_TX, rx=DEFAULT_PIN_RX, baud=DEFAULT_BAUD, pilock=None, clock=None):
        threading.Thread.__init__(self)
        self.pi = pi
        self.baud = baud
        self.rx = rx
        self.tx = tx
        self.daemon = True
        self.sendLf = False
        self.timeSep = ""
        self.dateSep = ""
        self.hr24 = True
        self.pilock = pilock
        self.waveSerial = None
        self.clock = clock
        
        self.rxBuffer = ""

        # close the serial reader if it's already open
        try:
            self.pi.bb_serial_read_close(self.rx)
        except:
            pass

        status = self.pi.bb_serial_read_open(self.rx, self.baud)
        if status != 0:
            print("Error %d setting up bb serial reader" % status, file=sys.stderr)
            sys.exit(-1)

        self.pi.bb_serial_invert(self.rx, 0)

        self.pi.set_mode(self.tx, pigpio.OUTPUT)

        self.output("hello, world\r\n")

    def setMode(self, mode):
        if self.clock:
            self.clock.setMode(mode)

    def output(self, line):
        line = line + "\r"
        if self.sendLf:
            line = line + "\n"

        if self.pilock:
            self.pilock.acquire()
        try:
            if self.waveSerial:
                self.pi.wave_delete(self.waveSerial)

            self.pi.wave_clear()

            self.pi.wave_add_serial(self.tx, self.baud, line)
            self.waveSerial = self.pi.wave_create()

            self.pi.wave_send_once(self.waveSerial)
            while self.pi.wave_tx_busy():
                time.sleep(0.0001)
        finally:
            if self.pilock:
                self.pilock.release()

    def processLine(self, line):
        dt = datetime.datetime.now()
        uline = line.upper()
        if uline == "ATDT":
            # display mode: time
            self.setMode(MODE_TIME)
        elif uline == "ATDD":
            # display mode: date
            self.setMode(MODE_DATE)
        elif uline == "ATDE":
            # display mode: tenths (nonstandard)
            self.setMode(MODE_TIME_TENTHS)
        elif uline == "ATDO":
            # display mode: off (nonstandard)
            self.setMode(MODE_OFF)
        elif uline == "ATRD":
            s = "%02d%s%02d%s%02d" % \
                (dt.year-2000, self.dateSep, dt.month, self.dateSep, dt.day)
            self.output(s)
        elif uline == "ATRT":
            # read time
            if self.hr24:
                hour = dt.hour
                ampm = ""
            else:
                hour = dt.hour
                if hour >= 12:
                    ampm = "P"
                else:
                    ampm = "A"
                if hour > 12:
                    hour = hour-12
            s = "%02d%s%02d%s%0d%s" % \
                (hour, self.timeSep, dt.minute, self.timeSep, dt.second, ampm)
            self.output(s)
        elif uline == "ATRW":
            s = "%d" % dt.isoweekday()
            self.output(s)
        elif uline.startswith("ATVT") and (len(line) > 4):
            self.timeSep = line[4]
            self.output(RESULT_OKAY)
        elif uline.startswith("ATVD") and (len(line) > 4):
            self.dateSep = line[4]
            self.output(RESULT_OKAY)
        elif uline == "ATLS":
            self.sendLf = True
            self.output(RESULT_OKAY)
        elif uline == "ATLC":
            self.sendLf = False
            self.output(RESULT_OKAY)
        elif uline.startswith("ATST"):
            # set time
            if uline.endswith("A") or uline.endswith("P"):
                self.hr24 = False
            else:
                self.hr24 = True
            self.output(RESULT_OKAY)
        else:
            self.output(RESULT_SYNTAX_ERROR)

    def processByte(self, c):
        c = chr(c)
        if c == "\r":
            self.processLine(self.rxBuffer)
            self.rxBuffer = ""
        elif c == "\n":
            pass  # ignore
        else:
            self.rxBuffer = self.rxBuffer + c

    def runOnce(self):
        (count, data) = self.pi.bb_serial_read(self.rx)
        if count > 0:
            for c in data:
                self.processByte(c)

    def run(self):
        while True:
            self.runOnce()
            time.sleep(0.01)


def main():
    pi = pigpio.pi()
    hayes = HayesHandlerTrhead(pi)
    hayes.start()
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
