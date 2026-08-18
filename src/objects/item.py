import pygame
import os
import config

_latinha_image = None

def _get_latinha_image():
    global _latinha_image
    if _latinha_image is None:
        caminho = os.path.join("assets", "latinhas", "latinha-azul.png")
        try:
            _latinha_image = pygame.image.load(caminho).convert_alpha()
        except Exception as e:
            print(f"Aviso: Não foi possível carregar imagem da latinha ({caminho}): {e}")
            _latinha_image = False
    return _latinha_image


class RedBullItem(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.largura = 26
        self.altura = 40
        
        img_base = _get_latinha_image()
        if img_base and img_base is not False:
            self.image = pygame.transform.scale(img_base, (self.largura, self.altura))
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
