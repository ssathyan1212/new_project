import carla
import time
class RecoveryController:
    def __init__(self):
        self.phase = "IDLE"
        self.start_time = None
        self.throttle = 0.0

    def start_recovery(self):
        self.phase = "STOP"
        self.start_time = time.time()
        self.throttle = 0.0

    def recover(self, vehicle):
        control = carla.VehicleControl()

        # =========================
        # PHASE 1: FULL STOP
        # =========================
        if self.phase == "STOP":
            control.throttle = 0.0
            control.brake = 1.0
            control.steer = 0.0   # 🔥 stabilize direction

            # Move to WAIT phase
            if time.time() - self.start_time > 2:
                self.phase = "WAIT"
                self.start_time = time.time()

        # =========================
        # PHASE 2: WAIT (STABLE)
        # =========================
        elif self.phase == "WAIT":
            control.throttle = 0.0
            control.brake = 1.0
            control.steer = 0.0   # 🔥 keep straight

            # Move to gradual start
            if time.time() - self.start_time > 2:
                self.phase = "GRADUAL"

        # =========================
        # PHASE 3: GRADUAL START
        # =========================
        elif self.phase == "GRADUAL":
            self.throttle += 0.02

            control.throttle = min(self.throttle, 0.5)
            control.brake = 0.0
            control.steer = 0.0   # 🔥 VERY IMPORTANT

        # =========================
        # APPLY CONTROL
        # =========================
        vehicle.apply_control(control)

    def is_done(self):
        return self.phase == "GRADUAL" and self.throttle >= 0.5

    def reset(self):
        self.phase = "IDLE"
        self.throttle = 0.0
        self.start_time = None