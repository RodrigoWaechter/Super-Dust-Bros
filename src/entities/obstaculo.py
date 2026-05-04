"""
obstaculo.py
Define a classe Obstaculo, responsável por representar elementos físicos do cenário
com suporte a renderização por cores sólidas ou texturas.
"""

from src.entities.game_object import GameObject
from src.utils import load_texture
from OpenGL.GL import *

class Obstaculo(GameObject):
    """
    Bloco sólido que interage com a física do jogo servindo como plataformas ou paredes.
    Pode renderizar texturas utilizando cache para otimização ou cores sólidas como fallback.
    """

    _texture_cache = {}

    def __init__(self, x, y, width, height, color=(0.4, 0.2, 0.0), texture_path=None):
        super().__init__(x, y, width, height, color)
        self.texture_path = texture_path

    def draw(self, camera_x=0.0):
        """
        Avalia se há uma textura a ser renderizada. Caso não haja,
        aciona o método draw() base da classe GameObject.
        """
        if not self.texture_path:
            super().draw(camera_x)
            return

        # Carregamento sob demanda (Lazy Loading) na GPU
        if self.texture_path not in Obstaculo._texture_cache:
            tex_id = load_texture(self.texture_path)[0]
            Obstaculo._texture_cache[self.texture_path] = tex_id

        texture_id = Obstaculo._texture_cache[self.texture_path]

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glColor3f(1.0, 1.0, 1.0)

        x = self.centro_x - camera_x
        y = self.centro_y
        half_w = self.width / 2
        half_h = self.height / 2

        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(x - half_w, y - half_h)
        glTexCoord2f(1, 1); glVertex2f(x + half_w, y - half_h)
        glTexCoord2f(1, 0); glVertex2f(x + half_w, y + half_h)
        glTexCoord2f(0, 0); glVertex2f(x - half_w, y + half_h)
        glEnd()
        glDisable(GL_TEXTURE_2D)