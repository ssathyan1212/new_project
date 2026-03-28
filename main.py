import carla
import time
import numpy as np
import cv2
import random

from sensors.gps_sensor import GPSSensor
from sensors.collision_sensor import CollisionSensor
from recovery.recovery_controller import RecoveryController
from control.system_controller import SystemController

from detection.ml_detector import MLDetector
from utils.dataset_logger import DatasetLogger


def draw_text(world, loc, text, color):
    world.debug.draw_string(loc, text, True, color, 1.5)


def setup_drone_camera(world, vehicle):
    blueprint = world.get_blueprint_library().find('sensor.camera.rgb')

    transform = carla.Transform(
        carla.Location(z=50),
        carla.Rotation(pitch=-90)
    )

    camera = world.spawn_actor(blueprint, transform, attach_to=vehicle)

    def process_image(image):
        array = np.frombuffer(image.raw_data, dtype=np.uint8)
        array = np.reshape(array, (image.height, image.width, 4))
        frame = array[:, :, :3]

        cv2.imshow("🚁 DRONE VIEW", frame)
        cv2.waitKey(1)

    camera.listen(process_image)
    return camera


def draw_visuals(world, vehicle_loc, fake_loc, attack_type):
    world.debug.draw_line(vehicle_loc,
                          vehicle_loc + carla.Location(x=20),
                          0.3,
                          carla.Color(0, 255, 0),
                          1.2)

    world.debug.draw_line(vehicle_loc,
                          fake_loc,
                          1.0,
                          carla.Color(255, 0, 0),
                          1.2)

    world.debug.draw_point(fake_loc,
                           1.0,
                           carla.Color(255, 255, 0),
                           1.2)

    draw_text(world,
              vehicle_loc + carla.Location(z=4),
              attack_type,
              carla.Color(255, 255, 255))


def get_speed(vehicle):
    vel = vehicle.get_velocity()
    return (vel.x**2 + vel.y**2)**0.5


def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(30.0)

    world = client.get_world()
    blueprint = world.get_blueprint_library()

    spawn_point = world.get_map().get_spawn_points()[0]
    vehicle = world.spawn_actor(blueprint.filter('vehicle.*')[0], spawn_point)

    gps = GPSSensor(vehicle)
    collision_sensor = CollisionSensor(vehicle)

    drone_camera = setup_drone_camera(world, vehicle)

    recovery = RecoveryController()
    system = SystemController()
    ml_detector = MLDetector()
    dataset_logger = DatasetLogger()

    # 🚧 RED OBSTACLE
    waypoint = world.get_map().get_waypoint(vehicle.get_location())
    obstacle_wp = waypoint.next(30)[0]

    obstacle_bp = blueprint.find('static.prop.streetbarrier')
    obstacle = world.spawn_actor(obstacle_bp, obstacle_wp.transform)
    obstacle_loc = obstacle_wp.transform.location

    # FLAGS
    recovery_started = False
    attack_started = False
    scenario_switched = False

    prev_speed = 0
    prev_acc = 0
    throttle_val = 0.2   # 🔥 gradual start

    try:
        while True:
            world.tick()

            vehicle_loc = vehicle.get_location()
            distance = vehicle_loc.distance(obstacle_loc)

            fake_loc = vehicle_loc
            attack_type = "NONE"

            # =========================
            # 🟢 BEFORE COLLISION → GRADUAL DRIVE
            # =========================
            if not attack_started:
                throttle_val = min(throttle_val + 0.01, 0.5)

                control = carla.VehicleControl()
                control.throttle = throttle_val
                control.steer = 0.0

                vehicle.apply_control(control)

                draw_text(world,
                          vehicle_loc + carla.Location(z=3),
                          "NORMAL DRIVING",
                          carla.Color(0, 255, 0))

            # =========================
            # 🔴 AFTER COLLISION → DRIFT ATTACK
            # =========================
            else:
                attack_type = "DRIFT"

                # 🔥 RANDOM DRIFT (VISIBLE)
                drift = random.uniform(-0.6, 0.6)

                control = carla.VehicleControl()
                control.throttle = 0.5
                control.steer = drift

                vehicle.apply_control(control)

                fake_loc = vehicle_loc + carla.Location(y=drift * 20)

                draw_text(world,
                          vehicle_loc + carla.Location(z=3),
                          "🚨 DRIFT ATTACK",
                          carla.Color(255, 0, 0))

            # =========================
            # FEATURES
            # =========================
            diff = vehicle_loc.distance(fake_loc)
            speed = get_speed(vehicle)

            acc = abs(speed - prev_speed)
            jerk = abs(acc - prev_acc)

            prev_speed = speed
            prev_acc = acc

            label = 1 if attack_started else 0

            dataset_logger.log(diff, speed, distance, acc, jerk, label)

            # =========================
            # ML DETECTION
            # =========================
            ml_result = 1 if diff > 5 else 0
            status = "ATTACK" if ml_result else "NORMAL"

            print(f"[ML] {status} | diff={diff:.2f}")

            # =========================
            # COLLISION
            # =========================
            collision = collision_sensor.is_collision()

            if collision and not recovery_started:
                recovery.start_recovery()
                recovery_started = True
                attack_started = True

                print("💥 COLLISION → DRIFT ATTACK STARTED")

            # =========================
            # RECOVERY
            # =========================
            if recovery_started and not scenario_switched:
                recovery.recover(vehicle)

                if recovery.is_done():
                    scenario_switched = True

            # =========================
            # 🟢 SAFE MODE
            # =========================
            if scenario_switched:
                waypoint = world.get_map().get_waypoint(vehicle.get_location())
                next_wp = waypoint.next(5.0)[0]

                direction = next_wp.transform.location - vehicle.get_location()
                steer = max(min(direction.y * 0.05, 0.3), -0.3)

                control = carla.VehicleControl()
                control.throttle = 0.4
                control.steer = steer

                vehicle.apply_control(control)

                draw_text(world,
                          vehicle_loc + carla.Location(z=3),
                          "SAFE MODE",
                          carla.Color(0, 255, 255))

                continue

            # =========================
            # VISUALS
            # =========================
            draw_visuals(world, vehicle_loc, fake_loc, attack_type)

            world.debug.draw_box(
                carla.BoundingBox(obstacle_loc, carla.Vector3D(2, 2, 2)),
                carla.Rotation(),
                0.5,
                carla.Color(255, 0, 0),
                1.2
            )

            time.sleep(0.1)

    finally:
        vehicle.destroy()
        obstacle.destroy()
        drone_camera.destroy()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()