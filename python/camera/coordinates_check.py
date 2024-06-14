# main.py

import coordinate_transformation as ct

# Define camera coordinates (x, y) and corresponding real-world coordinates (X, Y)
camera_coords = [
    [202, 204],
    [209, 277],
    [217, 352],
    [266, 179],
    [274, 269],
    [282, 345],
    [330, 190],
    [339, 262],
    [347, 337]
]

real_world_coords = [
    [-140, 375],
    [-140, 295],
    [-140, 215],
    [-70, 374],
    [-70, 294],
    [-70, 214],
    [0, 375],
    [0, 298],
    [0, 219]
]

# Initialize the transformer
transformer = ct(camera_coords, real_world_coords)

# Get real-world coordinates from the camera
try:
    camera_coordinates, real_world_coordinates = transformer.get_real_world_coordinates()

    print("Camera Coordinates:")
    for coord in camera_coordinates:
        print(coord)

    print("\nConverted Real-World Coordinates:")
    for coord in real_world_coordinates:
        print(coord)
except Exception as e:
    print(e)
