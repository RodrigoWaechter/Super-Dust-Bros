from src.entities.game_object import GameObject

class Inimigo(GameObject):
    def __init__(self, x, y, width, height, settings, color=(1.0, 0.0, 0.0)):
        super().__init__(x, y, width, height, color)
        self.settings = settings

        self.vel_x = 0.0
        self.vel_y = 0.0
        self.no_chao = False

        self.velocidade = 0.5
        self.direcao = -1

    def update_physics(self, delta_time):
        self.vel_y += self.settings.gravity * delta_time

        if self.no_chao:
            self.vel_x = self.velocidade * self.direcao
        else:
            self.vel_x = 0

        self.centro_x += self.vel_x * delta_time
        self.centro_y += self.vel_y * delta_time

    def validar_chao(self, obstacles):
        offset_x = (self.width / 2) * self.direcao
        check_x = self.centro_x + offset_x
        check_y = self.centro_y - (self.height / 2) - 0.02

        for obj in obstacles:
            if (obj.canto_inf_esq_x <= check_x <= obj.canto_inf_dir_x and
                    obj.canto_inf_esq_y <= check_y <= obj.canto_sup_esq_y):
                return True

        return False