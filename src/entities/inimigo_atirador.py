"""
inimigo_atirador.py
Implementa a classe InimigoAtirador, um tipo especializado de inimigo que ataca
à distância utilizando um comportamento de mira e disparo periódico.
"""

from src.entities.inimigo import Inimigo
from src.entities.projetil import Projetil
from src.utils import load_texture

class InimigoAtirador(Inimigo):
    """
    Inimigo especializado que mantém a posição fixa e dispara projéteis em direção ao jogador.
    Sobrescreve o pacote de sprites padrão e adiciona instanciamento de entidades filhas (Projéteis).
    """
    def __init__(self, x, y, width, height, settings, color=(0.0, 0.0, 1.0)):
        escala_altura = 0.95
        super().__init__(x, y, width, settings.player_height * escala_altura, settings, color)

        self.cooldown_tiro = 0.0
        self.tempo_entre_tiros = 2.0
        self.velocidade = 0.0
        self.sprite_offset_y = -0.04

    def load_sprites(self):
        """Sobrescreve o pipeline de sprites para carregar a versão estacionária/sniper."""
        self.sprites_idle =[
            load_texture("assets/enemy/idle/ct-atirador-idle.jpg"),
        ]
        self.sprites_carregados = True

    def update(self, delta_time, player, projeteis):
        """
        Gerencia o rastreamento do jogador para virar o sprite e o timer de disparos.
        """
        # Define a direção visual garantindo que o atirador sempre olhe para o player
        self.direcao = -1 if player.centro_x > self.centro_x else 1

        if self.cooldown_tiro > 0:
            self.cooldown_tiro -= delta_time

        if self.cooldown_tiro <= 0:
            # Calcula a direção lógica independente da direção do sprite
            direcao_tiro = 1 if player.centro_x > self.centro_x else -1

            # Desloca a origem do projétil para fora do hitbox do inimigo
            offset = (self.width / 2) + 0.1
            spawn_x = self.centro_x + (offset * direcao_tiro)
            spawn_y = self.centro_y

            proj = Projetil(spawn_x, spawn_y, direcao_tiro, origem="inimigo")
            projeteis.append(proj)

            self.cooldown_tiro = self.tempo_entre_tiros