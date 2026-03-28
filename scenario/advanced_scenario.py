import carla

def spawn_complex_scenario(world, vehicle):
    map = world.get_map()
    waypoint = map.get_waypoint(vehicle.get_location())

    # Obstacle 1 (main crash)
    wp1 = waypoint.next(25)[0]

    obstacle1 = world.spawn_actor(
        world.get_blueprint_library().filter('static.prop.streetbarrier')[0],
        wp1.transform
    )

    # Obstacle 2 (narrow zone)
    wp2 = waypoint.next(35)[0]

    obstacle2 = world.spawn_actor(
        world.get_blueprint_library().filter('static.prop.streetbarrier')[0],
        wp2.transform
    )

    return [(obstacle1, wp1.transform.location),
            (obstacle2, wp2.transform.location)]