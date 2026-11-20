#################################################################################
######################### SOFTWARE BASE - PROJETO T-TEA #########################
#################################################################################
################################# VERSÃO 1.0 ####################################
#################################################################################
import csv
import cv2
# import mediapipe as mp
import numpy as np
import pygame
import time
import random
import settings
from settings import resource_path
from camera import abrir_camera, _ponto

pygame.init()
#################################################################################
################################## Hora de Inicio ###############################
#################################################################################
inicio_da_sessao=False
if inicio_da_sessao==False:
    inicio_da_sessao_t0 = int(time.time())
    inicio_da_sessao=True
#################################################################################
#################################### Hardware ###################################
#################################################################################
# Tamanho das Telas:
largura_projetor = 800  # A ltere este valor de acordo com a resolução da projeção do jogo.
altura_projetor = 600  # A ltere este valor de acordo com a resolução da projeção do jogo.
largura_tela_controle = 640  # Esta tela é usada pelo terapeuta/operador. Altere o valor caso necessário.
altura_tela_controle = 480  # Esta tela é usada pelo terapeuta/operador. Altere o valor caso necessário.
relacao_largura = (largura_projetor / largura_tela_controle)  # Esta relação é usada na correção de perspectiva.
relacao_altura = (altura_projetor / altura_tela_controle)  # Esta relação é usada na correção de perspectiva.
tela_de_calibracao = np.zeros((altura_projetor, largura_projetor, 3),
                            np.uint8)  # Tela que será usada para o projetar o jogo.
tela_de_controle = np.zeros((altura_tela_controle, largura_tela_controle, 3),
                            np.uint8)  # Tela que será usada para o projetar o jogo.


csv.register_dialect(
    'mydialect',
    delimiter = ';',
    quotechar = '"',
    doublequote = True,
    skipinitialspace = True,
    lineterminator = '\n',
    quoting = csv.QUOTE_MINIMAL)


#################################################################################
################################## SPRITES ######################################
#################################################################################
icone_fig=pygame.image.load(resource_path('assets/Repetea_Figuras/icone.png'))
avisos_fig=pygame.image.load(resource_path('assets/Repetea_Figuras/avisos.png'))
ajuda_f1_fig=pygame.image.load(resource_path('assets/Repetea_Figuras/ajuda_F1.png'))
instrucao_calibrar_fig=pygame.image.load(resource_path('assets/Repetea_Figuras/calibrar.png'))
calibracao_finalizada_fig=pygame.image.load(resource_path('assets/Repetea_Figuras/calibracao_ok.png'))

#################################################################################
################################## CORES & FONTES ###############################
#################################################################################
azul = 0, 0, 255
verde = 0, 255, 0
vermelho = 255, 0, 0
amarelo = 255, 255, 0
branco = 255, 255, 255
preto = 0, 0, 0

fonte = cv2.FONT_HERSHEY_SIMPLEX
font = pygame.font.SysFont(None, 25)

#################################################################################
############################# VARIÁVEIS DE PROGRAMA #############################
#################################################################################
# mp_drawing = mp.solutions.drawing_utils  # Configuração do MediaPipe. Ver https://google.github.io/mediapipe/solutions/pose.html para maiores detalhes.
# mp_pose = mp.solutions.pose  # Configuração do MediaPipe. Ver https://google.github.io/mediapipe/solutions/pose.html para maiores detalhes.
pontos_calibracao = np.zeros((4, 2), int)  # Matriz para os pontos de calibração de perspectiva - 4 linhas/ 2 colunas
contador = 0  # Contador utilizado nos 4 pontos de calibração
figura_selecionada=False # Usada para evitar que o usuário apenas selecione uma vez a figura e não ficar piscando
lista_sorteio=[] #São as figuras sorteadas pelo computador e colocadas nesta lista, para depois fazer a comparação com as escolhas do usuário
pontuacao=0 # Pontos conseguidos em durante a rodada
tempo_ajuda=5 # Tempo até a ajuda aparecer
tempo_total=10 # Tempo máximo da jogada
atencao_memorizar=False
hud_switch=True
pausa_switch=False
tempo_ajuda_switch=False
tentativa=1
x_pose = 0
y_pose = 0

def resetar_vars():

    global pontos_calibracao, contador

    #pygame.init()

    #relacao_largura = (largura_projetor / largura_tela_controle)  # Esta relação é usada na correção de perspectiva.
    #relacao_altura = (altura_projetor / altura_tela_controle)  # Esta relação é usada na correção de perspectiva.
    #tela_de_calibracao = np.zeros((altura_projetor, largura_projetor, 3), np.uint8)  # Tela que será usada para o projetar o jogo.
    #tela_de_controle = np.zeros((altura_tela_controle, largura_tela_controle, 3), np.uint8)  # Tela que será usada para o projetar o jogo.

    #mp_drawing = mp.solutions.drawing_utils  # Configuração do MediaPipe. Ver https://google.github.io/mediapipe/solutions/pose.html para maiores detalhes.
    #mp_pose = mp.solutions.pose  # Configuração do MediaPipe. Ver https://google.github.io/mediapipe/solutions/pose.html para maiores detalhes.
    pontos_calibracao = np.zeros((4, 2), int)  # Matriz para os pontos de calibração de perspectiva - 4 linhas/ 2 colunas
    contador = 0  # Contador utilizado nos 4 pontos de calibração
    #hud_switch=True
    #pausa_switch=False
    #tempo_ajuda_switch=False
    #tentativa=1
    #x_pose = 0
    #y_pose = 0


def calibrar_ttea(camera=None):
    """Rotina de calibração dos 4 cantos da área de jogo.

    camera: um cv2.VideoCapture já aberto (o jogo passa a própria câmera, para
    não abrir o mesmo dispositivo duas vezes). Se for None, abre a câmera
    configurada em settings (com fallback automático para os índices 0, 1, 2).

    Devolve os 4 pontos calibrados (array 4x2) se a calibração for concluída e
    salva em calibracao.csv, ou None se for cancelada. Não fecha o pygame nem
    encerra o programa: quem chamou continua a execução normalmente.
    """

    global gameDisplay#, x_pose, y_pose

    resetar_vars()

    camera_propria = camera is None
    if camera_propria:
        camera, _ = abrir_camera()
        if camera is None:
            print("Calibração cancelada: nenhuma câmera disponível.")
            return None

    def liberar_camera():
        if camera_propria:
            camera.release()

    gameDisplay = pygame.display.set_mode((largura_projetor, altura_projetor))
    pygame.display.set_caption('T-TEA')
    pygame.display.set_icon(icone_fig)
    gameDisplay.blit(avisos_fig,(0, 0))
    pygame.display.update()

    # Tela de avisos: C continua para a calibração, Q/Esc cancela e volta
    gameWarning = False
    while not gameWarning:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                liberar_camera()
                return None
            # SAIR ou CONCORDO
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    instrucao_calibrar()
                    pygame.display.update()
                    gameWarning = True
                elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                    liberar_camera()
                    return None
        pygame.time.wait(10)

    #################################################################################
    ############################### Calibração ######################################
    #################################################################################
    gameExit = False  # Sai da calibração
    tela_ok = False   # Evita redesenhar a tela de "calibração ok" a cada frame
    cv2.namedWindow("TELA DE CONTROLE")
    cv2.setMouseCallback("TELA DE CONTROLE", mousePoints)

    while not gameExit:
        ret, frame = camera.read()
        if not ret or frame is None:
            print("Falha ao ler a câmera durante a calibração.")
            break

        tela_de_controle = frame

        # Pontos já marcados.
        for i in range(contador):
            cv2.circle(tela_de_controle, _ponto(pontos_calibracao[i]), 5, azul, 3)

        # Depois da Calibração.
        if contador == 4:
            cv2.line(tela_de_controle, _ponto(pontos_calibracao[0]), _ponto(pontos_calibracao[1]), verde, 2)
            cv2.line(tela_de_controle, _ponto(pontos_calibracao[1]), _ponto(pontos_calibracao[3]), verde, 2)
            cv2.line(tela_de_controle, _ponto(pontos_calibracao[2]), _ponto(pontos_calibracao[0]), verde, 2)
            cv2.line(tela_de_controle, _ponto(pontos_calibracao[2]), _ponto(pontos_calibracao[3]), verde, 2)
            if not tela_ok:
                pygame.display.set_caption('Calibracao')
                calibracao_ok()
                tela_ok = True
        tela_update()

        # Atualização das telas
        cv2.imshow("TELA DE CONTROLE", tela_de_controle)
        cv2.waitKey(1)

        # Teclas de Atalho: fechar a janela, Q ou Esc encerram a calibração
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key in (pygame.K_q, pygame.K_ESCAPE)
            ):
                gameExit = True

    try:
        cv2.destroyWindow("TELA DE CONTROLE")
    except cv2.error:
        pass
    liberar_camera()

    if contador < 4:
        print("Calibração incompleta (menos de 4 pontos); mantendo a calibração anterior.")
        return None

    grava_calibracao()
    print('P1: ', pontos_calibracao[0], ' P2: ', pontos_calibracao[1], ' P3: ', pontos_calibracao[2], ' P4: ', pontos_calibracao[3])
    return pontos_calibracao.copy()

#################################################################################
################################### FUNÇÕES #####################################
#################################################################################
def avisos(): #Tela inicial com os avisos do equipamento
    global gameDisplay
    gameDisplay.blit(avisos_fig,(0, 0))

def instrucao_calibrar():
    global gameDisplay
    gameDisplay.blit(instrucao_calibrar_fig, (0, 0))

def ajuda_f1(): #Tela com as teclas de atalho
    global gameDisplay
    gameDisplay.blit(ajuda_f1_fig, (0, 0))

def calibracao_ok():
    global gameDisplay
    gameDisplay.blit(calibracao_finalizada_fig, (0, 0))

def fill_preto():
    global gameDisplay
    gameDisplay.fill(preto)

def mousePoints(event, x, y, flags, params):
    # Função para capturar cliques do Mouse:
    global contador
    # Clique esquerdo marca o próximo canto (no máximo 4); clique direito recomeça.
    if event == cv2.EVENT_LBUTTONDOWN and contador < 4:
        pontos_calibracao[contador] = x, y
        contador = contador + 1
    elif event == cv2.EVENT_RBUTTONDOWN:
        pontos_calibracao[:] = 0
        contador = 0

def posicao():

    # Função para determinar a posição do jogador na área de projeçao:
    # Transformação de Perspectiva:
    pts1 = np.float32([pontos_calibracao[0], pontos_calibracao[1], pontos_calibracao[2], pontos_calibracao[3]])
    pts2 = np.float32(
        [[0, 0], [largura_tela_controle, 0], [0, altura_tela_controle], [largura_tela_controle, altura_tela_controle]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    perspectiva = cv2.warpPerspective(tela_de_controle, matrix, (largura_tela_controle, altura_tela_controle))

    # Posição do jogador:
    p = (int(x_pose * largura_tela_controle), int(y_pose * altura_tela_controle))
    position_x = (matrix[0][0] * p[0] + matrix[0][1] * p[1] + matrix[0][2]) / (
    (matrix[2][0] * p[0] + matrix[2][1] * p[1] + matrix[2][2]))
    position_y = (matrix[1][0] * p[0] + matrix[1][1] * p[1] + matrix[1][2]) / (
    (matrix[2][0] * p[0] + matrix[2][1] * p[1] + matrix[2][2]))
    p_after = (int((position_x) * (relacao_largura)), int((position_y) * (relacao_altura)))

    return p_after

def rand():
    #Função para sortear a figura
    rand_figura = round(random.randrange(0, 4))
    return rand_figura

def delay():
    time.sleep(0.5)

def tela_update():
    pygame.display.update()

def grava_calibracao():
    Config = ['Ponto 1 x', 'Ponto 1 y', 'Ponto 2 x', 'Ponto 2 y', 'Ponto 3 x', 'Ponto 3 y', 'Ponto 4 x', 'Ponto 4 y']
    Dados = [int(v) for v in pontos_calibracao.flatten()]
    # Grava no mesmo arquivo que settings.py lê (pasta do projeto), e não na pasta atual
    file = settings.csv_path

    with open(file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, dialect='mydialect')
        csvwriter.writerow(Config)
        csvwriter.writerow(Dados)