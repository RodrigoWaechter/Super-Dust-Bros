"""
utils.py
Concentra funções e métodos utilitários auxiliares que agem fora do escopo de entidades lógicas,
especialmente focados na ponte entre leitura de arquivos IO e a API do OpenGL.
"""
import os
from OpenGL.GL import *
from PIL import Image


def load_texture(path):
    """
    Carrega uma imagem física no disco, trata a conversão de canais e armazena
    diretamente na memória de vídeo (VRAM) formatando os dados via OpenGL.
    Retorna o Texture ID a ser utilizado pelo motor.
    """

    # Resolve dinamicamente o caminho absoluto garantindo portabilidade do script
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base_dir, path)

    try:
        # Tenta carregar e forçar conversão para ter o Alpha (RGBA), necessário para texturas vazadas
        image = Image.open(full_path).convert("RGBA")
    except FileNotFoundError:
        print(f"\n[ERRO CRÍTICO] Não foi possível encontrar o arquivo em: {full_path}")
        print(f"Certifique-se de que a pasta 'assets' está em: {base_dir}")
        raise

    # Como o sistema de coordenadas do OpenGL define o (0,0) no canto inferior esquerdo e o PIL
    # usa o (0,0) padrão web no topo esquerdo, devemos espelhar verticalmente antes de mapear.
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image_data = image.tobytes("raw", "RGBA", 0, -1)

    width, height = image.size

    # Gera um identificador único alocado na GPU
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    # GL_NEAREST instrui a GPU a não utilizar interpolação/blur no upscale visual
    # Isso preserva bordas duras, mantendo o estético "Pixel Art" nítido.
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    # Envia os arrays de bytes para a placa de vídeo
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

    glBindTexture(GL_TEXTURE_2D, 0)

    return texture, width, height