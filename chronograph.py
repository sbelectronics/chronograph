from __future__ import print_function
import pigpio
import threading
import time
import RPi.GPIO as GPIO
from clock import ClockThread
from hayes import HayesHandlerThread
from buttons import ButtonThread


def main():
    GPIO.setmode(GPIO.BCM)

    pi = pigpio.pi()

    # clear all waveforms
    pi.wave_clear()

    # allocate a lock to synchronize acceess to creating
    # waves with pgipio
    pilock = threading.Lock()

    threadClock = ClockThread(pi, pilock=pilock)
    threadClock.start()

    threadHayes = HayesHandlerThread(pi, pilock=pilock, clock=threadClock)
    threadHayes.start()

    threadButtons = ButtonThread(clock=threadClock)
    threadButtons.start()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
