from src.entities.game_object import GameObject
from src.utils import load_texture
from OpenGL.GL import *


class Projetil(GameObject):
    """
    Projétil padrão em linha reta (AK-47 / AWP).
    """

    def __init__(self, x, y, direcao, origem="player", speed=0.9):
        # aumanta levemente o tamanho (0.1, 0.05) para o sprite da munição aparecer bem
        super().__init__(x, y, 0.1, 0.05, (1.0, 1.0, 1.0))
        self.vel_x = speed * direcao
        self.direcao = direcao  # necessário para o espelhamento (direita/esquerda) do sprite
        self.start_x = x
        self.max_distance = 0.8
        self.destruir = False
        self.origem = origem
        self.texture = None

    def update(self, delta_time):
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
        # Se a direcao for 1 (direita), usa o padrão. Se -1 (esquerda), inverte as coordenadas X da textura
        if self.direcao == 1:
            glTexCoord2f(0, 1);
            glVertex2f(-half_w, -half_h)
            glTexCoord2f(1, 1);
            glVertex2f(half_w, -half_h)
            glTexCoord2f(1, 0);
            glVertex2f(half_w, half_h)
            glTexCoord2f(0, 0);
            glVertex2f(-half_w, half_h)
        else:
            glTexCoord2f(1, 1);
            glVertex2f(-half_w, -half_h)
            glTexCoord2f(0, 1);
            glVertex2f(half_w, -half_h)
            glTexCoord2f(0, 0);
            glVertex2f(half_w, half_h)
            glTexCoord2f(1, 0);
            glVertex2f(-half_w, half_h)
        glEnd()

        glPopMatrix()
        glDisable(GL_TEXTURE_2D)


class GranadaAtiva(GameObject):
    def __init__(self, x, y, direcao, origem="player"):
        super().__init__(x, y, 0.08, 0.08, (1.0, 1.0, 1.0))

        self.origem = origem
        self.destruir = False
        self.texture = None  # lazy loading para a arte

        # Física do arremesso
        self.vel_x = 0.8 * direcao
        self.vel_y = 1.2
        self.gravity = -3.0
        self.tempo_vida = 1.5
        self.raio_explosao = 0.5
        self.dano = 100

        # Para animação de rotação
        self.rotacao = 0.0

    def update(self, delta_time):
        # Gravidade na velocidade Y
        self.vel_y += self.gravity * delta_time

        # Move a granada nos eixos X e Y
        self.centro_x += self.vel_x * delta_time
        self.centro_y += self.vel_y * delta_time
        self.rotacao += 360.0 * delta_time

        # Diminui o temporizador
        self.tempo_vida -= delta_time
        if self.tempo_vida <= 0:
            self.destruir = True

    def draw(self, camera_x=0.0):
        # granada girando no ar
        if self.texture is None:
            self.texture = load_texture("assets/power_ups/power-up-he.png")[0]

        glEnable(GL_TEXTURE_2D)

        # Habilita transparência para o PNG
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glBindTexture(GL_TEXTURE_2D, self.texture)
        glColor3f(1.0, 1.0, 1.0)

        x = self.centro_x - camera_x
        y = self.centro_y
        half_w = self.width / 2
        half_h = self.height / 2

        glPushMatrix()

        # Translada para o centro do objeto
        glTranslatef(x, y, 0.0)

        # Rotaciona no eixo Z (perpendicular à tela)
        glRotatef(self.rotacao, 0.0, 0.0, 1.0)

        # Desenha o Quad centralizado no (0,0) local
        glBegin(GL_QUADS)
        # Vértices são relativas ao centro (-half, +half)
        glTexCoord2f(0, 1)
        glVertex2f(-half_w, -half_h)
        glTexCoord2f(1, 1)
        glVertex2f(half_w, -half_h)
        glTexCoord2f(1, 0)
        glVertex2f(half_w, half_h)
        glTexCoord2f(0, 0)
        glVertex2f(-half_w, half_h)
        glEnd()

        # Restaura a matriz de transformação original
        glPopMatrix()

        glDisable(GL_TEXTURE_2D)


class MolotovAtiva(GameObject):
    """
    Garrafa da Molotov voando pelo ar antes de quebrar.
    """

    def __init__(self, x, y, direcao, origem="player"):
        super().__init__(x, y, 0.08, 0.08, (1.0, 1.0, 1.0))

        self.origem = origem
        self.destruir = False
        self.texture = None

        # Física do arremesso idêntica à da Granada
        self.vel_x = 0.8 * direcao
        self.vel_y = 1.2
        self.gravity = -3.0
        self.tempo_vida = 1.5

        # Para animação de rotação
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
        # Garrafa girando no ar
        if self.texture is None:
            self.texture = load_texture("assets/power_ups/power-up-molotov.png")[0]

        glEnable(GL_TEXTURE_2D)

        # Habilita transparência para o PNG
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
        glTexCoord2f(0, 1)
        glVertex2f(-half_w, -half_h)
        glTexCoord2f(1, 1)
        glVertex2f(half_w, -half_h)
        glTexCoord2f(1, 0)
        glVertex2f(half_w, half_h)
        glTexCoord2f(0, 0)
        glVertex2f(-half_w, half_h)
        glEnd()

        glPopMatrix()

        glDisable(GL_TEXTURE_2D)