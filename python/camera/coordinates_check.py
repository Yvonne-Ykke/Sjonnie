# main.py

import coordinate_transformation as ct

# Define camera coordinates (x, y) and corresponding real-world coordinates (X, Y)
camera_coords = [
        [313, 223],
        [313, 293],
        [313, 363],
        [374, 223],
        [374, 293],
        [374, 363],
        [434, 223],
        [434, 293],
        [434, 362]
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
