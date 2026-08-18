import pygame
import sys
import random
import os
import config
from src.objects.touro import Touro
from src.objects.plataforma import Platform
from src.objects.item import RedBullItem
from src.utils.leaderboard import salvar_tempo, carregar_top_ranking

# Estados do Jogo
ESTADO_NOME = 0
ESTADO_JOGANDO = 1
ESTADO_GAMEOVER = 2
ESTADO_VITORIA = 3

def carregar_fundo():
    caminho = os.path.join("assets", "fundo-espacial.png")
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

def carregar_tela_inicial():
    """Carrega a arte pixelada da tela inicial."""
    caminho = os.path.join("assets", "tela-inicial.png")
    try:
        imagem = pygame.image.load(caminho).convert()
        return imagem
    except Exception as e:
        print(f"Aviso: Não foi possível carregar a tela inicial ({caminho}): {e}")
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

        # 20% de chance de spawnar uma latinha de Red Bull sobre a plataforma
        if random.random() < 0.20:
            item_x = plat.rect.centerx - 13
            item_y = plat.rect.top - 40
            itens.add(RedBullItem(item_x, item_y))

    # 3. Plataforma Final de Chegada (Finish Line)
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
    """Desenha a barra de energia no topo da tela."""
    bar_width = 180
    bar_height = 18
    x = config.WIDTH // 2 - bar_width // 2
    y = 12

    pct = max(0.0, min(1.0, energia_atual / max_energia))
    fill_width = int(bar_width * pct)

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
    tela.blit(txt_lbl, (x + bar_width // 2 - txt_lbl.get_width() // 2, y + 1))

def main():
    pygame.init()
    pygame.font.init()

    LARGURA, ALTURA = config.WIDTH, config.HEIGHT
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Overtime")

    clock = pygame.time.Clock()
    fonte_pequena = pygame.font.SysFont("Arial", 13, bold=True)
    fonte_media = pygame.font.SysFont("Arial", 16, bold=True)
    fonte_grande = pygame.font.SysFont("Arial", 26, bold=True)
    fonte_muito_grande = pygame.font.SysFont("Arial", 46, bold=True)

    fundo_img = carregar_fundo()
    tela_inicial_img = carregar_tela_inicial()


    # Estado Inicial
    estado_atual = ESTADO_NOME
    nome_input = ""
    cursor_visivel = True
    cursor_timer = 0.0

    # Dados da partida
    touro = None
    plataformas = None
    itens = None
    energia = config.MAX_ENERGY
    tempo_jogo = 0.0
    altura_maxima_alcancada = 0
    motivo_game_over = ""
    ranking_top5 = []
    bg_y_offset = 0.0

    # Botões Touch (Rodapé da tela durante o jogo)
    btn_altura = 90
    btn_largura = LARGURA // 2
    btn_esquerda = pygame.Rect(0, ALTURA - btn_altura, btn_largura, btn_altura)
    btn_direita = pygame.Rect(btn_largura, ALTURA - btn_altura, btn_largura, btn_altura)

    # Áreas clicáveis da arte da tela inicial.
    # Coordenadas baseadas na imagem tela-inicial.png (1024 x 1536).
    # Elas são redimensionadas para qualquer resolução definida em config.py.
    def area_tela_inicial(x, y, w, h):
        if tela_inicial_img:
            sx = LARGURA / tela_inicial_img.get_width()
            sy = ALTURA / tela_inicial_img.get_height()
        else:
            sx = sy = 1.0
        return pygame.Rect(int(x * sx), int(y * sy), int(w * sx), int(h * sy))

    box_nome_rect = area_tela_inicial(314, 694, 418, 128)
    btn_iniciar_rect = area_tela_inicial(311, 854, 424, 126)

    tecla_esq_pressionada = False
    tecla_dir_pressionada = False
    touch_esq_pressionado = False
    touch_dir_pressionado = False

    def iniciar_nova_partida():
        nonlocal touro, plataformas, itens, energia, tempo_jogo, altura_maxima_alcancada, bg_y_offset, estado_atual
        touro = Touro(LARGURA // 2 - 32, ALTURA - 160)
        plataformas, itens = gerar_nivel()
        energia = config.MAX_ENERGY
        tempo_jogo = 0.0
        altura_maxima_alcancada = 0
        bg_y_offset = 0.0
        estado_atual = ESTADO_JOGANDO

    rodando = True
    while rodando:
        dt = clock.tick(config.FPS) / 1000.0
        scroll = 0

        # --- Eventos ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            # --- ESTADO 1: ENTRADA DE NOME ---
            if estado_atual == ESTADO_NOME:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_RETURN:
                        if nome_input.strip():
                            iniciar_nova_partida()
                    elif evento.key == pygame.K_BACKSPACE:
                        nome_input = nome_input[:-1]
                    else:
                        if len(nome_input) < 12 and evento.unicode.isprintable():
                            nome_input += evento.unicode

                elif evento.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                    if hasattr(evento, 'pos'):
                        pos_x, pos_y = evento.pos
                    else:
                        pos_x = int(evento.x * LARGURA)
                        pos_y = int(evento.y * ALTURA)

                    if box_nome_rect.collidepoint(pos_x, pos_y):
                        # Mantém o foco visual no campo; a digitação continua por KEYDOWN.
                        cursor_visivel = True
                        cursor_timer = 0.0
                    elif btn_iniciar_rect.collidepoint(pos_x, pos_y):
                        if not nome_input.strip():
                            nome_input = "Piloto"
                        iniciar_nova_partida()

            # --- ESTADO 2: JOGANDO ---
            elif estado_atual == ESTADO_JOGANDO:
                if evento.type == pygame.KEYDOWN:
                    if evento.key in (pygame.K_LEFT, pygame.K_a):
                        tecla_esq_pressionada = True
                    elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                        tecla_dir_pressionada = True

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

            # --- ESTADO 3 & 4: GAME OVER OU VITÓRIA ---
            elif estado_atual in (ESTADO_GAMEOVER, ESTADO_VITORIA):
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_r:
                        iniciar_nova_partida()
                    elif evento.key == pygame.K_n:
                        estado_atual = ESTADO_NOME
                        nome_input = ""

                elif evento.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                    # Reinicia toque rápido ao clicar
                    iniciar_nova_partida()

        # --- Lógica por Estado ---
        if estado_atual == ESTADO_NOME:
            cursor_timer += dt
            if cursor_timer >= 0.5:
                cursor_visivel = not cursor_visivel
                cursor_timer = 0.0

        elif estado_atual == ESTADO_JOGANDO:
            tempo_jogo += dt

            # Consumo acelerado de energia
            taxa_consumo = config.INITIAL_DECAY_RATE + (tempo_jogo * config.DECAY_ACCELERATION)
            energia -= taxa_consumo * dt

            if energia <= 0:
                energia = 0
                estado_atual = ESTADO_GAMEOVER
                motivo_game_over = "Energia Esgotada!"

            # Controles
            mover_esq = tecla_esq_pressionada or touch_esq_pressionado
            mover_dir = tecla_dir_pressionada or touch_dir_pressionado

            if mover_esq and not mover_dir:
                touro.mover_esquerda()
            elif mover_dir and not mover_esq:
                touro.mover_direita()
            else:
                touro.parar_horizontal()

            # Atualiza touro
            touro.update()

            # Câmera Vertical
            if touro.rect.y < ALTURA // 2:
                scroll = ALTURA // 2 - touro.rect.y
                touro.y += scroll
                touro.rect.y += scroll
                altura_maxima_alcancada += scroll
                bg_y_offset += scroll * 0.5

            plataformas.update(scroll)
            itens.update(scroll)

            # Colisão com Plataformas
            if touro.vy > 0 and not touro.voando:
                for plat in plataformas:
                    if plat.rect.colliderect(touro.rect):
                        if touro.rect.bottom - touro.vy <= plat.rect.top + 10:
                            touro.rect.bottom = plat.rect.top
                            touro.y = float(touro.rect.y)
                            touro.quicar()

                            if plat.is_finish_line:
                                estado_atual = ESTADO_VITORIA
                                salvar_tempo(nome_input if nome_input.strip() else "Piloto", tempo_jogo)
                                ranking_top5 = carregar_top_ranking(5)
                            break

            # Colisão com Red Bull
            coletados = pygame.sprite.spritecollide(touro, itens, True)
            for item in coletados:
                energia = min(config.MAX_ENERGY, energia + config.ENERGY_REFILL)
                touro.ativar_voo()

            # Queda
            if touro.rect.top > ALTURA:
                estado_atual = ESTADO_GAMEOVER
                motivo_game_over = "Você caiu!"

        # --- Desenho na Tela ---
        if fundo_img:
            h_fundo = fundo_img.get_height()
            pos_y = int(bg_y_offset % h_fundo) - h_fundo
            tela.blit(fundo_img, (0, pos_y))
            if pos_y + h_fundo < ALTURA:
                tela.blit(fundo_img, (0, pos_y + h_fundo))
        else:
            tela.fill(config.BG_COLOR)

        # ----------------------------------------------------
        # RENDERIZAR TELA INICIAL
        # ----------------------------------------------------
        if estado_atual == ESTADO_NOME:
            if tela_inicial_img:
                tela_inicial = pygame.transform.scale(tela_inicial_img, (LARGURA, ALTURA))
                tela.blit(tela_inicial, (0, 0))
            else:
                tela.fill((5, 10, 30))

            # O texto, moldura e botão já fazem parte da arte.
            # Aqui o Pygame desenha apenas o texto digitado dentro do retângulo.
            txt_nome_display = nome_input + ("|" if cursor_visivel else "")
            if nome_input or cursor_visivel:
                txt_nome_draw = fonte_media.render(txt_nome_display, True, (255, 255, 255))
                tela.blit(
                    txt_nome_draw,
                    (
                        box_nome_rect.x + 18,
                        box_nome_rect.y + box_nome_rect.height // 2 - txt_nome_draw.get_height() // 2,
                    ),
                )

        # ----------------------------------------------------
        # RENDERIZAR JOGO
        # ----------------------------------------------------
        # ----------------------------------------------------
        else:
            plataformas.draw(tela)
            itens.draw(tela)
            touro.draw(tela)

            # Botões Touch (Rodapé)
            superficie_btn = pygame.Surface((LARGURA, btn_altura), pygame.SRCALPHA)
            cor_esq = (255, 255, 255, 90) if touch_esq_pressionado else (255, 255, 255, 35)
            cor_dir = (255, 255, 255, 90) if touch_dir_pressionado else (255, 255, 255, 35)

            txt_esq = fonte_muito_grande.render("◄", True, (255, 255, 255))
            txt_dir = fonte_muito_grande.render("►", True, (255, 255, 255))
            tela.blit(txt_esq, (btn_largura // 2 - txt_esq.get_width() // 2, ALTURA - btn_altura // 2 - 10))
            tela.blit(txt_dir, (btn_largura + btn_largura // 2 - txt_dir.get_width() // 2, ALTURA - btn_altura // 2 - 10))

            # HUD Topo
            desenhar_barra_energia(tela, energia, config.MAX_ENERGY, fonte_pequena)

            txt_cronometro = fonte_pequena.render(f"Tempo: {tempo_jogo:.2f}s", True, (255, 220, 100))
            tela.blit(txt_cronometro, (LARGURA - txt_cronometro.get_width() - 15, 12))

            if touro.voando:
                txt_voo = fonte_pequena.render("⚡ VOO RED BULL! ⚡", True, (0, 220, 255))
                tela.blit(txt_voo, (LARGURA // 2 - txt_voo.get_width() // 2, 36))

        # ----------------------------------------------------
        # RENDERIZAR GAME OVER
        # ----------------------------------------------------
        if estado_atual == ESTADO_GAMEOVER:
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            tela.blit(overlay, (0, 0))

            txt_go = fonte_grande.render("GAME OVER", True, (230, 40, 40))
            txt_sub = fonte_media.render(motivo_game_over, True, (255, 200, 200))
            txt_r1 = fonte_media.render("[R] Jogar Novamente", True, (255, 255, 255))
            txt_r2 = fonte_pequena.render("[N] Trocar de Jogador", True, (180, 200, 220))
            
            tela.blit(txt_go, (LARGURA // 2 - txt_go.get_width() // 2, ALTURA // 3))
            tela.blit(txt_sub, (LARGURA // 2 - txt_sub.get_width() // 2, ALTURA // 3 + 40))
            tela.blit(txt_r1, (LARGURA // 2 - txt_r1.get_width() // 2, ALTURA // 3 + 85))
            tela.blit(txt_r2, (LARGURA // 2 - txt_r2.get_width() // 2, ALTURA // 3 + 115))

        # ----------------------------------------------------
        # RENDERIZAR VITÓRIA & LEADERBOARD
        # ----------------------------------------------------
        elif estado_atual == ESTADO_VITORIA:
            overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            overlay.fill((5, 15, 35, 220))
            tela.blit(overlay, (0, 0))

            txt_vit = fonte_grande.render("🏆 VOCÊ CHEGOU AO TOPO! 🏆", True, (255, 215, 0))
            txt_final = fonte_media.render(f"Piloto: {nome_input} | Tempo: {tempo_jogo:.2f}s", True, (255, 255, 255))
            
            tela.blit(txt_vit, (LARGURA // 2 - txt_vit.get_width() // 2, 40))
            tela.blit(txt_final, (LARGURA // 2 - txt_final.get_width() // 2, 80))

            # Tabela de Ranking Top 5
            txt_rk_title = fonte_media.render("--- MELHORES TEMPOS ---", True, (0, 200, 255))
            tela.blit(txt_rk_title, (LARGURA // 2 - txt_rk_title.get_width() // 2, 125))

            y_rk = 160
            for idx, item in enumerate(ranking_top5, start=1):
                linha = f"{idx}. {item.get('nome', 'Piloto')} - {item.get('tempo', 0.0):.2f}s"
                cor_linha = (255, 215, 0) if idx == 1 else (240, 240, 240)
                txt_item = fonte_media.render(linha, True, cor_linha)
                tela.blit(txt_item, (LARGURA // 2 - 100, y_rk))
                y_rk += 30

            txt_op1 = fonte_media.render("[R] Jogar Novamente", True, (255, 255, 255))
            txt_op2 = fonte_pequena.render("[N] Trocar de Jogador", True, (180, 200, 220))
            
            tela.blit(txt_op1, (LARGURA // 2 - txt_op1.get_width() // 2, ALTURA - 100))
            tela.blit(txt_op2, (LARGURA // 2 - txt_op2.get_width() // 2, ALTURA - 65))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
