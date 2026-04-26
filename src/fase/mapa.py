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
        # Escala o tamanho e a dificuldade com base no nível atual
        tamanho_fase = 50 + (self.dificuldade * 15)
        chance_buraco = min(0.05 + (self.dificuldade * 0.02), 0.20)
        chance_bloco = min(0.10 + (self.dificuldade * 0.05), 0.40)
        chance_inimigo = min(0.02 + (self.dificuldade * 0.03), 0.15)

        buraco_restante = 0

        # Constrói o mapa coluna por coluna da esquerda para a direita
        for col in range(tamanho_fase):
            x = -1.0 + (col * self.tile_size) + (self.tile_size / 2)
            y_chao = -1.0 + (self.tile_size / 2)

            # Pula a geração desta coluna se estiver no meio de um abismo
            if buraco_restante > 0:
                buraco_restante -= 1
                continue

            # Gera chão sólido nas pontas ou aleatoriamente pelo mapa
            if col < 4 or col > tamanho_fase - 4 or random.random() > chance_buraco:
                self.obstacles.append(Obstaculo(x, y_chao, self.tile_size, self.tile_size, (0.3, 0.3, 0.3)))

                # Adiciona elementos verticais apenas onde existe chão seguro
                if 4 < col < tamanho_fase - 4:

                    # Gera plataformas voadoras (normais ou power-ups)
                    if random.random() < chance_bloco:
                        altura = y_chao + (self.tile_size * random.randint(3, 5))
                        if random.random() < 0.1:
                            self.obstacles.append(blocoPowerUp(x, altura, self.tile_size, self.tile_size))
                        else:
                            self.obstacles.append(Obstaculo(x, altura, self.tile_size, self.tile_size, (0.6, 0.4, 0.2)))

                    # Spawna inimigos (atiradores ou corpo-a-corpo)
                    elif random.random() < chance_inimigo:
                        y_inimigo = y_chao + self.tile_size
                        if random.random() < 0.3:
                            self.inimigos.append(
                                InimigoAtirador(x, y_inimigo, self.tile_size, self.tile_size, self.settings))
                        else:
                            self.inimigos.append(Inimigo(x, y_inimigo, self.tile_size, self.tile_size, self.settings))
            else:
                # Inicia um buraco que durará de 1 a 2 blocos de largura
                buraco_restante = random.randint(1, 2)

        # Configura o bloco de objetivo final no extremo direito do mapa
        x_fim = -1.0 + ((tamanho_fase - 2) * self.tile_size) + (self.tile_size / 2)
        y_fim = -1.0 + self.tile_size
        self.objetivo = Obstaculo(x_fim, y_fim, self.tile_size * 2, self.tile_size * 2, (0.8, 0.1, 0.1))