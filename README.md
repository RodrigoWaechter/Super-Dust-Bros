# Super Dust Bros

Um jogo 2D de plataforma com ação, tiro e itens arremessáveis, inspirado na estrutura clássica de **Super Mario Bros** com estética e elementos de **Counter-Strike**.
Foi desenvolvido como projeto da disciplina de **Computação Gráfica**, explorando renderização, animação, colisão e loop de jogo com OpenGL.

<img width="805" height="638" alt="image" src="https://github.com/user-attachments/assets/9266aeea-b6e5-4d55-ab42-9634b1dd2bae" />

## Descrição do projeto

**Super Dust Bros** é um jogo de plataforma lateral em que o jogador atravessa fases, desvia de buracos, enfrenta inimigos e coleta itens para avançar pelo mapa.
O objetivo de cada fase é chegar ao bloco final antes que o tempo acabe e sem perder toda a vida no caminho.

A proposta mistura duas referências bem claras:

- **Super Mario Bros** na estrutura de plataforma 2D, pulo, progressão por fases e blocos de item
- **Counter-Strike** na identidade visual, nos cenários inspirados em mapas clássicos e nos itens como AK-47, granada, molotov e cura

<img width="810" height="643" alt="image" src="https://github.com/user-attachments/assets/3ee4be62-bd51-41b4-9437-bcbb46867968" />

Do ponto de vista acadêmico, o projeto foi criado para aplicar conceitos de **computação gráfica** em um jogo jogável, incluindo:

- renderização 2D com OpenGL
- animação por sprites
- colisão entre objetos
- movimentação com física simples
- HUD e telas de estado
- organização do jogo em engine, entidades, fase e renderização

## Tecnologias utilizadas

- **Python**
- **PyOpenGL**
- **GLFW**
- **Pillow**

## Funcionalidades do jogo

- **Movimento do player** com deslocamento lateral
- **Pulo** com efeito de gravidade
- **Sistema de tiro** com projétil em linha reta quando o jogador coleta a arma
- **Inimigos** com dois comportamentos:
  - inimigos que patrulham o cenário
  - inimigos atiradores que ficam parados e disparam em direção ao player
- **Power-ups** obtidos em blocos especiais, com sorteio de:
  - AK-47
  - granada
  - molotov
  - item de cura
- **Sistema de fases/mapa** com geração procedural de chão, buracos, obstáculos e inimigos
- **HUD** com barra de vida, valor numérico da vida, tempo restante, mundo/fase e indicador de arremessáveis
- **Menu inicial** antes do começo da partida
- **Game Over** quando a vida acaba ou o tempo se esgota
- **Câmera lateral** acompanhando o avanço horizontal do jogador
- **Fundo com parallax** para dar profundidade visual

## Controles

- `Enter`: iniciar o jogo no menu
- `A`: mover para a esquerda
- `D`: mover para a direita
- `W`: pular
- `Botão esquerdo do mouse`: atirar, se o jogador tiver coletado a arma
- `Botão direito do mouse`: arremessar granada ou molotov, se houver item equipado
- `Enter`: reiniciar após o Game Over
- `Esc`: fechar o jogo na tela de Game Over

## Como executar o projeto

### Pré-requisitos

- Python 3 instalado
- Ambiente gráfico disponível
- Apenas para Linux: Sistemas baseados em Debian/Ubuntu precisam do pacote de ambiente virtual instalado manualmente:
```bash
sudo apt update && sudo apt install python3-venv -y
```
> Observação: o jogo abre uma janela com GLFW/OpenGL. Em ambientes sem interface gráfica, como alguns servidores, terminais remotos ou containers headless, a execução pode falhar.

### Passo a passo no *Linux*

1. Clone o repositório:

```bash
git clone https://github.com/RodrigoWaechter/Super-Dust-Bros.git
cd Super-Dust-Bros
```

2. Crie um ambiente virtual:

```bash
python3 -m venv .venv
```

3. Ative o ambiente virtual:

```bash
source .venv/bin/activate
```

4. Instale as dependências usadas pelo código:

```bash
pip install -r requirements.txt
```

5. Execute o jogo a partir da raiz do projeto:

```bash
python3 -m src.main
```
### Passo a passo no *Windows*

1. Clone o repositório e entre na pasta

```bash
git clone https://github.com/RodrigoWaechter/Super-Dust-Bros.git
cd Super-Dust-Bros
```

2. Crie um ambiente virtual:

```bash
py -m venv .venv
```

3. Ative o ambiente virtual:

```bash
.venv\Scripts\activate
```

4. Instale as dependências usadas pelo código:

```bash
pip install -r requirements.txt
```

5. Execute o jogo a partir da raiz do projeto:

```bash
py -m src.main
```

### Observação importante sobre a execução

O ponto de entrada está em `src/main.py`, mas a forma mais segura de rodar o projeto é com:

```bash
python3 -m src.main
```

Isso evita problema de importação do pacote `src` ao tentar rodar diretamente com `python3 src/main.py`.

## Estrutura do projeto

```text
Super-Dust-Bros/
├── README.md
├── requirements.txt
└── src/
    ├── main.py
    ├── engine.py
    ├── settings.py
    ├── utils.py
    ├── assets/
    ├── entities/
    ├── fase/
    └── renderer/
```

### `src/engine.py`

É o coração do jogo.
Esse arquivo concentra a lógica principal da aplicação:

- criação e controle da janela com GLFW
- gerenciamento dos estados `menu`, `jogo` e `game_over`
- leitura de input do teclado e mouse
- atualização da física do player
- atualização de inimigos, projéteis, explosões e power-ups
- verificação de colisões
- controle de câmera
- renderização dos elementos na ordem correta
- avanço de fase e reinício do jogo

### `src/entities/`

Reúne as classes que representam os objetos do jogo.
Entre os principais arquivos estão:

- `player.py`: jogador, movimentação, animações, tiro, arremesso e vida
- `personagem.py`: base de comportamento físico para personagens
- `inimigo.py`: inimigo comum que patrulha o cenário
- `inimigo_atirador.py`: inimigo que mira no player e dispara projéteis
- `projetil.py`: projétil comum, granada ativa e molotov ativa
- `power_ups.py`: itens coletáveis e bloco especial que sorteia os power-ups
- `explosao.py`: efeito visual de explosão e fogo no chão da molotov
- `obstaculo.py`: blocos sólidos do cenário
- `chao.py`: blocos de chão texturizados
- `game_object.py`: classe base com posição, tamanho, desenho simples e colisão

### `src/fase/`

Contém a lógica de construção das fases.
O arquivo principal é:

- `mapa.py`: gera o layout da fase com base em mundo e fase, definindo:
  - tamanho do mapa
  - chance de buracos
  - chance de blocos
  - chance de inimigos
  - bloco objetivo no final

Um detalhe interessante é que as fases **não são desenhadas manualmente uma a uma**.
Elas são montadas com aleatoriedade controlada, então a distribuição de blocos, buracos e inimigos pode mudar entre execuções.

### `src/renderer/`

Responsável pelos elementos visuais auxiliares:

- `hud.py`: desenha barra de vida, número da vida, timer, mundo/fase, indicadores de arremessáveis, menu inicial e tela de Game Over
- `parallax.py`: renderiza o fundo com efeito de parallax, criando sensação de profundidade

### `src/utils.py`

Arquivo utilitário usado para carregar texturas.
Ele abre imagens com Pillow, prepara os dados em RGBA e envia a textura para a GPU com OpenGL.

## Como o jogo funciona

O jogo segue o modelo clássico de **game loop**, que pode ser explicado de forma bem simples assim:

### 1. Input

O programa lê as entradas do jogador a cada frame:

- teclas para andar e pular
- clique esquerdo para atirar
- clique direito para arremessar item
- `Enter` para iniciar ou reiniciar

### 2. Update

Depois de ler os comandos, o jogo atualiza o estado interno:

- aplica gravidade e movimento
- resolve colisões com chão e obstáculos
- atualiza inimigos
- move projéteis
- cria explosões e fogo da molotov
- verifica coleta de power-ups
- controla câmera
- checa fim da fase, queda no mapa, vida e tempo restante

### 3. Render

Por fim, tudo é desenhado na tela:

- fundo
- cenário
- objetivo da fase
- inimigos
- power-ups
- projéteis e explosões
- player
- HUD

Esse ciclo de **input -> update -> render** se repete continuamente enquanto a janela está aberta.
Na prática, é isso que faz o jogo parecer vivo: o jogador aperta uma tecla, o estado muda e a nova cena é desenhada quase instantaneamente.

Para apresentação, uma forma simples de resumir é:

> O jogo lê a ação do jogador, atualiza a lógica interna e redesenha a cena várias vezes por segundo.

## Créditos

- **Integrantes:** Bernardo Bencke, Gabriel Fontanari, Gabriel Reckziegel, Lucas da Silva e Rodrigo Waechter
- **Disciplina:** Computação Gráfica
- **Professor:** Rafael Peiter
