from src.entities.obstaculo import Obstaculo
from src.entities.power_ups import blocoPowerUp
from src.entities.inimigo import Inimigo
from src.entities.inimigo_atirador import InimigoAtirador

class Mapa:
    def __init__(self, level_design, settings):
        self.obstacles = []
        self.inimigos = []
        self.tile_size = 0.1
        self.settings = settings
        self.load_from_design(level_design)

    def load_from_design(self, design):
        num_linhas = len(design)

        for row_idx, row in enumerate(design):
            for col_idx, char in enumerate(row):
                x = -1.0 + (col_idx * self.tile_size) + (self.tile_size / 2)
                y = -1.0 + ((num_linhas - 1 - row_idx) * self.tile_size) + (self.tile_size / 2)

                # Mapeamento de caracteres para objetos
                if char == "G":
                    self.obstacles.append(Obstaculo(x, y, self.tile_size, self.tile_size, (0.3, 0.3, 0.3)))
                elif char == "C":
                    self.obstacles.append(Obstaculo(x, y, self.tile_size, self.tile_size, (0.6, 0.4, 0.2)))
                elif char == "T":
                    self.obstacles.append(Obstaculo(x, y + (self.tile_size/2), self.tile_size, self.tile_size * 2, (0.0, 0.7, 0.0)))
                elif char == "P":
                    bloco = blocoPowerUp(x, y, self.tile_size, self.tile_size)
                    self.obstacles.append(bloco)
                elif char == "I":
                    self.inimigos.append(Inimigo(x, y, self.tile_size, self.tile_size, self.settings))
                elif char == "S":
                    self.inimigos.append(InimigoAtirador(x, y, self.tile_size, self.tile_size, self.settings))