class Player:
    def __init__(self, settings):
        self.width = settings.player_width
        self.height = settings.player_height

        # Velocidades de movimento
        self.vel_x = 0.0
        self.vel_y = 0.0

        # Limite do chão temporário
        self.chao_da_tela = -1 + self.height / 2

        # Inicia a posição
        self.set_posicao(settings.player_start_x, settings.player_start_y)

    def set_posicao(self, x, y):
        # Colisão básica com o chão
        if y <= self.chao_da_tela:
            y = self.chao_da_tela
            self.vel_y = 0.0  # Zera a força de queda se tocou o chão

        self.centro_x = x
        self.centro_y = y

        # Calcula as extremidades
        self.canto_inf_esq_x = x - self.width / 2
        self.canto_inf_esq_y = y - self.height / 2
        self.canto_inf_dir_x = x + self.width / 2
        self.canto_inf_dir_y = y - self.height / 2
        self.canto_sup_dir_x = x + self.width / 2
        self.canto_sup_dir_y = y + self.height / 2
        self.canto_sup_esq_x = x - self.width / 2
        self.canto_sup_esq_y = y + self.height / 2