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
        self.tem_item = False

    def jump(self):
        if self.no_chao:
            self.vel_y = self.settings.jump_speed
            self.no_chao = False

    def tomar_dano(self):
        self.vidas -= 1
        print(f"Vidas restantes: {self.vidas}")  # Temporário

        if self.vidas > 0:
            self.reset_posicao()
        else:
            self.morrer()

    def reset_posicao(self):
        # Volta pro início do mapa e zera inércia
        self.centro_x = self.settings.player_start_x
        self.centro_y = self.settings.player_start_y
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.tem_item = False

    def morrer(self):
        print("GAME OVER!")