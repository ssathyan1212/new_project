import carla
import time

from sensors.gps_sensor import GPSSensor
from sensors.camera_sensor import CameraSensor
from sensors.collision_sensor import CollisionSensor
from attack.gps_spoofer import GPSSpoofer
from recovery.recovery_controller import RecoveryController
from control.system_controller import SystemController
from scenario.obstacle_scenario import spawn_obstacle


def draw_text(world, loc, text, color):
    world.debug.draw_string(
        loc,
        text,
        draw_shadow=True,
        color=color,
        life_time=1.0
    )


def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(30.0)

    world = client.get_world()
    blueprint = world.get_blueprint_library()

    spawn_point = world.get_map().get_spawn_points()[0]
    vehicle_bp = blueprint.filter('vehicle.*')[0]

    vehicle = world.spawn_actor(vehicle_bp, spawn_point)

    # Sensors
    gps = GPSSensor(vehicle)
    camera = CameraSensor(vehicle)
    collision_sensor = CollisionSensor(vehicle)

    # Modules
    spoofer = GPSSpoofer()
    recovery = RecoveryController()
    system = SystemController()

    # Scenario
    obstacle, obstacle_loc = spawn_obstacle(world, vehicle)

    recovery_started = False

    try:
        while True:
            world.tick()

            vehicle_loc = vehicle.get_location()

            lat, lon = gps.get_data()
            spoof_lat, spoof_lon = spoofer.spoof(lat, lon)

            collision = collision_sensor.is_collision()

            # 🔥 Start recovery only once
            if collision and not recovery_started:
                recovery.start_recovery()
                recovery_started = True

            state = system.update(
                spoofer.active,
                collision,
                recovery.is_done()
            )

            control = carla.VehicleControl()

            # =========================
            # NORMAL STATE
            # =========================
            if state == "NORMAL":
                control.throttle = 0.5
                control.steer = 0.0
                control.brake = 0.0

                draw_text(world, vehicle_loc + carla.Location(z=3),
                          "SAFE NORMAL DRIVING", carla.Color(0, 255, 0))

                vehicle.apply_control(control)

                # 🔥 FULL RESET
                recovery.reset()
                collision_sensor.reset()
                recovery_started = False

            # =========================
            # ATTACK STATE
            # =========================
            elif state == "ATTACK":
                control.throttle = 0.5
                control.steer = 0.0

                draw_text(world, vehicle_loc + carla.Location(z=3),
                          "GPS SPOOFING ATTACK", carla.Color(255, 0, 0))

                vehicle.apply_control(control)

            # =========================
            # RECOVERY STATE
            # =========================
            elif state == "RECOVERY":
                draw_text(world, vehicle_loc + carla.Location(z=3),
                          f"RECOVERY: {recovery.phase}",
                          carla.Color(0, 0, 255))

                recovery.recover(vehicle)

                # 🔥 AFTER RECOVERY → DISABLE ATTACK
                if recovery.is_done():
                    spoofer.disable()

            # =========================
            # COLLISION ALERT
            # =========================
            if collision:
                draw_text(world, vehicle_loc + carla.Location(z=5),
                          "COLLISION DETECTED",
                          carla.Color(255, 255, 0))

            # =========================
            # OBSTACLE VISUAL
            # =========================
            world.debug.draw_box(
                carla.BoundingBox(obstacle_loc, carla.Vector3D(2, 2, 2)),
                carla.Rotation(),
                thickness=0.4,
                color=carla.Color(255, 0, 0),
                life_time=1.0
            )

            time.sleep(0.05)

    finally:
        vehicle.destroy()
        obstacle.destroy()


if __name__ == "__main__":
    main()