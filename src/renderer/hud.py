from OpenGL.GL import *
import time

class HUD:
    def __init__(self):
        self.limit = 120
        self.start_time = None

    # Chamadas de desenho da hud
    def draw(self, player, nivel):
        self.draw_health_bar(player.vidas)
        self.draw_number(player.vidas, -0.54, 0.85)
        self.draw_timer()
        self.draw_level_counter(nivel)

    # Construção do dígito
    def draw_digit(self, digit, x, y, size):
        segmentos = {
            "0": [1, 1, 1, 1, 1, 1, 0], "1": [0, 1, 1, 0, 0, 0, 0],
            "2": [1, 1, 0, 1, 1, 0, 1], "3": [1, 1, 1, 1, 0, 0, 1],
            "4": [0, 1, 1, 0, 0, 1, 1], "5": [1, 0, 1, 1, 0, 1, 1],
            "6": [1, 0, 1, 1, 1, 1, 1], "7": [1, 1, 1, 0, 0, 0, 0],
            "8": [1, 1, 1, 1, 1, 1, 1], "9": [1, 1, 1, 1, 0, 1, 1],
        }

        seg = segmentos[digit]

        thickness = size * 0.3
        w = size
        h = size * 2

        def quad(x1, y1, x2, y2):
            glVertex2f(x1, y1)
            glVertex2f(x2, y1)
            glVertex2f(x2, y2)
            glVertex2f(x1, y2)

        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)

        # topo
        if seg[0]: quad(x, y + h - thickness, x + w, y + h)

        # direita superior
        if seg[1]: quad(x + w - thickness, y + h / 2, x + w, y + h)

        # direita inferior
        if seg[2]: quad(x + w - thickness, y, x + w, y + h / 2)

        # base
        if seg[3]: quad(x, y, x + w, y + thickness)

        # esquerda inferior
        if seg[4]: quad(x, y, x + thickness, y + h / 2)

        # esquerda superior
        if seg[5]: quad(x, y + h / 2, x + thickness, y + h)

        # meio
        if seg[6]: quad(x, y + h / 2 - thickness / 2, x + w, y + h / 2 + thickness / 2)

        glEnd()

    def draw_level_counter(self, nivel):
        # Desenha o número do nível no centro superior
        self.draw_number(nivel, -0.05, 0.85)

    # Métodos do Timer
    def start_timer(self):
        self.start_time = time.time()

    def reset_timer(self):
        self.start_timer()

    def get_time(self):
        elapsed_time = int(time.time() - self.start_time)
       # print(self.start_time)
       # print(elapsed_time)
        remaining_time = max(0, self.limit - elapsed_time)
        return remaining_time

    def is_time_up(self):
        elapsed_time = time.time() - self.start_time
        return elapsed_time >= self.limit

    def draw_timer(self):
        seconds = self.get_time()

        time_str = f"{seconds:02}"

        size = 0.03
        spacing = size * 1.4

        width = len(time_str) * spacing
        x = 0.95 - width  # alinhado à direita
        y = 0.85

        for i, char in enumerate(time_str):
            self.draw_digit(char, x + i * spacing, y, size)

    # Métodos da barra de vida
    def draw_health_bar(self, vida):
        percentual = vida / 100

        x = -0.95
        y = 0.85
        largura = 0.4
        altura = 0.07

        # fundo
        glColor4f(0.965, 0.937, 0.914, 0.3)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + largura, y)
        glVertex2f(x + largura, y + altura)
        glVertex2f(x, y + altura)
        glEnd()

        # barra
        glColor4f(1.0, 0.965, 0.929, 1.0)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + largura * percentual, y)
        glVertex2f(x + largura * percentual, y + altura)
        glVertex2f(x, y + altura)
        glEnd()

    def draw_number(self, number, x, y):
        size = 0.03
        spacing = size * 1.4
        thickness = size * 0.3

        for i, digit in enumerate(str(int(number))):
            self.draw_digit(digit, x + i * spacing, y, size)