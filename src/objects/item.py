from numpy.lib import _polynomial_impl
import pygame
import os
import config
import random

_latinha_image = None

def _get_latinha_image():
    caminho_imagem = os.path.join("assets", "latinhas", f"lata-{random.randint(1, 3)}.png")
    _latinha_image = pygame.image.load(caminho_imagem).convert_alpha()
    return _latinha_image


class RedBullItem(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.largura = 26
        self.altura = 40
        
        img_base = _get_latinha_image()
        if img_base and img_base is not False:
            self.image = pygame.transform.smoothscale(img_base, (self.largura, self.altura))
        else:
            # Fallback visual (retângulo azul com texto)
            self.image = pygame.Surface((self.largura, self.altura))
            self.image.fill((0, 102, 204))
            pygame.draw.rect(self.image, (255, 255, 255), (3, 3, self.largura - 6, self.altura - 6), 2)

        self.rect = self.image.get_rect()
        self.rect.x = int(x)
        self.rect.y = int(y)

    def update(self, scroll=0):
        # Atualiza a posição com o scroll da câmera
        self.rect.y += scroll

        # Se sair da tela por baixo, remove o item
        if self.rect.top > config.HEIGHT + 50:
            self.kill()
