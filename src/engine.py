import glfw
from OpenGL.GL import *
from src.settings import Settings
from src.entities.player import Player
from src.fase.mapa import Mapa
from src.renderer import HUD
from src.entities.inimigo import Inimigo
from src.entities.inimigo_atirador import InimigoAtirador

class GameEngine:
    def __init__(self):
        self.settings = Settings()
        self.player = Player(self.settings)
        self.camera_x = 0.0
        self.mapa_atual = Mapa(self.settings.levels["fase_teste"], self.settings)
        self.inimigos = self.mapa_atual.inimigos
        self.power_ups_ativos = []
        self.projeteis = []
        self.mouse_pressed = False
        self.game_objects = (self.mapa_atual.obstacles + [self.player] + self.inimigos)
        self.hud = HUD()
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
        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS:
            self.player.vel_x = -self.settings.move_speed
            self.player.direcao = -1

        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS:
            self.player.vel_x = self.settings.move_speed
            self.player.direcao = 1
        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS: self.player.jump()
        if glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
            if not self.mouse_pressed:
                proj = self.player.atirar()
                self.projeteis.append(proj)
                self.mouse_pressed = True
        else:
            self.mouse_pressed = False

    def update(self):
        delta_time = glfw.get_time() - self.last_time
        self.last_time = glfw.get_time()

        # invulnerabilidade do player
        if self.player.invulneravel_tempo > 0:
            self.player.invulneravel_tempo -= delta_time
            if self.player.invulneravel_tempo < 0:
                self.player.invulneravel_tempo = 0

        self.player.update_physics(delta_time)
        self.player.no_chao = False

        # física dos inimigos
        for inimigo in self.inimigos:
            inimigo.update_physics(delta_time)
            inimigo.no_chao = False

        for proj in self.projeteis[:]:
            proj.update(delta_time)

            # colisão com inimigos
            for inimigo in self.inimigos[:]:
                if proj.check_collision(inimigo):
                    self.inimigos.remove(inimigo)

                    if inimigo in self.game_objects:
                        self.game_objects.remove(inimigo)

                    if proj in self.projeteis:
                        self.projeteis.remove(proj)

                    break

            # colisão com obstáculos
            for obj in self.mapa_atual.obstacles:
                if proj.check_collision(obj):
                    if proj in self.projeteis:
                        self.projeteis.remove(proj)
                    break

            # colisão com player
            if proj in self.projeteis and self.player.check_collision(proj):
                if self.player.invulneravel_tempo <= 0:
                    self.player.vidas -= 35
                    self.player.invulneravel_tempo = 1.0
                    if self.player.vidas < 0:
                        self.player.vidas = 0

                self.projeteis.remove(proj)
                continue

            # remove se sair da tela
            if proj.centro_x < self.camera_x - 2 or proj.centro_x > self.camera_x + 2:
                self.projeteis.remove(proj)

        for p_up in self.power_ups_ativos[:]:

            p_up.update(delta_time)


            if self.player.check_collision(p_up):
                self.player.tem_item = True

                self.power_ups_ativos.remove(p_up)
                if p_up in self.game_objects:
                    self.game_objects.remove(p_up)
                continue

            if getattr(p_up, 'is_spawning', False) == False:
                for obj in self.mapa_atual.obstacles:
                    if p_up.check_collision(obj):

                        if p_up.vel_y < 0 and p_up.centro_y > obj.centro_y:
                            p_up.centro_y = obj.canto_sup_esq_y + (p_up.height / 2)
                            p_up.vel_y = 0

        for obj in self.mapa_atual.obstacles:
            if self.player.check_collision(obj):


                if self.player.vel_y <= 0 and self.player.centro_y > obj.centro_y:
                    self.player.centro_y = obj.canto_sup_esq_y + (self.player.height / 2)
                    self.player.vel_y = 0
                    self.player.no_chao = True


                elif self.player.vel_y > 0 and self.player.centro_y < obj.centro_y:
                    self.player.centro_y = obj.canto_inf_esq_y - (self.player.height / 2)
                    self.player.vel_y = 0


                    from src.entities.power_ups import blocoPowerUp
                    if isinstance(obj, blocoPowerUp):
                        novo_power_up = obj.baterPorBaixo()
                        if novo_power_up:
                            self.power_ups_ativos.append(novo_power_up)
                            self.game_objects.append(novo_power_up)


                elif self.player.vel_x > 0:
                    self.player.centro_x = obj.canto_inf_esq_x - (self.player.width / 2)


                elif self.player.vel_x < 0:
                    self.player.centro_x = obj.canto_inf_dir_x + (self.player.width / 2)

            # colisão inimigo x mapa
            for inimigo in self.inimigos:
                if inimigo.check_collision(obj):
                    if inimigo.vel_y <= 0 and inimigo.centro_y > obj.centro_y:
                        inimigo.centro_y = obj.canto_sup_esq_y + (inimigo.height / 2)
                        inimigo.vel_y = 0
                        inimigo.no_chao = True

                    elif inimigo.vel_y > 0 and inimigo.centro_y < obj.centro_y:
                        inimigo.centro_y = obj.canto_inf_esq_y - (inimigo.height / 2)
                        inimigo.vel_y = 0

                    elif inimigo.vel_x > 0:
                        inimigo.centro_x = obj.canto_inf_esq_x - (inimigo.width / 2)
                        inimigo.direcao *= -1

                    elif inimigo.vel_x < 0:
                        inimigo.centro_x = obj.canto_inf_dir_x + (inimigo.width / 2)
                        inimigo.direcao *= -1

        # câmera
        if self.player.centro_x > 0:
            self.camera_x = self.player.centro_x

        # player x inimigo
        for inimigo in self.inimigos[:]:
            if self.player.check_collision(inimigo):
                if self.player.invulneravel_tempo <= 0:
                    self.player.vidas -= 35
                    self.player.invulneravel_tempo = 1.0
                    if self.player.vidas < 0:
                        self.player.vidas = 0

        # inimigo andando na borda
        for inimigo in self.inimigos:
            if inimigo.no_chao:
                if not inimigo.validar_chao(self.mapa_atual.obstacles):
                    inimigo.direcao *= -1

        # tiro do inimigo atirador
        for inimigo in self.inimigos:
            if isinstance(inimigo, InimigoAtirador):
                inimigo.update(delta_time, self.player, self.projeteis)

    def render(self):
        glClearColor(0.5, 0.8, 0.9, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        for obj in self.game_objects:
            obj.draw(self.camera_x)
        for proj in self.projeteis:
            proj.draw(self.camera_x)
        self.hud.draw(self.player)
        glfw.swap_buffers(self.window)

    def run(self):
        self.init_window()
        self.hud.start_timer()
        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            self.process_input()
            self.update()
            self.render()
        glfw.terminate()