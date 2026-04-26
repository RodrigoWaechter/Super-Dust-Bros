import os
import random
from src.entities.obstaculo import Obstaculo
from src.entities.power_ups import blocoPowerUp


class Mapa:
    def __init__(self, dificuldade=1):
        self.obstacles = []
        self.tile_size = 0.1
        self.dificuldade = dificuldade
        self.objetivo = None
        self.gerar_fase_aleatoria()

    def gerar_fase_aleatoria(self):
        # A fase aumenta 10 blocos a cada nível de dificuldade
        tamanho_fase = 30 + (self.dificuldade * 10)

        chance_buraco = min(0.05 + (self.dificuldade * 0.02), 0.25)
        chance_bloco = min(0.10 + (self.dificuldade * 0.05), 0.40)

        for col in range(tamanho_fase):
            x = -1.0 + (col * self.tile_size) + (self.tile_size / 2)
            y_chao = -1.0 + (self.tile_size / 2)

            # Evita buracos no spawn (início) e no fim
            if col < 4 or col > tamanho_fase - 4 or random.random() > chance_buraco:
                # Chão (G)
                self.obstacles.append(Obstaculo(x, y_chao, self.tile_size, self.tile_size, (0.3, 0.3, 0.3)))

                # Caixas e PowerUps aéreos
                if 4 < col < tamanho_fase - 4 and random.random() < chance_bloco:
                    altura = y_chao + (self.tile_size * random.randint(2, 4))
                    if random.random() < 0.3:
                        self.obstacles.append(blocoPowerUp(x, altura, self.tile_size, self.tile_size))
                    else:
                        self.obstacles.append(Obstaculo(x, altura, self.tile_size, self.tile_size, (0.6, 0.4, 0.2)))

        # Objetivo final da fase (Tubo verde alto)
        x_fim = -1.0 + ((tamanho_fase - 2) * self.tile_size) + (self.tile_size / 2)
        y_fim = -1.0 + (self.tile_size / 2) + (self.tile_size * 2)
        self.objetivo = Obstaculo(x_fim, y_fim, self.tile_size, self.tile_size * 4, (0.0, 1.0, 0.0))
        self.obstacles.append(self.objetivo)