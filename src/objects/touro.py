import pygame
import os
import config

class Touro:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        
        # Dimensões para exibição no jogo
        self.largura = 64
        self.altura = 64
        
        self.olhando_direita = True
        
        # Animação normal de pulo (4 frames)
        self.frames_direita = []
        self.frames_esquerda = []
        self.frame_index = 0.0
        self.frame_speed = 0.1  # Velocidade da troca de frames
        
        # Sprites de Voo (Red Bull Power-up)
        self.sprite_voando_direita = None
        self.sprite_voando_esquerda = None
        self.voando = False
        self.tempo_voo_restante = 0.0
        
        self._carregar_sprites()
        
        # Hitbox (rect para colisão e desenho)
        self.rect = pygame.Rect(int(self.x), int(self.y), self.largura, self.altura)

    def _carregar_sprites(self):
        caminho_base = os.path.join("assets", "tourinho")
        try:
            # Carrega os 4 frames de pulo
            for i in range(1, 4):
                img_dir = pygame.image.load(os.path.join(caminho_base, f"pulando{i}-direita.png")).convert_alpha()
                img_esq = pygame.image.load(os.path.join(caminho_base, f"pulando{i}-esquerda.png")).convert_alpha()
                
                self.frames_direita.append(pygame.transform.scale(img_dir, (self.largura, self.altura)))
                self.frames_esquerda.append(pygame.transform.scale(img_esq, (self.largura, self.altura)))

            # Carrega sprites de voo
            v_dir = pygame.image.load(os.path.join(caminho_base, "voando-direita.png")).convert_alpha()
            v_esq = pygame.image.load(os.path.join(caminho_base, "voando-esquerda.png")).convert_alpha()
            
            self.sprite_voando_direita = pygame.transform.scale(v_dir, (self.largura, self.altura))
            self.sprite_voando_esquerda = pygame.transform.scale(v_esq, (self.largura, self.altura))
        except Exception as e:
            print(f"Aviso: Não foi possível carregar animações do touro ({e})")
            self.frames_direita = []
            self.frames_esquerda = []

    def mover_esquerda(self):
        self.vx = -config.MOVE_SPEED
        self.olhando_direita = False

    def mover_direita(self):
        self.vx = config.MOVE_SPEED
        self.olhando_direita = True

    def parar_horizontal(self):
        self.vx = 0.0

    def quicar(self):
        """Faz o touro pulando para cima ao tocar em uma superfície válida."""
        if not self.voando:
            self.vy = config.JUMP_FORCE
            self.frame_index = 0.0

    def ativar_voo(self):
        """Ativa o modo de voo/dash por 1 segundo."""
        self.voando = True
        self.tempo_voo_restante = config.FLY_DURATION

    def update(self):
        if self.voando:
            # Impulso constante para cima durante o voo
            self.vy = config.FLY_SPEED
            self.tempo_voo_restante -= 1.0 / config.FPS
            if self.tempo_voo_restante <= 0:
                self.voando = False
                self.tempo_voo_restante = 0.0
        else:
            # Gravidade normal
            self.vy += config.GRAVITY

        # Atualiza posições
        self.x += self.vx
        self.y += self.vy
        
        # Limites estritos nas bordas laterais
        if self.x < 0:
            self.x = 0
        elif self.x > config.WIDTH - self.largura:
            self.x = config.WIDTH - self.largura

        # Atualiza a rect
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Atualiza o ciclo de animação
        if self.frames_direita and self.frames_esquerda:
            self.frame_index += self.frame_speed
            if self.frame_index >= len(self.frames_direita):
                self.frame_index = 0.0

    def draw(self, tela):
        if self.voando and self.sprite_voando_direita and self.sprite_voando_esquerda:
            sprite = self.sprite_voando_direita if self.olhando_direita else self.sprite_voando_esquerda
            tela.blit(sprite, (self.rect.x, self.rect.y))
        else:
            idx = int(self.frame_index)
            if self.olhando_direita and self.frames_direita:
                tela.blit(self.frames_direita[idx % len(self.frames_direita)], (self.rect.x, self.rect.y))
            elif not self.olhando_direita and self.frames_esquerda:
                tela.blit(self.frames_esquerda[idx % len(self.frames_esquerda)], (self.rect.x, self.rect.y))
            else:
                # Fallback visual
                pygame.draw.rect(tela, (220, 20, 60), self.rect, border_radius=8)
                olho_x = self.rect.x + (45 if self.olhando_direita else 10)
                pygame.draw.circle(tela, (255, 255, 255), (olho_x, self.rect.y + 20), 6)
