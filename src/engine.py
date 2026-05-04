"""
engine.py

Módulo responsável pelo gerenciamento central do jogo.
Implementa o loop principal, controle de estados, atualização de física,
detecção de colisões, renderização e interação entre entidades.

Autor: (seu nome)
Disciplina: (disciplina)
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
    Controla estados, lógica, renderização e interação entre objetos.
    """

    def __init__(self):
        """Inicializa variáveis e estruturas principais do jogo."""
        self.settings = Settings()
        self.player = Player(self.settings)

        # Controle da câmera (scroll horizontal)
        self.camera_x = 0.0

        # Controle de progressão de jogo
        self.mundo = 1
        self.fase = 1
        self.fases_por_mundo = 3

        # Inicialização do mapa atual
        self.mapa_atual = Mapa(self.mundo, self.fase, self.settings)
        self.inimigos = self.mapa_atual.inimigos

        # Estado do jogo: "menu", "jogo" ou "game_over"
        self.estado = "menu"

        # Listas de entidades dinâmicas
        self.power_ups_ativos = []
        self.projeteis = []
        self.explosoes_visuais = []

        # Camadas de fundo (efeito parallax)
        self.bg_layers = []

        # Controle de clique do mouse (evita disparos contínuos)
        self.mouse_pressed = False

        self.hud = HUD()
        self.window = None

        # Controle de tempo entre frames
        self.last_time = 0

        # Flag para evitar múltiplas transições simultâneas
        self.em_transicao = False

    def init_window(self):
        """
        Inicializa a janela gráfica utilizando GLFW
        e configura o sistema de projeção ortográfica.
        """
        if not glfw.init():
            raise Exception("Erro GLFW")

        self.window = glfw.create_window(
            self.settings.window_width,
            self.settings.window_height,
            self.settings.window_title,
            None,
            None
        )

        glfw.make_context_current(self.window)

        # Ativa V-Sync (sincronização com taxa de atualização do monitor)
        glfw.swap_interval(1)

        self.last_time = glfw.get_time()

        # Configuração da projeção 2D
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-1, 1, -1, 1, -1, 1)
        glMatrixMode(GL_MODELVIEW)

    def load_backgrounds(self):
        """
        Carrega o background correspondente ao mundo atual,
        utilizando efeito de parallax.
        """
        backgrounds = {
            1: "assets/background/dust.jpg",
            2: "assets/background/mirage.jpg",
            3: "assets/background/cache.jpg",
        }

        path = backgrounds.get(self.mundo, "assets/background/dust.jpg")

        # Cria camada de fundo com velocidade reduzida (parallax)
        self.bg_layers = [ParallaxLayer(path, 0.1)]

    def process_input(self):
        """
        Processa entradas do usuário (teclado e mouse),
        controlando movimentação, pulo e ataques.
        """

        # Controle do menu
        if self.estado == "menu":
            if glfw.get_key(self.window, glfw.KEY_ENTER) == glfw.PRESS:
                self.estado = "jogo"
                self.hud.start_timer()
                self.last_time = glfw.get_time()
            return

        # Controle da tela de game over
        if self.estado == "game_over":
            if glfw.get_key(self.window, glfw.KEY_ENTER) == glfw.PRESS:
                self.reiniciar_jogo()
                self.estado = "jogo"
                self.last_time = glfw.get_time()
            elif glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
                glfw.set_window_should_close(self.window, True)
            return

        # Reset da velocidade horizontal
        self.player.vel_x = 0

        # Movimento lateral
        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS:
            self.player.vel_x = -self.settings.move_speed
            self.player.direcao = -1

        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS:
            self.player.vel_x = self.settings.move_speed
            self.player.direcao = 1

        # Pulo
        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS:
            self.player.jump()

        # Disparo com botão esquerdo
        if glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
            if not self.mouse_pressed and self.player.tem_item:
                proj = self.player.atirar()
                if proj:
                    self.projeteis.append(proj)
                self.mouse_pressed = True
        else:
            self.mouse_pressed = False

        # Arremesso com botão direito
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
        Atualiza o estado do jogo a cada frame.
        Inclui física, colisões, IA e lógica geral.
        """
        if self.estado in ("menu", "game_over"):
            return

        # Cálculo do tempo entre frames
        delta_time = glfw.get_time() - self.last_time
        self.last_time = glfw.get_time()

        # Atualização de invulnerabilidade
        if self.player.invulneravel_tempo > 0:
            self.player.invulneravel_tempo -= delta_time

        # Atualizações principais
        self.handle_player_physics_x(delta_time)
        self.handle_player_physics_y(delta_time)
        self.handle_inimigos(delta_time)
        self.handle_projeteis(delta_time)
        self.handle_explosoes(delta_time)
        self.update_power_ups(delta_time)

        # Atualização de estado e animação
        self.player.update_estado()
        self.player.update_animacao(delta_time)

        self.update_camera()
        self.check_world_bounds()

        # Verifica avanço de fase
        if self.player.check_collision(self.mapa_atual.objetivo):
            self.avancar_fase()

    def avancar_fase(self):
        """
        Avança para a próxima fase ou mundo.
        Realiza reset de variáveis importantes.
        """
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

    def reiniciar_jogo(self):
        """
        Reinicia completamente o jogo (estado inicial).
        """
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
        """
        Coloca o jogo em estado de game over sem reiniciar imediatamente.
        """
        if self.estado == "game_over":
            return

        self.estado = "game_over"
        self.player.vel_x = 0
        self.player.vel_y = 0

    def handle_player_physics_x(self, dt):
        """
        Atualiza movimento horizontal do jogador e resolve colisões laterais.
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
        Atualiza física vertical (gravidade/pulo) e colisões com chão.
        """
        self.player.no_chao = False
        self.player.update_physics_y(dt)

        for obj in self.mapa_atual.obstacles:
            if self.player.check_collision(obj):

                # Colisão ao subir (bater em bloco)
                if self.player.vel_y > 0 and self.player.centro_y < obj.centro_y:
                    self.player.centro_y = obj.canto_inf_esq_y - (self.player.hitbox_height / 2)
                    self.player.vel_y = 0
                    self.handle_power_up_block(obj)

                # Colisão ao cair (chão)
                elif self.player.vel_y <= 0 and self.player.canto_inf_esq_y > (obj.canto_sup_esq_y - 0.2):
                    self.player.centro_y = obj.canto_sup_esq_y + (self.player.hitbox_height / 2)
                    self.player.vel_y = 0
                    self.player.no_chao = True

    def handle_inimigos(self, dt):
        """
        Atualiza comportamento dos inimigos, incluindo movimento,
        colisões e interação com o jogador.
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

                    elif inimigo.vel_x > 0:
                        inimigo.centro_x = obj.canto_inf_esq_x - (inimigo.width / 2)
                        inimigo.direcao *= -1

                    elif inimigo.vel_x < 0:
                        inimigo.centro_x = obj.canto_inf_dir_x + (inimigo.width / 2)
                        inimigo.direcao *= -1

            # Verifica se ainda há chão à frente
            if inimigo.no_chao:
                if not inimigo.validar_chao(self.mapa_atual.obstacles):
                    inimigo.direcao *= -1

            # Colisão com player
            if self.player.check_collision(inimigo) and self.player.invulneravel_tempo <= 0:
                self.player.tomar_dano(20)
                if self.player.vidas <= 0:
                    self.entrar_game_over()
                    return

            # Inimigo atirador
            if isinstance(inimigo, InimigoAtirador):
                inimigo.update(dt, self.player, self.projeteis)

    def handle_explosoes(self, dt):
        """
        Atualiza efeitos de explosão e aplica dano em área no fogo,
        afetando inimigos e o jogador.
        """
        for exp in self.explosoes_visuais[:]:
            exp.update(dt)

            # Fogo contínuo no chão (Molotov)
            if isinstance(exp, FogoChao):
                # Dano nos inimigos
                for inimigo in self.inimigos[:]:
                    if abs(inimigo.centro_x - exp.centro_x) < (exp.largura / 2) + (inimigo.width / 2):
                        if abs(inimigo.centro_y - exp.centro_y) < (inimigo.height / 2) + 0.2:
                            # CORREÇÃO APLICADA AQUI
                            if inimigo in self.inimigos:
                                self.inimigos.remove(inimigo)

                # NOVO: Dano no próprio jogador se pisar no fogo!
                if abs(self.player.centro_x - exp.centro_x) < (exp.largura / 2) + (self.player.width / 2):
                    if abs(self.player.centro_y - exp.centro_y) < (self.player.height / 2) + 0.2:
                        # Dano menor, pois se ele ficar parado, vai tomar várias vezes.
                        # (O seu sistema de invulnerabilidade de 1s que configuramos no player
                        # impede que a vida derreta instantaneamente!)
                        self.player.tomar_dano(15)

                        if self.player.vidas <= 0:
                            self.entrar_game_over()
                            return

            # Remove explosão finalizada
            if exp.destruir:
                self.explosoes_visuais.remove(exp)

    def handle_projeteis(self, dt):
        """
        Atualiza projéteis, detecta colisões e aplica dano.
        """
        for proj in self.projeteis[:]:
            proj.update(dt)

            # Verifica se deve ser destruído (ex: tempo acabou)
            if getattr(proj, 'destruir', False):
                if isinstance(proj, GranadaAtiva):
                    self.explodir_granada(proj)
                elif isinstance(proj, MolotovAtiva):
                    self.quebrar_molotov(proj)

                if proj in self.projeteis:
                    self.projeteis.remove(proj)
                continue

            # Colisão com cenário
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

            # Se já bateu na parede/chão e sumiu, não precisa checar inimigos
            if bateu_no_cenario:
                continue

            # Dano direto nos inimigos
            if proj.origem == "player":
                for inimigo in self.inimigos[:]:
                    if proj.check_collision(inimigo):

                        # AQUI ESTÁ A CORREÇÃO:
                        # Se for Granada ou Molotov, aciona o efeito na cara do inimigo antes de sumir!
                        if isinstance(proj, GranadaAtiva):
                            self.explodir_granada(proj)
                        elif isinstance(proj, MolotovAtiva):
                            self.quebrar_molotov(proj)

                        # Remove o inimigo atingido - CORREÇÃO APLICADA AQUI
                        if inimigo in self.inimigos:
                            self.inimigos.remove(inimigo)

                        # Remove o projétil da tela - CORREÇÃO APLICADA AQUI
                        if proj in self.projeteis:
                            self.projeteis.remove(proj)
                        break

            # Dano no jogador (caso inimigos atirem)
            elif proj.origem == "inimigo":
                if proj.check_collision(self.player) and self.player.invulneravel_tempo <= 0:
                    self.player.tomar_dano(30)
                    if proj in self.projeteis:
                        self.projeteis.remove(proj)

                    if self.player.vidas <= 0:
                        self.entrar_game_over()
                    break

    def handle_power_up_block(self, obj):
        """
        Ativa blocos de power-up quando atingidos por baixo.
        """
        from src.entities.power_ups import blocoPowerUp

        if isinstance(obj, blocoPowerUp):
            novo_p_up = obj.baterPorBaixo()
            if novo_p_up:
                self.power_ups_ativos.append(novo_p_up)

    def update_power_ups(self, dt):
        """
        Atualiza física e coleta de power-ups.
        """
        for p_up in self.power_ups_ativos[:]:
            p_up.update(dt)
            p_up.no_chao = False

            for obj in self.mapa_atual.obstacles:
                if p_up.check_collision(obj):
                    if p_up.vel_y < 0:
                        p_up.centro_y = obj.canto_sup_esq_y + (p_up.height / 2)
                        p_up.vel_y = 0
                        p_up.no_chao = True

            # Coleta pelo jogador
            if self.player.check_collision(p_up):
                tipo_item = p_up.__class__.__name__

                if tipo_item == "ItemGranada":
                    self.player.tem_arremessavel = True
                    self.player.tipo_arremessavel = "GRANADA"

                elif tipo_item == "ItemMolotov":
                    self.player.tem_arremessavel = True
                    self.player.tipo_arremessavel = "MOLOTOV"

                # Lógica para pegar o item de Cura (Heal)
                elif tipo_item == "ItemCura":
                    # Usa o valor do settings, ou 100 como padrão para evitar erros
                    self.player.vidas = getattr(self.settings, 'player_vidas', 100)

                    # Garante 1 segundo de invulnerabilidade após curar
                    self.player.invulneravel_tempo = 1.0
                    print("Vida restaurada ao máximo!")

                else:
                    self.player.tem_item = True

                # Remove o item da tela após ser coletado
                self.power_ups_ativos.remove(p_up)

    def update_camera(self):
        """
        Atualiza posição da câmera com base no jogador.
        """
        if self.player.centro_x > 0:
            self.camera_x = self.player.centro_x

    def check_world_bounds(self):
        """
        Verifica limites do mundo (queda ou tempo esgotado).
        """
        if self.player.invulneravel_tempo > 0:
            return

        # Queda fora do mapa
        if self.player.centro_y < -5.0:
            self.player.tomar_dano(20)

            if self.player.vidas > 0:
                self.player.reset_posicao()
                self.player.invulneravel_tempo = 2.0
                self.camera_x = 0.0
            else:
                self.entrar_game_over()

        # Tempo esgotado
        if self.hud.is_time_up() or self.player.vidas <= 0:
            self.entrar_game_over()

    def render(self):
        """
        Renderiza todos os elementos do jogo na tela.
        """
        if self.estado == "menu":
            self.hud.draw_menu(self.bg_layers)
            glfw.swap_buffers(self.window)
            return

        if self.estado == "game_over":
            self.hud.draw_game_over(self.bg_layers)
            glfw.swap_buffers(self.window)
            return

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

        glfw.swap_buffers(self.window)

    def run(self):
        """
        Executa o loop principal do jogo.
        """
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
        Cria explosão de granada e aplica dano em área, tanto em inimigos
        quanto no próprio jogador (fogo amigo ativado).
        """
        efeito = ExplosaoVisual(
            granada.centro_x,
            granada.centro_y,
            granada.raio_explosao * 2.0
        )

        self.explosoes_visuais.append(efeito)

        # Dano em área nos inimigos
        for inimigo in self.inimigos[:]:
            if math.sqrt(
                    (inimigo.centro_x - granada.centro_x) ** 2 +
                    (inimigo.centro_y - granada.centro_y) ** 2
            ) <= granada.raio_explosao:
                # CORREÇÃO APLICADA AQUI
                if inimigo in self.inimigos:
                    self.inimigos.remove(inimigo)

        # NOVO: Dano em área no próprio jogador!
        distancia_player = math.sqrt(
            (self.player.centro_x - granada.centro_x) ** 2 +
            (self.player.centro_y - granada.centro_y) ** 2
        )

        if distancia_player <= granada.raio_explosao:
            # O dano da granada costuma ser alto. Coloquei 40, mas você pode ajustar.
            self.player.tomar_dano(40)

            # Verifica se o jogador morreu na própria explosão
            if self.player.vidas <= 0:
                self.reiniciar_jogo()

    def quebrar_molotov(self, molotov):
        """
        Cria efeito de fogo no chão ao quebrar molotov.
        """
        chao_y = -9999.0

        # Detecta o chão mais próximo
        for obj in self.mapa_atual.obstacles:
            if obj.canto_inf_esq_x <= molotov.centro_x <= obj.canto_inf_dir_x and \
               obj.canto_sup_esq_y <= molotov.centro_y + 0.2:
                chao_y = max(chao_y, obj.canto_sup_esq_y)

        if chao_y == -9999.0:
            return

        # Cria áreas de fogo
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