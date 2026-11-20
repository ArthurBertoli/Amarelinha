import cv2
import settings


def abrir_camera(indice=None):
    """Abre a webcam e devolve (captura, indice).

    Tenta primeiro o índice pedido (ou settings.CAMERA, que pode vir da
    variável de ambiente AMARELINHA_CAMERA) e, se ele não abrir ou não
    entregar imagens, tenta os índices de settings.CAMERA_FALLBACK (0, 1, 2).
    Devolve (None, None) se nenhuma câmera funcionar.
    """
    preferido = settings.CAMERA if indice is None else indice
    candidatos = [preferido] + [i for i in settings.CAMERA_FALLBACK if i != preferido]

    for i in candidatos:
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ok, _ = cap.read()
            if ok:
                if i != preferido:
                    print(f"Câmera {preferido} indisponível; usando a câmera {i}.")
                return cap, i
        cap.release()

    print(f"Nenhuma câmera encontrada (índices testados: {candidatos}).")
    return None, None


def _ponto(p):
    """Converte um ponto (array do NumPy) para a tupla de int que o OpenCV espera."""
    return int(p[0]), int(p[1])


def desenhar_area_calibrada(frame, pontos):
    """Desenha o contorno e os cantos da área calibrada sobre o frame."""
    p = [_ponto(pt) for pt in pontos]
    cv2.line(frame, p[0], p[1], settings.verde, 2)
    cv2.line(frame, p[1], p[3], settings.verde, 2)
    cv2.line(frame, p[2], p[0], settings.verde, 2)
    cv2.line(frame, p[2], p[3], settings.verde, 2)
    for pt in p:
        cv2.circle(frame, pt, 5, settings.azul, 3)


class Camera:
    def __init__(self, indice=None):
        # Load camera (índice configurável, com fallback automático)
        self.cap, self.indice = abrir_camera(indice)
        self.ret, self.frame = False, None
        if self.cap is None:
            raise RuntimeError(
                "Não foi possível abrir nenhuma câmera. Conecte uma webcam ou "
                "defina AMARELINHA_CAMERA com o índice correto."
            )
        self.ret, self.frame = self.cap.read()

        # Get actual webcam resolution
        if self.ret:
            altura_webcam, largura_webcam, _ = self.frame.shape
            settings.largura_webcam = largura_webcam
            settings.altura_webcam = altura_webcam
            print(f"Webcam {self.indice} resolution: {largura_webcam}x{altura_webcam}")

    def load_camera(self):
        self.ret, self.frame = self.cap.read()
        if not self.ret or self.frame is None:
            self.frame = None
            return
        #self.frame = cv2.flip(self.frame, 1)

        desenhar_area_calibrada(self.frame, settings.pontos_calibracao)

    def display_camera(self):
        if self.frame is not None:
            cv2.imshow("Tela de Captura", self.frame)
        cv2.waitKey(1)

    def close_camera(self):
        if self.cap is not None:
            self.cap.release()
        try:
            cv2.destroyWindow("Tela de Captura")
        except cv2.error:
            pass
