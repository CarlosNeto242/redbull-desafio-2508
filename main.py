import asyncio
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

NOMES_GENERICOS = [
    "Blue", "Red", "Green", "Gold", "Silver",
    "Indigo", "Cyan", "Amber", "Violet", "Coral",
    "Onyx", "Jade", "Ruby", "Sage", "Azure",
    "Ivory", "Teal", "Crimson", "Aqua", "Gray",
]

def carregar_sky():
    caminho0 = os.path.join("assets", "sky", "sky0.png")
    caminho1 = os.path.join("assets", "sky", "sky1.png")
    sky0_img = None
    sky1_img = None
    
    try:
        fundo_img0 = pygame.image.load(caminho0).convert()
        largura0 = config.WIDTH
        altura0 = int(fundo_img0.get_height() * (config.WIDTH / fundo_img0.get_width()))
        sky0_img = pygame.transform.smoothscale(fundo_img0, (largura0, altura0))
    except Exception as e:
        print(f"Aviso: N\u00e3o foi poss\u00edvel carregar {caminho0}: {e}")
        
    try:
        fundo_img1 = pygame.image.load(caminho1).convert()
        largura1 = config.WIDTH
        altura1 = int(fundo_img1.get_height() * (config.WIDTH / fundo_img1.get_width()))
        sky1_img = pygame.transform.smoothscale(fundo_img1, (largura1, altura1))
    except Exception as e:
        print(f"Aviso: N\u00e3o foi poss\u00edvel carregar {caminho1}: {e}")
        
    return sky0_img, sky1_img

def carregar_tela_inicial():
    """Carrega a arte pixelada da tela inicial."""
    caminho = os.path.join("assets", "tela-inicial.png")
    try:
        imagem = pygame.image.load(caminho).convert()
        return imagem
    except Exception as e:
        print(f"Aviso: N\u00e3o foi poss\u00edvel carregar a tela inicial ({caminho}): {e}")
        return None


def carregar_tela_vitoria():
    """Carrega a arte pixelada da tela de vit\u00f3ria."""
    caminho = os.path.join("assets", "tela-vitoria.png")
    try:
        imagem = pygame.image.load(caminho).convert()
        return imagem
    except Exception as e:
        print(f"Aviso: N\u00e3o foi poss\u00edvel carregar a tela de vit\u00f3ria ({caminho}): {e}")
        return None


def carregar_tela_game_over():
    caminho = os.path.join("assets", "tela-game-over.png")
    try:
        return pygame.image.load(caminho).convert()
    except Exception as e:
        print(f"Aviso: N\u00e3o foi poss\u00edvel carregar a tela de game over ({caminho}): {e}")
        return None


def gerar_nivel():
    """Gera o grupo de plataformas e latinhas de Red Bull da base at\u00e9 o topo."""
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

    # 2. Gerar plataformas e itens subindo at\u00e9 a altura total
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
    """Desenha a barra de energia no estilo Pixel Retr\u00f4."""
    bar_width = config.WIDTH - 40
    bar_height = 24
    x = 20
    y = 12

    pct = max(0.0, min(1.0, energia_atual / max_energia))
    
    # Cores
    cor_borda_clara = (200, 200, 255)
    cor_borda_escura = (30, 40, 80)
    cor_fundo = (5, 10, 25)
    
    if pct > 0.5:
        cor_fill = (0, 180, 255) # Cyan Retro
    elif pct > 0.25:
        cor_fill = (255, 190, 0)
    else:
        cor_fill = (230, 30, 30)

    # 1. Borda Pixelada Externa
    pygame.draw.rect(tela, cor_borda_escura, (x+2, y, bar_width-4, bar_height))
    pygame.draw.rect(tela, cor_borda_escura, (x, y+2, bar_width, bar_height-4))
    
    # 2. Borda Interna (1 pixel de espessura)
    pygame.draw.rect(tela, cor_borda_clara, (x+4, y+2, bar_width-8, bar_height-4))
    pygame.draw.rect(tela, cor_borda_clara, (x+2, y+4, bar_width-4, bar_height-8))
    
    # 3. Fundo Escuro
    pygame.draw.rect(tela, cor_fundo, (x+4, y+4, bar_width-8, bar_height-8))

    # 4. Blocos de Preenchimento (Estilo Pixel)
    blocos_totais = 25
    blocos_ativos = int(blocos_totais * pct)
    largura_bloco = (bar_width - 12) / blocos_totais
    
    for i in range(blocos_ativos):
        bx = x + 6 + i * largura_bloco
        by = y + 6
        bw = largura_bloco - 2 # Gap entre os pixels
        bh = bar_height - 12
        pygame.draw.rect(tela, cor_fill, (bx, by, bw, bh))
        
        # Detalhe de brilho no bloco
        brilho = (min(255, cor_fill[0]+60), min(255, cor_fill[1]+60), min(255, cor_fill[2]+60))
        pygame.draw.rect(tela, brilho, (bx, by, bw, 2))

async def main():
    pygame.init()
    pygame.font.init()

    LARGURA, ALTURA = config.WIDTH, config.HEIGHT
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Overtime")

    clock = pygame.time.Clock()
    fonte_pequena = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 13)
    fonte_media = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 11)
    fonte_grande = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 15)
    fonte_muito_grande = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 50)

    fundo_sky0, fundo_sky1 = carregar_sky()
    tela_inicial_img = carregar_tela_inicial()
    tela_vitoria_img = carregar_tela_vitoria()
    tela_game_over_img = carregar_tela_game_over()


    # Estado Inicial
    estado_atual = ESTADO_NOME
    nome_input = random.choice(NOMES_GENERICOS)
    cursor_visivel = False
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
    frase_voo_atual = ""

    # Bot\u00f5es Touch (Rodap\u00e9 da tela durante o jogo)
    btn_altura = 90
    btn_largura = LARGURA // 2
    btn_esquerda = pygame.Rect(0, ALTURA - btn_altura, btn_largura, btn_altura)
    btn_direita = pygame.Rect(btn_largura, ALTURA - btn_altura, btn_largura, btn_altura)

    # \u00c1reas clic\u00e1veis da arte da tela inicial.
    # Coordenadas baseadas na imagem tela-inicial.png (1024 x 1536).
    # Elas s\u00e3o redimensionadas para qualquer resolu\u00e7\u00e3o definida em config.py.
    def area_tela_inicial(x, y, w, h):
        if tela_inicial_img:
            sx = LARGURA / tela_inicial_img.get_width()
            sy = ALTURA / tela_inicial_img.get_height()
        else:
            sx = sy = 1.0
        return pygame.Rect(int(x * sx), int(y * sy), int(w * sx), int(h * sy))

    btn_iniciar_rect = area_tela_inicial(311, 785, 424, 125)

    # Campo HTML real para que Safari/iPad possa abrir o teclado virtual.
    # Em desktop, o input nao existe e o texto continua sendo tratado pelo Pygame.
    # No campo de nome: o jogador inicia diretamente.

    def area_tela_vitoria(x, y, w, h):
        if tela_vitoria_img:
            sx = LARGURA / tela_vitoria_img.get_width()
            sy = ALTURA / tela_vitoria_img.get_height()
        else:
            sx = sy = 1.0
        return pygame.Rect(int(x * sx), int(y * sy), int(w * sx), int(h * sy))

    # Aproxima as \u00e1reas dos bot\u00f5es JOGAR NOVAMENTE e TROCAR DE JOGADOR da arte.
    btn_vitoria_repetir = area_tela_vitoria(300, 1175, 450, 105)
    btn_vitoria_trocar = area_tela_vitoria(300, 1272, 450, 105)

    # \u00c1reas clic\u00e1veis da tela de Game Over (base 1024x1536).
    def area_tela_game_over(x, y, w, h):
        if tela_game_over_img:
            sx = LARGURA / tela_game_over_img.get_width()
            sy = ALTURA / tela_game_over_img.get_height()
        else:
            sx = sy = 1.0
        return pygame.Rect(
            int(x * sx),
            int(y * sy),
            int(w * sx),
            int(h * sy)
        )

    btn_gameover_repetir = area_tela_game_over(290, 1110, 470, 105)
    btn_gameover_trocar = area_tela_game_over(290, 1220, 470, 105)

    tecla_esq_pressionada = False
    tecla_dir_pressionada = False
    touch_esq_pressionado = False
    touch_dir_pressionado = False

    def iniciar_nova_partida():
        nonlocal touro, plataformas, itens, energia, tempo_jogo, altura_maxima_alcancada, bg_y_offset, estado_atual
        nonlocal tecla_esq_pressionada, tecla_dir_pressionada, touch_esq_pressionado, touch_dir_pressionado
        nonlocal frase_voo_atual
        touro = Touro(LARGURA // 2 - 32, ALTURA - 160)
        touro.vx = 0
        touro.vy = 0
        plataformas, itens = gerar_nivel()
        energia = config.MAX_ENERGY
        tempo_jogo = 0.0
        altura_maxima_alcancada = 0
        bg_y_offset = 0.0
        frase_voo_atual = ""
        tecla_esq_pressionada = False
        tecla_dir_pressionada = False
        touch_esq_pressionado = False
        touch_dir_pressionado = False
        estado_atual = ESTADO_JOGANDO

    rodando = True
    while rodando:
        dt = clock.tick(config.FPS) / 1000.0
        scroll = 0

        # --- Eventos ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            # --- ESTADO 1: TELA INICIAL ---
            if estado_atual == ESTADO_NOME:
                if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                    iniciar_nova_partida()
                elif evento.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                    if hasattr(evento, "pos"):
                        pos_x, pos_y = evento.pos
                    else:
                        pos_x = int(evento.x * LARGURA)
                        pos_y = int(evento.y * ALTURA)
                    if btn_iniciar_rect.collidepoint(pos_x, pos_y):
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

            # --- ESTADO 3 & 4: GAME OVER OU VIT\u00d3RIA ---
            elif estado_atual in (ESTADO_GAMEOVER, ESTADO_VITORIA):
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_r:
                        iniciar_nova_partida()
                    elif evento.key == pygame.K_n:
                        estado_atual = ESTADO_NOME
                        nome_input = random.choice(NOMES_GENERICOS)
                        cursor_visivel = False
                        cursor_timer = 0.0

                elif evento.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                    if hasattr(evento, 'pos'):
                        pos_x, pos_y = evento.pos
                    else:
                        pos_x = int(evento.x * LARGURA)
                        pos_y = int(evento.y * ALTURA)

                    if estado_atual == ESTADO_GAMEOVER:
                        if btn_gameover_trocar.collidepoint(pos_x, pos_y):
                            estado_atual = ESTADO_NOME
                            nome_input = random.choice(NOMES_GENERICOS)
                            cursor_visivel = True
                            cursor_timer = 0.0
                        elif btn_gameover_repetir.collidepoint(pos_x, pos_y):
                            iniciar_nova_partida()

                    elif estado_atual == ESTADO_VITORIA:
                        if btn_vitoria_trocar.collidepoint(pos_x, pos_y):
                            estado_atual = ESTADO_NOME
                            nome_input = random.choice(NOMES_GENERICOS)
                            cursor_visivel = True
                            cursor_timer = 0.0
                        elif btn_vitoria_repetir.collidepoint(pos_x, pos_y):
                            iniciar_nova_partida()

        # --- L\u00f3gica por Estado ---
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

            # C\u00e2mera Vertical
            if touro.rect.y < ALTURA // 2:
                scroll = ALTURA // 2 - touro.rect.y
                touro.y += scroll
                touro.rect.y += scroll
                altura_maxima_alcancada += scroll
                bg_y_offset += scroll * 0.5

            plataformas.update(scroll)
            itens.update(scroll)

            # Colis\u00e3o com Plataformas
            if touro.vy > 0 and not touro.voando:
                for plat in plataformas:
                    if plat.rect.colliderect(touro.rect):
                        if touro.rect.bottom - touro.vy <= plat.rect.top + 10:
                            touro.rect.bottom = plat.rect.top
                            touro.y = float(touro.rect.y)
                            touro.quicar()

                            if plat.is_finish_line:
                                estado_atual = ESTADO_VITORIA
                                salvar_tempo(nome_input, tempo_jogo)
                                ranking_top5 = carregar_top_ranking(5)
                            break

            # Colis\u00e3o com Red Bull
            coletados = pygame.sprite.spritecollide(touro, itens, True)
            for item in coletados:
                energia = min(config.MAX_ENERGY, energia + config.ENERGY_REFILL)
                touro.ativar_voo()
                voo_frases =["ISSO NINGUÉM FAZ", "PULO E OUSADIA", "RADICAL!!", "SE JOGA!!","INACREDITÁVEL"]
                frase_voo_atual = random.choice(voo_frases)

            # Queda
            if touro.rect.top > ALTURA:
                estado_atual = ESTADO_GAMEOVER
                motivo_game_over = "Voc\u00ea caiu!"

        # --- Desenho na Tela ---
        if fundo_sky0 and fundo_sky1:
            h_sky0 = fundo_sky0.get_height()
            h_sky1 = fundo_sky1.get_height()
            
            y_sky0 = ALTURA - h_sky0 + bg_y_offset
            
            if y_sky0 < ALTURA:
                tela.blit(fundo_sky0, (0, y_sky0))
            
            y_atual = y_sky0 - h_sky1
            while y_atual + h_sky1 > 0:
                tela.blit(fundo_sky1, (0, y_atual))
                y_atual -= h_sky1
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

        # ----------------------------------------------------
        # RENDERIZAR JOGO
        # ----------------------------------------------------
        # ----------------------------------------------------
        else:
            plataformas.draw(tela)
            itens.draw(tela)
            touro.draw(tela)

            # Bot\u00f5es Touch (Rodap\u00e9)
            superficie_btn = pygame.Surface((LARGURA, btn_altura), pygame.SRCALPHA)
            cor_esq = (255, 255, 255, 90) if touch_esq_pressionado else (255, 255, 255, 35)
            cor_dir = (255, 255, 255, 90) if touch_dir_pressionado else (255, 255, 255, 35)

            txt_esq = fonte_muito_grande.render("<", True, (255, 255, 255))
            txt_dir = fonte_muito_grande.render(">", True, (255, 255, 255))
            tela.blit(txt_esq, (btn_largura // 2 - txt_esq.get_width() // 2, ALTURA - btn_altura // 2 - 10))
            tela.blit(txt_dir, (btn_largura + btn_largura // 2 - txt_dir.get_width() // 2, ALTURA - btn_altura // 2 - 10))

            # HUD Topo
            desenhar_barra_energia(tela, energia, config.MAX_ENERGY, fonte_pequena)

            txt_cronometro = fonte_pequena.render(f"Tempo: {tempo_jogo:.2f}s", True, (255, 220, 100))
            tela.blit(txt_cronometro, (LARGURA - txt_cronometro.get_width() - 15, 37))

            if touro.voando and frase_voo_atual:
                txt_voo = fonte_grande.render(frase_voo_atual, True, (200, 0, 60))
                tela.blit(txt_voo, (LARGURA // 2 - txt_voo.get_width() // 2, 400))

        # ----------------------------------------------------
        # RENDERIZAR GAME OVER
        # ----------------------------------------------------
        if estado_atual == ESTADO_GAMEOVER:
            if tela_game_over_img:
                tela_game_over = pygame.transform.scale(tela_game_over_img, (LARGURA, ALTURA))
                tela.blit(tela_game_over, (0, 0))
            else:
                tela.fill((5, 10, 30))
                txt_go = fonte_grande.render("GAME OVER", True, (230, 40, 40))
                tela.blit(txt_go, (LARGURA // 2 - txt_go.get_width() // 2, ALTURA // 3))

        # ----------------------------------------------------
        # RENDERIZAR VIT\u00d3RIA & LEADERBOARD
        # ----------------------------------------------------
        elif estado_atual == ESTADO_VITORIA:
            # A arte cont\u00e9m toda a interface visual: t\u00edtulo, molduras, touro e bot\u00f5es.
            if tela_vitoria_img:
                tela_vitoria = pygame.transform.scale(tela_vitoria_img, (LARGURA, ALTURA))
                tela.blit(tela_vitoria, (0, 0))
            else:
                tela.fill((5, 10, 30))

            # O n\u00famero do tempo fica propositalmente vazio na imagem e \u00e9 escrito pelo Pygame.
            txt_tempo = fonte_media.render(f"{tempo_jogo:.2f}s", True, (255, 215, 0))
            tempo_x = int(LARGURA * 0.56) - txt_tempo.get_width() // 2
            tempo_y = int(ALTURA * (530 / 1536))  # antes era 482
            tela.blit(txt_tempo, (tempo_x, tempo_y))

            # A lista da arte tamb\u00e9m fica vazia; o Pygame preenche somente os nomes e tempos.
            y_rk = int(ALTURA * (660 / 1536))  # antes era 610
            passo_rk = int(ALTURA * (72 / 1536))

            for idx, item in enumerate(ranking_top5[:5], start=1):
                nome = str(item.get('nome', 'Blue'))
                tempo = float(item.get('tempo', 0.0))

                txt_nome = fonte_media.render(nome, True, (255, 255, 255))
                txt_item_tempo = fonte_media.render(
                    f"{tempo:.1f} s".replace(".", ","),
                    True,
                    (255, 215, 0) if idx == 1 else (255, 255, 255)
                )

                tela.blit(
                    txt_nome,
                    (int(LARGURA * (300 / 1024)), y_rk)
                )

                tela.blit(
                    txt_item_tempo,
                    (int(LARGURA * (700 / 1024)) - txt_item_tempo.get_width() // 2, y_rk)
                )

                y_rk += passo_rk
        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
