"""
inimigo.py
Responsável pela lógica, movimentação e renderização dos inimigos (CTs) no jogo.
Gerencia o carregamento dinâmico de sprites, estados de animação e física básica.
"""

from src.entities.game_object import GameObject
from src.utils import load_texture
from OpenGL.GL import *

class Inimigo(GameObject):
    """
    Inimigo com comportamento padrão de patrulha.
    Possui sistema de gravidade, verificação de chão à frente e animação baseada em estado.
    """
    def __init__(self, x, y, width, height, settings, color=(1.0, 0.0, 0.0)):
        # Aplica uma escala para manter a coesão visual de altura com o protagonista
        escala_altura = 0.95
        super().__init__(x, y, width, settings.player_height * escala_altura, color)
        self.settings = settings

        self.vel_x = 0.0
        self.vel_y = 0.0
        self.no_chao = False
        self.velocidade = 0.5
        self.direcao = -1

        # Controle da Máquina de Estados de Animação
        self.estado = "idle"
        self.frame_atual = 0
        self.tempo_animacao = 0
        self.duracao_frame = 0.15

        # Offsets visuais para alinhar perfeitamente o sprite ao hitbox
        self.sprite_offset_x = 0.02
        self.sprite_offset_y = -0.01

        self.sprites_idle = []
        self.sprites_walk = []
        self.sprites_carregados = False

    def load_sprites(self):
        """Carrega e armazena em memória as texturas de animação do inimigo."""
        self.sprites_idle = [
            load_texture("assets/enemy/idle/ct-idle-1.jpg"),
            load_texture("assets/enemy/idle/ct-idle-2.jpg"),
        ]

        self.sprites_walk = [
            load_texture("assets/enemy/walk/ct-walk-1.jpg"),
            load_texture("assets/enemy/walk/ct-walk-2.jpg"),
            load_texture("assets/enemy/walk/ct-walk-3.jpg"),
            load_texture("assets/enemy/walk/ct-walk-4.jpg")
        ]
        self.sprites_carregados = True

    def update_estado(self):
        """Atualiza a string de estado visual de acordo com o vetor de velocidade X."""
        if self.vel_x != 0:
            self.estado = "walk"
        else:
            self.estado = "idle"

    def update_animacao(self, delta_time):
        """Avança o ciclo de frames baseado no tempo decorrido, iterando os sprites."""
        if not self.sprites_carregados:
            self.load_sprites()

        self.tempo_animacao += delta_time
        if self.tempo_animacao > self.duracao_frame:
            self.tempo_animacao = 0
            self.frame_atual += 1

            lista = self.sprites_walk if self.estado == "walk" else self.sprites_idle
            if len(lista) > 0:
                self.frame_atual %= len(lista)

    def get_sprite_atual(self):
        """Retorna os dados da textura do frame atual (ID, largura, altura)."""
        if not self.sprites_carregados:
            self.load_sprites()

        lista = self.sprites_walk if self.estado == "walk" else self.sprites_idle
        return lista[self.frame_atual]

    def draw(self, camera_x=0.0):
        """Renderiza o sprite mapeando as texturas no OpenGL e invertendo o eixo X conforme direção."""
        texture, tex_w, tex_h = self.get_sprite_atual()

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture)
        glColor3f(1.0, 1.0, 1.0)

        x = self.centro_x - camera_x + self.sprite_offset_x
        pe_y = self.centro_y - (self.height / 2)
        aspect = tex_w / tex_h
        h = self.height / 2
        w = h * aspect
        y = pe_y + h + self.sprite_offset_y

        glBegin(GL_QUADS)
        # Controle de espelhamento (flip horizontal) manipulando as coordenadas UV
        if self.direcao == 1:
            glTexCoord2f(0, 1); glVertex2f(x - w, y - h)
            glTexCoord2f(1, 1); glVertex2f(x + w, y - h)
            glTexCoord2f(1, 0); glVertex2f(x + w, y + h)
            glTexCoord2f(0, 0); glVertex2f(x - w, y + h)
        else:
            glTexCoord2f(1, 1); glVertex2f(x - w, y - h)
            glTexCoord2f(0, 1); glVertex2f(x + w, y - h)
            glTexCoord2f(0, 0); glVertex2f(x + w, y + h)
            glTexCoord2f(1, 0); glVertex2f(x - w, y + h)
        glEnd()
        glDisable(GL_TEXTURE_2D)

    def update_physics(self, delta_time):
        """Aplica gravidade e movimento, incluindo proteção contra atravessamento de colisão em lag spikes."""
        # Hard cap do delta_time para prevenir física instável (clipping) em quedas de FPS
        if delta_time > 0.1:
            delta_time = 0.016

        if not self.sprites_carregados:
            return

        self.vel_y += self.settings.gravity * delta_time

        if self.no_chao:
            self.vel_x = self.velocidade * self.direcao
        else:
            self.vel_x = 0

        self.centro_x += self.vel_x * delta_time
        self.centro_y += self.vel_y * delta_time

        self.update_estado()
        self.update_animacao(delta_time)

    def validar_chao(self, obstacles):
        """Analisa colisões logo à frente e abaixo da entidade para prever o fim de plataformas."""
        offset_x = (self.width / 2) * self.direcao
        check_x = self.centro_x + offset_x
        check_y = self.centro_y - (self.height / 2) - 0.02

        for obj in obstacles:
            if (obj.canto_inf_esq_x <= check_x <= obj.canto_inf_dir_x and
                    obj.canto_inf_esq_y <= check_y <= obj.canto_sup_esq_y):
                return True

        return False