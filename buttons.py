import threading
import time
import RPi.GPIO as GPIO

DEFAULT_BUTTON_RIGHT = 25
DEFAULT_BUTTON_LEFT = 4

class ButtonThread(threading.Thread):
    def __init__(self, clock, left=DEFAULT_BUTTON_LEFT, right=DEFAULT_BUTTON_RIGHT):
        threading.Thread.__init__(self)
        self.clock = clock
        self.daemon = True
        self.left = left
        self.right = right

        GPIO.setup(left, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(right, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def rightRelease(self):
        self.clock.incrementMode()

    def leftRelease(self):
        pass

    def run(self):
        lastLeftState = 1
        lastRightState = 1

        while True:
            rightState = GPIO.input(self.right)
            if rightState and (not lastRightState):
                self.rightRelease()
            lastRightState = rightState

            leftState = GPIO.input(self.left)
            if leftState and (not lastLeftState):
                time.sleep(0.01)
                self.leftRelease()
            lastLeftState = leftState

            time.sleep(0.01)



    