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

        self.nivel_atual = 1
        self.mapa_atual = Mapa(dificuldade=self.nivel_atual)
        self.game_objects = self.mapa_atual.obstacles + [self.player]

        self.window = None
        self.power_ups_ativos = []
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
        # 1. Calcula o tempo desde o último frame
        delta_time = glfw.get_time() - self.last_time
        self.last_time = glfw.get_time()

        # 2. Executa as fases da física em ordem rigorosa
        self.handle_player_physics_x(delta_time)
        self.handle_player_physics_y(delta_time)
        self.update_power_ups(delta_time)

        # 3. Atualiza estado global (Câmera e Queda)
        self.update_camera()
        self.check_world_bounds()

        if self.player.check_collision(self.mapa_atual.objetivo):
            self.avancar_fase()

    def avancar_fase(self):
        self.nivel_atual += 1
        print(f"Avançando para o Nível {self.nivel_atual}")
        self.mapa_atual = Mapa(dificuldade=self.nivel_atual)
        self.player.reset_posicao()
        self.camera_x = 0.0
        self.power_ups_ativos.clear()
        self.game_objects = self.mapa_atual.obstacles + [self.player]

    def handle_player_physics_x(self, dt):
        """Resolve apenas o movimento e colisão lateral."""
        self.player.update_physics_x(dt)
        for obj in self.mapa_atual.obstacles:
            if self.player.check_collision(obj):
                if self.player.vel_x > 0:  # Indo para direita
                    self.player.centro_x = obj.canto_inf_esq_x - (self.player.width / 2)
                elif self.player.vel_x < 0:  # Indo para esquerda
                    self.player.centro_x = obj.canto_inf_dir_x + (self.player.width / 2)

    def handle_player_physics_y(self, dt):
        """Resolve gravidade, pulo e colisões verticais."""
        self.player.no_chao = False
        self.player.update_physics_y(dt)

        margem_quina = 0.02  # Evita que o boneco "suba" em paredes sem querer

        for obj in self.mapa_atual.obstacles:
            if self.player.check_collision(obj):
                # Caso 1: Batendo a cabeça (Subindo)
                if self.player.vel_y > 0:
                    if self.player.centro_y < obj.centro_y:
                        self.player.centro_y = obj.canto_inf_esq_y - (self.player.height / 2)
                        self.player.vel_y = 0
                        self.handle_power_up_block(obj)

                # Caso 2: Pousando (Descendo)
                elif self.player.vel_y <= 0:
                    if self.player.canto_inf_esq_y > (obj.canto_sup_esq_y - margem_quina):
                        self.player.centro_y = obj.canto_sup_esq_y + (self.player.height / 2)
                        self.player.vel_y = 0
                        self.player.no_chao = True

    def handle_power_up_block(self, obj):
        """Gerencia a ativação de blocos de interrogação."""
        from src.entities.power_ups import blocoPowerUp
        if isinstance(obj, blocoPowerUp):
            novo_p_up = obj.baterPorBaixo()
            if novo_p_up:
                self.power_ups_ativos.append(novo_p_up)
                self.game_objects.append(novo_p_up)

    def update_power_ups(self, dt):
        """Atualiza movimento e colisão de itens soltos no mapa."""
        for p_up in self.power_ups_ativos[:]:
            p_up.update(dt)

            # Coleta pelo jogador
            if self.player.check_collision(p_up):
                self.player.tem_item = True
                self.power_ups_ativos.remove(p_up)
                if p_up in self.game_objects:
                    self.game_objects.remove(p_up)
                continue

            # Colisão do item com o cenário (para ele não atravessar o chão)
            if not getattr(p_up, 'is_spawnning', False):
                for obj in self.mapa_atual.obstacles:
                    if p_up.check_collision(obj):
                        if p_up.vel_y < 0 and p_up.centro_y > obj.centro_y:
                            p_up.centro_y = obj.canto_sup_esq_y + (p_up.height / 2)
                            p_up.vel_y = 0

    def update_camera(self):
        """Faz a câmera seguir o jogador suavemente."""
        if self.player.centro_x > 0:
            self.camera_x = self.player.centro_x

    def check_world_bounds(self):
        if self.player.centro_y < -1.5:
            self.player.tomar_dano()
            if self.player.vidas > 0:
                self.camera_x = 0.0
            else:
                # O jogo SÓ finaliza quando termina as vidas
                glfw.set_window_should_close(self.window, True)

    def render(self):
        glClearColor(0.5, 0.8, 0.9, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        # Desenha o mundo com o deslocamento da câmera
        for obj in self.game_objects:
            obj.draw(self.camera_x)

        # Desenha o HUD de vidas FIXO na tela
        self.desenhar_hud()

        glfw.swap_buffers(self.window)

    def desenhar_hud(self):
        tamanho = 0.04
        for i in range(self.player.vidas):
            x = -0.95 + (i * 0.06)
            y = 0.90

            glBegin(GL_QUADS)
            glColor3f(1.0, 0.0, 0.0)  # Quadrados vermelhos (Vidas)
            glVertex2f(x - tamanho / 2, y - tamanho / 2)
            glVertex2f(x + tamanho / 2, y - tamanho / 2)
            glVertex2f(x + tamanho / 2, y + tamanho / 2)
            glVertex2f(x - tamanho / 2, y + tamanho / 2)
            glEnd()
    def run(self):
        self.init_window()
        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            self.process_input()
            self.update()
            self.render()
        glfw.terminate()