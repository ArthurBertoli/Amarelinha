# Amarelinha

> Projeto de exergame — Ciência da Computação, UDESC.

## Sobre

Jogo de amarelinha controlado pelo corpo: uma câmera filma o jogador e o MediaPipe Pose detecta a ponta dos pés, que são mapeados para a área de jogo projetada no chão por uma transformação de perspectiva. O jogador pisa nos quadrados da amarelinha desenhada pelo Pygame e ganha pontos a cada quadrado pisado. A calibração da área e parte das configurações foram aproveitadas de projetos anteriores (KarTEA / T-TEA).

## Funcionalidades

- Rastreamento dos pés esquerdo e direito com MediaPipe Pose, mostrados na tela como círculos (azul para o esquerdo, vermelho para o direito).
- Menu inicial em que o jogo começa quando o jogador pisa no botão "Iniciar".
- Amarelinha com 7 quadrados no padrão 2-1-2-1-1, numerados de 1 a 7.
- Pontuação: +10 pontos (e um som de acerto, se o arquivo de som existir) cada vez que um pé entra em um quadrado; o quadrado pisado fica verde.
- Calibração da área de jogo: o operador clica nos 4 cantos da área na janela da câmera e os pontos são salvos em `calibracao.csv` (na pasta do projeto). A nova calibração passa a valer na hora, sem reiniciar o jogo, e é carregada automaticamente nas próximas execuções.
- Janela auxiliar "Tela de Captura" com a imagem da câmera, o esqueleto detectado e o contorno da área calibrada.

## Tecnologias

- Python 3.11 ou 3.12
- Pygame
- MediaPipe (Pose)
- OpenCV
- NumPy

## Estrutura

| Arquivo | Descrição |
|---|---|
| `jogo.py` | Ponto de entrada: menu, laço do jogo, desenho da amarelinha e pontuação |
| `pose_tracking.py` | Detecção dos pés com MediaPipe e conversão para coordenadas da tela |
| `camera.py` | Abertura da webcam (índice configurável, com tentativa automática de outros índices), captura e desenho da área calibrada |
| `calibrate.py` | Telas e rotina de calibração dos 4 cantos da área de jogo |
| `settings.py` | Configurações gerais, caminhos dos assets e leitura de `calibracao.csv` |
| `sequencia.py` | Classe de sequência de notas herdada de outro projeto; não é usada pelo jogo |
| `calibracao.csv` | Pontos de calibração salvos |
| `assets/` | Imagens do menu, botões e telas de calibração |

## Como executar

```bash
pip install -r requirements.txt
python jogo.py
```

Use Python 3.11 ou 3.12. O `requirements.txt` fixa o `mediapipe==0.10.21`, que ainda tem a API `mp.solutions` usada pelo código (versões mais novas do MediaPipe a removeram).

O jogo abre em tela cheia (800x600).

### Escolha da câmera

Por padrão o jogo tenta a câmera de índice `2` (valor de `CAMERA` em `settings.py`). Se ela não abrir ou não entregar imagens, tenta automaticamente os índices `0`, `1` e `2` (`CAMERA_FALLBACK`) e avisa no terminal qual câmera foi usada. Para escolher outra câmera sem editar o código, use a variável de ambiente `AMARELINHA_CAMERA`:

```bash
# Linux / macOS
AMARELINHA_CAMERA=0 python jogo.py
```

```powershell
# Windows (PowerShell)
$env:AMARELINHA_CAMERA = "0"; python jogo.py
```

A calibração usa a mesma câmera do jogo.

### Controles

| Tecla | Ação |
|---|---|
| `C` (no menu) | Abre a calibração |
| `C` / `Q` ou `Esc` (tela de avisos) | Continua para a calibração / cancela e volta ao menu |
| Clique esquerdo (janela "TELA DE CONTROLE") | Marca os 4 cantos da área de jogo, na ordem dos cantos da imagem projetada: superior esquerdo, superior direito, inferior esquerdo, inferior direito |
| Clique direito (janela "TELA DE CONTROLE") | Apaga os pontos marcados e recomeça |
| `Q` ou `Esc` (calibração) | Salva a calibração em `calibracao.csv` (se os 4 pontos foram marcados) e volta ao menu |
| `D` | Liga/desliga o modo de depuração |
| `Esc` | Sai do jogo |

## Sons (opcionais)

Os arquivos de áudio `assets/snd_dumbvictory.wav` (som de acerto) e `assets/snd_hurt1.wav` não fazem parte deste repositório por questões de direitos autorais. Eles são opcionais: se não existirem (ou se não houver saída de áudio disponível), o jogo avisa no terminal e roda sem som. Para ter som, coloque arquivos `.wav` próprios com exatamente esses nomes dentro da pasta `assets/`.

## Autores

Arthur Bertoli
