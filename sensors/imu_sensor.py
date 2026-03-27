import carla

class IMUSensor:
    def __init__(self, vehicle):
        self.acc = 0

        world = vehicle.get_world()
        blueprint = world.get_blueprint_library().find('sensor.other.imu')
        self.sensor = world.spawn_actor(blueprint, carla.Transform(), attach_to=vehicle)

        self.sensor.listen(self.callback)

    def callback(self, data):
        self.acc = data.accelerometer.x

    def get_data(self):
        return self.acc