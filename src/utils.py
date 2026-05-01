from OpenGL.GL import *
from PIL import Image

def load_texture(path):
    image = Image.open(path).convert("RGBA")

    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image_data = image.tobytes("raw", "RGBA", 0, -1)

    width, height = image.size

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

    glBindTexture(GL_TEXTURE_2D, 0)

    return texture, width, height