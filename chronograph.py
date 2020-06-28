from __future__ import print_function
import pigpio
import time
from clock import ClockThread
from smbpi.gps import GPS


class GPSSync(GPS):
    def __init__(self, pi, clock):
        super().__init__(pi)
        self.clock = clock

    def eventGPRMC(self):
        super().eventGPRMC()

        if time.daylight:
            timestamp = time.mktime(self.getDateTime().timetuple()) - time.altzone
        else:
            timestamp = time.mktime(self.getDateTime().timetuple()) - time.timezone    
        time.clock_settime(time.CLOCK_REALTIME, timestamp)

        self.clock.indicateGPSSynced()


def main():
    pi = pigpio.pi()

    threadClock = ClockThread(pi)
    threadClock.start()

    #threadGPS = GPSSync(pi, threadClock)
    #threadGPS.start()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
