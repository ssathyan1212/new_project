import carla
import time
import math

from sensors.gps_sensor import GPSSensor
from sensors.camera_sensor import CameraSensor
from attack.gps_spoofer import GPSSpoofer
from detection.anomaly_detector import AnomalyDetector
from recovery.recovery_controller import RecoveryController
from scenario.obstacle_scenario import spawn_obstacle
from utils.logger import log


def distance(loc1, loc2):
    return math.sqrt(
        (loc1.x - loc2.x) ** 2 +
        (loc1.y - loc2.y) ** 2
    )


def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)

    world = client.get_world()
    blueprint = world.get_blueprint_library()

    spawn_point = world.get_map().get_spawn_points()[0]
    vehicle_bp = blueprint.filter('vehicle.*')[0]

    vehicle = world.spawn_actor(vehicle_bp, spawn_point)

    # =========================
    # SENSORS
    # =========================
    gps = GPSSensor(vehicle)
    camera = CameraSensor(vehicle)

    # =========================
    # MODULES
    # =========================
    spoofer = GPSSpoofer()
    detector = AnomalyDetector()
    recovery = RecoveryController()

    # =========================
    # SCENARIO
    # =========================
    obstacle, obstacle_loc = spawn_obstacle(world, vehicle)

    log("🚧 Obstacle placed on road ahead")

    try:
        while True:
            world.tick()

            vehicle_loc = vehicle.get_location()
            dist = distance(vehicle_loc, obstacle_loc)

            # =========================
            # DEFAULT CONTROL (STRAIGHT)
            # =========================
            control = carla.VehicleControl()
            control.throttle = 0.5
            control.steer = 0.0
            control.brake = 0.0

            # =========================
            # GPS DATA
            # =========================
            lat, lon = gps.get_data()
            spoof_lat, spoof_lon = spoofer.spoof(lat, lon)

            # =========================
            # NORMAL LOGIC (SAFE SYSTEM)
            # =========================
            should_stop = dist < 8   # stop if close

            # =========================
            # GPS SPOOFING EFFECT
            # =========================
            if spoofer.active:
                log("🚨 GPS SPOOFING ACTIVE → IGNORING OBSTACLE")
                should_stop = False   # 🚨 critical attack behavior

            # =========================
            # DETECTION
            # =========================
            attack_detected = detector.detect(spoof_lat, spoof_lon)

            # =========================
            # CONTROL DECISION
            # =========================
            if should_stop:
                log(f"🛑 Obstacle detected at distance {dist:.2f} → stopping")
                control.throttle = 0.0
                control.brake = 1.0
                vehicle.apply_control(control)

            elif attack_detected:
                log("⚠️ Attack detected → recovery activated")
                recovery.recover(vehicle)

            else:
                vehicle.apply_control(control)

            # =========================
            # VISUAL DEBUG (VERY IMPORTANT)
            # =========================

            # 🔴 Highlight obstacle clearly
            world.debug.draw_box(
                carla.BoundingBox(obstacle_loc, carla.Vector3D(1.5, 1.5, 1.5)),
                carla.Rotation(),
                thickness=0.3,
                color=carla.Color(255, 0, 0),
                life_time=0.1
            )

            # 🟢 Straight path line
            forward_loc = vehicle_loc + carla.Location(x=10)

            world.debug.draw_line(
                vehicle_loc,
                forward_loc,
                thickness=0.1,
                color=carla.Color(0, 255, 0),
                life_time=0.1
            )

            # 🟡 Distance indicator (optional)
            world.debug.draw_string(
                vehicle_loc + carla.Location(z=2),
                f"Dist: {dist:.2f}",
                draw_shadow=False,
                color=carla.Color(255, 255, 0),
                life_time=0.1
            )

            time.sleep(0.05)

    finally:
        log("🧹 Cleaning up actors")
        vehicle.destroy()
        obstacle.destroy()


if __name__ == "__main__":
    main()