import math
import numpy as np
from OpenGL.GL import *
from graphics import world_to_screen
from math_utils import is_light_in_view


def check_light_visibility(camera_pos, camera_rotation, light_pos, light_visibility, cube_rotation):
    """Checks and updates light visibility"""
    # Check if light is in field of view (dot product)
    in_view, view_factor = is_light_in_view(camera_pos, camera_rotation, light_pos)
    if not in_view:
        return max(0.0, light_visibility - 0.08)

    # Light position on screen
    screen_pos = world_to_screen(light_pos)
    x = int(screen_pos[0])
    y = int(screen_pos[1])

    # Check if it's within screen bounds
    if x < 0 or x >= 800 or y < 0 or y >= 600:
        return max(0.0, light_visibility - 0.08)

    # Get depth at light position from Z-buffer
    depth = glReadPixels(x, y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)

    if isinstance(depth, np.ndarray):
        depth = float(depth[0][0])  # or depth[0] depending on PyOpenGL version

    # Normalized light depth
    light_ndc_z = screen_pos[2]

    # If depth buffer contains smaller value, something is occluding the light
    if depth + 0.001 < light_ndc_z:
        target_visibility = 0.05  # occluded
    else:
        target_visibility = view_factor * 0.8 + 0.2  # partially/transparent

    # Smooth transition
    transition_speed = 0.04
    if light_visibility < target_visibility:
        return min(target_visibility, light_visibility + transition_speed)
    elif light_visibility > target_visibility:
        return max(target_visibility, light_visibility - transition_speed)

    return light_visibility


def draw_lens_flares(light_pos, light_visibility):
    """Draws lens flares with size dependent on light brightness"""
    if light_visibility < 0.02:
        return  # Don't draw if light is invisible

    # Switch to 2D mode
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 800, 0, 600, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Disable depth test for 2D
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)

    # Light position on screen
    light_screen_pos = world_to_screen(light_pos)
    center_x, center_y = 400, 300  # Screen center

    # Check if light is on screen
    if not (0 <= light_screen_pos[0] <= 800 and 0 <= light_screen_pos[1] <= 600):
        # Restore settings and exit
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        return

    # Line from screen center to light position
    dx = light_screen_pos[0] - center_x
    dy = light_screen_pos[1] - center_y

    # Size scaling based on light visibility
    size_multiplier = 0.3 + 0.7 * light_visibility  # From 30% to 100% size

    # Configuration of different flare types (without animation)
    flare_configs = [
        [0.0, 'circle', 100, [1.0, 1.0, 0.8], 'filled'],
        [0.2, 'circle', 80, [0.8, 0.9, 1.0], 'filled'],
        [0.4, 'circle', 60, [1.0, 1.0, 0.6], 'filled'],
        [0.6, 'circle', 45, [1.0, 0.95, 0.6], 'hollow'],
        [0.8, 'circle', 30, [1.0, 1.0, 1.0], 'filled'],
        [1.0, 'circle', 20, [0.85, 0.95, 1.0], 'filled'],
        [1.2, 'circle', 10, [1.0, 1.0, 1.0], 'hollow']
    ]

    for config in flare_configs:
        pos, flare_type, base_size, color, fill_mode = config

        flare_x = center_x + dx * pos
        flare_y = center_y + dy * pos

        if -100 <= flare_x <= 900 and -100 <= flare_y <= 700:
            size = base_size * size_multiplier
            alpha = light_visibility * (0.4 + 0.4 * (1 - pos * 0.3))
            glColor4f(color[0], color[1], color[2], alpha)

            if flare_type == 'circle':
                # Draw filled or hollow circle
                if fill_mode == 'filled':
                    glBegin(GL_POLYGON)
                else:
                    glLineWidth(2.0)
                    glBegin(GL_LINE_LOOP)

                for angle in range(0, 360, 15):
                    rad = math.radians(angle)
                    x = flare_x + math.cos(rad) * size
                    y = flare_y + math.sin(rad) * size
                    glVertex2f(x, y)
                glEnd()

    # Main light - also scaled
    main_alpha = light_visibility * 0.4
    glColor4f(1.0, 1.0, 0.8, main_alpha)

    # Large circle at light position
    main_size = 80 * size_multiplier
    glBegin(GL_POLYGON)
    for angle in range(0, 360, 10):
        rad = math.radians(angle)
        x = light_screen_pos[0] + math.cos(rad) * main_size
        y = light_screen_pos[1] + math.sin(rad) * main_size
        glVertex2f(x, y)
    glEnd()

    # Restore settings
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)

    # Restore matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)