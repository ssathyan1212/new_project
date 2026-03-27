import carla

class RecoveryController:
    def recover(self, vehicle):
        control = carla.VehicleControl()
        control.throttle = 0.0
        control.brake = 1.0
        vehicle.apply_control(control)