import carla

def spawn_obstacle(world, vehicle):
    map = world.get_map()

    vehicle_loc = vehicle.get_location()

    # Get road waypoint of vehicle
    waypoint = map.get_waypoint(vehicle_loc)

    # Move forward along same lane
    obstacle_wp = waypoint.next(30)[0]

    obstacle_transform = obstacle_wp.transform

    # Slightly raise to avoid sinking
    obstacle_transform.location.z += 0.5

    blueprint = world.get_blueprint_library().filter('static.prop.streetbarrier')[0]

    obstacle = world.spawn_actor(
        blueprint,
        obstacle_transform
    )

    return obstacle, obstacle_transform.location