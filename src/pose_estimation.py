import cv2
import mediapipe as mp
import numpy as np
import logging
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from .pose_storage import PoseStorage
from .pose_models import PoseLandmark

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
        self.storage = PoseStorage()
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
            last_progress_update = 0
            update_interval = max(1, total_frames // 200)  # Atualiza a cada 0.5% do progresso
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    logger.info("Fim do vídeo alcançado")
                    break
                
                landmarks = self.process_frame(frame)
                frame_landmarks.append(landmarks)
                
                frame_count += 1
                if progress_callback and (frame_count - last_progress_update >= update_interval):
                    progress_callback(frame_count, total_frames)
                    last_progress_update = frame_count
            
            # Garante que o último progresso seja reportado
            if progress_callback and frame_count > last_progress_update:
                progress_callback(frame_count, total_frames)
            
            cap.release()
            logger.info(f"Processamento do vídeo concluído. Total de frames processados: {frame_count}")
            
            # Salva os dados de pose
            self.storage.save_pose_data(
                video_path=video_path,
                fps=fps,
                resolution=(width, height),
                total_frames=total_frames,
                frame_landmarks=frame_landmarks
            )
            
            return frame_landmarks
            
        except Exception as e:
            logger.error(f"Erro ao processar vídeo: {str(e)}")
            return []

    def load_pose_data(self, video_path: str) -> Optional[List[Optional[Dict[int, PoseLandmark]]]]:
        """
        Carrega os dados de pose de um vídeo.
        
        Args:
            video_path: Caminho do vídeo
            
        Returns:
            Lista de dicionários com os landmarks de cada frame ou None se os dados não forem encontrados
        """
        pose_data = self.storage.load_pose_data(video_path)
        if pose_data is None:
            return None
            
        # Converte os frames de volta para o formato original
        frame_landmarks = [None] * pose_data.total_frames
        for frame in pose_data.frames:
            frame_landmarks[frame.frame_number] = frame.landmarks
            
        return frame_landmarks

    def __del__(self):
        """Libera recursos do MediaPipe."""
        self.pose.close() 
