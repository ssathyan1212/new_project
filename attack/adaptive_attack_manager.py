import time

class AdaptiveAttackManager:
    def __init__(self):
        self.start = time.time()

    def get_attack(self, vehicle_loc, obstacle_loc):
        t = time.time() - self.start
        distance = vehicle_loc.distance(obstacle_loc)

        # 🔥 Context-aware attacks
        if distance > 30:
            return "DRIFT"

        elif 15 < distance < 30:
            return "OFFSET"

        elif 5 < distance < 15:
            return "REPLAY"

        elif distance < 5:
            return "FREEZE"

        return None