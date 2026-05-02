from src.entities.personagem import Personagem
from src.entities.projetil import Projetil
from OpenGL.GL import *
from src.utils import load_texture

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
        self.tem_granada = False
        self.invulneravel_tempo = 0
        self.direcao = 1
        self.hitbox_width = self.width * 0.5
        self.hitbox_height = self.height * 0.75
        self.sprite_offset_y = -0.02
        self.sprite_offset_x = 0.02

        self.estado = "idle"
        self.frame_atual = 0
        self.tempo_animacao = 0
        self.duracao_frame = 0.15

    def load_sprites(self):

        self.sprites_idle = [
            load_texture("assets/player/idle/idle_0.png"),
            load_texture("assets/player/idle/idle_1.png")
        ]

        self.sprites_idle_arma = [
            load_texture("assets/player/idle/idle_gun_0.png"),
            load_texture("assets/player/idle/idle_gun_1.png")
        ]

        self.sprites_walk = [
            load_texture("assets/player/walk/walk_0.png"),
            load_texture("assets/player/walk/walk_1.png"),
            load_texture("assets/player/walk/walk_2.png"),
            load_texture("assets/player/walk/walk_3.png")
        ]

        self.sprites_walk_arma = [
            load_texture("assets/player/walk/walk_gun_0.png"),
            load_texture("assets/player/walk/walk_gun_1.png"),
            load_texture("assets/player/walk/walk_gun_2.png"),
            load_texture("assets/player/walk/walk_gun_3.png")
        ]

        self.sprites_jump = [
            load_texture("assets/player/jump/jump_0.png"),
            load_texture("assets/player/jump/jump_1.png"),
            load_texture("assets/player/jump/jump_2.png")
        ]

        self.sprites_jump_arma = [
            load_texture("assets/player/jump/jump_gun_0.png"),
            load_texture("assets/player/jump/jump_gun_1.png"),
            load_texture("assets/player/jump/jump_gun_2.png")
        ]

    def update_estado(self):
        estado_anterior = self.estado

        if not self.no_chao:
            self.estado = "jump"
        elif self.vel_x != 0:
            self.estado = "walk"
        else:
            self.estado = "idle"

        if self.estado != estado_anterior:
            self.frame_atual = 0
            self.tempo_animacao = 0

    def draw(self, camera_x=0.0):
        texture, tex_w, tex_h = self.get_sprite_atual()

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture)
        glColor3f(1.0, 1.0, 1.0)

        x = self.centro_x - camera_x + self.sprite_offset_x
        pe_y = self.centro_y - (self.hitbox_height / 2)

        aspect = tex_w / tex_h

        h = self.render_height / 2
        w = h * aspect

        y = pe_y + h + self.sprite_offset_y

        glBegin(GL_QUADS)

        if self.direcao == 1:
            glTexCoord2f(0, 1)
            glVertex2f(x - w, y - h)

            glTexCoord2f(1, 1)
            glVertex2f(x + w, y - h)

            glTexCoord2f(1, 0)
            glVertex2f(x + w, y + h)

            glTexCoord2f(0, 0)
            glVertex2f(x - w, y + h)
        else:
            glTexCoord2f(1, 1)
            glVertex2f(x - w, y - h)

            glTexCoord2f(0, 1)
            glVertex2f(x + w, y - h)

            glTexCoord2f(0, 0)
            glVertex2f(x + w, y + h)

            glTexCoord2f(1, 0)
            glVertex2f(x - w, y + h)

        glEnd()
        glDisable(GL_TEXTURE_2D)

    def jump(self):
        if self.no_chao:
            self.vel_y = self.settings.jump_speed
            self.no_chao = False

    def atirar(self):
        if not self.tem_item:
            return None

        direcao = self.direcao
        offset = (self.hitbox_width / 2) + 0.1
        spawn_x = self.centro_x + (offset * direcao)
        spawn_y = self.centro_y

        return Projetil(spawn_x, spawn_y, direcao, origem="player")

    def arremessar(self):
        # Só arremessa se tiver a granada
        if not getattr(self, 'tem_granada', False):
            return None

        # Consome a granada
        self.tem_granada = False
        print("Lançou a granada!")

        direcao = self.direcao

        # AUMENTAMOS o offset_x para nascer mais longe do corpo
        offset_x = (self.hitbox_width / 2) + 0.1

        spawn_x = self.centro_x + (offset_x * direcao)

        # AUMENTAMOS o spawn_y para nascer na altura da cabeça (evita bater no chão na hora)
        spawn_y = self.centro_y + 0.1

        from src.entities.projetil import GranadaAtiva
        return GranadaAtiva(spawn_x, spawn_y, direcao, origem="player")

    def tomar_dano(self, quantidade):
        if self.invulneravel_tempo <= 0:
            self.vidas -= quantidade
            self.invulneravel_tempo = 1.0

            if self.vidas <= 0:
                self.vidas = 0
                self.morrer()

    def reset_posicao(self):
        self.centro_x = self.settings.player_start_x
        self.centro_y = self.settings.player_start_y
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.tem_item = False
        self.tem_granada = False

    def morrer(self):
        pass

    def update_physics_y(self, dt):
        if not self.no_chao or self.vel_y > 0:
            self.vel_y += self.settings.gravity * dt

            if self.vel_y < -4.5:
                self.vel_y = -4.5

            self.centro_y += self.vel_y * dt
        else:
            self.vel_y = 0

    def update_animacao(self, delta_time):
        self.tempo_animacao += delta_time

        if self.tempo_animacao >= self.duracao_frame:
            self.tempo_animacao = 0
            self.frame_atual += 1

            if self.estado == "idle":
                lista = self.sprites_idle_arma if self.tem_item else self.sprites_idle
                self.frame_atual %= len(lista)

            elif self.estado == "walk":
                lista = self.sprites_walk_arma if self.tem_item else self.sprites_walk
                self.frame_atual %= len(lista)

            elif self.estado == "jump":
                self.frame_atual = 0

    def get_sprite_atual(self):
        if self.estado == "idle":
            if self.tem_item:
                return self.sprites_idle_arma[self.frame_atual]
            else:
                return self.sprites_idle[self.frame_atual]
        elif self.estado == "walk":
            if self.tem_item:
                return self.sprites_walk_arma[self.frame_atual]
            else:
                return self.sprites_walk[self.frame_atual]
        elif self.estado == "jump":
            if self.vel_y > 1:
                if self.tem_item:
                    return self.sprites_jump_arma[2]
                else:
                    return self.sprites_jump[2]
            elif self.vel_y <= 1 and self.vel_y >= 0:
                if self.tem_item:
                    return self.sprites_jump_arma[1]
                else:
                    return self.sprites_jump[1]
            elif self.vel_y < 0:
                if self.tem_item:
                    return self.sprites_jump_arma[0]
                else:
                    return self.sprites_jump[0]

