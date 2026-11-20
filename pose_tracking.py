import cv2
import mediapipe as mp
import numpy as np

import settings

# Os valores abaixo são lidos sempre de "settings." (e não copiados com
# "from settings import *"), porque a resolução real da webcam só é conhecida
# depois que a câmera abre e os pontos de calibração podem mudar durante o jogo.

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_poses = mp.solutions.pose


def posicao(x: float, y: float, debug: bool = False) -> tuple[int, int]:
    # Função para determinar a posição do jogador na área de projeçao:
    # x, y são coordenadas normalizadas (0-1) do MediaPipe
    # Converte para coordenadas de pixel da webcam
    p_webcam = (int(x * settings.largura_webcam), int(y * settings.altura_webcam))

    if debug:
        print(
            f"DEBUG posicao: normalized ({x:.3f}, {y:.3f}) -> webcam pixel {p_webcam} (resolution: {settings.largura_webcam}x{settings.altura_webcam})"
        )
        print(f"  Calibration points: {settings.pontos_calibracao}")

    # Transformação de Perspectiva: da área calibrada para a área de projeção
    pts1 = np.float32(
        [
            settings.pontos_calibracao[0],
            settings.pontos_calibracao[1],
            settings.pontos_calibracao[2],
            settings.pontos_calibracao[3],
        ]
    )
    
    # Margens virtuais para compensar a distorção trapezoidal do projetor no chão
    margemH: int = int(settings.largura_projetor * 0.15)
    
    pts2 = np.float32(
        [
            [-margemH, -120],
            [settings.largura_projetor + margemH, -120],
            [margemH, settings.altura_projetor + 20],
            [settings.largura_projetor - margemH, settings.altura_projetor + 20],
        ]
    )
    matrix = cv2.getPerspectiveTransform(pts1, pts2)

    # Aplica a transformação de perspectiva
    denom = (matrix[2][0] * p_webcam[0] + matrix[2][1] * p_webcam[1] + matrix[2][2])
    if denom == 0:
        denom = 0.001
        
    position_x = (matrix[0][0] * p_webcam[0] + matrix[0][1] * p_webcam[1] + matrix[0][2]) / denom
    position_y = (matrix[1][0] * p_webcam[0] + matrix[1][1] * p_webcam[1] + matrix[1][2]) / denom

    result = (int(position_x), int(position_y))

    if debug:
        print(f"  Transformed to pygame: {result}")

    return result


def is_point_in_calibration_area(x: float, y: float) -> bool:
    # Verifica se o ponto (x, y em coordenadas normalizadas 0-1) está dentro da área de calibração
    p_webcam = (int(x * settings.largura_webcam), int(y * settings.altura_webcam))

    # Usa cv2.pointPolygonTest para verificar se está dentro do polígono
    polygon = np.array(
        [
            settings.pontos_calibracao[0],
            settings.pontos_calibracao[1],
            settings.pontos_calibracao[3],
            settings.pontos_calibracao[2],
        ],
        np.int32,
    )

    result = cv2.pointPolygonTest(polygon, (float(p_webcam[0]), float(p_webcam[1])), False)
    return result >= 0  # >= 0 significa dentro ou na borda


class PoseTracking:
    def __init__(self) -> None:
        self.pose_tracking = mp_poses.Pose(
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )
        self.feet_x: int | None = None
        self.feet_y: int | None = None
        self.feet1_x: float | None = None
        self.feet1_y: float | None = None
        self.feet2_x: float | None = None
        self.feet2_y: float | None = None
        self.results = None
        self.pose_closed: bool = False
        self.pose_detected: bool = False
        self.feet_in_calibration_area: bool = False
        self.debug_counter: int = 0
        self.image: np.ndarray | None = None

    def scan_feets(self, image: np.ndarray | None) -> np.ndarray | None:
        # Adicione esta verificação de segurança no início da função
        if image is None:
            return None
        rows, cols, _ = image.shape

        # Convert the BGR image to RGB.
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # To improve performance, optionally mark the image as not writeable to pass by reference.
        image.flags.writeable = False
        self.results = self.pose_tracking.process(image)

        # Draw the pose annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        self.pose_closed = False

        if self.results.pose_landmarks:
            self.pose_detected = True

            # Captura puramente a ponta do pé esquerdo (LEFT_FOOT_INDEX = 31)
            self.feet1_x, self.feet1_y = (
                self.results.pose_landmarks.landmark[31].x,
                self.results.pose_landmarks.landmark[31].y,
            )
            
            # Captura puramente a ponta do pé direito (RIGHT_FOOT_INDEX = 32)
            self.feet2_x, self.feet2_y = (
                self.results.pose_landmarks.landmark[32].x,
                self.results.pose_landmarks.landmark[32].y,
            )

            # Ponto médio (média simples) entre as duas pontas dos pés
            x: float = (self.feet1_x + self.feet2_x) / 2
            y: float = (self.feet1_y + self.feet2_y) / 2

            # Verifica se a média dos pés está dentro da área de calibração
            self.feet_in_calibration_area = is_point_in_calibration_area(x, y)

            # Debug a cada 60 frames
            self.debug_counter += 1
            debug = self.debug_counter % 60 == 0

            # Atualiza o centro comum calculado a partir da média
            self.feet_x, self.feet_y = posicao(x, y, debug=False)

            mp_drawing.draw_landmarks(
                image,
                self.results.pose_landmarks,
                mp_poses.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
            )
        else:
            self.pose_detected = False
            self.feet_in_calibration_area = False

        self.image = image
        return image

    def get_feet_center(self) -> tuple[int | None, int | None]:
        if self.feet_x is not None and self.feet_y is not None:
            return (self.feet_x, self.feet_y)
        return (None, None)

    def get_left_foot(self) -> tuple[int | None, int | None]:
        if self.feet1_x is not None and self.feet1_y is not None:
            return posicao(self.feet1_x, self.feet1_y)
        return (None, None)

    def get_right_foot(self) -> tuple[int | None, int | None]:
        if self.feet2_x is not None and self.feet2_y is not None:
            return posicao(self.feet2_x, self.feet2_y)
        return (None, None)

    def display_feet(self) -> None:
        if self.image is not None:
            cv2.imshow("image", self.image)
            cv2.waitKey(1)

    def is_feet_closed(self) -> None:
        pass