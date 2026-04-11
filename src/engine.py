import glfw
from OpenGL.GL import *
import time
from src.settings import Settings
from src.player import Player

class GameEngine:
    def __init__(self):
        self.settings = Settings()
        self.player = Player(self.settings)
        self.window = None
        self.is_running = False
        self.last_time = 0

    def init_window(self):
        if not glfw.init():
            raise Exception("Falha ao inicializar o GLFW")

        self.window = glfw.create_window(
            self.settings.window_width,
            self.settings.window_height,
            self.settings.window_title,
            None, None
        )

        if not self.window:
            glfw.terminate()
            raise Exception("Falha ao criar a janela")

        glfw.make_context_current(self.window)
        glfw.swap_interval(1)  # Limita a 60 FPS
        self.is_running = True

    def process_input(self):
        if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(self.window, True)

        # Movimento Horizontal (A e D)
        self.player.vel_x = 0
        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS:
            self.player.vel_x = -self.settings.move_speed
        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS:
            self.player.vel_x = self.settings.move_speed

        # Pulo (W ou Espaço)
        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS or glfw.get_key(self.window,
                                                                               glfw.KEY_SPACE) == glfw.PRESS:
            # Só permite pular se estiver encostado no chão
            if self.player.centro_y <= self.player.chao_da_tela:
                self.player.vel_y = self.settings.jump_speed

    def update(self, delta_time):
        # Aplica a gravidade constantemente
        self.player.vel_y += self.settings.gravity * delta_time

        # Calcula a nova posição baseada na velocidade * tempo
        novo_x = self.player.centro_x + (self.player.vel_x * delta_time)
        novo_y = self.player.centro_y + (self.player.vel_y * delta_time)

        self.player.set_posicao(novo_x, novo_y)

    def render(self):
        # Limpa a tela com uma cor de fundo
        glClearColor(0.5, 0.8, 0.9, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        # Desenha o jogador
        glBegin(GL_QUADS)
        glColor3f(1.0, 0.5, 0.0) #Laranja
        glVertex3f(self.player.canto_inf_esq_x, self.player.canto_inf_esq_y, 0)
        glVertex3f(self.player.canto_inf_dir_x, self.player.canto_inf_dir_y, 0)
        glVertex3f(self.player.canto_sup_dir_x, self.player.canto_sup_dir_y, 0)
        glVertex3f(self.player.canto_sup_esq_x, self.player.canto_sup_esq_y, 0)
        glEnd()

        glfw.swap_buffers(self.window)

    def run(self):
        self.init_window()
        self.last_time = time.time()

        while not glfw.window_should_close(self.window) and self.is_running:
            current_time = time.time()
            delta_time = current_time - self.last_time
            self.last_time = current_time

            glfw.poll_events()
            self.process_input()
            self.update(delta_time)
            self.render()

        glfw.terminate()