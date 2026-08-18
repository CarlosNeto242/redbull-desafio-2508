import pygame
import random
import os
import config

# Carregamento seguro da imagem da plataforma
_platform_image = None

def _get_platform_image():
    global _platform_image
    if _platform_image is None:
        caminho = os.path.join("assets", "plataforma.png")
        try:
            _platform_image = pygame.image.load(caminho).convert_alpha()
        except Exception as e:
            print(f"Aviso: Não foi possível carregar imagem da plataforma ({caminho}): {e}")
            _platform_image = False
    return _platform_image


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width=config.PLATFORM_WIDTH, height=config.PLATFORM_HEIGHT, moving=False, is_finish_line=False):
        super().__init__()
        self.width = width
        self.height = height
        self.moving = moving
        self.is_finish_line = is_finish_line
        
        self.move_counter = random.randint(0, 50)
        self.direction = random.choice([-1, 1])
        self.speed = random.randint(1, 2)
        
        img_base = _get_platform_image()
        if img_base and img_base is not False:
            self.image = pygame.transform.smoothscale(img_base, (self.width, self.height))
            if is_finish_line:
                # Destaca a linha de chegada com uma tonalidade dourada/brilhante
                overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                overlay.fill((255, 215, 0, 80))
                self.image.blit(overlay, (0, 0))
        else:
            # Fallback visual caso a imagem não exista
            self.image = pygame.Surface((self.width, self.height))
            cor = (255, 215, 0) if is_finish_line else (50, 180, 80)
            self.image.fill(cor)

        self.rect = self.image.get_rect()
        self.rect.x = int(x)
        self.rect.y = int(y)

    def update(self, scroll=0):
        # Movimento horizontal se for plataforma móvel
        if self.moving:
            self.move_counter += 1
            self.rect.x += self.direction * self.speed

            # Inverte direção ao atingir bordas ou limite de contador
            if self.move_counter >= 100 or self.rect.left <= 0 or self.rect.right >= config.WIDTH:
                self.direction *= -1
                self.move_counter = 0

        # Atualiza a posição vertical com base no scroll da câmera
        self.rect.y += scroll

        # Se sair da tela por baixo (fora da visão da câmera), é removida do jogo
        if self.rect.top > config.HEIGHT + 50:
            self.kill()