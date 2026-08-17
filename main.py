import pygame
import sys
import config

# Inicializa o pygame
pygame.init()

# Configura a janela
LARGURA, ALTURA = config.WIDTH, config.HEIGHT
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Overtime")

# Relógio para controlar FPS
clock = pygame.time.Clock()
FPS = config.FPS

# Loop principal
rodando = True
while rodando:
    # 1. Tratar eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    # 2. Atualizar lógica do jogo
    # (mover objetos, checar colisões, etc.)

    # 3. Desenhar na tela
    tela.fill((30, 30, 30))  # limpa a tela com uma cor de fundo
    # pygame.draw.rect(...), tela.blit(...), etc.

    # 4. Atualizar a tela
    pygame.display.flip()

    # 5. Controlar velocidade do loop
    clock.tick(FPS)

pygame.quit()
sys.exit() 
