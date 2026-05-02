""" obstaculo.py
Define a classe Obstaculo, responsável por representar elementos físicos do cenário
com suporte a renderização por cores sólidas ou texturas.
"""

from src.entities.game_object import GameObject
from src.utils import load_texture
from OpenGL.GL import *

class Obstaculo(GameObject):
    """
    Representa um objeto sólido no cenário.
    Utiliza um cache estático de texturas para otimização de performance e permite renderização customizada via path de imagem.
    """

    _texture_cache = {} # cache estático (compartilhado entre todas as instâncias de Obstaculo)

    def __init__(self, x, y, width, height, color=(0.4, 0.2, 0.0), texture_path=None):
        """
        Inicializa o obstáculo.
        :param color: Cor RGB padrão caso nenhuma textura seja fornecida.
        :param texture_path: Caminho opcional da textura a ser renderizada.
        """

        super().__init__(x, y, width, height, color)
        self.texture_path = texture_path

    def draw(self, camera_x=0.0):
        """
        Renderiza o obstáculo na tela.
        Se uma texture_path estiver definida, renderiza a imagem correspondente.
        Caso contrário, utiliza o metodo draw() padrão da classe GameObject (cor sólida).
        """

        # caso não houver textura, desenha o obstáculo colorido padrão
        if not self.texture_path:
            super().draw(camera_x)
            return

        # carregamento sob demanda
        if self.texture_path not in Obstaculo._texture_cache:
            tex_id = load_texture(self.texture_path)[0]
            Obstaculo._texture_cache[self.texture_path] = tex_id

        texture_id = Obstaculo._texture_cache[self.texture_path]

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glColor3f(1.0, 1.0, 1.0)  # branco para não alterar a cor da imagem

        x = self.centro_x - camera_x
        y = self.centro_y
        half_w = self.width / 2
        half_h = self.height / 2

        # desenha o quad texturizado cobrindo a área do obstáculo
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1);
        glVertex2f(x - half_w, y - half_h)
        glTexCoord2f(1, 1);
        glVertex2f(x + half_w, y - half_h)
        glTexCoord2f(1, 0);
        glVertex2f(x + half_w, y + half_h)
        glTexCoord2f(0, 0);
        glVertex2f(x - half_w, y + half_h)
        glEnd()
        glDisable(GL_TEXTURE_2D)