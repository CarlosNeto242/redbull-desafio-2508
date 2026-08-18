import json
import os

ARQUIVO_RANKING = "ranking.json"

def carregar_top_ranking(limite=5):
    """Carrega o histórico de rankings ordenado pelo menor tempo."""
    if not os.path.exists(ARQUIVO_RANKING):
        return []
    
    try:
        with open(ARQUIVO_RANKING, "r", encoding="utf-8") as f:
            dados = json.load(f)
            # Ordena por menor tempo
            dados_ordenados = sorted(dados, key=lambda x: x.get("tempo", 999999))
            return dados_ordenados[:limite]
    except Exception as e:
        print(f"Erro ao ler arquivo de ranking: {e}")
        return []

def salvar_tempo(nome, tempo_segundos):
    """Salva a nova pontuação no arquivo JSON local."""
    nome_formatado = nome.strip() if nome.strip() else "Jogador"
    tempo_arredondado = round(float(tempo_segundos), 2)
    
    rankings = []
    if os.path.exists(ARQUIVO_RANKING):
        try:
            with open(ARQUIVO_RANKING, "r", encoding="utf-8") as f:
                rankings = json.load(f)
        except Exception:
            rankings = []

    rankings.append({
        "nome": nome_formatado,
        "tempo": tempo_arredondado
    })

    # Ordena do menor tempo para o maior
    rankings = sorted(rankings, key=lambda x: x["tempo"])

    # Salva os 20 melhores tempos
    try:
        with open(ARQUIVO_RANKING, "w", encoding="utf-8") as f:
            json.dump(rankings[:20], f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erro ao salvar arquivo de ranking: {e}")
