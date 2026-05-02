import glfw
from OpenGL.GL import *

from src.entities.projetil import GranadaAtiva
from src.settings import Settings
from src.entities.player import Player
from src.fase.mapa import Mapa
from src.renderer.hud import HUD
from src.entities.inimigo import Inimigo
from src.entities.inimigo_atirador import InimigoAtirador
from src.utils import load_texture
from src.renderer.parallax import ParallaxLayer


class GameEngine:
    def __init__(self):
        # Inicializa o estado principal do jogo e gera o nível 1
        self.settings = Settings()
        self.player = Player(self.settings)
        self.camera_x = 0.0

        self.mundo = 1
        self.fase = 1
        self.fases_por_mundo = 3
        self.mapa_atual = Mapa(self.mundo, self.fase, self.settings)
        self.inimigos = self.mapa_atual.inimigos
        self.estado = "menu"

        self.power_ups_ativos = []
        self.projeteis = []
        self.explosoes_visuais = []
        self.bg_layers = []
        self.mouse_pressed = False
        self.hud = HUD()
        self.window = None
        self.last_time = 0

    def init_window(self):
        # Configurações iniciais do motor gráfico GLFW
        if not glfw.init(): raise Exception("Erro GLFW")
        self.window = glfw.create_window(self.settings.window_width, self.settings.window_height,
                                         self.settings.window_title, None, None)
        glfw.make_context_current(self.window)
        glfw.swap_interval(1)
        self.last_time = glfw.get_time()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-1, 1, -1, 1, -1, 1)

        glMatrixMode(GL_MODELVIEW)

    def process_input(self):

        if self.estado == "menu":
            if glfw.get_key(self.window, glfw.KEY_ENTER) == glfw.PRESS:
                self.estado = "jogo"
                self.hud.start_timer()
            return

        self.player.vel_x = 0

        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS:
            self.player.vel_x = -self.settings.move_speed
            self.player.direcao = -1

        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS:
            self.player.vel_x = self.settings.move_speed
            self.player.direcao = 1

        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS:
            self.player.jump()

        # Controle de Tiro (AK-47) - Botão Esquerdo
        if glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
            if not self.mouse_pressed and self.player.tem_item:
                proj = self.player.atirar()
                if proj:
                    self.projeteis.append(proj)
                self.mouse_pressed = True
        else:
            self.mouse_pressed = False

        # Controle da Granada - Botão Direito
        if glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS:
            if not getattr(self, 'mouse_right_pressed', False) and getattr(self.player, 'tem_granada', False):

                granada_arremessada = self.player.arremessar()
                if granada_arremessada:
                    self.projeteis.append(granada_arremessada)
                    print("Lançou a granada e adicionou na tela!")

                self.mouse_right_pressed = True
        else:
            self.mouse_right_pressed = False

    def update(self):

        if self.estado == "menu":
            return

        # Atualiza o ciclo lógico de todos os elementos na tela a cada frame
        delta_time = glfw.get_time() - self.last_time
        self.last_time = glfw.get_time()

        if self.player.invulneravel_tempo > 0:
            self.player.invulneravel_tempo -= delta_time
            if self.player.invulneravel_tempo < 0:
                self.player.invulneravel_tempo = 0

        self.handle_player_physics_x(delta_time)
        self.handle_player_physics_y(delta_time)
        self.handle_inimigos(delta_time)
        self.handle_projeteis(delta_time)
        self.handle_explosoes(delta_time)
        self.update_power_ups(delta_time)
        self.player.update_estado()
        self.player.update_animacao(delta_time)

        self.update_camera()
        self.check_world_bounds()

        # Gatilho para passar de fase
        if self.player.check_collision(self.mapa_atual.objetivo):
            print(f"\nAvançando para {self.mundo}-{self.fase}")
            self.avancar_fase()

    def load_backgrounds(self):
        backgrounds = {
            1: "assets/background/dust.jpg",
            2: "assets/background/mirage.jpg",
            3: "assets/background/cache.jpg",
        }

        path = backgrounds.get(self.mundo, "assets/background/dust.jpg")

        tex, w, h = load_texture(path)

        self.bg_layers = [
            ParallaxLayer(tex, w, h, 0.2),
        ]

    def avancar_fase(self):
        self.fase += 1

        if self.fase > self.fases_por_mundo:
            self.fase = 1
            self.mundo += 1
            self.load_backgrounds()

        self.mapa_atual = Mapa(self.mundo, self.fase, self.settings)
        self.inimigos = self.mapa_atual.inimigos

        self.player.reset_posicao()
        self.camera_x = 0.0
        self.power_ups_ativos.clear()
        self.projeteis.clear()
        self.hud.reset_timer()

    def reiniciar_jogo(self):
        # Volta ao estaca zero caso perca vidas ou tempo esgote
        self.mundo = 1
        self.fase = 1

        self.mapa_atual = Mapa(self.mundo, self.fase, self.settings)
        self.inimigos = self.mapa_atual.inimigos

        self.player.vidas = self.settings.player_vidas
        self.player.reset_posicao()
        self.camera_x = 0.0
        self.power_ups_ativos.clear()
        self.projeteis.clear()
        self.hud.reset_timer()

        self.load_backgrounds()

        print("\n*** GAME OVER! Jogo reiniciado na fase inicial. ***")

    def handle_player_physics_x(self, dt):
        self.player.update_physics_x(dt)
        for obj in self.mapa_atual.obstacles:
            if self.player.check_collision(obj):
                if self.player.vel_x > 0:
                    self.player.centro_x = obj.canto_inf_esq_x - (self.player.hitbox_width  / 2)
                elif self.player.vel_x < 0:
                    self.player.centro_x = obj.canto_inf_dir_x + (self.player.hitbox_width  / 2)

    def handle_player_physics_y(self, dt):
        # Aplicação da gravidade e detecção de colisão com teto e chão
        self.player.no_chao = False
        self.player.update_physics_y(dt)

        margem_quina = 0.2

        for obj in self.mapa_atual.obstacles:
            if self.player.check_collision(obj):
                if self.player.vel_y > 0:
                    if self.player.centro_y < obj.centro_y:
                        self.player.centro_y = obj.canto_inf_esq_y - (self.player.hitbox_height / 2)
                        self.player.vel_y = 0
                        self.handle_power_up_block(obj)
                elif self.player.vel_y <= 0:
                    if self.player.canto_inf_esq_y > (obj.canto_sup_esq_y - margem_quina):
                        self.player.centro_y = obj.canto_sup_esq_y + (self.player.hitbox_height / 2)
                        self.player.vel_y = 0
                        self.player.no_chao = True

    def handle_inimigos(self, dt):
        # Move os inimigos e garante que eles fiquem em cima dos blocos sem cair em buracos
        for inimigo in self.inimigos[:]:
            inimigo.update_physics(dt)
            inimigo.no_chao = False

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

            if inimigo.no_chao:
                if not inimigo.validar_chao(self.mapa_atual.obstacles):
                    inimigo.direcao *= -1

            # Causa dano no jogador caso ele encoste na IA
            if self.player.check_collision(inimigo):
                self.player.tomar_dano(35)

            if isinstance(inimigo, InimigoAtirador):
                inimigo.update(dt, self.player, self.projeteis)

    def handle_explosoes(self, dt):
        for exp in self.explosoes_visuais[:]:
            exp.update(dt)
            if exp.destruir:
                self.explosoes_visuais.remove(exp)

    def handle_projeteis(self, dt):
        for proj in self.projeteis[:]:
            proj.update(dt)

            #Checa se o tempo de vida acabou ou saiu da tela
            if getattr(proj, 'destruir', False):
                if isinstance(proj, GranadaAtiva):
                    self.explodir_granada(proj)  # Explode antes de sumir
                self.projeteis.remove(proj)
                continue

            # Checa colisão com paredes/chão
            bateu_obstaculo = False
            for obj in self.mapa_atual.obstacles:
                if proj.check_collision(obj):
                    if isinstance(proj, GranadaAtiva):
                        self.explodir_granada(proj)  # Explode ao tocar no chão/parede
                    self.projeteis.remove(proj)
                    bateu_obstaculo = True
                    break
            if bateu_obstaculo: continue

            # Checa colisão direta com inimigos
            if proj.origem == "player":
                for inimigo in self.inimigos[:]:
                    if proj.check_collision(inimigo):
                        if isinstance(proj, GranadaAtiva):
                            self.explodir_granada(proj)
                        else:
                            # Comportamento normal da AK-47
                            self.inimigos.remove(inimigo)

                        if proj in self.projeteis:
                            self.projeteis.remove(proj)
                        break

    def handle_power_up_block(self, obj):
        # Solta um item de upgrade quando o player cabeceia um bloco de poder
        from src.entities.power_ups import blocoPowerUp
        if isinstance(obj, blocoPowerUp):
            novo_p_up = obj.baterPorBaixo()
            if novo_p_up:
                self.power_ups_ativos.append(novo_p_up)

    def update_power_ups(self, dt):
        # Aplica gravidade ao item solto e equipa o jogador na coleta
        for p_up in self.power_ups_ativos[:]:
            p_up.update(dt)

            if self.player.check_collision(p_up):
                #identificação do item coletado
                tipo_item = p_up.__class__.__name__

                if tipo_item == "ItemGranada":
                    self.player.tem_granada = True
                    print("Granada coletada!")
                else:
                    self.player.tem_item = True
                    print("AK-47 coletada!")

                self.power_ups_ativos.remove(p_up)
                continue

            # Física de queda do item
            if not getattr(p_up, 'is_spawnning', False):
                for obj in self.mapa_atual.obstacles:
                    if p_up.check_collision(obj):
                        if p_up.vel_y < 0 and p_up.centro_y > obj.centro_y:
                            p_up.centro_y = obj.canto_sup_esq_y + (p_up.height / 2)
                            p_up.vel_y = 0

    def update_camera(self):
        # Faz a câmera de visão seguir apenas o movimento horizontal
        if self.player.centro_x > 0:
            self.camera_x = self.player.centro_x

    def check_world_bounds(self):
        # Punições gerais: Morte por queda e Game Over
        if self.player.centro_y < -1.5:
            self.player.invulneravel_tempo = 0
            self.player.tomar_dano(100)
            if self.player.vidas > 0:
                self.camera_x = 0.0

        if self.player.vidas <= 0 or self.hud.is_time_up():
            self.reiniciar_jogo()

    def render(self):

        if self.estado == "menu":
            self.hud.draw_menu(self.bg_layers)
            glfw.swap_buffers(self.window)
            return

        # Limpa o frame anterior e desenha o fundo, objetos físicos e a Interface gráfica
        glClearColor(0.5, 0.8, 0.9, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glLoadIdentity()

        screen_w = 2.0
        screen_h = 2.0

        for layer in self.bg_layers:
            layer.draw(self.camera_x)

        self.mapa_atual.objetivo.draw(self.camera_x)

        for obj in self.mapa_atual.obstacles:
            obj.draw(self.camera_x)
        for inimigo in self.inimigos:
            inimigo.draw(self.camera_x)
        for p_up in self.power_ups_ativos:
            p_up.draw(self.camera_x)
        for proj in self.projeteis:
            proj.draw(self.camera_x)

        for exp in self.explosoes_visuais:
            exp.draw(self.camera_x)

        self.player.draw(self.camera_x)
        self.hud.draw(self.player, self.mundo, self.fase)

        glfw.swap_buffers(self.window)

    def run(self):
        # Loop central de execução contínua
        self.init_window()
        self.load_backgrounds()
        self.player.load_sprites()
        self.hud.start_timer()

        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            self.process_input()
            self.update()
            self.render()

        glfw.terminate()

    def explodir_granada(self, granada):
        import math
        from src.entities.explosao import ExplosaoVisual  # Importa o efeito

        print("A granada explodiu!")

        # Cria o efeito visual na posição da granada
        efeito = ExplosaoVisual(granada.centro_x, granada.centro_y, granada.raio_explosao * 2.0)
        self.explosoes_visuais.append(efeito)

        # Lógica de dano que você já fez
        inimigos_atingidos = []
        for inimigo in self.inimigos:
            dx = inimigo.centro_x - granada.centro_x
            dy = inimigo.centro_y - granada.centro_y
            distancia = math.sqrt(dx ** 2 + dy ** 2)

            if distancia <= granada.raio_explosao:
                inimigos_atingidos.append(inimigo)

        for inimigo in inimigos_atingidos:
            if inimigo in self.inimigos:
                self.inimigos.remove(inimigo)
                print("Inimigo eliminado pela explosão!")