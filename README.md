# Amarelinha

> Projeto de exergame — Ciência da Computação, UDESC.

## Sobre

Jogo de amarelinha controlado pelo corpo: uma câmera filma o jogador e o MediaPipe Pose detecta a ponta dos pés, que são mapeados para a área de jogo projetada no chão por uma transformação de perspectiva. O jogador pisa nos quadrados da amarelinha desenhada pelo Pygame e ganha pontos a cada quadrado pisado. A calibração da área e parte das configurações foram aproveitadas de projetos anteriores (KarTEA / T-TEA).

## Funcionalidades

- Rastreamento dos pés esquerdo e direito com MediaPipe Pose, mostrados na tela como círculos (azul para o esquerdo, vermelho para o direito).
- Menu inicial em que o jogo começa quando o jogador pisa no botão "Iniciar".
- Amarelinha com 7 quadrados no padrão 2-1-2-1-1, numerados de 1 a 7.
- Pontuação: +10 pontos e um som de acerto cada vez que um pé entra em um quadrado; o quadrado pisado fica verde.
- Calibração da área de jogo: o operador clica nos 4 cantos da área na janela da câmera e os pontos são salvos em `calibracao.csv`, carregado automaticamente na próxima execução.
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
| `camera.py` | Captura da webcam e desenho da área calibrada |
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

O jogo abre em tela cheia (800x600) e usa a câmera de índice `2` (`cv2.VideoCapture(2)` em `camera.py` e `calibrate.py`); ajuste esse número se a sua webcam tiver outro índice.

### Controles

| Tecla | Ação |
|---|---|
| `C` (no menu) | Abre a calibração |
| `C` / `Q` (tela de avisos) | Continua para a calibração / sai |
| Clique do mouse (janela "TELA DE CONTROLE") | Marca os 4 cantos da área de jogo |
| `Q` ou `Esc` (calibração) | Salva a calibração em `calibracao.csv` e volta |
| `D` | Liga/desliga o modo de depuração |
| `Esc` | Sai do jogo |

## Sons não incluídos

Os arquivos de áudio `assets/snd_dumbvictory.wav` (som de acerto) e `assets/snd_hurt1.wav` foram removidos deste repositório por questões de direitos autorais. Como o `jogo.py` carrega esses dois arquivos ao iniciar, **o jogo não abre sem eles**. Para rodar, coloque arquivos `.wav` próprios com exatamente esses nomes dentro da pasta `assets/`.

## Autores

Arthur Bertoli
