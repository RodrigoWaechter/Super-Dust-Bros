""" chao.py
Responsável pela renderização de blocos de chão texturizados.
 - Implementa cache de texturas para otimização de performance e renderização com tiling.
"""

from src.entities.game_object import GameObject
from src.utils import load_texture
from OpenGL.GL import *

class ChaoTexturizado(GameObject):
    """
    Representa um bloco de chão físico que renderiza uma textura externa.
     - Utiliza um cache estático para evitar recarregamento redundante de assets na GPU.
    """

    # dicionário estático para compartilhar ids de textura entre instâncias
    _texture_cache = {}

    def __init__(self, x, y, width, height, textura_path):
        """
        Inicializa o bloco de chão texturizado.
        """
        super().__init__(x, y, width, height, (1.0, 1.0, 1.0))
        self.texture_path = textura_path

    def draw(self, camera_x=0.0):
        """
        Renderiza o bloco de chão no plano da tela com offset de câmera.
        Gerencia o carregamento de texturas sob demanda.
        """

        # carregamento sob demanda: carrega apenas na primeira vez que for chamado
        if self.texture_path not in ChaoTexturizado._texture_cache:
            tex_id = load_texture(self.texture_path)[0]

            # configura o OpenGL para repetir a textura (tiling) em ambos os eixos
            glBindTexture(GL_TEXTURE_2D, tex_id)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

            ChaoTexturizado._texture_cache[self.texture_path] = tex_id

        # recupera o id da textura do cache
        texture_id = ChaoTexturizado._texture_cache[self.texture_path]

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glColor3f(1.0, 1.0, 1.0)

        x = self.centro_x - camera_x
        y = self.centro_y
        half_w = self.width / 2
        half_h = self.height / 2

        # controle de zoom
        zoom = 0.15

        glBegin(GL_QUADS)
        glTexCoord2f(0, zoom);
        glVertex2f(x - half_w, y - half_h)
        glTexCoord2f(zoom, zoom);
        glVertex2f(x + half_w, y - half_h)
        glTexCoord2f(zoom, 0);
        glVertex2f(x + half_w, y + half_h)
        glTexCoord2f(0, 0);
        glVertex2f(x - half_w, y + half_h)
        glEnd()
        glDisable(GL_TEXTURE_2D)