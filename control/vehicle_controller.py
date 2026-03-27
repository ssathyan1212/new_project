
import carla
class VehicleController:
    def __init__(self, vehicle):
        self.vehicle = vehicle

    def drive_forward(self):
        control = carla.VehicleControl()
        control.throttle = 0.5
        control.steer = 0.0
        self.vehicle.apply_control(control)