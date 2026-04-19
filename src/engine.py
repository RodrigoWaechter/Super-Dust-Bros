import glfw
from OpenGL.GL import *
from src.settings import Settings
from src.entities.player import Player
from src.fase.mapa import Mapa


class GameEngine:
    def __init__(self):
        self.settings = Settings()
        self.player = Player(self.settings)
        self.camera_x = 0.0
        self.mapa_atual = Mapa(self.settings.levels["fase_teste"])
        self.game_objects = self.mapa_atual.obstacles + [self.player]
        self.window = None
        self.last_time = 0

    def init_window(self):
        if not glfw.init(): raise Exception("Erro GLFW")
        self.window = glfw.create_window(self.settings.window_width, self.settings.window_height,
                                         self.settings.window_title, None, None)
        glfw.make_context_current(self.window)
        glfw.swap_interval(1)
        self.last_time = glfw.get_time()

    def process_input(self):
        self.player.vel_x = 0
        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS: self.player.vel_x = -self.settings.move_speed
        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS: self.player.vel_x = self.settings.move_speed
        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS: self.player.jump()

    def update(self):
        delta_time = glfw.get_time() - self.last_time
        self.last_time = glfw.get_time()

        self.player.update_physics(delta_time)
        self.player.no_chao = False

        # Lógica de colisão e câmera
        for obj in self.mapa_atual.obstacles:
            if self.player.check_collision(obj):
                if self.player.vel_y <= 0 and self.player.centro_y > obj.centro_y:
                    self.player.centro_y = obj.canto_sup_esq_y + (self.player.height / 2)
                    self.player.vel_y = 0
                    self.player.no_chao = True
                elif self.player.vel_x > 0:
                    self.player.centro_x = obj.canto_inf_esq_x - (self.player.width / 2)
                elif self.player.vel_x < 0:
                    self.player.centro_x = obj.canto_inf_dir_x + (self.player.width / 2)

        if self.player.centro_x > 0:
            self.camera_x = self.player.centro_x

    def render(self):
        glClearColor(0.5, 0.8, 0.9, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        for obj in self.game_objects:
            obj.draw(self.camera_x)
        glfw.swap_buffers(self.window)

    def run(self):
        self.init_window()
        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            self.process_input()
            self.update()
            self.render()
        glfw.terminate()