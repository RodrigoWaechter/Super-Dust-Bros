import os
from OpenGL.GL import *
from PIL import Image


def load_texture(path):

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 3. Une a raiz do projeto com o caminho do asset
    full_path = os.path.join(base_dir, path)

    try:
        # Tenta abrir a imagem usando o caminho absoluto construído[cite: 2]
        image = Image.open(full_path).convert("RGBA")
    except FileNotFoundError:
        print(f"\n[ERRO CRÍTICO] Não foi possível encontrar o arquivo em: {full_path}")
        print(f"Certifique-se de que a pasta 'assets' está em: {base_dir}")
        raise

    # Inverte a imagem (OpenGL espera que o 0,0 seja no canto inferior esquerdo)[cite: 2]
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image_data = image.tobytes("raw", "RGBA", 0, -1)

    width, height = image.size

    # Gera e configura a textura no OpenGL[cite: 2]
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    # Configurações de filtro (NEAREST para manter o estilo pixel art)[cite: 2]
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    # Configurações de repetição[cite: 2]
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    # Envia os dados para a GPU[cite: 2]
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

    glBindTexture(GL_TEXTURE_2D, 0)

    return texture, width, height