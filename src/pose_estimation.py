import cv2
import mediapipe as mp
import numpy as np
import logging
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from .pose_storage import PoseStorage
from .pose_models import PoseLandmark
from .comparison_params import ComparisonParams
from .comparison_results import ComparisonResults
from .comparador_movimento import DanceComparison

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PoseExtractor:
    """Classe responsável por extrair pontos-chave do corpo usando MediaPipe."""
    
    def __init__(self, min_detection_confidence: float = 0.5, 
                 min_tracking_confidence: float = 0.5,
                 comparison_params: Optional[ComparisonParams] = None):
        """
        Inicializa o extrator de pose.
        
        Args:
            min_detection_confidence: Confiança mínima para detecção (0.0 a 1.0)
            min_tracking_confidence: Confiança mínima para tracking (0.0 a 1.0)
            comparison_params: Parâmetros de comparação (opcional)
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
        self.comparison_params = comparison_params or ComparisonParams()
        logger.info("PoseExtractor inicializado com sucesso")

        self.landmarks = []
        self.fps = 0.0
        self.resolution = (0, 0)
        self.total_frames = 0

    def close(self):
        """Libera explicitamente os recursos do MediaPipe."""
        if hasattr(self, 'pose') and self.pose:
            self.pose.close()
            self.pose = None # Define como None após fechar

    def normalize_landmarks(self, landmarks: Dict[int, PoseLandmark]) -> Dict[int, PoseLandmark]:
        """
        Normaliza os landmarks se a normalização estiver ativada.
        
        Args:
            landmarks: Dicionário com os landmarks
            
        Returns:
            Dicionário com os landmarks normalizados
        """
        if not self.comparison_params.normalize:
            return landmarks
            
        # Encontra os limites do corpo
        x_coords = [lm.x for lm in landmarks.values()]
        y_coords = [lm.y for lm in landmarks.values()]
        z_coords = [lm.z for lm in landmarks.values()]
        
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        min_z, max_z = min(z_coords), max(z_coords)
        
        # Calcula as escalas
        scale_x = max_x - min_x if max_x > min_x else 1.0
        scale_y = max_y - min_y if max_y > min_y else 1.0
        scale_z = max_z - min_z if max_z > min_z else 1.0
        
        # Normaliza os landmarks
        normalized = {}
        for idx, landmark in landmarks.items():
            normalized[idx] = PoseLandmark(
                x=(landmark.x - min_x) / scale_x,
                y=(landmark.y - min_y) / scale_y,
                z=(landmark.z - min_z) / scale_z,
                visibility=landmark.visibility
            )
        
        return normalized

    def apply_landmark_weights(self, landmarks: Dict[int, PoseLandmark]) -> Dict[int, PoseLandmark]:
        """
        Aplica os pesos aos landmarks se definidos.
        
        Args:
            landmarks: Dicionário com os landmarks
            
        Returns:
            Dicionário com os landmarks ponderados
        """
        if not self.comparison_params.landmark_weights:
            return landmarks
            
        weighted = {}
        for idx, landmark in landmarks.items():
            # Obtém o nome do landmark (ex: "shoulder", "hip", etc.)
            landmark_name = self.mp_pose.PoseLandmark(idx).name.lower()
            
            # Aplica o peso se definido, senão usa 1.0
            weight = self.comparison_params.landmark_weights.get(landmark_name, 1.0)
            
            # Aplica o peso apenas se for maior que 0
            if weight > 0:
                weighted[idx] = PoseLandmark(
                    x=landmark.x * weight,
                    y=landmark.y * weight,
                    z=landmark.z * weight,
                    visibility=landmark.visibility
                )
            else:
                weighted[idx] = landmark
        
        return weighted

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
            
            # Aplica as transformações configuradas
            landmarks = self.normalize_landmarks(landmarks)
            landmarks = self.apply_landmark_weights(landmarks)
            
            return landmarks
            
        except Exception as e:
            logger.error(f"Erro ao processar frame: {str(e)}")
            return None

    def process_video(self, video_path: str, output_path: Optional[str] = None,
                     resolution: Optional[Tuple[int, int]] = None,
                     progress_callback: Optional[callable] = None) -> bool:
        """
        Processa um vídeo para extrair os landmarks de pose.
        
        Args:
            video_path: Caminho do vídeo
            output_path: Caminho para salvar o vídeo processado (opcional)
            resolution: Resolução do vídeo processado (opcional)
            progress_callback: Função de callback para atualizar o progresso (opcional)
            
        Returns:
            bool: True se o processamento foi bem-sucedido
        """
        try:
            # Abre o vídeo
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Erro ao abrir vídeo: {video_path}")
                return False
                
            # Obtém informações do vídeo
            self.fps = cap.get(cv2.CAP_PROP_FPS)
            self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Atualiza a resolução do extrator
            self.resolution = (width, height)
            
            # Define a resolução para processamento se especificada
            if resolution:
                width, height = resolution
                
            # Prepara o writer se output_path for especificado
            writer = None
            if output_path:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                writer = cv2.VideoWriter(output_path, fourcc, self.fps, (width, height))
                
            # Processa cada frame
            frame_count = 0
            self.landmarks = []
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Redimensiona o frame se necessário
                if resolution:
                    frame = cv2.resize(frame, resolution)
                    
                # Processa o frame
                landmarks = self.process_frame(frame)
                self.landmarks.append(landmarks)
                
                # Salva o frame processado se necessário
                if writer and landmarks:
                    # Desenha os landmarks no frame
                    for landmark in landmarks.values():
                        x = int(landmark.x * width)
                        y = int(landmark.y * height)
                        cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)
                    writer.write(frame)
                    
                # Atualiza o progresso
                frame_count += 1
                if progress_callback:
                    progress_callback(frame_count, self.total_frames)
                    
            # Limpa os recursos
            cap.release()
            if writer:
                writer.release()
                
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar vídeo: {str(e)}")
            return False

    def get_landmarks(self) -> List[Optional[Dict[int, PoseLandmark]]]:
        """
        Retorna os landmarks extraídos.
        
        Returns:
            Lista de dicionários com os landmarks de cada frame
        """
        return self.landmarks
        
    def get_fps(self) -> float:
        """
        Retorna o FPS do vídeo.
        
        Returns:
            float: FPS do vídeo
        """
        return self.fps
        
    def get_resolution(self) -> Tuple[int, int]:
        """
        Retorna a resolução do vídeo.
        
        Returns:
            Tuple[int, int]: Resolução do vídeo (width, height)
        """
        return self.resolution
        
    def get_total_frames(self) -> int:
        """
        Retorna o total de frames do vídeo.
        
        Returns:
            int: Total de frames
        """
        return self.total_frames

    def compare_videos(self, video1_path: str, video2_path: str,
                      output_path: Optional[str] = None) -> Optional[ComparisonResults]:
        """
        Compara dois vídeos.
        
        Args:
            video1_path: Caminho do primeiro vídeo
            video2_path: Caminho do segundo vídeo
            output_path: Caminho para salvar o vídeo processado (opcional)
            
        Returns:
            ComparisonResults ou None se a comparação falhar
        """
        try:
            # Processa o primeiro vídeo
            if not self.process_video(video1_path, output_path):
                return None
                
            video1_landmarks = self.landmarks
            video1_fps = self.fps
            video1_resolution = self.resolution
            video1_total_frames = self.total_frames
            
            # Processa o segundo vídeo
            if not self.process_video(video2_path, output_path):
                return None
                
            video2_landmarks = self.landmarks
            video2_fps = self.fps
            video2_resolution = self.resolution
            video2_total_frames = self.total_frames
            
            # Cria o objeto de resultados
            results = ComparisonResults(
                video1_path=video1_path,
                video2_path=video2_path,
                video1_fps=video1_fps,
                video2_fps=video2_fps,
                video1_resolution=video1_resolution,
                video2_resolution=video2_resolution,
                video1_total_frames=video1_total_frames,
                video2_total_frames=video2_total_frames,
                video1_processed_frames=len([l for l in video1_landmarks if l is not None]),
                video2_processed_frames=len([l for l in video2_landmarks if l is not None]),
                video1_landmarks_per_frame=len(next(l for l in video1_landmarks if l is not None)),
                video2_landmarks_per_frame=len(next(l for l in video2_landmarks if l is not None)),
                video1_landmark_weights={str(i): 1.0 for i in range(33)},
                video2_landmark_weights={str(i): 1.0 for i in range(33)},
                frame_comparisons=[],  # Será preenchido pelo comparador
                overall_metrics={},  # Será preenchido pelo comparador
                metadata={
                    "comparison_date": "2024-01-01T00:00:00",  # Será atualizado pelo comparador
                    "comparison_duration": 0.0,  # Será atualizado pelo comparador
                    "comparison_version": "1.0.0"
                }
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Erro ao comparar vídeos: {str(e)}")
            return None

    def __del__(self):
        """Libera recursos do MediaPipe."""
        # Chama o método close para garantir a liberação dos recursos
        self.close()
