class Settings:
    def __init__(self):
        # Configurações da Janela
        self.window_width = 800
        self.window_height = 600
        self.window_title = "Super UNISC Bros"

        # Física do Jogo
        self.gravity = -3.0
        self.jump_speed = 1.5
        self.move_speed = 1.2

        # Configurações Iniciais do Jogador
        self.player_start_x = -0.9
        self.player_start_y = -0.5
        self.player_width = 0.08  
        self.player_height = 0.10  #Altura do Mario (Mario pequeno)
        self.player_vidas = 3

        # Dicionário de Fases
        self.levels = {
            "fase_teste": "levels/level_1_1.txt"
        }