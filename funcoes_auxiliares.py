"""
Funções auxiliares (helpers) do jogo Overtime.

Este módulo reúne funções reutilizáveis que não fazem parte do fluxo de
estados do jogo (main.py): carregamento de recursos, geração do nível e
funções de desenho de interface (fundo, HUD, barra de energia, texto,
botões, overlay). Mantê-las separadas do main.py segue o mesmo padrão
de coesão usado nos exemplos de referência (funcoes_auxiliares.py /
gerador.py importados por seus respectivos main.py).
"""

import os
import random

import pygame

import config
from src.objects.plataforma import Platform
from src.objects.item import RedBullItem


# ---------------------------------------------------------------------------
# Recursos (assets)
# ---------------------------------------------------------------------------
def carregar_fundo():
    """Carrega e redimensiona a imagem de fundo do jogo.

    Retorna None se o arquivo não existir ou não puder ser carregado,
    para que o chamador use uma cor sólida (config.BG_COLOR) como fallback.
    """
    caminho = os.path.join("assets", "fundo.png")
    try:
        fundo_img = pygame.image.load(caminho).convert()
        largura_fundo = config.WIDTH
        altura_fundo = int(fundo_img.get_height() * (config.WIDTH / fundo_img.get_width()))
        if altura_fundo < config.HEIGHT:
            altura_fundo = config.HEIGHT
        return pygame.transform.smoothscale(fundo_img, (largura_fundo, altura_fundo))
    except Exception as e:
        print(f"Aviso: Não foi possível carregar imagem de fundo ({caminho}): {e}")
        return None


# ---------------------------------------------------------------------------
# Geração do nível
# ---------------------------------------------------------------------------
def gerar_nivel():
    """Gera o grupo de plataformas e latinhas de Red Bull da base até o topo."""
    plataformas = pygame.sprite.Group()
    itens = pygame.sprite.Group()

    # 1. Plataforma base
    plataforma_base = Platform(
        x=config.WIDTH // 2 - config.PLATFORM_WIDTH // 2,
        y=config.HEIGHT - 60,
        width=config.PLATFORM_WIDTH + 40,
        moving=False
    )
    plataformas.add(plataforma_base)

    # 2. Gerar plataformas e itens subindo até a altura total
    y_atual = config.HEIGHT - 60
    altura_alvo = config.HEIGHT - config.LEVEL_HEIGHT

    while y_atual > altura_alvo:
        gap_y = random.randint(config.PLATFORM_MIN_GAP, config.PLATFORM_MAX_GAP)
        y_atual -= gap_y

        x_plat = random.randint(10, config.WIDTH - config.PLATFORM_WIDTH - 10)
        eh_movel = random.random() < 0.20

        plat = Platform(x=x_plat, y=y_atual, width=config.PLATFORM_WIDTH, moving=eh_movel)
        plataformas.add(plat)

        # 20% de chance de spawnar uma latinha de Red Bull sobre a plataforma
        if random.random() < 0.20:
            item_x = plat.rect.centerx - 13
            item_y = plat.rect.top - 40
            itens.add(RedBullItem(item_x, item_y))

    # 3. Plataforma final de chegada
    plataforma_chegada = Platform(
        x=config.WIDTH // 2 - 100,
        y=y_atual - 80,
        width=200,
        height=25,
        moving=False,
        is_finish_line=True
    )
    plataformas.add(plataforma_chegada)

    return plataformas, itens


# ---------------------------------------------------------------------------
# Interface: texto e botões genéricos
# ---------------------------------------------------------------------------
def texto(tela, fonte, conteudo, pos, cor):
    """Renderiza uma linha de texto na tela na posição indicada (canto sup. esq.)."""
    text_surface = fonte.render(str(conteudo), True, cor)
    tela.blit(text_surface, pos)


def desenha_botao(tela, texto_botao, pos, tamanho, cor, fonte, hover_color=None):
    """Desenha um botão interativo, centralizado em `pos`, e retorna seu rect.

    Reservado para telas futuras de menu (INIT/END), seguindo o mesmo
    padrão usado nos exemplos de referência.
    """
    rect = pygame.Rect(0, 0, *tamanho)
    rect.center = pos

    mouse_pos = pygame.mouse.get_pos()
    if hover_color and rect.collidepoint(mouse_pos):
        pygame.draw.rect(tela, hover_color, rect, border_radius=8)
    else:
        pygame.draw.rect(tela, cor, rect, border_radius=8)

    text_surface = fonte.render(texto_botao, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=rect.center)
    tela.blit(text_surface, text_rect)

    return rect


# ---------------------------------------------------------------------------
# Interface: cenário e HUD
# ---------------------------------------------------------------------------
def desenhar_fundo(tela, fundo_img, bg_y_offset, largura, altura):
    """Desenha o fundo do jogo com efeito de rolagem (parallax simples)."""
    if fundo_img:
        h_fundo = fundo_img.get_height()
        pos_y = int(bg_y_offset % h_fundo) - h_fundo
        tela.blit(fundo_img, (0, pos_y))
        if pos_y + h_fundo < altura:
            tela.blit(fundo_img, (0, pos_y + h_fundo))
    else:
        tela.fill(config.BG_COLOR)


def desenhar_barra_energia(tela, energia_atual, max_energia, fonte):
    """Desenha a barra de energia no topo da tela com cor dinâmica."""
    bar_width = 220
    bar_height = 20
    x = config.WIDTH // 2 - bar_width // 2
    y = 15

    pct = max(0.0, min(1.0, energia_atual / max_energia))
    fill_width = int(bar_width * pct)

    # Cor dinâmica: Azul -> Amarelo -> Vermelho conforme a energia cai
    if pct > 0.5:
        cor_fill = (0, 150, 255)
    elif pct > 0.25:
        cor_fill = (255, 190, 0)
    else:
        cor_fill = (230, 30, 30)

    fundo_rect = pygame.Rect(x, y, bar_width, bar_height)
    pygame.draw.rect(tela, config.ENERGY_BAR_BG, fundo_rect, border_radius=6)

    if fill_width > 0:
        fill_rect = pygame.Rect(x, y, fill_width, bar_height)
        pygame.draw.rect(tela, cor_fill, fill_rect, border_radius=6)

    pygame.draw.rect(tela, (255, 255, 255), fundo_rect, width=2, border_radius=6)

    txt_lbl = fonte.render(f"ENERGIA {int(pct * 100)}%", True, (255, 255, 255))
    tela.blit(txt_lbl, (x + bar_width // 2 - txt_lbl.get_width() // 2, y + 2))


def desenhar_hud(tela, fonte, energia, altura_maxima_alcancada, voando, largura):
    """Desenha a barra de energia, a altura alcançada e o indicador de voo ativo."""
    desenhar_barra_energia(tela, energia, config.MAX_ENERGY, fonte)

    texto(tela, fonte, f"Altura: {int(altura_maxima_alcancada // 10)}m", (15, 45), (255, 220, 100))

    if voando:
        txt_voo = fonte.render("⚡ VOO RED BULL! ⚡", True, (0, 220, 255))
        tela.blit(txt_voo, (largura // 2 - txt_voo.get_width() // 2, 45))


def desenhar_botoes_touch(tela, largura, altura, btn_altura, touch_esq, touch_dir, fonte):
    """Desenha os botões touch de esquerda/direita no rodapé e retorna seus rects."""
    btn_largura = largura // 2
    btn_esquerda = pygame.Rect(0, altura - btn_altura, btn_largura, btn_altura)
    btn_direita = pygame.Rect(btn_largura, altura - btn_altura, btn_largura, btn_altura)

    superficie_btn = pygame.Surface((largura, btn_altura), pygame.SRCALPHA)
    cor_esq = (255, 255, 255, 90) if touch_esq else (255, 255, 255, 35)
    cor_dir = (255, 255, 255, 90) if touch_dir else (255, 255, 255, 35)

    pygame.draw.rect(superficie_btn, cor_esq, (0, 0, btn_largura - 2, btn_altura), border_radius=10)
    pygame.draw.rect(superficie_btn, cor_dir, (btn_largura + 2, 0, btn_largura - 2, btn_altura), border_radius=10)
    tela.blit(superficie_btn, (0, altura - btn_altura))

    txt_esq = fonte.render("◄ ESQUERDA", True, (255, 255, 255))
    txt_dir = fonte.render("DIREITA ►", True, (255, 255, 255))
    tela.blit(txt_esq, (btn_largura // 2 - txt_esq.get_width() // 2, altura - btn_altura // 2 - 10))
    tela.blit(txt_dir, (btn_largura + btn_largura // 2 - txt_dir.get_width() // 2, altura - btn_altura // 2 - 10))

    return btn_esquerda, btn_direita


def desenhar_overlay(tela, largura, altura, alpha):
    """Desenha uma camada escura semitransparente sobre a tela (telas de fim de jogo)."""
    overlay = pygame.Surface((largura, altura), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, alpha))
    tela.blit(overlay, (0, 0))
