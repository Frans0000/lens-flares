import pygame
import math
from OpenGL.GL import *

# Import our modules
from graphics import (
    load_texture_from_file,
    draw_textured_cube,
    draw_background_with_texture,
    draw_ground,
    draw_light_source
)
from lens_flare import draw_lens_flares, check_light_visibility
from math_utils import is_light_in_view, ray_intersects_rotated_cube

# Global variables
camera_pos = [0, 0, 3]
camera_rotation = [0, 0]
cube_rotation = 0
light_pos = [2, 1, -3]  # Light source position
light_visibility = 1.0  # 0.0 = completely occluded, 1.0 = completely visible


def handle_input(keys):
    """Handle camera controls"""
    global camera_pos, camera_rotation, cube_rotation

    speed = 0.1
    rot_speed = 2

    # Camera movement
    if keys[pygame.K_w]:
        camera_pos[2] -= speed
    if keys[pygame.K_s]:
        camera_pos[2] += speed
    if keys[pygame.K_a]:
        camera_pos[0] -= speed
    if keys[pygame.K_d]:
        camera_pos[0] += speed
    if keys[pygame.K_q]:
        camera_pos[1] += speed
    if keys[pygame.K_e]:
        camera_pos[1] -= speed

    # Camera rotation
    if keys[pygame.K_UP]:
        camera_rotation[0] -= rot_speed
    if keys[pygame.K_DOWN]:
        camera_rotation[0] += rot_speed
    if keys[pygame.K_LEFT]:
        camera_rotation[1] -= rot_speed
    if keys[pygame.K_RIGHT]:
        camera_rotation[1] += rot_speed

    # Cube rotation
    cube_rotation += 1


def print_debug_info():
    """Debug information"""
    print(f"Camera: {camera_pos}")
    print(f"Camera rotation: {camera_rotation}")
    print(f"Cube rotation: {cube_rotation:.1f}°")
    print(f"Light visibility: {light_visibility:.2f}")

    in_view, view_factor = is_light_in_view(camera_pos, camera_rotation, light_pos)
    print(f"Light in field of view: {in_view}, factor: {view_factor:.2f}")

    from graphics import world_to_screen
    light_screen = world_to_screen(light_pos)
    print(f"Light on screen: [{light_screen[0]:.1f}, {light_screen[1]:.1f}]")

    # Ray-casting test
    light_dir = [
        light_pos[0] - camera_pos[0],
        light_pos[1] - camera_pos[1],
        light_pos[2] - camera_pos[2]
    ]
    light_distance = math.sqrt(sum(x ** 2 for x in light_dir))
    if light_distance > 0:
        light_dir = [x / light_distance for x in light_dir]
        intersects, dist = ray_intersects_rotated_cube(
            camera_pos, light_dir, [0, 0, 0], 1.0, cube_rotation, [1, 1, 0]
        )
        print(f"Ray-casting: intersection={intersects}, distance={dist:.2f}, light_distance={light_distance:.2f}")


def main():
    global light_visibility

    pygame.init()

    screen = pygame.display.set_mode((800, 600), pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("lens flare project")

    # Load textures
    background_texture = load_texture_from_file("sky_background.jpg")
    cube_texture = load_texture_from_file("moon_texture.png")

    # Basic OpenGL settings
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.02, 0.02, 0.08, 1.0)  # Darker background

    # Perspective
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glFrustum(-1.0, 1.0, -0.75, 0.75, 1.0, 10.0)
    glMatrixMode(GL_MODELVIEW)

    clock = pygame.time.Clock()
    running = True

    print("WASD - movement, QE - up/down, arrows - rotation")
    print("ESC - exit, SPACE - debug")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    print_debug_info()

        # Handle input
        keys = pygame.key.get_pressed()
        handle_input(keys)

        # Check light visibility
        light_visibility = check_light_visibility(
            camera_pos, camera_rotation, light_pos, light_visibility, cube_rotation
        )

        # Clear screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        draw_background_with_texture(background_texture)

        # Reset modelview matrix
        glLoadIdentity()

        # Camera transformations
        glTranslatef(-camera_pos[0], -camera_pos[1], -camera_pos[2])
        glRotatef(camera_rotation[0], 1, 0, 0)
        glRotatef(camera_rotation[1], 0, 1, 0)

        # Draw 3D scene
        draw_ground()

        # Draw rotating cube
        glPushMatrix()
        glRotatef(cube_rotation, 1, 1, 0)
        draw_textured_cube(cube_texture)
        glPopMatrix()

        # Draw light source
        draw_light_source(light_pos, light_visibility)

        # Draw lens flares (2D overlay)
        draw_lens_flares(light_pos, light_visibility)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()