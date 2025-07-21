import pygame
from OpenGL.GL import *

from pygame import image


def load_texture_from_file(filename):
    surf = image.load(filename)
    surf = pygame.transform.flip(surf, False, True)
    image_data = pygame.image.tostring(surf, "RGB", True)
    width, height = surf.get_size()

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    return tex_id


def draw_textured_cube(texture_id):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glBegin(GL_QUADS)

    # front
    glTexCoord2f(0, 0); glVertex3f(-0.5, -0.5, 0.5)
    glTexCoord2f(1, 0); glVertex3f(0.5, -0.5, 0.5)
    glTexCoord2f(1, 1); glVertex3f(0.5, 0.5, 0.5)
    glTexCoord2f(0, 1); glVertex3f(-0.5, 0.5, 0.5)

    # back
    glTexCoord2f(0, 0); glVertex3f(0.5, -0.5, -0.5)
    glTexCoord2f(1, 0); glVertex3f(-0.5, -0.5, -0.5)
    glTexCoord2f(1, 1); glVertex3f(-0.5, 0.5, -0.5)
    glTexCoord2f(0, 1); glVertex3f(0.5, 0.5, -0.5)

    # left
    glTexCoord2f(0, 0); glVertex3f(-0.5, -0.5, -0.5)
    glTexCoord2f(1, 0); glVertex3f(-0.5, -0.5, 0.5)
    glTexCoord2f(1, 1); glVertex3f(-0.5, 0.5, 0.5)
    glTexCoord2f(0, 1); glVertex3f(-0.5, 0.5, -0.5)

    # right
    glTexCoord2f(0, 0); glVertex3f(0.5, -0.5, 0.5)
    glTexCoord2f(1, 0); glVertex3f(0.5, -0.5, -0.5)
    glTexCoord2f(1, 1); glVertex3f(0.5, 0.5, -0.5)
    glTexCoord2f(0, 1); glVertex3f(0.5, 0.5, 0.5)

    # up
    glTexCoord2f(0, 0); glVertex3f(-0.5, 0.5, 0.5)
    glTexCoord2f(1, 0); glVertex3f(0.5, 0.5, 0.5)
    glTexCoord2f(1, 1); glVertex3f(0.5, 0.5, -0.5)
    glTexCoord2f(0, 1); glVertex3f(-0.5, 0.5, -0.5)

    # down
    glTexCoord2f(0, 0); glVertex3f(-0.5, -0.5, -0.5)
    glTexCoord2f(1, 0); glVertex3f(0.5, -0.5, -0.5)
    glTexCoord2f(1, 1); glVertex3f(0.5, -0.5, 0.5)
    glTexCoord2f(0, 1); glVertex3f(-0.5, -0.5, 0.5)

    glEnd()
    glDisable(GL_TEXTURE_2D)


def draw_background_with_texture(texture_id):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 800, 0, 600, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(0, 0)
    glTexCoord2f(1, 0); glVertex2f(800, 0)
    glTexCoord2f(1, 1); glVertex2f(800, 600)
    glTexCoord2f(0, 1); glVertex2f(0, 600)
    glEnd()

    glDisable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_ground():
    """drawing a grey plane """
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(-5, -2, -5)
    glVertex3f(5, -2, -5)
    glVertex3f(5, -2, 5)
    glVertex3f(-5, -2, 5)
    glEnd()


def draw_light_source(light_pos, light_visibility):
    """drawing light source"""
    glPushMatrix()
    glTranslatef(light_pos[0], light_pos[1], light_pos[2])

    # Color depends on visibility
    brightness = 0.3 + 0.7 * light_visibility  # minimum 30% brightness
    glColor3f(1.0, 1.0, brightness)

    glPointSize(15.0)
    glBegin(GL_POINTS)
    glVertex3f(0, 0, 0)
    glEnd()
    glPopMatrix()


def world_to_screen(world_pos):
    """Converts 3D position to on-screen position"""
    # modelview and projection matrices
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)
    viewport = glGetIntegerv(GL_VIEWPORT)

    try:
        from OpenGL.GLU import gluProject
        screen_x, screen_y, screen_z = gluProject(
            world_pos[0], world_pos[1], world_pos[2],
            modelview, projection, viewport
        )
        return [screen_x, screen_y, screen_z]
    except:
        # Fallback
        return [400, 300, 0]  # screen center