""" inimigo_atirador.py
Implementa a classe InimigoAtirador, um tipo especializado de inimigo que ataca
à distância utilizando um comportamento de mira e disparo periódico.
"""

from src.entities.inimigo import Inimigo
from src.entities.projetil import Projetil
from src.utils import load_texture

class InimigoAtirador(Inimigo):
    """
    Inimigo especializado que mantém a posição fixa e dispara projéteis em direção ao jogador.
     - Sobrescreve comportamentos visuais de Inimigo para carregar sprites únicos (Awp)
    """
    def __init__(self, x, y, width, height, settings, color=(0.0, 0.0, 1.0)):
        """
        Inicializa o inimigo atirador.
        """
        # redução para garantir alinhamento visual com o player
        escala_altura = 0.95
        super().__init__(x, y, width, settings.player_height * escala_altura, settings, color)
        self.cooldown_tiro = 0.0
        self.tempo_entre_tiros = 2.0
        self.velocidade = 0.0   # o sniper fica parado

        # ajuste visual de compensação para alinhar o sprite ao chão
        self.sprite_offset_y = -0.04

    def load_sprites(self):
        """
        Sobrescreve o metodo do pai para carregar os sprites específicos do atirador.
        """

        self.sprites_idle =[
            load_texture("assets/enemy/idle/ct-atirador-idle.jpg"),
        ]
        self.sprites_carregados = True

    def update(self, delta_time, player, projeteis):
        """
        Gerencia o estado de mira e a lógica de disparo do atirador.
         - A direção visual (self.direcao) é calculada separadamente da direção lógica
           do tiro (direcao_tiro) para compensar a orientação nativa do asset de imagem.
        """

        # atualiza a direção visual para o draw() espelhar o sprite corretamente
        self.direcao = -1 if player.centro_x > self.centro_x else 1
        # print(f"DEBUG: Sniper direcao={self.direcao}") --> debug ativo

        # gerenciamento de cooldown
        if self.cooldown_tiro > 0:
            self.cooldown_tiro -= delta_time

        # disparo
        if self.cooldown_tiro <= 0:
            # calcula a direção lógica do projétil (independente do sprite)
            direcao_tiro = 1 if player.centro_x > self.centro_x else -1

            # define o ponto de origem do projétil
            offset = (self.width / 2) + 0.1
            spawn_x = self.centro_x + (offset * direcao_tiro)
            spawn_y = self.centro_y

            # instancia e registra o novo projétil
            proj = Projetil(spawn_x, spawn_y, direcao_tiro, origem="inimigo")
            projeteis.append(proj)

            # reseta o tempo de espera
            self.cooldown_tiro = self.tempo_entre_tiros