"""
engine.py

Módulo responsável pelo gerenciamento central do jogo.
Implementa o loop principal, controle de estados, atualização de física,
detecção de colisões, renderização e interação entre entidades.
"""

import glfw
from OpenGL.GL import *
import math

from src.entities.projetil import GranadaAtiva, MolotovAtiva
from src.entities.explosao import ExplosaoVisual, FogoChao
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
    Classe principal responsável por orquestrar toda a execução do jogo.
    Controla o ciclo de vida (game loop), lógica de framerate, física e chamadas de renderização.
    """

    def __init__(self):
        self.settings = Settings()
        self.player = Player(self.settings)

        # Controle da câmera (scroll horizontal)
        self.camera_x = 0.0

        # Controle de progressão
        self.mundo = 1
        self.fase = 1
        self.fases_por_mundo = 3

        # Instanciação dinâmica das entidades baseadas no layout do mapa gerado
        self.mapa_atual = Mapa(self.mundo, self.fase, self.settings)
        self.inimigos = self.mapa_atual.inimigos

        # Máquina de estados primária do jogo
        self.estado = "menu"

        self.power_ups_ativos = []
        self.projeteis = []
        self.explosoes_visuais = []

        self.bg_layers = []

        # Flags de controle de input para evitar ações contínuas em um único clique
        self.mouse_pressed = False

        self.hud = HUD()
        self.window = None
        self.last_time = 0
        self.em_transicao = False

    def init_window(self):
        """
        Inicializa a janela gráfica utilizando GLFW
        e configura o sistema de projeção ortográfica.
        """
        if not glfw.init():
            raise Exception("Erro GLFW")

        # Garante que a janela permite ser redimensionada pelo usuário
        glfw.window_hint(glfw.RESIZABLE, glfw.TRUE)

        self.window = glfw.create_window(
            self.settings.window_width,
            self.settings.window_height,
            self.settings.window_title,
            None,
            None
        )

        glfw.make_context_current(self.window)

        # Diz ao GLFW para chamar a nossa função quando a janela mudar
        glfw.set_framebuffer_size_callback(self.window, self.redimensionar_janela)

        # Ativa V-Sync
        glfw.swap_interval(1)
        self.last_time = glfw.get_time()

        # Força uma primeira configuração do tamanho da tela
        self.redimensionar_janela(self.window, self.settings.window_width, self.settings.window_height)

    def redimensionar_janela(self, window, width, height):
        """
        Ajusta a área de renderização do OpenGL para manter a proporção
        original do jogo, adicionando barras pretas (letterboxing) se necessário,
        para evitar que a imagem fique esticada.
        """
        if height == 0:
            height = 1  # Evita erro de divisão por zero se minimizar

        # Calcula a proporção original do jogo (ex: 800 / 600 = 1.333)
        target_aspect = self.settings.window_width / self.settings.window_height
        window_aspect = width / height

        # Compara as proporções para decidir onde colocar as barras pretas
        if window_aspect > target_aspect:
            # Janela é mais larga que o jogo (Barras pretas nas laterais)
            view_width = int(height * target_aspect)
            view_height = height
            view_x = (width - view_width) // 2
            view_y = 0
        else:
            # Janela é mais alta/quadrada que o jogo (Barras pretas em cima/embaixo)
            view_width = width
            view_height = int(width / target_aspect)
            view_x = 0
            view_y = (height - view_height) // 2

        # Diz ao OpenGL para desenhar apenas dentro da área com a proporção correta
        glViewport(view_x, view_y, view_width, view_height)

        # A matriz de projeção continua -1 a 1, assim a HUD e física não quebram!
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-1, 1, -1, 1, -1, 1)
        glMatrixMode(GL_MODELVIEW)

    def toggle_fullscreen(self):
        """
        Alterna entre Modo Janela e Tela Cheia de forma limpa.
        """
        monitor = glfw.get_primary_monitor()
        mode = glfw.get_video_mode(monitor)

        if not getattr(self, 'is_fullscreen', False):
            # Salva posição e tamanho atuais antes de maximizar
            self.old_x, self.old_y = glfw.get_window_pos(self.window)
            self.old_width, self.old_height = glfw.get_window_size(self.window)

            # Vai para tela cheia
            glfw.set_window_monitor(self.window, monitor, 0, 0, mode.size.width, mode.size.height, mode.refresh_rate)
            self.is_fullscreen = True
        else:
            # Volta pro modo janela com os tamanhos que estavam salvos
            glfw.set_window_monitor(self.window, None, self.old_x, self.old_y, self.old_width, self.old_height, 0)
            self.is_fullscreen = False

    def load_backgrounds(self):
        """
        Carrega a camada de fundo correspondente ao mundo atual.
        Utiliza o ParallaxLayer para criar ilusão de profundidade através de rolagem mais lenta.
        """

        # mapeia mundos > 4 para o ciclo 1, 2 ou 3 (para futuros mapas)
        mundo_mapeado = ((self.mundo - 1) % 4) + 1

        backgrounds = {
            1: "assets/background/dust.jpg",
            2: "assets/background/mirage.jpg",
            3: "assets/background/cache.jpg",
            4: "assets/background/poolday.jpg"
        }

        path = backgrounds.get(mundo_mapeado, "assets/background/dust.jpg")
        self.bg_layers = [ParallaxLayer(path, 0.1)]

    def process_input(self):
        """
        Captura e traduz eventos do sistema (teclado e mouse) para ações
        das entidades, respeitando a máquina de estados (Menu/Jogo/Game_Over).
        """
        # Controle de Tela Cheia com F11 (Global: funciona no menu, jogo e game over)
        if glfw.get_key(self.window, glfw.KEY_F11) == glfw.PRESS:
            # Impede que a tela fique piscando loucamente ao segurar a tecla
            if not getattr(self, 'f11_pressed', False):
                self.toggle_fullscreen()
                self.f11_pressed = True
        else:
            self.f11_pressed = False

        if self.estado == "menu":
            if glfw.get_key(self.window, glfw.KEY_ENTER) == glfw.PRESS:
                self.estado = "jogo"
                self.hud.start_timer()
                self.last_time = glfw.get_time()
            return

        if self.estado == "game_over":
            if glfw.get_key(self.window, glfw.KEY_ENTER) == glfw.PRESS:
                self.reiniciar_jogo()
                self.estado = "jogo"
                self.last_time = glfw.get_time()
            elif glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
                glfw.set_window_should_close(self.window, True)
            return

        # Reseta o vetor X a cada frame, exigindo input ativo para o movimento (Sem inércia no chão)
        self.player.vel_x = 0

        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS:
            self.player.vel_x = -self.settings.move_speed
            self.player.direcao = -1

        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS:
            self.player.vel_x = self.settings.move_speed
            self.player.direcao = 1

        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS:
            self.player.jump()

        if glfw.get_key(self.window, glfw.KEY_SPACE) == glfw.PRESS:
            self.player.jump()

        # Gatilho de disparo (Arma primária)
        if glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
            if not self.mouse_pressed and self.player.tem_item:
                proj = self.player.atirar()
                if proj:
                    self.projeteis.append(proj)
                self.mouse_pressed = True
        else:
            self.mouse_pressed = False

        # Gatilho de arremesso (Granadas/Molotovs)
        if glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS:
            if not getattr(self, 'mouse_right_pressed', False) and getattr(self.player, 'tem_arremessavel', False):
                item = self.player.arremessar()
                if item:
                    self.projeteis.append(item)
                self.mouse_right_pressed = True
        else:
            self.mouse_right_pressed = False

    def update(self):
        """
        Coração do Game Loop. Calcula o Delta Time (dt) para desacoplar a física do framerate.
        Orquestra a atualização sequencial de físicas, colisões e estados.
        """
        if self.estado in ("menu", "game_over"):
            return

        delta_time = glfw.get_time() - self.last_time
        self.last_time = glfw.get_time()

        if delta_time > 0.1:
            delta_time = 0.016

        if self.player.invulneravel_tempo > 0:
            self.player.invulneravel_tempo -= delta_time

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

        # Avanço de nível via colisão com a entidade objetivo
        if self.player.check_collision(self.mapa_atual.objetivo):
            self.avancar_fase()

    def avancar_fase(self):
        """Trata o carregamento do próximo nível lógico ou mundo e reseta o ambiente."""
        if self.em_transicao:
            return

        self.em_transicao = True
        self.fase += 1

        if self.fase > self.fases_por_mundo:
            self.fase = 1
            self.mundo += 1

        self.load_backgrounds()
        self.mapa_atual = Mapa(self.mundo, self.fase, self.settings)
        self.inimigos = self.mapa_atual.inimigos

        self.player.reset_posicao()
        self.player.invulneravel_tempo = 3.0

        self.camera_x = 0.0
        self.power_ups_ativos.clear()
        self.projeteis.clear()

        self.hud.reset_timer()
        self.em_transicao = False

        self.last_time = glfw.get_time()

    def reiniciar_jogo(self):
        """Executa um Hard Reset no progresso devolvendo o jogador ao 1-1."""
        self.mundo = 1
        self.fase = 1

        self.mapa_atual = Mapa(self.mundo, self.fase, self.settings)
        self.inimigos = self.mapa_atual.inimigos

        self.player.vidas = self.settings.player_vidas
        self.player.reset_posicao()
        self.player.invulneravel_tempo = 0

        self.camera_x = 0.0
        self.power_ups_ativos.clear()
        self.projeteis.clear()
        self.explosoes_visuais.clear()
        self.mouse_pressed = False
        self.mouse_right_pressed = False
        self.em_transicao = False

        self.hud.reset_timer()
        self.load_backgrounds()

    def entrar_game_over(self):
        """Altera a máquina de estado para bloquear interações do jogo principal."""
        if self.estado == "game_over":
            return

        self.estado = "game_over"
        self.player.vel_x = 0
        self.player.vel_y = 0

    def handle_player_physics_x(self, dt):
        """
        Computa o movimento em X e realiza a resolução de colisão lateral empurrando
        a Bounding Box do jogador gentilmente para fora do obstáculo interceptado.
        """
        self.player.update_physics_x(dt)

        for obj in self.mapa_atual.obstacles:
            if self.player.check_collision(obj):
                if self.player.vel_x > 0:
                    self.player.centro_x = obj.canto_inf_esq_x - (self.player.hitbox_width / 2)
                elif self.player.vel_x < 0:
                    self.player.centro_x = obj.canto_inf_dir_x + (self.player.hitbox_width / 2)

    def handle_player_physics_y(self, dt):
        """
        Computa gravidade/salto em Y e trata resoluções tanto para a aterrissagem no chão
        quanto para colisões verticais na "cabeça" do player.
        """
        self.player.no_chao = False
        self.player.update_physics_y(dt)

        for obj in self.mapa_atual.obstacles:
            if self.player.check_collision(obj):

                # Colisão de topo (ex: batendo a cabeça em um bloco Power-Up)
                if self.player.vel_y > 0 and self.player.centro_y < obj.centro_y:
                    self.player.centro_y = obj.canto_inf_esq_y - (self.player.hitbox_height / 2)
                    self.player.vel_y = 0
                    self.handle_power_up_block(obj)

                # Colisão de base (Aterrissagem)
                elif self.player.vel_y <= 0 and self.player.canto_inf_esq_y > (obj.canto_sup_esq_y - 0.2):
                    self.player.centro_y = obj.canto_sup_esq_y + (self.player.hitbox_height / 2)
                    self.player.vel_y = 0
                    self.player.no_chao = True

    def handle_inimigos(self, dt):
        """
        Atualiza física, detecção de bordas e colisões de todos os NPCs carregados na fase.
        """
        for inimigo in self.inimigos[:]:
            inimigo.update_physics(dt)
            inimigo.no_chao = False

            for obj in self.mapa_atual.obstacles:
                if inimigo.check_collision(obj):

                    if inimigo.vel_y <= 0 and inimigo.centro_y > obj.centro_y:
                        inimigo.centro_y = obj.canto_sup_esq_y + (inimigo.height / 2)
                        inimigo.vel_y = 0
                        inimigo.no_chao = True

                    # Efeito de bate-volta em obstáculos laterais
                    elif inimigo.vel_x > 0:
                        inimigo.centro_x = obj.canto_inf_esq_x - (inimigo.width / 2)
                        inimigo.direcao *= -1

                    elif inimigo.vel_x < 0:
                        inimigo.centro_x = obj.canto_inf_dir_x + (inimigo.width / 2)
                        inimigo.direcao *= -1

            # Rotina de IA básica: Vira para a outra direção se detectar queda à frente
            if inimigo.no_chao:
                if not inimigo.validar_chao(self.mapa_atual.obstacles):
                    inimigo.direcao *= -1

            # Dano por contato direto
            if self.player.check_collision(inimigo) and self.player.invulneravel_tempo <= 0:
                self.player.tomar_dano(20)
                if self.player.vidas <= 0:
                    self.entrar_game_over()
                    return

            # Gatilho exclusivo de ataque para a classe Sniper
            if isinstance(inimigo, InimigoAtirador):
                inimigo.update(dt, self.player, self.projeteis)

    def handle_explosoes(self, dt):
        """
        Atualiza o tempo de vida de efeitos em área e aplica os danos correspondentes
        para entidades dentro do raio delimitado pela matemática da explosão.
        """
        for exp in self.explosoes_visuais[:]:
            exp.update(dt)

            if isinstance(exp, FogoChao):
                for inimigo in self.inimigos[:]:
                    if abs(inimigo.centro_x - exp.centro_x) < (exp.largura / 2) + (inimigo.width / 2):
                        if abs(inimigo.centro_y - exp.centro_y) < (inimigo.height / 2) + 0.2:
                            if inimigo in self.inimigos:
                                self.inimigos.remove(inimigo)

                # Avaliação de dano no jogador (Fogo Amigo)
                if abs(self.player.centro_x - exp.centro_x) < (exp.largura / 2) + (self.player.width / 2):
                    if abs(self.player.centro_y - exp.centro_y) < (self.player.height / 2) + 0.2:
                        self.player.tomar_dano(15)

                        if self.player.vidas <= 0:
                            self.entrar_game_over()
                            return

            if exp.destruir:
                self.explosoes_visuais.remove(exp)

    def handle_projeteis(self, dt):
        """
        Move e faz o culling (remoção) de projéteis. Aciona funções filhas se o projétil
        for uma entidade explosiva (Granada/Molotov).
        """
        for proj in self.projeteis[:]:
            proj.update(dt)

            # Destruição por expiração de timer lógico da entidade
            if getattr(proj, 'destruir', False):
                if isinstance(proj, GranadaAtiva):
                    self.explodir_granada(proj)
                elif isinstance(proj, MolotovAtiva):
                    self.quebrar_molotov(proj)

                if proj in self.projeteis:
                    self.projeteis.remove(proj)
                continue

            # Destruição por impacto contra o cenário físico
            bateu_no_cenario = False
            for obj in self.mapa_atual.obstacles:
                if proj.check_collision(obj):
                    if isinstance(proj, GranadaAtiva):
                        self.explodir_granada(proj)
                    elif isinstance(proj, MolotovAtiva):
                        self.quebrar_molotov(proj)

                    if proj in self.projeteis:
                        self.projeteis.remove(proj)

                    bateu_no_cenario = True
                    break

            if bateu_no_cenario:
                continue

            # Avaliação de Hit: Jogador -> Inimigos
            if proj.origem == "player":
                for inimigo in self.inimigos[:]:
                    if proj.check_collision(inimigo):

                        if isinstance(proj, GranadaAtiva):
                            self.explodir_granada(proj)
                        elif isinstance(proj, MolotovAtiva):
                            self.quebrar_molotov(proj)

                        if inimigo in self.inimigos:
                            self.inimigos.remove(inimigo)

                        if proj in self.projeteis:
                            self.projeteis.remove(proj)
                        break

            # Avaliação de Hit: Inimigos -> Jogador
            elif proj.origem == "inimigo":
                if proj.check_collision(self.player) and self.player.invulneravel_tempo <= 0:
                    self.player.tomar_dano(30)
                    if proj in self.projeteis:
                        self.projeteis.remove(proj)

                    if self.player.vidas <= 0:
                        self.entrar_game_over()
                    break

    def handle_power_up_block(self, obj):
        """Invoca a função interativa da entidade do bloco gerando um item dropável no mundo."""
        from src.entities.power_ups import blocoPowerUp

        if isinstance(obj, blocoPowerUp):
            novo_p_up = obj.baterPorBaixo()
            if novo_p_up:
                self.power_ups_ativos.append(novo_p_up)

    def update_power_ups(self, dt):
        """Gerencia a física de queda dos itens recém-ejetados e detecta colisões de aquisição."""
        for p_up in self.power_ups_ativos[:]:
            p_up.update(dt)
            p_up.no_chao = False

            # Física simples de aterrissagem
            for obj in self.mapa_atual.obstacles:
                if p_up.check_collision(obj):
                    if p_up.vel_y < 0:
                        p_up.centro_y = obj.canto_sup_esq_y + (p_up.height / 2)
                        p_up.vel_y = 0
                        p_up.no_chao = True

            # Coleta do loot preenchendo os inventários lógicos do player
            if self.player.check_collision(p_up):
                tipo_item = p_up.__class__.__name__

                if tipo_item == "ItemGranada":
                    self.player.tem_arremessavel = True
                    self.player.tipo_arremessavel = "GRANADA"
                elif tipo_item == "ItemMolotov":
                    self.player.tem_arremessavel = True
                    self.player.tipo_arremessavel = "MOLOTOV"
                elif tipo_item == "ItemCura":
                    self.player.vidas = getattr(self.settings, 'player_vidas', 100)
                    self.player.invulneravel_tempo = 1.0
                else:
                    self.player.tem_item = True

                self.power_ups_ativos.remove(p_up)

    def update_camera(self):
        """Trava o vetor X da câmera ao centro do player, originando o side-scrolling."""
        if self.player.centro_x > 0:
            self.camera_x = self.player.centro_x

    def check_world_bounds(self):
        """Implementa culling posicional (morte por queda) e limites temporais (Time Up)."""
        if self.player.invulneravel_tempo > 0:
            return

        # Limite inferior rígido (Kill Z)
        if self.player.centro_y < -5.0:
            self.player.tomar_dano(20)

            if self.player.vidas > 0:
                self.player.reset_posicao()
                self.player.invulneravel_tempo = 2.0
                self.camera_x = 0.0
            else:
                self.entrar_game_over()

        if self.hud.is_time_up() or self.player.vidas <= 0:
            self.entrar_game_over()

    def render(self):
        """
        Pipeline de renderização visual no OpenGL.
        A ordem define a técnica do algoritmo do pintor (Painter's Algorithm),
        onde elementos desenhados por último sobrepõem os primeiros.
        """
        if self.estado == "menu":
            self.hud.draw_menu(self.bg_layers)
            glfw.swap_buffers(self.window)
            return

        if self.estado == "game_over":
            self.hud.draw_game_over(self.bg_layers)
            glfw.swap_buffers(self.window)
            return

        # Limpeza do frame-buffer
        glClear(GL_COLOR_BUFFER_BIT)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

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

        # Envia as informações preparadas no Back Buffer para a tela visual
        glfw.swap_buffers(self.window)

    def run(self):
        """Ponto de entrada do loop infinito. Mantém o jogo vivo até que seja solicitada a saída."""
        self.init_window()
        self.load_backgrounds()
        self.player.load_sprites()

        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            self.process_input()
            self.update()
            self.render()

        glfw.terminate()

    def explodir_granada(self, granada):
        """
        Instancia uma entidade visual explosiva e calcula dano radical circular
        utilizando Teorema de Pitágoras no distanciamento das matrizes.
        """
        efeito = ExplosaoVisual(
            granada.centro_x,
            granada.centro_y,
            granada.raio_explosao * 2.0
        )

        self.explosoes_visuais.append(efeito)

        for inimigo in self.inimigos[:]:
            if math.sqrt(
                    (inimigo.centro_x - granada.centro_x) ** 2 +
                    (inimigo.centro_y - granada.centro_y) ** 2
            ) <= granada.raio_explosao:
                if inimigo in self.inimigos:
                    self.inimigos.remove(inimigo)

        distancia_player = math.sqrt(
            (self.player.centro_x - granada.centro_x) ** 2 +
            (self.player.centro_y - granada.centro_y) ** 2
        )

        if distancia_player <= granada.raio_explosao:
            self.player.tomar_dano(40)

            if self.player.vidas <= 0:
                self.reiniciar_jogo()

    def quebrar_molotov(self, molotov):
        """
        Analisa fisicamente o terreno abaixo do impacto por método de Raycasting simplificado,
        espalhando um tapete de entidades de FogoChao pelas plataformas viáveis abaixo.
        """
        chao_y = -9999.0

        for obj in self.mapa_atual.obstacles:
            if obj.canto_inf_esq_x <= molotov.centro_x <= obj.canto_inf_dir_x and \
               obj.canto_sup_esq_y <= molotov.centro_y + 0.2:
                chao_y = max(chao_y, obj.canto_sup_esq_y)

        if chao_y == -9999.0:
            return

        for obj in self.mapa_atual.obstacles:
            if abs(obj.canto_sup_esq_y - chao_y) <= 0.1 and \
               obj.canto_inf_dir_x > (molotov.centro_x - 0.25) and \
               obj.canto_inf_esq_x < (molotov.centro_x + 0.25):

                largura = min((molotov.centro_x + 0.25), obj.canto_inf_dir_x) - \
                          max((molotov.centro_x - 0.25), obj.canto_inf_esq_x)

                if largura > 0:
                    self.explosoes_visuais.append(
                        FogoChao(
                            max((molotov.centro_x - 0.25), obj.canto_inf_esq_x) + (largura / 2),
                            obj.canto_sup_esq_y,
                            largura
                        )
                    )