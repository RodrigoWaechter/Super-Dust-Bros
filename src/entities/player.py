from src.entities.personagem import Personagem
from src.entities.projetil import Projetil
from OpenGL.GL import *
from src.utils import load_texture


class Player(Personagem):
    """
    Controlador principal do jogador. Implementa máquina de estados para animações,
    sistema de inventário ativo, tratamento de dano com i-frames e limites de colisão específicos.
    """

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

        # Sistema de inventário consumível
        self.tem_arremessavel = False
        self.tipo_arremessavel = None

        self.invulneravel_tempo = 0
        self.direcao = 1

        # Override de hitboxes para garantir que a colisão seja mais permissiva que a área renderizada
        self.hitbox_width = self.width * 0.5
        self.hitbox_height = self.height * 0.75
        self.sprite_offset_y = -0.02
        self.sprite_offset_x = 0.02

        # Controle da Máquina de Estados
        self.estado = "idle"
        self.frame_atual = 0
        self.tempo_animacao = 0
        self.duracao_frame = 0.15

    def load_sprites(self):
        """Carrega e armazena múltiplas listas de animação para diferentes estados e equipamentos."""
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
        """Mapeia os dados da física atual para string de estados de animação."""
        estado_anterior = self.estado

        if not self.no_chao:
            self.estado = "jump"
        elif self.vel_x != 0:
            self.estado = "walk"
        else:
            self.estado = "idle"

        # Previne dessincronia no playback ao alterar estados de forma abrupta
        if self.estado != estado_anterior:
            self.frame_atual = 0
            self.tempo_animacao = 0

    def draw(self, camera_x=0.0):
        texture, tex_w, tex_h = self.get_sprite_atual()

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture)

        # Lógica de piscar em vermelho ao tomar dano
        if self.invulneravel_tempo > 0:
            # O cálculo (tempo * 15) % 2 cria um efeito rápido de "pisca-pisca"
            if int(self.invulneravel_tempo * 15) % 2 == 0:
                glColor3f(1.0, 0.0, 0.0)  # Fica Vermelho
            else:
                glColor3f(1.0, 1.0, 1.0)  # Fica Normal
        else:
            glColor3f(1.0, 1.0, 1.0)  # Normal (100% da cor original da textura)

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
        """Injeta aceleração vertical instantânea, quebrando o estado estático de chão."""
        if self.no_chao:
            self.vel_y = self.settings.jump_speed
            self.no_chao = False

    def atirar(self):
        """Produz e retorna uma instância de projétil caso o equipamento de tiro esteja ativado."""
        if not self.tem_item:
            return None

        direcao = self.direcao
        offset = (self.hitbox_width / 2) + 0.1
        spawn_x = self.centro_x + (offset * direcao)
        spawn_y = self.centro_y

        return Projetil(spawn_x, spawn_y, direcao, origem="player")

    def arremessar(self):
        """Consome o item do inventário secundário e instancia uma entidade balística correspondente."""
        if not self.tem_arremessavel:
            return None

        tipo = self.tipo_arremessavel

        # Esvazia o inventário
        self.tem_arremessavel = False
        self.tipo_arremessavel = None

        print(f"Lançou a {tipo}!")

        direcao = self.direcao

        # Offsets ajustados para evitar colisão imediata no nascimento da entidade
        offset_x = (self.hitbox_width / 2) + 0.1
        spawn_x = self.centro_x + (offset_x * direcao)
        spawn_y = self.centro_y + 0.1

        if tipo == "GRANADA":
            from src.entities.projetil import GranadaAtiva
            return GranadaAtiva(spawn_x, spawn_y, direcao, origem="player")
        elif tipo == "MOLOTOV":
            from src.entities.projetil import MolotovAtiva
            return MolotovAtiva(spawn_x, spawn_y, direcao, origem="player")

        return None

    def tomar_dano(self, quantidade):
        """Diminui a vida aplicando um tempo de invulnerabilidade (I-frames)."""
        if self.invulneravel_tempo <= 0:
            self.vidas -= quantidade
            self.invulneravel_tempo = 1.0

            if self.vidas <= 0:
                self.vidas = 0
                print(f"Vida atual: {self.vidas}")
                self.morrer()

    def reset_posicao(self):
        """Reverte o player ao estado inicial, limpando atributos físicos e de equipamentos."""
        self.centro_x = self.settings.player_start_x
        self.centro_y = self.settings.player_start_y
        self.vel_x = 0.0
        self.vel_y = 0.0

        self.tem_item = False
        self.tem_arremessavel = False
        self.tipo_arremessavel = None

    def morrer(self):
        pass

    def update_physics_y(self, dt):
        """Lida com a física de eixo Y aplicando limites rígidos na velocidade de queda."""
        if not self.no_chao or self.vel_y > 0:
            self.vel_y += self.settings.gravity * dt

            # Terminal velocity de proteção (Limite de queda livre)
            if self.vel_y < -4.5:
                self.vel_y = -4.5

            self.centro_y += self.vel_y * dt
        else:
            self.vel_y = 0

    def update_animacao(self, delta_time):
        """Gerencia os loops de frames com base no estado e condições do inventário."""
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
        """
        Retorna o sprite específico levando em conta o estado atual e a física (como diferentes frames
        para ascensão, ápice e queda no pulo).
        """
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