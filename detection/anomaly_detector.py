import math

class AnomalyDetector:
    def __init__(self):
        self.prev_lat = None
        self.prev_lon = None

    def detect(self, lat, lon, vehicle_speed):
        if self.prev_lat is None:
            self.prev_lat = lat
            self.prev_lon = lon
            return False

        gps_change = abs(lat - self.prev_lat) + abs(lon - self.prev_lon)

        self.prev_lat = lat
        self.prev_lon = lon

        # 🚨 Condition: GPS jumps but vehicle speed low OR mismatch
        if gps_change > 0.0005 and vehicle_speed < 5:
            return True

        return False