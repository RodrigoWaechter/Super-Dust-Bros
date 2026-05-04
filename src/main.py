"""
main.py
Ponto de entrada padronizado da aplicação.
Importa e despacha a classe core GameEngine.
"""
from src.engine import GameEngine

if __name__ == "__main__":
    game = GameEngine()
    game.run()