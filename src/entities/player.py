from src.entities.personagem import Personagem
from src.entities.projetil import Projetil


class Player(Personagem):
    def __init__(self, settings):
        super().__init__(
            x=settings.player_start_x,
            y=settings.player_start_y,
            width=settings.player_width,
            height=settings.player_height,
            color=(1.0, 0.5, 0.0),
            settings=settings
        )
        self.vidas = settings.player_vidas
        self.tem_item = False
        self.invulneravel_tempo = 0
        self.direcao = 1

    def jump(self):
        if self.no_chao:
            self.vel_y = self.settings.jump_speed
            self.no_chao = False

    def atirar(self):
        if not self.tem_item:
            return None

        direcao = self.direcao
        offset = (self.width / 2) + 0.1
        spawn_x = self.centro_x + (offset * direcao)
        spawn_y = self.centro_y

        return Projetil(spawn_x, spawn_y, direcao, origem="player")

    def tomar_dano(self, quantidade):
        if self.invulneravel_tempo <= 0:
            self.vidas -= quantidade
            self.invulneravel_tempo = 1.0

            if self.vidas <= 0:
                self.vidas = 0
                self.morrer()

    def reset_posicao(self):
        self.centro_x = self.settings.player_start_x
        self.centro_y = self.settings.player_start_y
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.tem_item = False

    def morrer(self):
        pass

    def update_physics_y(self, dt):
        if not self.no_chao or self.vel_y > 0:
            self.vel_y += self.settings.gravity * dt

            # Limita a velocidade pro player nãoo bugar e atravessar o chão
            if self.vel_y < -4.5:
                self.vel_y = -4.5

            self.centro_y += self.vel_y * dt
        else:
            self.vel_y = 0