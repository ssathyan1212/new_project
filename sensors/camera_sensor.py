import carla
import numpy as np
import cv2

class CameraSensor:
    def __init__(self, vehicle):
        world = vehicle.get_world()

        blueprint = world.get_blueprint_library().find('sensor.camera.rgb')
        blueprint.set_attribute('image_size_x', '800')
        blueprint.set_attribute('image_size_y', '600')
        blueprint.set_attribute('fov', '90')

        transform = carla.Transform(carla.Location(x=-6, z=3), carla.Rotation(pitch=-15))

        self.sensor = world.spawn_actor(blueprint, transform, attach_to=vehicle)
        self.sensor.listen(self.process_image)

    def process_image(self, image):
        array = np.frombuffer(image.raw_data, dtype=np.uint8)
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]

        cv2.imshow("CARLA VIEW", array)
        cv2.waitKey(1)