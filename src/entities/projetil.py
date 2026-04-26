from src.entities.game_object import GameObject

class Projetil(GameObject):
    def __init__(self, x, y, direcao, origem="player", speed=0.9):
        super().__init__(x, y, 0.03, 0.03, (1.0, 1.0, 0.0))
        self.vel_x = speed * direcao
        self.start_x = x
        self.max_distance = 0.8
        self.destruir = False
        self.origem = origem

    def update(self, delta_time):
        self.centro_x += self.vel_x * delta_time
        if abs(self.centro_x - self.start_x) >= self.max_distance:
            self.destruir = True