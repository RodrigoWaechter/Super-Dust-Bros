class Settings:
    def __init__(self):
        # Janela
        self.window_width = 800
        self.window_height = 600
        self.window_title = "CS:GO 2D - OpenGL"

        # Física do Jogo
        self.gravity = -3.0          # Gravidade puxando para baixo
        self.jump_speed = 1.5        # Força do pulo
        self.move_speed = 1.2        # Velocidade de andar para os lados

        # Configurações Iniciais do Jogador (Terrorista)
        self.player_start_x = -0.8
        self.player_start_y = 0.0
        self.player_width = 0.1
        self.player_height = 0.15
        self.player_vidas = 3