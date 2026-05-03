import random

from src.entities.game_object import GameObject
from src.utils import load_texture
from OpenGL.GL import *

class power_ups(GameObject):
    """
    Representa a AK-47 que surge ao abrir uma caixa.
    - Gerencia a animação de spawn e a renderização da textura.
    """

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, (1.0, 1.0, 1.0))

        # movimentação do item
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.gravity = -2.5
        self.texture = None  # lazy loading

        # animação de spawn
        self.is_spawnning = True
        self.spawn_speed = 0.5
        # subir uma casa dps do spawn
        self.spawn_target_y = y + height

    def update(self, dt):
        if self.is_spawnning:
            self.centro_y += self.spawn_speed * dt
            if self.centro_y >= self.spawn_target_y:
                self.is_spawnning = False
                self.centro_y = self.spawn_target_y
        else:
            self.vel_y += self.gravity * dt
            self.centro_x += self.vel_x * dt
            self.centro_y += self.vel_y * dt

    def draw(self, camera_x=0.0):
        """Renderiza a imagem da AK-47."""
        if self.texture is None:
            # carrega a textura apenas uma vez
            self.texture = load_texture("assets/power_ups/power-up-ak.jpg")[0]

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glColor3f(1.0, 1.0, 1.0)

        escala = 1.15

        x = self.centro_x - camera_x
        y = self.centro_y
        half_w = (self.width / 2) * escala
        half_h = (self.height / 2) * escala

        glBegin(GL_QUADS)
        glTexCoord2f(0, 1)
        glVertex2f(x - half_w, y - half_h)
        glTexCoord2f(1, 1)
        glVertex2f(x + half_w, y - half_h)
        glTexCoord2f(1, 0)
        glVertex2f(x + half_w, y + half_h)
        glTexCoord2f(0, 0)
        glVertex2f(x - half_w, y + half_h)
        glEnd()
        glDisable(GL_TEXTURE_2D)

class ItemCura(GameObject):
    """
    Representa o Kit de Cura que surge ao abrir uma caixa.
    """

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, (1.0, 1.0, 1.0))

        self.vel_x = 0.0
        self.vel_y = 0.0
        self.gravity = -2.5
        self.texture = None

        self.is_spawnning = True
        self.spawn_speed = 0.5
        self.spawn_target_y = y + height
        self.no_chao = False

    def update(self, dt):
        if self.is_spawnning:
            self.centro_y += self.spawn_speed * dt
            if self.centro_y >= self.spawn_target_y:
                self.is_spawnning = False
                self.centro_y = self.spawn_target_y
        else:
            self.vel_y += self.gravity * dt
            self.centro_x += self.vel_x * dt
            self.centro_y += self.vel_y * dt

    def draw(self, camera_x=0.0):
        if self.texture is None:
            self.texture = load_texture("assets/power_ups/power-up-cura.png")[0]

        glEnable(GL_TEXTURE_2D)

        # Habilita suporte a fundo transparente (PNG)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glBindTexture(GL_TEXTURE_2D, self.texture)
        glColor3f(1.0, 1.0, 1.0)

        escala = 1.15

        x = self.centro_x - camera_x
        y = self.centro_y
        half_w = (self.width / 2) * escala
        half_h = (self.height / 2) * escala

        glBegin(GL_QUADS)
        glTexCoord2f(0, 1)
        glVertex2f(x - half_w, y - half_h)
        glTexCoord2f(1, 1)
        glVertex2f(x + half_w, y - half_h)
        glTexCoord2f(1, 0)
        glVertex2f(x + half_w, y + half_h)
        glTexCoord2f(0, 0)
        glVertex2f(x - half_w, y + half_h)
        glEnd()

        glDisable(GL_TEXTURE_2D)

class ItemGranada(GameObject):

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, (1.0, 1.0, 1.0))

        self.vel_x = 0.0
        self.vel_y = 0.0
        self.gravity = -2.5
        self.texture = None

        self.is_spawnning = True
        self.spawn_speed = 0.5
        self.spawn_target_y = y + height

    def update(self, dt):
        if self.is_spawnning:
            self.centro_y += self.spawn_speed * dt
            if self.centro_y >= self.spawn_target_y:
                self.is_spawnning = False
                self.centro_y = self.spawn_target_y
        else:
            self.vel_y += self.gravity * dt
            self.centro_x += self.vel_x * dt
            self.centro_y += self.vel_y * dt

    def draw(self, camera_x=0.0):
        if self.texture is None:
            self.texture = load_texture("assets/power_ups/power-up-he.png")[0]

        glEnable(GL_TEXTURE_2D)

        # Habilita suporte a fundo transparente (PNG)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glBindTexture(GL_TEXTURE_2D, self.texture)
        glColor3f(1.0, 1.0, 1.0)

        escala = 1.15

        x = self.centro_x - camera_x
        y = self.centro_y
        half_w = (self.width / 2) * escala
        half_h = (self.height / 2) * escala

        glBegin(GL_QUADS)
        glTexCoord2f(0, 1)
        glVertex2f(x - half_w, y - half_h)
        glTexCoord2f(1, 1)
        glVertex2f(x + half_w, y - half_h)
        glTexCoord2f(1, 0)
        glVertex2f(x + half_w, y + half_h)
        glTexCoord2f(0, 0)
        glVertex2f(x - half_w, y + half_h)
        glEnd()

        glDisable(GL_TEXTURE_2D)


class ItemMolotov(GameObject):
    """
    Representa a Molotov que surge ao abrir uma caixa.
    """

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, (1.0, 1.0, 1.0))

        self.vel_x = 0.0
        self.vel_y = 0.0
        self.gravity = -2.5
        self.texture = None

        self.is_spawnning = True
        self.spawn_speed = 0.5
        self.spawn_target_y = y + height

    def update(self, dt):
        if self.is_spawnning:
            self.centro_y += self.spawn_speed * dt
            if self.centro_y >= self.spawn_target_y:
                self.is_spawnning = False
                self.centro_y = self.spawn_target_y
        else:
            self.vel_y += self.gravity * dt
            self.centro_x += self.vel_x * dt
            self.centro_y += self.vel_y * dt

    def draw(self, camera_x=0.0):
        if self.texture is None:
            self.texture = load_texture("assets/power_ups/power-up-molotov.png")[0]

        glEnable(GL_TEXTURE_2D)

        # Habilita suporte a fundo transparente (PNG)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glBindTexture(GL_TEXTURE_2D, self.texture)
        glColor3f(1.0, 1.0, 1.0)

        escala = 1.15

        x = self.centro_x - camera_x
        y = self.centro_y
        half_w = (self.width / 2) * escala
        half_h = (self.height / 2) * escala

        glBegin(GL_QUADS)
        glTexCoord2f(0, 1)
        glVertex2f(x - half_w, y - half_h)
        glTexCoord2f(1, 1)
        glVertex2f(x + half_w, y - half_h)
        glTexCoord2f(1, 0)
        glVertex2f(x + half_w, y + half_h)
        glTexCoord2f(0, 0)
        glVertex2f(x - half_w, y + half_h)
        glEnd()

        glDisable(GL_TEXTURE_2D)


class blocoPowerUp(GameObject):

    def __init__(self, x, y, width, height):
        escala_horizontal = 2.2
        escala_vertical = 1.8
        super().__init__(x, y, width * escala_horizontal, height * escala_vertical, (0.8, 0.4, 0.0))

        self.foiAtingido = False

        self.tex_ativa = None
        self.tex_vazia = None
        self.texturas_carregadas = False

    def _load_assets(self):
        # carrega só quando for necessário
        self.tex_ativa = load_texture("assets/power_ups/power-up-padrao.jpg")
        self.tex_vazia = load_texture("assets/power_ups/power-up-atingido.jpg")
        self.texturas_carregadas = True

    def draw(self, camera_x=0.0):

        # verifica se as texturas já foram carregadas
        if not self.texturas_carregadas:
            self._load_assets()

        # extrai apenas o ID da textura
        texture_data = self.tex_vazia if self.foiAtingido else self.tex_ativa
        texture_id = texture_data[0]

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glColor3f(1.0, 1.0, 1.0)

        x = self.centro_x - camera_x
        y = self.centro_y
        half_w = self.width / 2
        half_h = self.height / 2

        glBegin(GL_QUADS)
        glTexCoord2f(0, 1)
        glVertex2f(x - half_w, y - half_h)
        glTexCoord2f(1, 1)
        glVertex2f(x + half_w, y - half_h)
        glTexCoord2f(1, 0)
        glVertex2f(x + half_w, y + half_h)
        glTexCoord2f(0, 0)
        glVertex2f(x - half_w, y + half_h)
        glEnd()
        glDisable(GL_TEXTURE_2D)

    def baterPorBaixo(self):
        if not self.foiAtingido:
            self.foiAtingido = True
            # Muda a cor do bloco para indicar que já foi usado
            self.color = (0.4, 0.4, 0.4)

            # Adicionamos a "CURA" na lista de possibilidades
            opcoes_de_itens = ["AK47", "GRANADA", "MOLOTOV", "CURA"]
            item_sorteado = random.choice(opcoes_de_itens)

            if item_sorteado == "GRANADA":
                return ItemGranada(self.centro_x, self.centro_y, self.width, self.height)
            elif item_sorteado == "MOLOTOV":
                return ItemMolotov(self.centro_x, self.centro_y, self.width, self.height)
            elif item_sorteado == "CURA":
                # AGORA CORRIGIDO: Passando a largura e altura do bloco para o item nascer proporcional
                return ItemCura(self.centro_x, self.centro_y, self.width, self.height)
            else:
                return power_ups(self.centro_x, self.centro_y, self.width, self.height)

        return None