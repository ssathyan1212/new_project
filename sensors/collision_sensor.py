import carla

class CollisionSensor:
    def __init__(self, vehicle):
        self.collision = False

        world = vehicle.get_world()
        blueprint = world.get_blueprint_library().find('sensor.other.collision')

        self.sensor = world.spawn_actor(blueprint, carla.Transform(), attach_to=vehicle)
        self.sensor.listen(self.callback)

    def callback(self, event):
        self.collision = True

    def is_collision(self):
        return self.collision

    def reset(self):
        self.collision = False