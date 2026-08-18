import pygame
import sys
import random
import os
import config
from src.objects.touro import Touro
from src.objects.plataforma import Platform
from src.objects.item import RedBullItem

def carregar_fundo():
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

def gerar_nivel():
    """Gera o grupo de plataformas e latinhas de Red Bull da base até o topo."""
    plataformas = pygame.sprite.Group()
    itens = pygame.sprite.Group()
    
    # 1. Plataforma Base
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

        # 30% de chance de spawnar uma latinha de Red Bull sobre a plataforma
        if random.random() < 0.20:
            item_x = plat.rect.centerx - 13
            item_y = plat.rect.top - 40
            itens.add(RedBullItem(item_x, item_y))

    # 3. Plataforma Final de Chegada
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

    # Fundo da barra
    fundo_rect = pygame.Rect(x, y, bar_width, bar_height)
    pygame.draw.rect(tela, config.ENERGY_BAR_BG, fundo_rect, border_radius=6)
    
    # Preenchimento
    if fill_width > 0:
        fill_rect = pygame.Rect(x, y, fill_width, bar_height)
        pygame.draw.rect(tela, cor_fill, fill_rect, border_radius=6)

    # Borda
    pygame.draw.rect(tela, (255, 255, 255), fundo_rect, width=2, border_radius=6)

    # Rótulo de texto
    txt_lbl = fonte.render(f"ENERGIA {int(pct * 100)}%", True, (255, 255, 255))
    tela.blit(txt_lbl, (x + bar_width // 2 - txt_lbl.get_width() // 2, y + 2))

def main():
    pygame.init()
    pygame.font.init()

    LARGURA, ALTURA = config.WIDTH, config.HEIGHT
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Overtime")

    clock = pygame.time.Clock()
    fonte = pygame.font.SysFont("Arial", 14, bold=True)
    fonte_grande = pygame.font.SysFont("Arial", 26, bold=True)

    fundo_img = carregar_fundo()
    bg_y_offset = 0.0

    # Instância do jogo
    touro = Touro(LARGURA // 2 - 32, ALTURA - 160)
    plataformas, itens = gerar_nivel()

    # Rastreamento de energia e estado do jogo
    energia = config.MAX_ENERGY
    tempo_jogo = 0.0
    altura_maxima_alcancada = 0
    venceu = False
    game_over = False
    motivo_game_over = ""

    # Botões Touch (Rodapé)
    btn_altura = 90
    btn_largura = LARGURA // 2
    btn_esquerda = pygame.Rect(0, ALTURA - btn_altura, btn_largura, btn_altura)
    btn_direita = pygame.Rect(btn_largura, ALTURA - btn_altura, btn_largura, btn_altura)

    tecla_esq_pressionada = False
    tecla_dir_pressionada = False
    touch_esq_pressionado = False
    touch_dir_pressionado = False

    rodando = True
    while rodando:
        dt = clock.tick(config.FPS) / 1000.0  # Tempo em segundos desde o último frame
        scroll = 0

        # 1. Tratar Eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_LEFT, pygame.K_a):
                    tecla_esq_pressionada = True
                elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                    tecla_dir_pressionada = True
                elif evento.key == pygame.K_r and (venceu or game_over):
                    # Reiniciar partida
                    touro = Touro(LARGURA // 2 - 32, ALTURA - 160)
                    plataformas, itens = gerar_nivel()
                    energia = config.MAX_ENERGY
                    tempo_jogo = 0.0
                    altura_maxima_alcancada = 0
                    bg_y_offset = 0.0
                    venceu = False
                    game_over = False

            elif evento.type == pygame.KEYUP:
                if evento.key in (pygame.K_LEFT, pygame.K_a):
                    tecla_esq_pressionada = False
                elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                    tecla_dir_pressionada = False

            elif evento.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                if hasattr(evento, 'pos'):
                    pos_x, pos_y = evento.pos
                else:
                    pos_x = int(evento.x * LARGURA)
                    pos_y = int(evento.y * ALTURA)

                if btn_esquerda.collidepoint(pos_x, pos_y):
                    touch_esq_pressionado = True
                elif btn_direita.collidepoint(pos_x, pos_y):
                    touch_dir_pressionado = True

            elif evento.type in (pygame.MOUSEBUTTONUP, pygame.FINGERUP):
                touch_esq_pressionado = False
                touch_dir_pressionado = False

        if not game_over and not venceu:
            tempo_jogo += dt

            # Consumo de Energia: Fica mais rápido quanto mais tempo passa
            taxa_consumo = config.INITIAL_DECAY_RATE + (tempo_jogo * config.DECAY_ACCELERATION)
            energia -= taxa_consumo * dt

            if energia <= 0:
                energia = 0
                game_over = True
                motivo_game_over = "Energia Esgotada!"

            # 2. Movimentação Horizontal
            mover_esq = tecla_esq_pressionada or touch_esq_pressionado
            mover_dir = tecla_dir_pressionada or touch_dir_pressionado

            if mover_esq and not mover_dir:
                touro.mover_esquerda()
            elif mover_dir and not mover_esq:
                touro.mover_direita()
            else:
                touro.parar_horizontal()

            # 3. Atualizar Touro
            touro.update()

            # 4. Câmera Vertical
            if touro.rect.y < ALTURA // 2:
                scroll = ALTURA // 2 - touro.rect.y
                touro.y += scroll
                touro.rect.y += scroll
                altura_maxima_alcancada += scroll
                bg_y_offset += scroll * 0.5

            # 5. Atualizar Plataformas e Itens
            plataformas.update(scroll)
            itens.update(scroll)

            # 6. Colisão com Plataformas
            if touro.vy > 0 and not touro.voando:
                for plat in plataformas:
                    if plat.rect.colliderect(touro.rect):
                        if touro.rect.bottom - touro.vy <= plat.rect.top + 10:
                            touro.rect.bottom = plat.rect.top
                            touro.y = float(touro.rect.y)
                            touro.quicar()

                            if plat.is_finish_line:
                                venceu = True
                            break

            # 7. Colisão com Latinhas de Red Bull
            coletados = pygame.sprite.spritecollide(touro, itens, True)
            for item in coletados:
                # Recarrega energia e ativa o voo de 1 segundo!
                energia = min(config.MAX_ENERGY, energia + config.ENERGY_REFILL)
                touro.ativar_voo()

            # 8. Checar Queda do Jogador
            if touro.rect.top > ALTURA:
                game_over = True
                motivo_game_over = "Você caiu!"

        # 9. Desenhar na Tela
        if fundo_img:
            h_fundo = fundo_img.get_height()
            pos_y = int(bg_y_offset % h_fundo) - h_fundo
            tela.blit(fundo_img, (0, pos_y))
            if pos_y + h_fundo < ALTURA:
                tela.blit(fundo_img, (0, pos_y + h_fundo))
        else:
            tela.fill(config.BG_COLOR)

        # Desenhar Plataformas, Itens e Touro
        plataformas.draw(tela)
        itens.draw(tela)
        touro.draw(tela)

        # Desenhar Botões Touch (Rodapé)
        superficie_btn = pygame.Surface((LARGURA, btn_altura), pygame.SRCALPHA)
        cor_esq = (255, 255, 255, 90) if touch_esq_pressionado else (255, 255, 255, 35)
        cor_dir = (255, 255, 255, 90) if touch_dir_pressionado else (255, 255, 255, 35)
        
        pygame.draw.rect(superficie_btn, cor_esq, (0, 0, btn_largura - 2, btn_altura), border_radius=10)
        pygame.draw.rect(superficie_btn, cor_dir, (btn_largura + 2, 0, btn_largura - 2, btn_altura), border_radius=10)
        tela.blit(superficie_btn, (0, ALTURA - btn_altura))

        txt_esq = fonte.render("◄ ESQUERDA", True, (255, 255, 255))
        txt_dir = fonte.render("DIREITA ►", True, (255, 255, 255))
        tela.blit(txt_esq, (btn_largura // 2 - txt_esq.get_width() // 2, ALTURA - btn_altura // 2 - 10))
        tela.blit(txt_dir, (btn_largura + btn_largura // 2 - txt_dir.get_width() // 2, ALTURA - btn_altura // 2 - 10))

        # HUD: Barra de Energia e Altura
        desenhar_barra_energia(tela, energia, config.MAX_ENERGY, fonte)
        
        txt_altura = fonte.render(f"Altura: {int(altura_maxima_alcancada // 10)}m", True, (255, 220, 100))
        tela.blit(txt_altura, (15, 45))

        # Indicador de Voo ativo
        if touro.voando:
            txt_voo = fonte.render("⚡ VOO RED BULL! ⚡", True, (0, 220, 255))
            tela.blit(txt_voo, (LARGURA // 2 - txt_voo.get_width() // 2, 45))

        # Tela de Game Over
        if game_over:
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            tela.blit(overlay, (0, 0))

            txt_go = fonte_grande.render("GAME OVER", True, (230, 40, 40))
            txt_sub = fonte.render(motivo_game_over, True, (255, 200, 200))
            txt_reiniciar = fonte.render("Pressione [R] para reiniciar", True, (255, 255, 255))
            
            tela.blit(txt_go, (LARGURA // 2 - txt_go.get_width() // 2, ALTURA // 3))
            tela.blit(txt_sub, (LARGURA // 2 - txt_sub.get_width() // 2, ALTURA // 3 + 40))
            tela.blit(txt_reiniciar, (LARGURA // 2 - txt_reiniciar.get_width() // 2, ALTURA // 3 + 75))

        # Tela de Vitória
        elif venceu:
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            tela.blit(overlay, (0, 0))

            txt_vitoria = fonte_grande.render("VOCÊ CHEGOU AO TOPO!", True, (255, 215, 0))
            txt_tempo = fonte.render(f"Tempo Final: {tempo_jogo:.2f}s", True, (255, 255, 255))
            txt_reiniciar = fonte.render("Pressione [R] para jogar novamente", True, (200, 220, 255))
            
            tela.blit(txt_vitoria, (LARGURA // 2 - txt_vitoria.get_width() // 2, ALTURA // 3))
            tela.blit(txt_tempo, (LARGURA // 2 - txt_tempo.get_width() // 2, ALTURA // 3 + 40))
            tela.blit(txt_reiniciar, (LARGURA // 2 - txt_reiniciar.get_width() // 2, ALTURA // 3 + 75))

        # 10. Atualizar Display
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
