from OpenGL.GL import *

class GameObject:
    def __init__(self, x, y, width, height, color):
        self.centro_x = x
        self.centro_y = y
        self.width = width
        self.height = height
        self.color = color

    # Propriedades para cálculo de bordas e colisões
    @property
    def canto_inf_esq_x(self): return self.centro_x - self.width / 2
    @property
    def canto_inf_esq_y(self): return self.centro_y - self.height / 2
    @property
    def canto_inf_dir_x(self): return self.centro_x + self.width / 2
    @property
    def canto_inf_dir_y(self): return self.centro_y - self.height / 2
    @property
    def canto_sup_dir_x(self): return self.centro_x + self.width / 2
    @property
    def canto_sup_dir_y(self): return self.centro_y + self.height / 2
    @property
    def canto_sup_esq_x(self): return self.centro_x - self.width / 2
    @property
    def canto_sup_esq_y(self): return self.centro_y + self.height / 2

    def check_collision(self, other):
        return (self.canto_inf_esq_x < other.canto_inf_dir_x and
                self.canto_inf_dir_x > other.canto_inf_esq_x and
                self.canto_inf_esq_y < other.canto_sup_esq_y and
                self.canto_sup_esq_y > other.canto_inf_esq_y)

    def draw(self, camera_x=0.0):
        glBegin(GL_QUADS)
        glColor3f(self.color[0], self.color[1], self.color[2])
        glVertex2f(self.canto_inf_esq_x - camera_x, self.canto_inf_esq_y)
        glVertex2f(self.canto_inf_dir_x - camera_x, self.canto_inf_dir_y)
        glVertex2f(self.canto_sup_dir_x - camera_x, self.canto_sup_dir_y)
        glVertex2f(self.canto_sup_esq_x - camera_x, self.canto_sup_esq_y)
        glEnd()