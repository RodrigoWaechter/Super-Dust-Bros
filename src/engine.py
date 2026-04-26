import glfw
from OpenGL.GL import *
from src.settings import Settings
from src.entities.player import Player
from src.fase.mapa import Mapa
from src.renderer.hud import HUD
from src.entities.inimigo import Inimigo
from src.entities.inimigo_atirador import InimigoAtirador


class GameEngine:
    def __init__(self):
        self.settings = Settings()
        self.player = Player(self.settings)
        self.camera_x = 0.0

        self.nivel_atual = 1
        self.mapa_atual = Mapa(dificuldade=self.nivel_atual, settings=self.settings)
        self.inimigos = self.mapa_atual.inimigos

        self.power_ups_ativos = []
        self.projeteis = []
        self.mouse_pressed = False
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

        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS:
            self.player.jump()

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

        # Controle de invulnerabilidade
        if self.player.invulneravel_tempo > 0:
            self.player.invulneravel_tempo -= delta_time
            if self.player.invulneravel_tempo < 0:
                self.player.invulneravel_tempo = 0

        # Física e Movimentos
        self.handle_player_physics_x(delta_time)
        self.handle_player_physics_y(delta_time)
        self.handle_inimigos(delta_time)
        self.handle_projeteis(delta_time)
        self.update_power_ups(delta_time)

        self.update_camera()
        self.check_world_bounds()

        # Avanço de Nível
        if self.player.check_collision(self.mapa_atual.objetivo):
            self.avancar_fase()

    def avancar_fase(self):
        self.nivel_atual += 1
        print(f"Avançando para o Nível {self.nivel_atual}")
        self.mapa_atual = Mapa(dificuldade=self.nivel_atual, settings=self.settings)
        self.inimigos = self.mapa_atual.inimigos
        self.player.reset_posicao()
        self.camera_x = 0.0
        self.power_ups_ativos.clear()
        self.projeteis.clear()
        self.hud.reset_timer()

    def handle_player_physics_x(self, dt):
        self.player.update_physics_x(dt)
        for obj in self.mapa_atual.obstacles:
            if self.player.check_collision(obj):
                if self.player.vel_x > 0:
                    self.player.centro_x = obj.canto_inf_esq_x - (self.player.width / 2)
                elif self.player.vel_x < 0:
                    self.player.centro_x = obj.canto_inf_dir_x + (self.player.width / 2)

    def handle_player_physics_y(self, dt):
        self.player.no_chao = False
        self.player.update_physics_y(dt)
        margem_quina = 0.02
        for obj in self.mapa_atual.obstacles:
            if self.player.check_collision(obj):
                if self.player.vel_y > 0:
                    if self.player.centro_y < obj.centro_y:
                        self.player.centro_y = obj.canto_inf_esq_y - (self.player.height / 2)
                        self.player.vel_y = 0
                        self.handle_power_up_block(obj)
                elif self.player.vel_y <= 0:
                    if self.player.canto_inf_esq_y > (obj.canto_sup_esq_y - margem_quina):
                        self.player.centro_y = obj.canto_sup_esq_y + (self.player.height / 2)
                        self.player.vel_y = 0
                        self.player.no_chao = True

    def handle_inimigos(self, dt):
        for inimigo in self.inimigos[:]:
            inimigo.update_physics(dt)
            inimigo.no_chao = False

            # Colisão do inimigo com o cenário
            for obj in self.mapa_atual.obstacles:
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

            # Evita que o inimigo caia das bordas
            if inimigo.no_chao:
                if not inimigo.validar_chao(self.mapa_atual.obstacles):
                    inimigo.direcao *= -1

            # Dano no jogador
            if self.player.check_collision(inimigo):
                self.player.tomar_dano(35)

            # Atualização de tiro para inimigos atiradores
            if isinstance(inimigo, InimigoAtirador):
                inimigo.update(dt, self.player, self.projeteis)

    def handle_projeteis(self, dt):
        for proj in self.projeteis[:]:
            proj.update(dt)

            # Remove projéteis fora da visão da câmera
            if proj.centro_x < self.camera_x - 2 or proj.centro_x > self.camera_x + 2:
                if proj in self.projeteis: self.projeteis.remove(proj)
                continue

            # Colisão do projétil com o cenário
            bateu = False
            for obj in self.mapa_atual.obstacles:
                if proj.check_collision(obj):
                    if proj in self.projeteis: self.projeteis.remove(proj)
                    bateu = True
                    break
            if bateu: continue

            # Colisão do projétil com inimigos
            for inimigo in self.inimigos[:]:
                if proj.check_collision(inimigo):
                    if inimigo in self.inimigos: self.inimigos.remove(inimigo)
                    if proj in self.projeteis: self.projeteis.remove(proj)
                    break

            # Colisão do projétil com o jogador
            if proj in self.projeteis and self.player.check_collision(proj):
                self.player.tomar_dano(35)
                self.projeteis.remove(proj)

    def handle_power_up_block(self, obj):
        from src.entities.power_ups import blocoPowerUp
        if isinstance(obj, blocoPowerUp):
            novo_p_up = obj.baterPorBaixo()
            if novo_p_up:
                self.power_ups_ativos.append(novo_p_up)

    def update_power_ups(self, dt):
        for p_up in self.power_ups_ativos[:]:
            p_up.update(dt)

            if self.player.check_collision(p_up):
                self.player.tem_item = True
                self.power_ups_ativos.remove(p_up)
                continue

            if not getattr(p_up, 'is_spawnning', False):
                for obj in self.mapa_atual.obstacles:
                    if p_up.check_collision(obj):
                        if p_up.vel_y < 0 and p_up.centro_y > obj.centro_y:
                            p_up.centro_y = obj.canto_sup_esq_y + (p_up.height / 2)
                            p_up.vel_y = 0

    def update_camera(self):
        if self.player.centro_x > 0:
            self.camera_x = self.player.centro_x

    def check_world_bounds(self):
        # Queda do mapa resulta em morte instantânea
        if self.player.centro_y < -1.5:
            self.player.tomar_dano(100)
            if self.player.vidas > 0:
                self.camera_x = 0.0

        if self.player.vidas <= 0 or self.hud.is_time_up():
            glfw.set_window_should_close(self.window, True)

    def render(self):
        glClearColor(0.5, 0.8, 0.9, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Renderização das camadas em ordem
        for obj in self.mapa_atual.obstacles:
            obj.draw(self.camera_x)
        for inimigo in self.inimigos:
            inimigo.draw(self.camera_x)
        for p_up in self.power_ups_ativos:
            p_up.draw(self.camera_x)
        for proj in self.projeteis:
            proj.draw(self.camera_x)

        self.player.draw(self.camera_x)

        # HUD sempre renderizado por último para ficar no topo
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