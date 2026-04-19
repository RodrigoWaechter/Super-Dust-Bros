from src.entities.game_object import GameObject

class Personagem(GameObject):
    def __init__(self, x, y, width, height, color, settings):
        super().__init__(x, y, width, height, color)
        self.settings = settings
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.no_chao = False

    def update_physics(self, delta_time):
        # Gravidade e movimento
        self.vel_y += self.settings.gravity * delta_time
        self.centro_x += self.vel_x * delta_time
        self.centro_y += self.vel_y * delta_time