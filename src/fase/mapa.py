import random
from src.entities.obstaculo import Obstaculo
from src.entities.power_ups import blocoPowerUp
from src.entities.inimigo import Inimigo
from src.entities.inimigo_atirador import InimigoAtirador
from src.entities.chao import ChaoTexturizado


class Mapa:
    def __init__(self, mundo, fase, settings):
        self.obstacles = []
        self.inimigos = []
        self.tile_size = 0.1
        self.mundo = mundo
        self.fase = fase
        self.settings = settings
        self.objetivo = None

        self.texturas_chao = {
            1: "assets/texturas_chao/chao-dust2.jpg",
            2: "assets/texturas_chao/chao-mirage.jpg",
            3: "assets/texturas_chao/chao-cache.jpg"
        }

        # pega a textura do mundo atual ou usa uma padrao se não existir
        self.tex_path = self.texturas_chao.get(mundo, "assets/textures/padrao_chao.jpg")    # não tem chão padrão :D

        self.texturas_obstaculos = {
            1: "assets/texturas_obstaculos/bloco-dust2.png",
            2: "assets/texturas_obstaculos/bloco-mirage.png",
            3: "assets/texturas_obstaculos/bloco-cache.png"
        }

        self.obs_path = self.texturas_obstaculos.get(self.mundo, None)

        self.gerar_fase()

    def gerar_fase(self):
        dificuldade = self.calcular_dificuldade()

        tamanho_fase = 40 + (self.mundo * 10) + (self.fase * 5)

        chance_buraco = min(0.05 + (dificuldade * 0.01), 0.20)
        chance_bloco = min(0.10 + (self.fase * 0.05), 0.40)
        chance_inimigo = min(0.02 + (self.mundo * 0.03), 0.20)

        self.gerar_layout(tamanho_fase, chance_buraco, chance_bloco, chance_inimigo)

    def gerar_layout(self, tamanho_fase, chance_buraco, chance_bloco, chance_inimigo):
        buraco_restante = 0

        for col in range(tamanho_fase):
            x = -1 + col * self.tile_size + (self.tile_size / 2)
            y_chao = -1.0 + (self.tile_size / 2)

            if buraco_restante > 0:
                buraco_restante -= 1
                continue

            # ALTERAÇÃO: Mudamos de col < 4 para col < 5 para garantir um spawn mais seguro
            if col < 5 or col > tamanho_fase - 4 or random.random() > chance_buraco:
                # substituímos o obstaculo cinza pelo chao texturizado
                self.obstacles.append(ChaoTexturizado(x, y_chao, self.tile_size, self.tile_size, self.tex_path))

                if 4 < col < tamanho_fase - 4:

                    if random.random() < chance_bloco:
                        altura = y_chao + (self.tile_size * random.randint(4, 7))
                        if random.random() < 0.1:
                            self.obstacles.append(blocoPowerUp(x, altura, self.tile_size, self.tile_size))
                        else:
                            self.obstacles.append(Obstaculo(x, altura, self.tile_size, self.tile_size, texture_path=self.obs_path))

                    elif random.random() < chance_inimigo:
                        y_inimigo = y_chao + self.tile_size
                        escala = 1.5

                        if random.random() < 0.3:
                            self.inimigos.append(InimigoAtirador(x, y_inimigo, self.tile_size * escala, self.tile_size * escala, self.settings))
                        else:
                            self.inimigos.append(Inimigo(x, y_inimigo, self.tile_size * escala, self.tile_size * escala, self.settings))
            else:
                buraco_restante = random.randint(1, 2)

        # ✔ objetivo corrigido (sem -1 fixo no X)
        x_fim = -1 + (tamanho_fase - 2) * self.tile_size
        y_fim = -1.0 + self.tile_size

        self.objetivo = Obstaculo(x_fim, y_fim, self.tile_size * 2, self.tile_size * 2,texture_path="assets/texturas_obstaculos/badfallen.png")

    def calcular_dificuldade(self):
        return (self.mundo - 1) * 3 + self.fase