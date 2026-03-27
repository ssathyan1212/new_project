from config import MAX_DEVIATION

class AnomalyDetector:
    def __init__(self):
        self.prev_lat = None
        self.prev_lon = None

    def detect(self, lat, lon):
        if self.prev_lat is None:
            self.prev_lat = lat
            self.prev_lon = lon
            return False

        deviation = abs(lat - self.prev_lat) + abs(lon - self.prev_lon)

        self.prev_lat = lat
        self.prev_lon = lon

        if deviation > MAX_DEVIATION:
            return True
        return False