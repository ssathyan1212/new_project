import carla
import math

class NavigationController:
    def __init__(self, vehicle, target_location):
        self.vehicle = vehicle
        self.target = target_location

    def run_step(self, current_location):
        vehicle_transform = self.vehicle.get_transform()
        vehicle_loc = vehicle_transform.location

        dx = self.target.x - vehicle_loc.x
        dy = self.target.y - vehicle_loc.y

        target_angle = math.atan2(dy, dx)
        vehicle_yaw = math.radians(vehicle_transform.rotation.yaw)

        steer = target_angle - vehicle_yaw

        control = carla.VehicleControl()
        control.throttle = 0.5
        control.steer = max(min(steer, 1.0), -1.0)

        return control