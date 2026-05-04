from OpenGL.GL import *
import math

class ExplosaoVisual:
    """
    Efeito visual de expansão rápida de raio, utilizado para representar a explosão de granadas.
    """
    def __init__(self, x, y, raio_maximo):
        self.centro_x = x
        self.centro_y = y
        self.raio_maximo = raio_maximo

        # Ciclo de vida da animação
        self.raio_atual = 0.01
        self.tempo_vida = 0.3
        self.tempo_passado = 0.0
        self.destruir = False

        self.cor_centro = (1.0, 1.0, 0.8)
        self.cor_borda = (1.0, 0.3, 0.0)

    def update(self, dt):
        """Atualiza o raio da explosão com base no tempo decorrido usando atenuação logarítmica."""
        self.tempo_passado += dt
        progresso = self.tempo_passado / self.tempo_vida

        if progresso >= 1.0:
            self.destruir = True
            return

        # Expansão rápida no início que desacelera gradativamente
        fator_expansao = 1 - (1 - progresso) * (1 - progresso)
        self.raio_atual = self.raio_maximo * fator_expansao

    def draw(self, camera_x=0.0):
        """Renderiza a explosão utilizando GL_TRIANGLE_FAN e cálculo de transparência (Fade-out)."""
        alpha = 1.0 - (self.tempo_passado / self.tempo_vida)
        if alpha < 0: alpha = 0

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        x = self.centro_x - camera_x
        y = self.centro_y

        glBegin(GL_TRIANGLE_FAN)

        # Vértice central
        glColor4f(self.cor_centro[0], self.cor_centro[1], self.cor_centro[2], alpha)
        glVertex2f(x, y)

        # Vértices periféricos gerando o círculo
        glColor4f(self.cor_borda[0], self.cor_borda[1], self.cor_borda[2], alpha * 0.5)
        num_segmentos = 16
        for i in range(num_segmentos + 1):
            angulo = 2.0 * math.pi * i / num_segmentos
            vx = x + math.cos(angulo) * self.raio_atual
            vy = y + math.sin(angulo) * self.raio_atual
            glVertex2f(vx, vy)

        glEnd()


class FogoChao:
    """
    Representa a área de efeito gerada por uma Molotov.
    Possui tempo de vida prolongado e animação de oscilação nas chamas.
    """
    def __init__(self, x, y, largura=1.5):
        self.centro_x = x
        self.centro_y = y
        self.largura = largura
        self.altura = 0.25

        self.tempo_vida = 5.0
        self.tempo_passado = 0.0
        self.destruir = False
        self.tempo_animacao = 0.0

    def update(self, dt):
        """Controla o tempo de vida e o timer para a função seno de oscilação."""
        self.tempo_passado += dt
        self.tempo_animacao += dt * 15.0

        if self.tempo_passado >= self.tempo_vida:
            self.destruir = True

    def draw(self, camera_x=0.0):
        """Renderiza o fogo com um fade-out suave no último segundo de vida e tremulação vertical."""
        alpha = 1.0
        tempo_restante = self.tempo_vida - self.tempo_passado
        if tempo_restante < 1.0:
            alpha = tempo_restante

        if alpha <= 0:
            alpha = 0

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        x = self.centro_x - camera_x
        y = self.centro_y
        half_w = self.largura / 2.0

        # Oscilação visual da altura usando seno
        altura_dinamica = self.altura + (math.sin(self.tempo_animacao) * 0.05)

        glBegin(GL_QUADS)
        # Base da chama (mais escura/opaca)
        glColor4f(0.8, 0.1, 0.0, alpha * 0.9)
        glVertex2f(x - half_w, y)
        glVertex2f(x + half_w, y)

        # Topo da chama (mais clara/transparente com altura variável)
        glColor4f(1.0, 0.6, 0.0, alpha * 0.6)
        glVertex2f(x + half_w, y + altura_dinamica)
        glVertex2f(x - half_w, y + altura_dinamica)
        glEnd()