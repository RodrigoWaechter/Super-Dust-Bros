from OpenGL.GL import *


class GameObject:
    """
    Classe base para todas as entidades e blocos renderizáveis do jogo.
    Gerencia dados dimensionais, de posicionamento e detecção de colisões via AABB.
    """

    def __init__(self, x, y, width, height, color):
        self.centro_x = x
        self.centro_y = y
        self.width = width
        self.height = height
        self.color = color

        # Separação entre dimensões lógicas (física) e visuais (render)
        self.hitbox_width = width
        self.hitbox_height = height
        self.render_width = width
        self.render_height = height

    # Propriedades auxiliares para extração rápida dos limites da Bounding Box (AABB)
    @property
    def canto_inf_esq_x(self): return self.centro_x - self.hitbox_width / 2

    @property
    def canto_inf_esq_y(self): return self.centro_y - self.hitbox_height / 2

    @property
    def canto_inf_dir_x(self): return self.centro_x + self.hitbox_width / 2

    @property
    def canto_inf_dir_y(self): return self.centro_y - self.hitbox_height / 2

    @property
    def canto_sup_dir_x(self): return self.centro_x + self.hitbox_width / 2

    @property
    def canto_sup_dir_y(self): return self.centro_y + self.hitbox_height / 2

    @property
    def canto_sup_esq_x(self): return self.centro_x - self.hitbox_width / 2

    @property
    def canto_sup_esq_y(self): return self.centro_y + self.hitbox_height / 2

    def check_collision(self, other):
        """
        Calcula colisão AABB (Axis-Aligned Bounding Box) com outro GameObject.
        Retorna True se houver sobreposição espacial nos eixos X e Y.
        """
        return (self.canto_inf_esq_x < other.canto_inf_dir_x and
                self.canto_inf_dir_x > other.canto_inf_esq_x and
                self.canto_inf_esq_y < other.canto_sup_esq_y and
                self.canto_sup_esq_y > other.canto_inf_esq_y)

    def draw(self, camera_x=0.0):
        """
        Renderização base de um quadrado sólido utilizando a cor da entidade,
        aplicando o offset de translação da câmera do jogo.
        """
        glBegin(GL_QUADS)
        glColor3f(self.color[0], self.color[1], self.color[2])
        glVertex2f(self.canto_inf_esq_x - camera_x, self.canto_inf_esq_y)
        glVertex2f(self.canto_inf_dir_x - camera_x, self.canto_inf_dir_y)
        glVertex2f(self.canto_sup_dir_x - camera_x, self.canto_sup_dir_y)
        glVertex2f(self.canto_sup_esq_x - camera_x, self.canto_sup_esq_y)
        glEnd()