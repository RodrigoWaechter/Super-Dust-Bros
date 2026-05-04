import random
from src.entities.obstaculo import Obstaculo
from src.entities.power_ups import blocoPowerUp
from src.entities.inimigo import Inimigo
from src.entities.inimigo_atirador import InimigoAtirador
from src.entities.chao import ChaoTexturizado


class Mapa:
    """
    Gerencia a geração procedural do layout das fases.
    Calcula a dificuldade baseada no mundo/fase atual e distribui de forma dinâmica
    chãos, buracos, obstáculos, blocos de power-up e inimigos.
    """

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

        self.tex_path = self.texturas_chao.get(mundo, "assets/textures/padrao_chao.jpg")

        self.texturas_obstaculos = {
            1: "assets/texturas_obstaculos/bloco-dust2.png",
            2: "assets/texturas_obstaculos/bloco-mirage.png",
            3: "assets/texturas_obstaculos/bloco-cache.png"
        }

        self.obs_path = self.texturas_obstaculos.get(self.mundo, None)

        self.gerar_fase()

    def gerar_fase(self):
        """
        Calcula os parâmetros escalonáveis da fase (tamanho, probabilidade de perigos)
        com base na dificuldade atual e inicia a geração do layout.
        """
        dificuldade = self.calcular_dificuldade()

        # Escalonamento dinâmico do tamanho do mapa baseado no progresso
        tamanho_fase = 60 + (self.mundo * 15) + (self.fase * 10)

        # Limita as probabilidades máximas (caps) para garantir que a fase continue jogável
        chance_buraco = min(0.05 + (dificuldade * 0.01), 0.20)
        chance_bloco = min(0.10 + (self.fase * 0.05), 0.40)
        chance_inimigo = min(0.02 + (self.mundo * 0.03), 0.20)

        self.gerar_layout(tamanho_fase, chance_buraco, chance_bloco, chance_inimigo)

    def gerar_layout(self, tamanho_fase, chance_buraco, chance_bloco, chance_inimigo):
        """
        Itera sobre a grade da fase (colunas) para instanciar os objetos do cenário.
        Possui áreas seguras de spawn e controle de plataformas contínuas.
        """
        buraco_restante = 0

        # Controle de estado para agrupamento de plataformas contínuas
        comprimento_plataforma_atual = 0
        altura_plataforma_atual = 0

        for col in range(tamanho_fase):
            x = -1 + col * self.tile_size + (self.tile_size / 2)
            y_chao = -1.0 + (self.tile_size / 2)

            if buraco_restante > 0:
                buraco_restante -= 1
                continue

            # Culling de extremidades: garante chão sólido na área de spawn e no objetivo final
            if col < 5 or col > tamanho_fase - 4 or random.random() > chance_buraco:
                self.obstacles.append(ChaoTexturizado(x, y_chao, self.tile_size, self.tile_size, self.tex_path))

                # Área permitida para plataformas flutuantes
                if 4 < col < tamanho_fase - 4:

                    if comprimento_plataforma_atual > 0:
                        if random.random() < 0.1:
                            self.obstacles.append(
                                blocoPowerUp(x, altura_plataforma_atual, self.tile_size, self.tile_size))
                        else:
                            self.obstacles.append(Obstaculo(x, altura_plataforma_atual, self.tile_size, self.tile_size,
                                                            texture_path=self.obs_path))

                        comprimento_plataforma_atual -= 1

                    else:
                        if random.random() < chance_bloco:
                            # Inicia uma nova cadeia de plataformas travando o eixo Y
                            comprimento_plataforma_atual = random.randint(1, 3)
                            altura_plataforma_atual = y_chao + (self.tile_size * random.randint(4, 6))

                            if random.random() < 0.1:
                                self.obstacles.append(
                                    blocoPowerUp(x, altura_plataforma_atual, self.tile_size, self.tile_size))
                            else:
                                self.obstacles.append(
                                    Obstaculo(x, altura_plataforma_atual, self.tile_size, self.tile_size,
                                              texture_path=self.obs_path))

                            comprimento_plataforma_atual -= 1

                # Área de Safe Zone para spawn de inimigos (evita instanciamento no early-game da fase)
                if 12 < col < tamanho_fase - 4:
                    if random.random() < chance_inimigo:
                        y_inimigo = y_chao + self.tile_size
                        escala = 1.5

                        # Distribuição ponderada de tipos de inimigos
                        if random.random() < 0.3:
                            self.inimigos.append(
                                InimigoAtirador(x, y_inimigo, self.tile_size * escala, self.tile_size * escala,
                                                self.settings))
                        else:
                            self.inimigos.append(
                                Inimigo(x, y_inimigo, self.tile_size * escala, self.tile_size * escala, self.settings))
            else:
                # Reseta a construção de plataformas em caso de buracos subjacentes
                buraco_restante = random.randint(1, 2)
                comprimento_plataforma_atual = 0

        # Fixação do trigger point de fim de nível
        x_fim = -1 + (tamanho_fase - 2) * self.tile_size
        y_fim = -1.0 + self.tile_size

        self.objetivo = Obstaculo(x_fim, y_fim, self.tile_size * 2, self.tile_size * 2,
                                  texture_path="assets/texturas_obstaculos/badfallen.png")

    def calcular_dificuldade(self):
        """Calcula um índice linear de dificuldade baseado na progressão atual."""
        return (self.mundo - 1) * 3 + self.fase