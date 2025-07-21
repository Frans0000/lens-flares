import math
import numpy as np


def create_rotation_matrix(angle_degrees, axis):
    """
    Creates a 3x3 rotation matrix around any axis
    angle_degrees - angle in degrees
    axis - rotation axis vector [x, y, z]
    """
    angle_rad = math.radians(angle_degrees)

    # Normalize rotation axis
    axis = np.array(axis, dtype=float)
    axis = axis / np.linalg.norm(axis)

    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    # Skew-symmetric matrix for cross product
    K = np.array([
        [0, -axis[2], axis[1]],
        [axis[2], 0, -axis[0]],
        [-axis[1], axis[0], 0]
    ])

    # Rodrigues' formula: R = I + sin(θ)K + (1-cos(θ))K²
    R = np.eye(3) + sin_a * K + (1 - cos_a) * np.dot(K, K)

    return R


def ray_intersects_cube(ray_origin, ray_direction, cube_center=[0, 0, 0], cube_size=1.0):
    """
    Checks if ray intersects cube (AABB intersection)
    Returns (intersects, distance) - True/False and distance to intersection
    """
    # Cube dimensions
    half_size = cube_size / 2.0
    cube_min = [cube_center[0] - half_size, cube_center[1] - half_size, cube_center[2] - half_size]
    cube_max = [cube_center[0] + half_size, cube_center[1] + half_size, cube_center[2] + half_size]

    # Check intersection with each axis
    t_min = float('-inf')
    t_max = float('inf')

    for i in range(3):  # x, y, z
        if abs(ray_direction[i]) < 1e-8:  # Ray parallel to plane
            if ray_origin[i] < cube_min[i] or ray_origin[i] > cube_max[i]:
                return False, float('inf')
        else:
            t1 = (cube_min[i] - ray_origin[i]) / ray_direction[i]
            t2 = (cube_max[i] - ray_origin[i]) / ray_direction[i]

            if t1 > t2:
                t1, t2 = t2, t1

            t_min = max(t_min, t1)
            t_max = min(t_max, t2)

            if t_min > t_max:
                return False, float('inf')

    # If t_min < 0, it means we're inside the cube
    distance = max(0, t_min)
    return t_max >= 0, distance


def ray_intersects_rotated_cube(ray_origin, ray_direction, cube_center=[0, 0, 0], cube_size=1.0, rotation_angle=0,
                                rotation_axis=[1, 1, 0]):
    """
    Checks if ray intersects rotated cube (OBB intersection)
    rotation_angle - rotation angle in degrees
    rotation_axis - rotation axis [x, y, z]
    """
    try:
        # Create rotation matrix
        R = create_rotation_matrix(rotation_angle, rotation_axis)

        # Inverse rotation matrix (transpose for orthogonal matrix)
        R_inv = R.T

        # Transform ray to cube's local coordinate system
        # (reverse the cube's rotation)
        ray_origin_np = np.array(ray_origin) - np.array(cube_center)
        ray_direction_np = np.array(ray_direction)

        local_origin = np.dot(R_inv, ray_origin_np) + np.array(cube_center)
        local_direction = np.dot(R_inv, ray_direction_np)

        # Now use standard AABB ray-casting in local coordinate system
        return ray_intersects_cube(local_origin.tolist(), local_direction.tolist(), cube_center, cube_size)

    except Exception as e:
        # Fallback - if something goes wrong, use larger AABB
        print(f"Error in ray_intersects_rotated_cube: {e}")
        return ray_intersects_cube(ray_origin, ray_direction, cube_center, cube_size * 1.8)


def get_camera_direction(camera_rotation):
    """Calculates camera look direction based on rotation"""
    # Convert rotations to radians
    pitch = math.radians(camera_rotation[0])
    yaw = math.radians(camera_rotation[1])

    # Calculate look direction (forward vector)
    forward_x = math.sin(yaw) * math.cos(pitch)
    forward_y = -math.sin(pitch)
    forward_z = -math.cos(yaw) * math.cos(pitch)

    return [forward_x, forward_y, forward_z]


def is_light_in_view(camera_pos, camera_rotation, light_pos):
    """Checks if light is in camera's field of view"""
    # Camera look direction
    camera_dir = get_camera_direction(camera_rotation)

    # Vector from camera to light
    light_dir = [
        light_pos[0] - camera_pos[0],
        light_pos[1] - camera_pos[1],
        light_pos[2] - camera_pos[2]
    ]

    # Normalize vector to light
    light_distance = math.sqrt(light_dir[0] ** 2 + light_dir[1] ** 2 + light_dir[2] ** 2)
    if light_distance > 0:
        light_dir = [x / light_distance for x in light_dir]
    else:
        return False, 0

    # Calculate dot product
    dot_product = (camera_dir[0] * light_dir[0] +
                   camera_dir[1] * light_dir[1] +
                   camera_dir[2] * light_dir[2])

    # If dot product > 0, light is in front of camera
    # Higher value = more centered in field of view
    return dot_product > 0, max(0, dot_product)