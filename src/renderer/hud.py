from OpenGL.GL import *
import time


class HUD:
    def __init__(self):
        self.limit = 120
        self.start_time = None

    # Chamadas de desenho da hud
    def draw(self, player, mundo, fase):
        # Agora passamos o objeto 'player' inteiro para a barra de vida
        self.draw_health_bar(player)
        self.draw_number(player.vidas, -0.54, 0.85)
        self.draw_timer()
        self.draw_world_stage(mundo, fase)

        # Chama a função de arremessáveis passando o player
        self.draw_arremessaveis_hud(player)

    def draw_world_stage(self, mundo, fase):
        texto = f"{mundo}-{fase}"

        size = 0.03
        spacing = size * 1.4

        x = -0.05
        y = 0.85

        for i, char in enumerate(texto):
            if char == "-":
                glBegin(GL_LINES)
                glVertex2f(x + i * spacing, y + size)
                glVertex2f(x + i * spacing + size, y + size)
                glEnd()
            else:
                self.draw_digit(char, x + i * spacing, y, size)

    def draw_arremessaveis_hud(self, player):
        """
        Desenha os ícones minimalistas da Granada e da Molotov abaixo da barra de vida.
        Acende (colore) apenas o que estiver equipado no momento.
        """
        # Verifica o estado do inventário do jogador usando getattr por segurança
        tem_arremessavel = getattr(player, 'tem_arremessavel', False)
        tipo = getattr(player, 'tipo_arremessavel', None)

        tem_granada = tem_arremessavel and tipo == "GRANADA"
        tem_molotov = tem_arremessavel and tipo == "MOLOTOV"

        # Dimensões base usadas para os dois ícones
        y = 0.72
        largura = 0.04
        altura = 0.05


        # 1. DESENHA A GRANADA

        x_g = -0.95

        # Define as cores dependendo se tem a granada ou não
        cor_corpo_g = (0.5, 0.0, 0.5) if tem_granada else (0.2, 0.2, 0.2)  # Roxo ou Cinza escuro
        cor_pino_g = (0.7, 0.7, 0.7) if tem_granada else (0.3, 0.3, 0.3)  # Cinza claro ou Cinza escuro

        # Corpo da Granada
        glColor3f(*cor_corpo_g)
        glBegin(GL_QUADS)
        glVertex2f(x_g, y)
        glVertex2f(x_g + largura, y)
        glVertex2f(x_g + largura, y + altura)
        glVertex2f(x_g, y + altura)
        glEnd()

        # Pino da Granada
        glColor3f(*cor_pino_g)
        glBegin(GL_QUADS)
        glVertex2f(x_g + largura * 0.3, y + altura)
        glVertex2f(x_g + largura * 0.7, y + altura)
        glVertex2f(x_g + largura * 0.7, y + altura + 0.02)
        glVertex2f(x_g + largura * 0.3, y + altura + 0.02)
        glEnd()


        # 2. DESENHA A MOLOTOV

        # Posiciona a Molotov ao lado da granada
        x_m = x_g + largura + 0.03

        # Define as cores dependendo se tem a molotov ou não
        cor_corpo_m = (1.0, 0.4, 0.0) if tem_molotov else (0.2, 0.2, 0.2)  # Laranja ou Cinza escuro
        cor_pano_m = (1.0, 0.9, 0.6) if tem_molotov else (0.3, 0.3, 0.3)  # Amarelinho ou Cinza escuro

        # Corpo da Garrafa (Laranja)
        glColor3f(*cor_corpo_m)
        glBegin(GL_QUADS)
        glVertex2f(x_m, y)
        glVertex2f(x_m + largura, y)
        glVertex2f(x_m + largura, y + altura)
        glVertex2f(x_m, y + altura)
        glEnd()

        # Pano em chamas / Gargalo da garrafa
        glColor3f(*cor_pano_m)
        glBegin(GL_QUADS)
        glVertex2f(x_m + largura * 0.3, y + altura)
        glVertex2f(x_m + largura * 0.7, y + altura)
        glVertex2f(x_m + largura * 0.7, y + altura + 0.03)  # Um pouco mais alto que o pino
        glVertex2f(x_m + largura * 0.3, y + altura + 0.03)
        glEnd()


        # Limpeza

        # Retorna para a cor branca padrão para não manchar o resto do jogo
        glColor3f(1.0, 1.0, 1.0)

    def draw_menu(self, bg_layers):
        glClearColor(0.5, 0.8, 0.9, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        for layer in bg_layers:
            layer.draw(0)

        self.draw_text("SUPER DUST BROS", -0.7, 0.2, 0.08)

        if int(time.time() * 2) % 2 == 0:
            self.draw_text("PLAY", -0.1, -0.1, 0.05)

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
    def draw_health_bar(self, player):
        # Descobre a vida máxima. Se o player tiver 'settings', usa o valor de lá; senão, usa 100.
        vida_maxima = 100
        if hasattr(player, 'settings'):
            vida_maxima = getattr(player.settings, 'player_vidas', 100)

        # Calcula o percentual
        percentual = player.vidas / vida_maxima

        # Trava o percentual entre 0.0 (0%) e 1.0 (100%) para a barra não vazar da tela
        percentual = max(0.0, min(percentual, 1.0))

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

    def draw_text(self, text, x, y, size):
        spacing = size * 1.2

        for i, char in enumerate(text):
            self.draw_char(char, x + i * spacing, y, size)

    def draw_char(self, char, x, y, size):
        char = char.upper()

        if char == " ":
            return

        thickness = size * 0.3
        w = size
        h = size * 2

        def quad(x1, y1, x2, y2):
            glVertex2f(x1, y1)
            glVertex2f(x2, y1)
            glVertex2f(x2, y2)
            glVertex2f(x1, y2)

        glColor3f(1, 1, 1)

        if char == "T":
            glBegin(GL_QUADS)

            quad(x, y + h - thickness, x + w, y + h)

            quad(x + w / 2 - thickness / 2, y, x + w / 2 + thickness / 2, y + h)

            glEnd()
            return

        if char == "M":
            glBegin(GL_QUADS)

            quad(x, y, x + thickness, y + h)
            quad(x + w - thickness, y, x + w, y + h)

            quad(x + w * 0.3, y + h * 0.5, x + w * 0.4, y + h)
            quad(x + w * 0.6, y + h * 0.5, x + w * 0.7, y + h)

            glEnd()
            return

        patterns = {
            "A": [1, 1, 1, 0, 1, 1, 1],
            "B": [1, 1, 1, 1, 1, 1, 1],
            "C": [1, 0, 0, 1, 1, 1, 0],
            "D": [1, 1, 1, 1, 1, 1, 0],
            "E": [1, 0, 0, 1, 1, 1, 1],
            "F": [1, 0, 0, 0, 1, 1, 1],
            "G": [1, 0, 1, 1, 1, 1, 0],
            "H": [0, 1, 1, 0, 1, 1, 1],
            "I": [0, 1, 1, 0, 0, 0, 0],
            "J": [0, 1, 1, 1, 0, 0, 0],
            "L": [0, 0, 0, 1, 1, 1, 0],
            "O": [1, 1, 1, 1, 1, 1, 0],
            "P": [1, 1, 0, 0, 1, 1, 1],
            "R": [1, 1, 1, 0, 1, 1, 1],
            "S": [1, 0, 1, 1, 0, 1, 1],
            "U": [0, 1, 1, 1, 1, 1, 0],
            "Y": [0, 1, 1, 1, 0, 1, 1],
        }

        if char not in patterns:
            return

        seg = patterns[char]

        glBegin(GL_QUADS)

        if seg[0]: quad(x, y + h - thickness, x + w, y + h)
        if seg[1]: quad(x + w - thickness, y + h / 2, x + w, y + h)
        if seg[2]: quad(x + w - thickness, y, x + w, y + h / 2)
        if seg[3]: quad(x, y, x + w, y + thickness)
        if seg[4]: quad(x, y, x + thickness, y + h / 2)
        if seg[5]: quad(x, y + h / 2, x + thickness, y + h)
        if seg[6]: quad(x, y + h / 2 - thickness / 2, x + w, y + h / 2 + thickness / 2)

        glEnd()