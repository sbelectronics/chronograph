import pigpio
import time
from clock import ClockThread

def main():
    pi = pigpio.pi()
    threadClock = ClockThread(pi)
    threadClock.start()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
