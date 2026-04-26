import os
import random
from src.entities.obstaculo import Obstaculo
from src.entities.power_ups import blocoPowerUp
from src.entities.inimigo import Inimigo
from src.entities.inimigo_atirador import InimigoAtirador

class Mapa:
    def __init__(self, dificuldade, settings):
        self.obstacles = []
        self.inimigos = []
        self.tile_size = 0.1
        self.dificuldade = dificuldade
        self.settings = settings
        self.objetivo = None
        self.gerar_fase_aleatoria()

    def gerar_fase_aleatoria(self):
        # Aumenta o tamanho da fase gradualmente
        tamanho_fase = 30 + (self.dificuldade * 10)

        chance_buraco = min(0.05 + (self.dificuldade * 0.02), 0.25)
        chance_bloco = min(0.10 + (self.dificuldade * 0.05), 0.40)
        chance_inimigo = min(0.05 + (self.dificuldade * 0.05), 0.20)

        for col in range(tamanho_fase):
            x = -1.0 + (col * self.tile_size) + (self.tile_size / 2)
            y_chao = -1.0 + (self.tile_size / 2)

            # Garante que o início e o fim da fase não tenham buracos
            if col < 4 or col > tamanho_fase - 4 or random.random() > chance_buraco:
                # Chão
                self.obstacles.append(Obstaculo(x, y_chao, self.tile_size, self.tile_size, (0.3, 0.3, 0.3)))

                # Gera obstáculos e inimigos apenas no meio da fase
                if 4 < col < tamanho_fase - 4:
                    # Caixas e Power-ups
                    if random.random() < chance_bloco:
                        altura = y_chao + (self.tile_size * random.randint(2, 4))
                        if random.random() < 0.3:
                            self.obstacles.append(blocoPowerUp(x, altura, self.tile_size, self.tile_size))
                        else:
                            self.obstacles.append(Obstaculo(x, altura, self.tile_size, self.tile_size, (0.6, 0.4, 0.2)))

                    # Inimigos
                    elif random.random() < chance_inimigo:
                        y_inimigo = y_chao + self.tile_size
                        if random.random() < 0.3:  # 30% atirador, 70% comum
                            self.inimigos.append(
                                InimigoAtirador(x, y_inimigo, self.tile_size, self.tile_size, self.settings))
                        else:
                            self.inimigos.append(Inimigo(x, y_inimigo, self.tile_size, self.tile_size, self.settings))

        # Objetivo de fim de fase
        x_fim = -1.0 + ((tamanho_fase - 2) * self.tile_size) + (self.tile_size / 2)
        y_fim = -1.0 + (self.tile_size / 2) + (self.tile_size * 2)
        self.objetivo = Obstaculo(x_fim, y_fim, self.tile_size, self.tile_size * 4, (0.0, 1.0, 0.0))
        self.obstacles.append(self.objetivo)