from OpenGL.GL import *

class ParallaxLayer:
    def __init__(self, texture, tex_w, tex_h, speed):
        self.texture = texture
        self.tex_w = tex_w
        self.tex_h = tex_h
        self.speed = speed

    def draw(self, camera_x):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glColor3f(1.0, 1.0, 1.0)

        u_offset = (camera_x * self.speed) / self.tex_w

        glBegin(GL_QUADS)

        glTexCoord2f(0.0 + u_offset, 1.0)
        glVertex2f(-1.0, -1.0)

        glTexCoord2f(1.0 + u_offset, 1.0)
        glVertex2f(1.0, -1.0)

        glTexCoord2f(1.0 + u_offset, 0.0)
        glVertex2f(1.0, 1.0)

        glTexCoord2f(0.0 + u_offset, 0.0)
        glVertex2f(-1.0, 1.0)

        glEnd()
        glDisable(GL_TEXTURE_2D)