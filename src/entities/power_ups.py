from src.entities.game_object import GameObject


class power_ups(GameObject):
    def __init__(self, x, y, width, height, color=(1.0, 0.0, 0.0)):
        #item vermelho
        super().__init__(x, y, width, height, color)
        #movmentação do item
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.gravity = -2.5

        #animação de spawn
        self.is_spawnning = True
        self.spawn_speed = 0.5
        #subir uma casa dps do spawn
        self.spawn_target_y = y + height

    def update(self, dt):
        if self.is_spawnning:
            self.centro_y += self.spawn_speed * dt
            if self.centro_y >= self.spawn_target_y:
                self.is_spawnning = False
                self.centro_y = self.spawn_target_y
        else:
            self.vel_y += self.gravity * dt
            self.centro_x += self.vel_x * dt
            self.centro_y += self.vel_y * dt

class blocoPowerUp(GameObject):
    def __init__(self, x, y, width, height):
        super().__init__(x,y,width,height,(0.8, 0.4, 0.0))
        self.foiAtingido = False

    def baterPorBaixo(self):
        if not self.foiAtingido:
            self.foiAtingido = True
            self.color = (0.4, 0.4, 0.4)
            return power_ups(self.centro_x, self.centro_y, self.width, self.height)
        return None