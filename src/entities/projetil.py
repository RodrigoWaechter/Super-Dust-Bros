from src.entities.game_object import GameObject
from src.utils import load_texture
from OpenGL.GL import *


class Projetil(GameObject):
    """
    Objeto balístico que se move linearmente com alcance pré-definido.
    Usado pelas armas do player e inimigo (AK-47 / AWP).
    """

    def __init__(self, x, y, direcao, origem="player", speed=1.8):
        # A escala é sensivelmente ajustada visualmente em X/Y para o quad da munição
        super().__init__(x, y, 0.1, 0.05, (1.0, 1.0, 1.0))
        self.vel_x = speed * direcao
        self.direcao = direcao
        self.start_x = x
        # Aumentamos o alcance máximo para o tiro rápido não sumir na metade do caminho
        self.max_distance = 1.5
        self.destruir = False
        self.origem = origem
        self.texture = None

    def update(self, delta_time):
        """Atualiza física linear e controla culling via distância percorrida."""
        self.centro_x += self.vel_x * delta_time
        if abs(self.centro_x - self.start_x) >= self.max_distance:
            self.destruir = True

    def draw(self, camera_x=0.0):
        if self.texture is None:
            self.texture = load_texture("assets/bullets/municao.png")[0]

        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glBindTexture(GL_TEXTURE_2D, self.texture)
        glColor3f(1.0, 1.0, 1.0)

        x = self.centro_x - camera_x
        y = self.centro_y
        half_w = self.width / 2
        half_h = self.height / 2

        glPushMatrix()
        glTranslatef(x, y, 0.0)

        glBegin(GL_QUADS)
        # Espelha as coordenadas UV baseadas na direção vetor X atual
        if self.direcao == 1:
            glTexCoord2f(0, 1); glVertex2f(-half_w, -half_h)
            glTexCoord2f(1, 1); glVertex2f(half_w, -half_h)
            glTexCoord2f(1, 0); glVertex2f(half_w, half_h)
            glTexCoord2f(0, 0); glVertex2f(-half_w, half_h)
        else:
            glTexCoord2f(1, 1); glVertex2f(-half_w, -half_h)
            glTexCoord2f(0, 1); glVertex2f(half_w, -half_h)
            glTexCoord2f(0, 0); glVertex2f(half_w, half_h)
            glTexCoord2f(1, 0); glVertex2f(-half_w, half_h)
        glEnd()

        glPopMatrix()
        glDisable(GL_TEXTURE_2D)


class GranadaAtiva(GameObject):
    """
    Entidade balística parabólica acionada por arremesso.
    Lida com gravidade, raio explosivo customizado e animação de rotação com matrizes.
    """
    def __init__(self, x, y, direcao, origem="player"):
        super().__init__(x, y, 0.08, 0.08, (1.0, 1.0, 1.0))

        self.origem = origem
        self.destruir = False
        self.texture = None

        # Vetores de lançamento parabólico e propriedades explosivas
        self.vel_x = 0.8 * direcao
        self.vel_y = 1.2
        self.gravity = -3.0
        self.tempo_vida = 1.5
        self.raio_explosao = 0.5
        self.dano = 100

        self.rotacao = 0.0

    def update(self, delta_time):
        """Computa física de lançamento oblíquo e variação rotacional."""
        self.vel_y += self.gravity * delta_time

        self.centro_x += self.vel_x * delta_time
        self.centro_y += self.vel_y * delta_time
        self.rotacao += 360.0 * delta_time

        self.tempo_vida -= delta_time
        if self.tempo_vida <= 0:
            self.destruir = True

    def draw(self, camera_x=0.0):
        if self.texture is None:
            self.texture = load_texture("assets/power_ups/power-up-he.png")[0]

        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glBindTexture(GL_TEXTURE_2D, self.texture)
        glColor3f(1.0, 1.0, 1.0)

        x = self.centro_x - camera_x
        y = self.centro_y
        half_w = self.width / 2
        half_h = self.height / 2

        glPushMatrix()

        # Isolamento do sistema de coordenadas para aplicar rotação centrada no modelo
        glTranslatef(x, y, 0.0)
        glRotatef(self.rotacao, 0.0, 0.0, 1.0)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(-half_w, -half_h)
        glTexCoord2f(1, 1); glVertex2f(half_w, -half_h)
        glTexCoord2f(1, 0); glVertex2f(half_w, half_h)
        glTexCoord2f(0, 0); glVertex2f(-half_w, half_h)
        glEnd()

        glPopMatrix()
        glDisable(GL_TEXTURE_2D)


class MolotovAtiva(GameObject):
    """
    Entidade balística parabólica equivalente à Granada,
    mas projetada para gerar uma classe FogoChao() ao invés de ExplosaoVisual().
    """

    def __init__(self, x, y, direcao, origem="player"):
        super().__init__(x, y, 0.08, 0.08, (1.0, 1.0, 1.0))

        self.origem = origem
        self.destruir = False
        self.texture = None

        self.vel_x = 0.8 * direcao
        self.vel_y = 1.2
        self.gravity = -3.0
        self.tempo_vida = 1.5

        self.rotacao = 0.0

    def update(self, delta_time):
        self.vel_y += self.gravity * delta_time

        self.centro_x += self.vel_x * delta_time
        self.centro_y += self.vel_y * delta_time
        self.rotacao += 360.0 * delta_time

        self.tempo_vida -= delta_time
        if self.tempo_vida <= 0:
            self.destruir = True

    def draw(self, camera_x=0.0):
        if self.texture is None:
            self.texture = load_texture("assets/power_ups/power-up-molotov.png")[0]

        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glBindTexture(GL_TEXTURE_2D, self.texture)
        glColor3f(1.0, 1.0, 1.0)

        x = self.centro_x - camera_x
        y = self.centro_y
        half_w = self.width / 2
        half_h = self.height / 2

        glPushMatrix()

        glTranslatef(x, y, 0.0)
        glRotatef(self.rotacao, 0.0, 0.0, 1.0)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(-half_w, -half_h)
        glTexCoord2f(1, 1); glVertex2f(half_w, -half_h)
        glTexCoord2f(1, 0); glVertex2f(half_w, half_h)
        glTexCoord2f(0, 0); glVertex2f(-half_w, half_h)
        glEnd()

        glPopMatrix()
        glDisable(GL_TEXTURE_2D)