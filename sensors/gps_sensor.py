import carla

class GPSSensor:
    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.lat = 0
        self.lon = 0

        world = vehicle.get_world()
        blueprint = world.get_blueprint_library().find('sensor.other.gnss')
        self.sensor = world.spawn_actor(blueprint, carla.Transform(), attach_to=vehicle)

        self.sensor.listen(self.callback)

    def callback(self, data):
        self.lat = data.latitude
        self.lon = data.longitude

    def get_data(self):
        return self.lat, self.lon