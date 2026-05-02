""" parallax.py
Implementa a lógica de rolagem paralaxe para fundos de tela.
 - Permite criar profundidade visual movendo camadas de fundo a velocidades diferentes em relação à câmera do jogo.
"""

from OpenGL.GL import *
from src.utils import load_texture

class ParallaxLayer:
    """
    Representa uma camada de fundo (background) que responde ao movimento da câmera.
     - Quanto menor o scroll_factor, mais distante a camada parece estar.
    """

    def __init__(self, texture_path, scroll_factor):
        """
        Inicializa uma nova camada de parallax.
        :param texture_path: Caminho da imagem (asset) do fundo.
        :param scroll_factor: Fator de velocidade (0.0 a 1.0).
         - Ex: 0.1 move bem devagar (fundo), 0.5 move mais rápido (meio).
        """
        self.texture_id = load_texture(texture_path)[0]
        self.scroll_factor = scroll_factor

    def draw(self, camera_x):
        """
        Renderiza a camada de fundo com o deslocamento calculado pela posição da câmera.
        :param camera_x: Posição atual da câmera no mundo.
        """

        # calcula o deslocamento baseado na posição da câmera e na velocidade da camada
        # o sinal negativo inverte o movimento para criar a ilusão de profundidade
        offset_x = -(camera_x * self.scroll_factor)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glColor3f(1.0, 1.0, 1.0)

        # usamos offsets calculados para deslizar a textura conforme a câmera se move.
        # os valores -1, 3 e 1 definem a área de cobertura extendida para evitar "buracos" quando o fundo desliza.
        glBegin(GL_QUADS)

        # coordenadas de textura e vértices de posição
        glTexCoord2f(0, 1);
        glVertex2f(-1 + offset_x, -1)
        glTexCoord2f(1, 1);
        glVertex2f(3 + offset_x, -1)
        glTexCoord2f(1, 0);
        glVertex2f(3 + offset_x, 1)
        glTexCoord2f(0, 0);
        glVertex2f(-1 + offset_x, 1)
        glEnd()
        glDisable(GL_TEXTURE_2D)