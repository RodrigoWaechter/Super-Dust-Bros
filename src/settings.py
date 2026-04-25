class Settings:
    def __init__(self):
        self.window_width = 800
        self.window_height = 600
        self.window_title = "Super UNISC Bros"

        self.gravity = -3.0
        self.jump_speed = 1.5
        self.move_speed = 1.2

        self.player_start_x = -0.9
        self.player_start_y = -0.5
        self.player_width = 0.1
        self.player_height = 0.15
        self.player_vidas = 100

        #mapa de teste
        self.levels = {
            "fase_teste": [
                "          P                                                                 ",
                "                                                                            ",
                "                                                                            ",
                "          I                                                                 ",
                "       CCCCCCC               TT     CCC     CCC            CCCC             ",
                "                    TT       TT                                             ",
                "                    TT   I   TT          S         TTT                      ",
                "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG             GGGGGGGGG",
            ]
        }