import os
import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, K_c, K_d

from pose_tracking import PoseTracking
from settings import path_assets, tamanho_tela, fps, resource_path
import calibrate
from camera import Camera


class Jogo:
    # Configuração visual otimizada para o padrão 2-1-2-1-1 com espaçamento exato
    TAMANHO_QUADRADO: int = 90
    GAP_HORIZONTAL: int = 90   # Espaço entre a dupla igual ao tamanho do quadrado
    GAP_VERTICAL: int = 12     
    TOPO_AMARELINHA: int = 10

    COR_QUADRADO_PADRAO: tuple[int, int, int] = (255, 215, 0)   # amarelo
    COR_QUADRADO_PROGRESSO: tuple[int, int, int] = (255, 140, 0)  # laranja
    COR_QUADRADO_CONFIRMADO: tuple[int, int, int] = (0, 220, 0)   # verde
    COR_BORDA: tuple[int, int, int] = (180, 140, 0)
    COR_FUNDO_JOGO: tuple[int, int, int] = (0, 195, 225)  # ciano

    def __init__(self) -> None:
        pygame.init()

        self.poseTracking: PoseTracking = PoseTracking()
        self.cap: Camera = Camera()

        self.running: bool = True
        self.tamanho: tuple[int, int] = tamanho_tela
        self.score: int = 0
        self.feedback: str | None = None
        self.debug: bool = False

        self.superficie: pygame.Surface = pygame.display.set_mode(
            size=self.tamanho, flags=pygame.FULLSCREEN, display=0
        )

        pygame.display.set_caption("Amarelinha Gen")
        self.origin: tuple[int, int, int] = (0, 0, 0)
        self.fonte: pygame.font.Font = pygame.font.SysFont("aakar", 35)
        self.fonteNumero: pygame.font.Font = pygame.font.SysFont("aakar", 40)

        self.menuBackgroundAsset: pygame.Surface = pygame.image.load(resource_path(os.path.join(path_assets, "tela-inicial.png")))
        self.startButtonAsset: pygame.Surface = pygame.image.load(resource_path(os.path.join(path_assets, "iniciar.png")))

        self.somCerto: pygame.mixer.Sound = pygame.mixer.Sound(os.path.join(path_assets, "snd_dumbvictory.wav"))
        self.somCerto.set_volume(0.2)
        self.somErrado: pygame.mixer.Sound = pygame.mixer.Sound(os.path.join(path_assets, "snd_hurt1.wav"))

        btnW: int = self.startButtonAsset.get_width()
        btnH: int = self.startButtonAsset.get_height()
        self.startButtonPos: tuple[int, int] = (
            (self.tamanho[0] - btnW) // 2,
            (self.tamanho[1] - btnH) // 2,
        )
        self.startButtonRect: pygame.Rect = pygame.Rect(
            self.startButtonPos[0], self.startButtonPos[1], btnW, btnH
        )

        self.squares: dict[int, pygame.Rect] = self.gerarSquares()

        self.estadoEsq: dict[str, any] = {"quadrado": 0, "confirmado": False}
        self.estadoDir: dict[str, any] = {"quadrado": 0, "confirmado": False}

        self.historico: list[str] = []

    def gerarSquares(self) -> dict[int, pygame.Rect]:
        """Calcula a posição dos 7 quadrados seguindo o layout pedido: 2, 1, 2, 1, 1."""
        s: int = self.TAMANHO_QUADRADO
        gapH: int = self.GAP_HORIZONTAL
        gapV: int = self.GAP_VERTICAL
        centroX: int = self.tamanho[0] // 2

        xSolo: int = centroX - s // 2
        xEsq: int = centroX - s - gapH // 2
        xDir: int = centroX + gapH // 2

        # Altura das 5 fileiras verticais distribuídas uniformemente
        y1: int = self.TOPO_AMARELINHA
        y2: int = y1 + s + gapV
        y3: int = y2 + s + gapV
        y4: int = y3 + s + gapV
        y5: int = y4 + s + gapV

        return {
            1: pygame.Rect(xEsq, y5, s, s),   # Linha 1 (Dupla - Esq)
            2: pygame.Rect(xDir, y5, s, s),   # Linha 1 (Dupla - Dir)
            3: pygame.Rect(xSolo, y4, s, s),  # Linha 2 (Solo)
            4: pygame.Rect(xEsq, y3, s, s),   # Linha 3 (Dupla - Esq)
            5: pygame.Rect(xDir, y3, s, s),   # Linha 3 (Dupla - Dir)
            6: pygame.Rect(xSolo, y2, s, s),  # Linha 4 (Solo)
            7: pygame.Rect(xSolo, y1, s, s),  # Linha 5 (Solo)
        }

    def menu(self) -> None:
        inMenu: bool = True
        clock: pygame.time.Clock = pygame.time.Clock()

        while inMenu and self.running:
            clock.tick(fps)
            self.loadCamera()
            self.getFeetPosition()
            self.cap.display_camera()

            lX, lY = self.poseTracking.get_left_foot()
            rX, rY = self.poseTracking.get_right_foot()

            peEsqNoBotao: bool = lX is not None and lY is not None and self.startButtonRect.collidepoint(lX, lY)
            peDirNoBotao: bool = rX is not None and rY is not None and self.startButtonRect.collidepoint(rX, rY)

            if peEsqNoBotao or peDirNoBotao:
                inMenu = False

            for e in pygame.event.get():
                if e.type == QUIT:
                    self.running = False
                if e.type == KEYDOWN:
                    if e.key == K_ESCAPE:
                        self.running = False
                    if e.key == K_c:
                        self.cap.close_camera()
                        calibrate.calibrar_ttea()
                    if e.key == K_d:
                        self.debug = not self.debug

            self.superficie.fill(self.origin)
            self.superficie.blit(self.menuBackgroundAsset, (0, 0))
            self.superficie.blit(self.startButtonAsset, self.startButtonPos)
            self.drawCircle()

            pygame.display.update()

    def run(self) -> None:
        self.score = 0
        self.feedback = None
        self.historico = []
        self.estadoEsq = {"quadrado": 0, "confirmado": False}
        self.estadoDir = {"quadrado": 0, "confirmado": False}

        clock: pygame.time.Clock = pygame.time.Clock()
        gaming: bool = True

        clock.tick()

        while self.running and gaming:
            clock.tick(fps)

            for e in pygame.event.get():
                if e.type == QUIT:
                    self.running = False
                if e.type == KEYDOWN:
                    if e.key == K_ESCAPE:
                        self.running = False
                    if e.key == K_d:
                        self.debug = not self.debug

            self.loadCamera()
            self.getFeetPosition()
            self.cap.display_camera()

            lX, lY = self.poseTracking.get_left_foot()
            rX, rY = self.poseTracking.get_right_foot()

            self.updatePermanencia(lX, lY, self.estadoEsq, "Esquerdo")
            self.updatePermanencia(rX, rY, self.estadoDir, "Direito")

            # Render
            self.superficie.fill(self.COR_FUNDO_JOGO)
            self.drawAmarelinha()

            self.superficie.blit(self.fonte.render(f"Pontos: {self.score}", True, (255, 255, 255)), (25, 25))
            if self.feedback:
                self.superficie.blit(self.fonte.render(self.feedback, True, (255, 255, 255)), (25, 60))

            self.drawCircle()

            pygame.display.update()

    def drawAmarelinha(self) -> None:
        """Desenha os 7 quadrados da amarelinha, destacando apenas o progresso ativo ou acertos."""
        for idSquare, rect in self.squares.items():
            cor: tuple[int, int, int] = self.COR_QUADRADO_PADRAO

            for estado in (self.estadoEsq, self.estadoDir):
                if estado["quadrado"] == idSquare:
                    cor = self.COR_QUADRADO_CONFIRMADO if estado["confirmado"] else self.COR_QUADRADO_PROGRESSO

            pygame.draw.rect(self.superficie, cor, rect, border_radius=6)
            pygame.draw.rect(self.superficie, self.COR_BORDA, rect, width=4, border_radius=6)

            texto: pygame.Surface = self.fonteNumero.render(str(idSquare), True, (0, 0, 0))
            textoRect: pygame.Rect = texto.get_rect(center=rect.center)
            self.superficie.blit(texto, textoRect)

    def updatePermanencia(self, footX: float | None, footY: float | None, estado: dict, nomePe: str) -> None:
        quadradoAtual: int = self.checkFootOnSquare(footX, footY)

        if quadradoAtual == 0:
            if estado["quadrado"] != 0:
                print(f"[{nomePe}] Saiu do quadrado {estado['quadrado']}")
            estado["quadrado"] = 0
            estado["confirmado"] = False
            return

        if quadradoAtual != estado["quadrado"]:
            print(f"[{nomePe}] Entrou no quadrado {quadradoAtual}")
            estado["quadrado"] = quadradoAtual
            estado["confirmado"] = False

        # Se pisou e ainda não foi computado nesta entrada, pontua na hora
        if not estado["confirmado"]:
            self.score += 10
            self.feedback = f"Acertou o quadrado {quadradoAtual}!"
            self.somCerto.play()
            estado["confirmado"] = True
            self.historico.append(f"{nomePe} confirmou quadrado {quadradoAtual}")
            if len(self.historico) > 5:
                self.historico.pop(0)
            print(f"[{nomePe}] CONFIRMOU quadrado {quadradoAtual} (+10 pontos imediatamente)")

    def checkFootOnSquare(self, footX: float | None, footY: float | None) -> int:
        if footX is None or footY is None:
            return 0
        for idSquare, rect in self.squares.items():
            if rect.collidepoint(footX, footY):
                return idSquare
        return 0

    def drawCircle(self) -> None:
        lX, lY = self.poseTracking.get_left_foot()
        rX, rY = self.poseTracking.get_right_foot()
        if lX is not None and lY is not None:
            pygame.draw.circle(self.superficie, (0, 0, 255), (int(lX), int(lY)), 30)
        if rX is not None and rY is not None:
            pygame.draw.circle(self.superficie, (255, 0, 0), (int(rX), int(rY)), 30)

    def loadCamera(self) -> None:
        self.cap.load_camera()

    def getFeetPosition(self) -> tuple[int | None, int | None]:
        self.cap.frame = self.poseTracking.scan_feets(self.cap.frame)
        return self.poseTracking.get_feet_center()

    def finish(self) -> None:
        pass


if __name__ == "__main__":
    g = Jogo()
    while g.running:
        g.menu()
        g.run()
        g.finish()
    pygame.quit()