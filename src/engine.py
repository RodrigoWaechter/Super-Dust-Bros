import glfw
import pygame  # Import necessário
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
    """
    Classe principal responsável pelo loop do jogo, gerenciamento de estado,
    física, processamento de inputs e renderização OpenGL.
    """
    def __init__(self):
        """Inicializa os componentes do jogo, física, estados e o sistema de áudio."""
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

        # --- INICIALIZAÇÃO DE SOM ---
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        try:
            pygame.mixer.music.load("assets/sounds/csgo_soundtrack.ogg")
            pygame.mixer.music.set_volume(0.2)
        except Exception as e:
            print(f"Aviso: Não foi possível carregar a música: {e}")

    def init_window(self):
        """Configura a janela, contexto OpenGL e a zona de projeção (ortho) do jogo."""
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
        """Captura entradas do teclado e mouse para movimentação, tiro e granadas."""
        # lógica unificada: processa o menu e o jogo de forma limpa
        if self.estado == "menu":
            if glfw.get_key(self.window, glfw.KEY_ENTER) == glfw.PRESS:
                self.estado = "jogo"
                self.hud.start_timer()

                # dispara a música apenas aqui, uma única vez
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1)
            return  # sai da função, não processa movimentos enquanto está no menu

        # movimentação do player
        self.player.vel_x = 0
        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS:
            self.player.vel_x = -self.settings.move_speed
            self.player.direcao = -1
        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS:
            self.player.vel_x = self.settings.move_speed
            self.player.direcao = 1
        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS:
            self.player.jump()

        # tiro e granada
        if glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
            if not self.mouse_pressed and self.player.tem_item:
                proj = self.player.atirar()
                if proj: self.projeteis.append(proj)
                self.mouse_pressed = True
        else:
            self.mouse_pressed = False

        if glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS:
            if not getattr(self, 'mouse_right_pressed', False) and getattr(self.player, 'tem_granada', False):
                granada_arremessada = self.player.arremessar()
                if granada_arremessada: self.projeteis.append(granada_arremessada)
                self.mouse_right_pressed = True
        else:
            self.mouse_right_pressed = False

    def update(self):
        """Atualiza a lógica física, colisão e estado dos elementos a cada frame."""
        if self.estado == "menu": return

        delta_time = glfw.get_time() - self.last_time
        self.last_time = glfw.get_time()

        if self.player.invulneravel_tempo > 0:
            self.player.invulneravel_tempo = max(0, self.player.invulneravel_tempo - delta_time)

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

        if self.player.check_collision(self.mapa_atual.objetivo):
            self.avancar_fase()

    def load_backgrounds(self):
        """Define e carrega as camadas de fundo (Parallax) baseadas no mapa atual."""
        backgrounds = {
            1: "assets/background/dust.jpg",
            2: "assets/background/mirage.jpg",
            3: "assets/background/cache.jpg",
        }
        path = backgrounds.get(self.mundo, "assets/background/dust.jpg")
        self.bg_layers = [ParallaxLayer(path, 0.1)]

    def avancar_fase(self):
        """Gerencia a transição de níveis, resetando entidades e carregando o próximo cenário."""
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
        """Reseta todos os estados do jogo, vidas e fases após uma derrota."""
        pygame.mixer.music.stop()
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
        self.estado = "menu"  # Volta para o menu ao reiniciar
        print("\n*** GAME OVER! Jogo reiniciado. ***")

    # --- MÉTODOS AUXILIARES ---
    def handle_player_physics_x(self, dt):
        """Gerencia colisão horizontal do player com obstáculos, aplicando resoluções de posição."""
        self.player.update_physics_x(dt)
        for obj in self.mapa_atual.obstacles:
            if self.player.check_collision(obj):
                if self.player.vel_x > 0:
                    self.player.centro_x = obj.canto_inf_esq_x - (self.player.hitbox_width / 2)
                elif self.player.vel_x < 0:
                    self.player.centro_x = obj.canto_inf_dir_x + (self.player.hitbox_width / 2)

    def handle_player_physics_y(self, dt):
        """Gerencia colisão vertical do player com obstáculos, aplicando resoluções de posição."""
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
        """Atualiza a "IA" dos inimigos, detecção de buracos e colisões contra o player."""
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
                if not inimigo.validar_chao(self.mapa_atual.obstacles): inimigo.direcao *= -1
            if self.player.check_collision(inimigo): self.player.tomar_dano(35)
            if isinstance(inimigo, InimigoAtirador): inimigo.update(dt, self.player, self.projeteis)

    def handle_explosoes(self, dt):
        for exp in self.explosoes_visuais[:]:
            exp.update(dt)
            if exp.destruir: self.explosoes_visuais.remove(exp)

    def handle_projeteis(self, dt):
        """Gerencia a trajetória, colisão e destruição de balas e granadas."""
        for proj in self.projeteis[:]:
            proj.update(dt)
            if getattr(proj, 'destruir', False):
                if isinstance(proj, GranadaAtiva): self.explodir_granada(proj)
                self.projeteis.remove(proj);
                continue

            bateu_obstaculo = False
            for obj in self.mapa_atual.obstacles:
                if proj.check_collision(obj):
                    if isinstance(proj, GranadaAtiva): self.explodir_granada(proj)
                    self.projeteis.remove(proj)
                    bateu_obstaculo = True;
                    break
            if bateu_obstaculo: continue

            if proj.origem == "player":
                for inimigo in self.inimigos[:]:
                    if proj.check_collision(inimigo):
                        if isinstance(proj, GranadaAtiva):
                            self.explodir_granada(proj)
                        else:
                            self.inimigos.remove(inimigo)
                        if proj in self.projeteis: self.projeteis.remove(proj)
                        break

    def handle_power_up_block(self, obj):
        from src.entities.power_ups import blocoPowerUp
        if isinstance(obj, blocoPowerUp):
            novo_p_up = obj.baterPorBaixo()
            if novo_p_up: self.power_ups_ativos.append(novo_p_up)

    def update_power_ups(self, dt):
        for p_up in self.power_ups_ativos[:]:
            p_up.update(dt)
            if self.player.check_collision(p_up):
                tipo_item = p_up.__class__.__name__
                if tipo_item == "ItemGranada":
                    self.player.tem_granada = True
                else:
                    self.player.tem_item = True
                self.power_ups_ativos.remove(p_up);
                continue
            if not getattr(p_up, 'is_spawnning', False):
                for obj in self.mapa_atual.obstacles:
                    if p_up.check_collision(obj):
                        if p_up.vel_y < 0 and p_up.centro_y > obj.centro_y:
                            p_up.centro_y = obj.canto_sup_esq_y + (p_up.height / 2)
                            p_up.vel_y = 0

    def update_camera(self):
        """Calcula o deslocamento horizontal da câmera baseado na posição do jogador."""
        if self.player.centro_x > 0: self.camera_x = self.player.centro_x

    def check_world_bounds(self):
        if self.player.centro_y < -1.5:
            self.player.invulneravel_tempo = 0
            self.player.tomar_dano(100)
            if self.player.vidas > 0: self.camera_x = 0.0
        if self.player.vidas <= 0 or self.hud.is_time_up(): self.reiniciar_jogo()

    def render(self):
        """Desenha todos os objetos na tela na ordem correta (Background -> Cenário -> Entidades -> HUD)."""
        if self.estado == "menu":
            self.hud.draw_menu(self.bg_layers)
            glfw.swap_buffers(self.window)
            return

        glClearColor(0.5, 0.8, 0.9, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glLoadIdentity()

        for layer in self.bg_layers: layer.draw(self.camera_x)
        self.mapa_atual.objetivo.draw(self.camera_x)
        for obj in self.mapa_atual.obstacles: obj.draw(self.camera_x)
        for inimigo in self.inimigos: inimigo.draw(self.camera_x)
        for p_up in self.power_ups_ativos: p_up.draw(self.camera_x)
        for proj in self.projeteis: proj.draw(self.camera_x)
        for exp in self.explosoes_visuais: exp.draw(self.camera_x)
        self.player.draw(self.camera_x)
        self.hud.draw(self.player, self.mundo, self.fase)
        glfw.swap_buffers(self.window)

    def run(self):
        """Loop principal de execução: Poll events -> Update -> Render."""
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
        """Calcula o dano em área da granada e instancia o efeito visual de explosão."""
        import math
        from src.entities.explosao import ExplosaoVisual
        efeito = ExplosaoVisual(granada.centro_x, granada.centro_y, granada.raio_explosao * 2.0)
        self.explosoes_visuais.append(efeito)
        inimigos_atingidos = [i for i in self.inimigos if math.sqrt(
            (i.centro_x - granada.centro_x) ** 2 + (i.centro_y - granada.centro_y) ** 2) <= granada.raio_explosao]
        for inimigo in inimigos_atingidos:
            if inimigo in self.inimigos: self.inimigos.remove(inimigo)