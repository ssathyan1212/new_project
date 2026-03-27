import time
from config import SPOOF_OFFSET, ATTACK_START_TIME, ATTACK_DURATION

class GPSSpoofer:
    def __init__(self):
        self.start_time = time.time()
        self.active = False

    def spoof(self, lat, lon):
        current = time.time() - self.start_time

        if ATTACK_START_TIME < current < (ATTACK_START_TIME + ATTACK_DURATION):
            self.active = True
            return lat + SPOOF_OFFSET, lon + SPOOF_OFFSET
        else:
            self.active = False
            return lat, lon