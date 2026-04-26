class Settings:
    def __init__(self):
        # Configurações da janela
        self.window_width = 800
        self.window_height = 600
        self.window_title = "Super UNISC Bros"

        # Física do jogo
        self.gravity = -3.0
        self.jump_speed = 1.5
        self.move_speed = 1.2

        # Configurações iniciais do jogador
        self.player_start_x = -0.9
        self.player_start_y = -0.5
        self.player_width = 0.1
        self.player_height = 0.15
        self.player_vidas = 100  # Valor base para a barra de 100% no HUD