from src.entities.personagem import Personagem

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
        self.invulneravel_tempo = 0
        self.direcao = 1

    def jump(self):
        if self.no_chao:
            self.vel_y = self.settings.jump_speed
            self.no_chao = False

    def atirar(self):
        direcao = self.direcao

        offset = (self.width / 2) + 0.1
        spawn_x = self.centro_x + (offset * direcao)
        spawn_y = self.centro_y

        from src.entities.projetil import Projetil
        return Projetil(spawn_x, spawn_y, direcao)