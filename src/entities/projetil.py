from src.entities.game_object import GameObject

class Projetil(GameObject):
    def __init__(self, x, y, direcao, speed=0.9):
        super().__init__(x, y, 0.05, 0.05, (1.0, 1.0, 0.0))
        self.vel_x = speed * direcao

    def update(self, delta_time):
        self.centro_x += self.vel_x * delta_time