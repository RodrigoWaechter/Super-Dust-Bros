# src/entities/explosao.py
from OpenGL.GL import *
import math


class ExplosaoVisual:
    def __init__(self, x, y, raio_maximo):
        self.centro_x = x
        self.centro_y = y
        self.raio_maximo = raio_maximo

        # Estado da animação
        self.raio_atual = 0.01  # Começa quase invisível
        self.tempo_vida = 0.3  # Duração total do efeito em segundos (bem rápido)
        self.tempo_passado = 0.0
        self.destruir = False  # Flag para o engine remover

        # Cores (R, G, B)
        self.cor_centro = (1.0, 1.0, 0.8)  # Amarelo brilhante
        self.cor_borda = (1.0, 0.3, 0.0)  # Laranja/Vermelho

    def update(self, dt):
        self.tempo_passado += dt

        # Calcula o progresso da animação (de 0.0 a 1.0)
        progresso = self.tempo_passado / self.tempo_vida

        if progresso >= 1.0:
            self.destruir = True
            return

        # O raio expande rapidamente no começo e para no final
        fator_expansao = 1 - (1 - progresso) * (1 - progresso)
        self.raio_atual = self.raio_maximo * fator_expansao

    def draw(self, camera_x=0.0):
        # Calcula a transparência (alpha) baseada no tempo
        alpha = 1.0 - (self.tempo_passado / self.tempo_vida)
        if alpha < 0: alpha = 0

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        x = self.centro_x - camera_x
        y = self.centro_y

        # Desenha um círculo usando Triangle Fan
        glBegin(GL_TRIANGLE_FAN)

        # Vértice central (brilhante e mais opaco)
        glColor4f(self.cor_centro[0], self.cor_centro[1], self.cor_centro[2], alpha)
        glVertex2f(x, y)

        # Vértices da borda (cor de fogo e vai sumindo)
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
    Representa a poça de fogo gerada pela Molotov ao quebrar no chão.
    """

    def __init__(self, x, y, largura=1.5):
        self.centro_x = x
        self.centro_y = y
        self.largura = largura
        self.altura = 0.25  # Altura base das chamas

        self.tempo_vida = 5.0  # Fica 5 segundos queimando o chão
        self.tempo_passado = 0.0
        self.destruir = False

        # Variável para animar a oscilação do fogo
        self.tempo_animacao = 0.0

    def update(self, dt):
        self.tempo_passado += dt
        self.tempo_animacao += dt * 15.0  # Velocidade da "tremulação" do fogo

        if self.tempo_passado >= self.tempo_vida:
            self.destruir = True

    def draw(self, camera_x=0.0):
        # O fogo começa totalmente visível, mas no último segundo ele apaga suavemente
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

        # Oscila a altura do fogo usando a função seno para parecer orgânico
        altura_dinamica = self.altura + (math.sin(self.tempo_animacao) * 0.05)

        # Desenha o tapete de fogo no chão
        glBegin(GL_QUADS)

        # Base do fogo (mais avermelhada e opaca)
        glColor4f(0.8, 0.1, 0.0, alpha * 0.9)
        glVertex2f(x - half_w, y)
        glVertex2f(x + half_w, y)

        # Topo do fogo (mais amarelado e um pouco mais transparente)
        glColor4f(1.0, 0.6, 0.0, alpha * 0.6)
        glVertex2f(x + half_w, y + altura_dinamica)
        glVertex2f(x - half_w, y + altura_dinamica)

        glEnd()