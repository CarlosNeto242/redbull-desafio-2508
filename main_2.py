# Bibliotecas
import sys

import pygame

import config
from src.objects.touro import Touro
from funcoes_auxiliares import (
    carregar_fundo,
    gerar_nivel,
    desenhar_fundo,
    desenhar_hud,
    desenhar_botoes_touch,
    desenhar_overlay,
)

# --- Estados do jogo (mesmo padrão dos exemplos de referência) ---
# INIT fica reservado para uma futura tela de menu; hoje o jogo começa
# direto em GAME, preservando o comportamento atual do programa.
INIT = 1
GAME = 2
END = 3
QUIT = 4


def inicializa():
    """Inicializa o pygame, a janela e os recursos globais (fonte, clock, fundo)."""
    pygame.init()
    pygame.font.init()

    tela = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption("Overtime")

    recursos = {
        'clock': pygame.time.Clock(),
        'fonte': pygame.font.SysFont("Arial", 14, bold=True),
        'fonte_grande': pygame.font.SysFont("Arial", 26, bold=True),
        'fundo_img': carregar_fundo(),
    }

    return tela, recursos


def novo_jogo():
    """Cria o estado de uma nova partida (touro, nível, energia, pontuação de altura)."""
    touro = Touro(config.WIDTH // 2 - 32, config.HEIGHT - 160)
    plataformas, itens = gerar_nivel()

    return {
        'touro': touro,
        'plataformas': plataformas,
        'itens': itens,
        'energia': config.MAX_ENERGY,
        'tempo_jogo': 0.0,
        'altura_maxima_alcancada': 0,
        'bg_y_offset': 0.0,
        'venceu': False,
        'game_over': False,
        'motivo_game_over': "",
    }


def novo_input():
    """Cria o estado de entrada (teclado/touch). Não é reiniciado ao reiniciar a partida,
    para não 'perder' uma tecla que o jogador ainda esteja segurando — mesmo
    comportamento do programa original."""
    return {
        'tecla_esq_pressionada': False,
        'tecla_dir_pressionada': False,
        'touch_esq_pressionado': False,
        'touch_dir_pressionado': False,
    }


def trata_eventos(entrada, btn_esquerda, btn_direita):
    """Processa a fila de eventos do pygame e atualiza as flags de `entrada`.

    Retorna False se o jogador fechou a janela, True caso contrário.
    """
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            return False

        elif evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_LEFT, pygame.K_a):
                entrada['tecla_esq_pressionada'] = True
            elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                entrada['tecla_dir_pressionada'] = True

        elif evento.type == pygame.KEYUP:
            if evento.key in (pygame.K_LEFT, pygame.K_a):
                entrada['tecla_esq_pressionada'] = False
            elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                entrada['tecla_dir_pressionada'] = False

        elif evento.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            if hasattr(evento, 'pos'):
                pos_x, pos_y = evento.pos
            else:
                pos_x = int(evento.x * config.WIDTH)
                pos_y = int(evento.y * config.HEIGHT)

            if btn_esquerda.collidepoint(pos_x, pos_y):
                entrada['touch_esq_pressionado'] = True
            elif btn_direita.collidepoint(pos_x, pos_y):
                entrada['touch_dir_pressionado'] = True

        elif evento.type in (pygame.MOUSEBUTTONUP, pygame.FINGERUP):
            entrada['touch_esq_pressionado'] = False
            entrada['touch_dir_pressionado'] = False

    return True


def atualiza_fisica(estado, entrada, dt):
    """Atualiza energia, movimentação, câmera e colisões de um frame de jogo."""
    touro = estado['touro']

    estado['tempo_jogo'] += dt

    # Consumo de energia: fica mais rápido quanto mais tempo passa
    taxa_consumo = config.INITIAL_DECAY_RATE + (estado['tempo_jogo'] * config.DECAY_ACCELERATION)
    estado['energia'] -= taxa_consumo * dt

    if estado['energia'] <= 0:
        estado['energia'] = 0
        estado['game_over'] = True
        estado['motivo_game_over'] = "Energia Esgotada!"

    # Movimentação horizontal
    mover_esq = entrada['tecla_esq_pressionada'] or entrada['touch_esq_pressionado']
    mover_dir = entrada['tecla_dir_pressionada'] or entrada['touch_dir_pressionado']

    if mover_esq and not mover_dir:
        touro.mover_esquerda()
    elif mover_dir and not mover_esq:
        touro.mover_direita()
    else:
        touro.parar_horizontal()

    touro.update()

    # Câmera vertical
    scroll = 0
    if touro.rect.y < config.HEIGHT // 2:
        scroll = config.HEIGHT // 2 - touro.rect.y
        touro.y += scroll
        touro.rect.y += scroll
        estado['altura_maxima_alcancada'] += scroll
        estado['bg_y_offset'] += scroll * 0.5

    estado['plataformas'].update(scroll)
    estado['itens'].update(scroll)

    # Colisão com plataformas
    if touro.vy > 0 and not touro.voando:
        for plat in estado['plataformas']:
            if plat.rect.colliderect(touro.rect):
                if touro.rect.bottom - touro.vy <= plat.rect.top + 10:
                    touro.rect.bottom = plat.rect.top
                    touro.y = float(touro.rect.y)
                    touro.quicar()

                    if plat.is_finish_line:
                        estado['venceu'] = True
                    break

    # Colisão com latinhas de Red Bull
    coletados = pygame.sprite.spritecollide(touro, estado['itens'], True)
    for _ in coletados:
        estado['energia'] = min(config.MAX_ENERGY, estado['energia'] + config.ENERGY_REFILL)
        touro.ativar_voo()

    # Queda do jogador
    if touro.rect.top > config.HEIGHT:
        estado['game_over'] = True
        estado['motivo_game_over'] = "Você caiu!"


def desenha_jogo(tela, estado, entrada, recursos, btn_altura):
    """Desenha o cenário, as entidades, os botões touch e o HUD de um frame."""
    desenhar_fundo(tela, recursos['fundo_img'], estado['bg_y_offset'], config.WIDTH, config.HEIGHT)

    estado['plataformas'].draw(tela)
    estado['itens'].draw(tela)
    estado['touro'].draw(tela)

    desenhar_botoes_touch(
        tela, config.WIDTH, config.HEIGHT, btn_altura,
        entrada['touch_esq_pressionado'], entrada['touch_dir_pressionado'],
        recursos['fonte']
    )

    desenhar_hud(
        tela, recursos['fonte'], estado['energia'],
        estado['altura_maxima_alcancada'], estado['touro'].voando, config.WIDTH
    )


def game_loop(tela, recursos, estado, entrada):
    """Executa a partida enquanto ela estiver em andamento.

    Retorna (proximo_estado_da_maquina, estado_do_jogo) quando a partida
    termina por derrota, vitória ou fechamento da janela.
    """
    btn_altura = 90
    btn_largura = config.WIDTH // 2
    btn_esquerda = pygame.Rect(0, config.HEIGHT - btn_altura, btn_largura, btn_altura)
    btn_direita = pygame.Rect(btn_largura, config.HEIGHT - btn_altura, btn_largura, btn_altura)

    while not estado['game_over'] and not estado['venceu']:
        dt = recursos['clock'].tick(config.FPS) / 1000.0

        if not trata_eventos(entrada, btn_esquerda, btn_direita):
            return QUIT, estado

        atualiza_fisica(estado, entrada, dt)
        desenha_jogo(tela, estado, entrada, recursos, btn_altura)
        pygame.display.flip()

    return END, estado


def end_screen(tela, recursos, estado, entrada):
    """Mostra a tela de fim de jogo (derrota ou vitória) sobre o último frame da partida.

    Pressionar [R] inicia uma nova partida; fechar a janela encerra o jogo.
    """
    btn_altura = 90

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return QUIT, estado
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
                return GAME, novo_jogo()

        desenha_jogo(tela, estado, entrada, recursos, btn_altura)

        alpha = 160 if estado['game_over'] else 140
        desenhar_overlay(tela, config.WIDTH, config.HEIGHT, alpha)

        if estado['game_over']:
            titulo, cor_titulo = "GAME OVER", (230, 40, 40)
            linha2, cor2 = estado['motivo_game_over'], (255, 200, 200)
            linha3, cor3 = "Pressione [R] para reiniciar", (255, 255, 255)
        else:
            titulo, cor_titulo = "VOCÊ CHEGOU AO TOPO!", (255, 215, 0)
            linha2, cor2 = f"Tempo Final: {estado['tempo_jogo']:.2f}s", (255, 255, 255)
            linha3, cor3 = "Pressione [R] para jogar novamente", (200, 220, 255)

        txt_titulo = recursos['fonte_grande'].render(titulo, True, cor_titulo)
        txt_linha2 = recursos['fonte'].render(linha2, True, cor2)
        txt_linha3 = recursos['fonte'].render(linha3, True, cor3)

        tela.blit(txt_titulo, (config.WIDTH // 2 - txt_titulo.get_width() // 2, config.HEIGHT // 3))
        tela.blit(txt_linha2, (config.WIDTH // 2 - txt_linha2.get_width() // 2, config.HEIGHT // 3 + 40))
        tela.blit(txt_linha3, (config.WIDTH // 2 - txt_linha3.get_width() // 2, config.HEIGHT // 3 + 75))

        pygame.display.flip()


def main():
    tela, recursos = inicializa()
    estado = novo_jogo()
    entrada = novo_input()
    state = GAME

    while state != QUIT:
        if state == GAME:
            state, estado = game_loop(tela, recursos, estado, entrada)
        elif state == END:
            state, estado = end_screen(tela, recursos, estado, entrada)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
