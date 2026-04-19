from src.entities.game_object import GameObject

class Obstaculo(GameObject):
    def __init__(self, x, y, width, height, color=(0.4, 0.2, 0.0)):
        super().__init__(x, y, width, height, color)