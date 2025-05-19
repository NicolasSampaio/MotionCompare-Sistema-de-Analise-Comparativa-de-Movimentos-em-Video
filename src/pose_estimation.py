import cv2
import mediapipe as mp
import numpy as np
import logging
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class PoseLandmark:
    """Classe para representar um landmark do corpo."""
    x: float
    y: float
    z: float
    visibility: float

class PoseExtractor:
    """Classe responsável por extrair pontos-chave do corpo usando MediaPipe."""
    
    def __init__(self, min_detection_confidence: float = 0.5, min_tracking_confidence: float = 0.5):
        """
        Inicializa o extrator de pose.
        
        Args:
            min_detection_confidence: Confiança mínima para detecção (0.0 a 1.0)
            min_tracking_confidence: Confiança mínima para tracking (0.0 a 1.0)
        """
        if not 0.0 <= min_detection_confidence <= 1.0:
            raise ValueError("min_detection_confidence deve estar entre 0.0 e 1.0")
        if not 0.0 <= min_tracking_confidence <= 1.0:
            raise ValueError("min_tracking_confidence deve estar entre 0.0 e 1.0")
            
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        logger.info("PoseExtractor inicializado com sucesso")

    def process_frame(self, frame: np.ndarray) -> Optional[Dict[int, PoseLandmark]]:
        """
        Processa um frame e extrai os landmarks do corpo.
        
        Args:
            frame: Frame do vídeo em formato numpy array
            
        Returns:
            Dicionário com os landmarks detectados ou None se nenhum landmark for detectado
            
        Raises:
            ValueError: Se o frame for None ou inválido
        """
        if frame is None:
            raise ValueError("Frame não pode ser None")
            
        if not isinstance(frame, np.ndarray):
            raise ValueError("Frame deve ser um numpy array")
            
        if len(frame.shape) != 3 or frame.shape[2] != 3:
            raise ValueError("Frame deve ser uma imagem colorida (3 canais)")
            
        try:
            # Converte BGR para RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Processa o frame
            results = self.pose.process(frame_rgb)
            
            if not results.pose_landmarks:
                logger.warning("Nenhum landmark detectado no frame")
                return None
            
            # Extrai os landmarks
            landmarks = {}
            for idx, landmark in enumerate(results.pose_landmarks.landmark):
                landmarks[idx] = PoseLandmark(
                    x=landmark.x,
                    y=landmark.y,
                    z=landmark.z,
                    visibility=landmark.visibility
                )
            
            return landmarks
            
        except Exception as e:
            logger.error(f"Erro ao processar frame: {str(e)}")
            return None

    def process_video(self, video_path: str, progress_callback=None) -> List[Optional[Dict[int, PoseLandmark]]]:
        """
        Processa um vídeo completo e extrai os landmarks de cada frame.
        
        Args:
            video_path: Caminho para o arquivo de vídeo
            progress_callback: Função de callback para reportar progresso (frame_count, total_frames)
            
        Returns:
            Lista de dicionários com os landmarks de cada frame
            
        Raises:
            ValueError: Se o caminho do vídeo for inválido ou o vídeo não puder ser aberto
        """
        if not video_path or not isinstance(video_path, str):
            raise ValueError("Caminho do vídeo inválido")
            
        # Verifica se o arquivo existe
        if not os.path.exists(video_path):
            raise ValueError(f"Arquivo de vídeo não encontrado: {video_path}")
            
        logger.info(f"Tentando abrir vídeo: {os.path.abspath(video_path)}")
            
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Não foi possível abrir o vídeo: {video_path}")
            
            # Obtém informações do vídeo
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            logger.info(f"Vídeo aberto com sucesso. Frames: {total_frames}, FPS: {fps}, Resolução: {width}x{height}")
            
            frame_landmarks = []
            frame_count = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    logger.info("Fim do vídeo alcançado")
                    break
                
                landmarks = self.process_frame(frame)
                frame_landmarks.append(landmarks)
                
                frame_count += 1
                if progress_callback:
                    progress_callback(frame_count, total_frames)
            
            cap.release()
            logger.info(f"Processamento do vídeo concluído. Total de frames processados: {frame_count}")
            return frame_landmarks
            
        except Exception as e:
            logger.error(f"Erro ao processar vídeo: {str(e)}")
            return []

    def __del__(self):
        """Libera recursos do MediaPipe."""
        self.pose.close() 
