# Red Bull Challenge 
## Grupo: 25/8

## Como executar o jogo:

1. Ative o ambiente virtual com as bibliotecas necessárias (consulte o passo 1 mais abaixo).
2. Edite o arquivo `config.py` para ajustar suas preferências de áudio e desempenho. As variáveis relevantes são:

   ```
   FPS = 90
   SOUND_VOLUME_SFX = 0.3
   SOUND_VOLUME_MUSIC = 0.5
   ```
3. Estando na pasta raiz do repositório, execute o jogo com o seguinte comando no terminal, ou abra o arquivo `main.py` com o VS Code e execute por lá:

   ```
   python main.py


```
redbull-desafio-2508/
│
├── assets/                    # Pasta para os recursos do jogo
│   │
│   ├── latinhas/              # Recursos relacionados às latinhas
│   │
│   └── tourinho/              # Recursos relacionados ao personagem/tourinho
│       ├── fundo.png           # Imagem de fundo
│       └── plataforma.png      # Imagem da plataforma
│
├── src/                       # Código-fonte principal do jogo
│   └── oi.txt                 # Arquivo de texto dentro da pasta src
│
├── .gitignore                 # Arquivos e pastas ignorados pelo Git
├── config.py                  # Configurações globais do projeto
├── main.py                    # Ponto de entrada principal do jogo
├── README.md                  # Documentação do projeto
└── requirements.txt           # Dependências necessárias do projeto
```


## 1. Ambiente virtual de Python

* Crie um ambiente virtual, para isso digite dentro da raiz os seguintes comandos em ordem (no Mac ou Linux):

```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

* Caso use Windows:

```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

* Lembre-se de ativar o ambiente virtual antes de executar o jogo!

## 2. Fluxo de trabalho com Git – Pull Requests e Issues

### Para contribuir com o projeto:

1. **Crie uma branch a partir da `main`:**

```bash
git checkout main #Volta pra branch main
git pull origin main #Sincroniza o repositorio
git checkout -b sua-feature-aqui # Cria a branch donde vc quer trabalhar
```

2. **Desenvolva e faça commits claros (exemplo):**

```bash
git add . # Adiciona as mudanças do diretorio atual
git commit -m "feat: adiciona tela de contato" #Cria o commit
```

3. **Suba sua branch:**

```bash
git push origin sua-feature-aqui #Envia a branch com os commit para criar o Pull Request (PR) no Github 
```

4. **Abra um Pull Request no GitHub:**

- Base: `main`
- Compare: `sua-feature-aqui`
- Preencha o título e a descrição do PR (ligue a issue com `Closes #número_da_issue` na descrição, quando você digitar `Closes #` já irá listar as issues)

5. **Espere aprovação para merge.**

- O Admin irá testar o PR, e posteriormente aceitar ou recusar. Se tiver algum erro será comunicado pelo grupo de Whats.