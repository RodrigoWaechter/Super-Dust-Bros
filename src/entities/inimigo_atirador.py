from src.entities.inimigo import Inimigo
from src.entities.projetil import Projetil

class InimigoAtirador(Inimigo):
    def __init__(self, x, y, width, height, settings, color=(0.0, 0.0, 1.0)):
        super().__init__(x, y, width, height, settings, color)
        self.cooldown_tiro = 0.0
        self.tempo_entre_tiros = 2.0
        self.velocidade = 0.0

    def update(self, delta_time, player, projeteis):

        if self.cooldown_tiro > 0:
            self.cooldown_tiro -= delta_time

        if self.cooldown_tiro <= 0:
            direcao = 1 if player.centro_x > self.centro_x else -1

            offset = (self.width / 2) + 0.1
            spawn_x = self.centro_x + (offset * direcao)
            spawn_y = self.centro_y

            proj = Projetil(spawn_x, spawn_y, direcao, origem="inimigo")
            projeteis.append(proj)

            self.cooldown_tiro = self.tempo_entre_tiros