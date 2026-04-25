from OpenGL.raw.GL.ARB.tessellation_shader import GL_QUADS
from OpenGL.GL import *

from src.entities.game_object import GameObject

class Personagem(GameObject):
    def __init__(self, x, y, width, height, color, settings):
        super().__init__(x, y, width, height, color)
        self.have_item = False
        self.settings = settings
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.no_chao = False

    #desenho da granada
    def draw(self, camera_x=0.0):

        super().draw(camera_x)
        if getattr(self, 'tem_item', False):
            tamanho_item = float(self.width * 0.4)

            item_x = float(self.centro_x + (self.width * 0.6) - camera_x)

            item_y = float(self.centro_y)

            metade_tam = float(tamanho_item / 2.0)

            glBegin(GL_QUADS)
            #cor do item
            glColor3f(1.0, 0.0, 0.0)

            glVertex2f(item_x - metade_tam, item_y - metade_tam)
            glVertex2f(item_x + metade_tam, item_y - metade_tam)
            glVertex2f(item_x + metade_tam, item_y + metade_tam)
            glVertex2f(item_x - metade_tam, item_y + metade_tam)

            glEnd()

    def update_physics(self, delta_time):
        # Gravidade e movimento
        self.vel_y += self.settings.gravity * delta_time
        self.centro_x += self.vel_x * delta_time
        self.centro_y += self.vel_y * delta_time