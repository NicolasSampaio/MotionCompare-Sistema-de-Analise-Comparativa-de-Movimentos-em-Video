import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import logging
from dataclasses import dataclass
from scipy.spatial.distance import euclidean
from scipy.signal import resample
from scipy.optimize import linear_sum_assignment
import mediapipe as mp
from datetime import datetime

from .comparison_params import ComparisonParams, DistanceMetric
from .comparison_results import ComparisonResults, DanceComparison
from .pose_models import PoseLandmark

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class FrameData:
    """Classe para armazenar dados de um frame."""
    landmarks: np.ndarray  # Array de landmarks (x, y, z)
    confidence: np.ndarray  # Array de confiança para cada landmark
    timestamp: float  # Timestamp do frame
    
    def __post_init__(self):
        """Garante que os landmarks sejam do tipo float."""
        self.landmarks = self.landmarks.astype(np.float64)
        self.confidence = self.confidence.astype(np.float64)

class ComparadorMovimento:
    def __init__(self, min_visibility: float = 0.5):
        """
        Inicializa o comparador de movimento.
        
        Args:
            min_visibility: Visibilidade mínima para considerar um landmark válido
        """
        self.min_visibility = min_visibility
        
    def compare_videos(self, video1_landmarks: List[Optional[Dict[int, PoseLandmark]]],
                      video2_landmarks: List[Optional[Dict[int, PoseLandmark]]],
                      video1_fps: float, video2_fps: float,
                      video1_resolution: Tuple[int, int],
                      video2_resolution: Tuple[int, int],
                      video1_landmark_weights: Optional[Dict[str, float]] = None,
                      video2_landmark_weights: Optional[Dict[str, float]] = None) -> ComparisonResults:
        """
        Compara dois vídeos usando os landmarks extraídos.
        
        Args:
            video1_landmarks: Lista de landmarks do primeiro vídeo
            video2_landmarks: Lista de landmarks do segundo vídeo
            video1_fps: FPS do primeiro vídeo
            video2_fps: FPS do segundo vídeo
            video1_resolution: Resolução do primeiro vídeo (width, height)
            video2_resolution: Resolução do segundo vídeo (width, height)
            video1_landmark_weights: Pesos dos landmarks do primeiro vídeo
            video2_landmark_weights: Pesos dos landmarks do segundo vídeo
            
        Returns:
            ComparisonResults: Resultados da comparação
        """
        # Valida os dados de entrada
        if not video1_landmarks or not video2_landmarks:
            raise ValueError("Listas de landmarks não podem estar vazias")
            
        # Prepara os pesos dos landmarks
        if video1_landmark_weights is None:
            video1_landmark_weights = {str(i): 1.0 for i in range(33)}
        if video2_landmark_weights is None:
            video2_landmark_weights = {str(i): 1.0 for i in range(33)}
            
        # Calcula o número de frames processados
        video1_processed_frames = sum(1 for frame in video1_landmarks if frame is not None)
        video2_processed_frames = sum(1 for frame in video2_landmarks if frame is not None)
        
        # Calcula o número de landmarks por frame
        video1_landmarks_per_frame = len(next(frame for frame in video1_landmarks if frame is not None))
        video2_landmarks_per_frame = len(next(frame for frame in video2_landmarks if frame is not None))
        
        # Compara os frames
        frame_comparisons = []
        frame_scores = []
        for frame_number, (frame1, frame2) in enumerate(zip(video1_landmarks, video2_landmarks)):
            if frame1 is None or frame2 is None:
                continue
                
            # Verifica se todos os landmarks têm visibilidade menor que min_visibility
            all_low_visibility1 = all(l.visibility < self.min_visibility for l in frame1.values())
            all_low_visibility2 = all(l.visibility < self.min_visibility for l in frame2.values())
            
            if all_low_visibility1 or all_low_visibility2:
                continue
                
            # Calcula a similaridade entre os frames
            similarity_score, landmark_similarities = self._compare_frames(
                frame1, frame2,
                video1_landmark_weights,
                video2_landmark_weights
            )
            
            # Calcula as métricas de alinhamento
            alignment_metrics = self._calculate_alignment_metrics(frame1, frame2)
            
            # Cria o objeto de comparação do frame
            frame_comparison = DanceComparison(
                frame_number=frame_number,
                timestamp=frame_number / video1_fps,
                similarity_score=float(similarity_score),
                landmark_similarities=landmark_similarities,
                alignment_metrics=alignment_metrics
            )
            
            frame_comparisons.append(frame_comparison)
            frame_scores.append(float(similarity_score))
            
        # Calcula as métricas gerais
        overall_metrics = self._calculate_overall_metrics(frame_comparisons)
        
        # Calcula o score global
        global_score = float(np.mean(frame_scores)) if frame_scores else 0.0
        
        # Cria o objeto de resultados
        results = ComparisonResults(
            video1_path="",  # Será preenchido pelo chamador
            video2_path="",  # Será preenchido pelo chamador
            video1_fps=video1_fps,
            video2_fps=video2_fps,
            video1_resolution=video1_resolution,
            video2_resolution=video2_resolution,
            video1_total_frames=len(video1_landmarks),
            video2_total_frames=len(video2_landmarks),
            video1_processed_frames=video1_processed_frames,
            video2_processed_frames=video2_processed_frames,
            video1_landmarks_per_frame=video1_landmarks_per_frame,
            video2_landmarks_per_frame=video2_landmarks_per_frame,
            video1_landmark_weights=video1_landmark_weights,
            video2_landmark_weights=video2_landmark_weights,
            frame_comparisons=frame_comparisons,
            overall_metrics=overall_metrics,
            global_score=global_score,
            frame_scores=frame_scores,
            metadata={
                "comparison_date": datetime.now().isoformat(),
                "comparison_duration": len(frame_comparisons) / video1_fps,
                "comparison_version": "1.0.0"
            }
        )
        
        return results
        
    def _compare_frames(self, frame1: Dict[int, PoseLandmark],
                       frame2: Dict[int, PoseLandmark],
                       weights1: Dict[str, float],
                       weights2: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
        """
        Compara dois frames usando os landmarks.
        
        Args:
            frame1: Landmarks do primeiro frame
            frame2: Landmarks do segundo frame
            weights1: Pesos dos landmarks do primeiro frame
            weights2: Pesos dos landmarks do segundo frame
            
        Returns:
            Tuple[float, Dict[str, float]]: Similaridade geral e similaridades por landmark
        """
        landmark_similarities = {}
        total_weight = 0.0
        weighted_sum = 0.0
        
        for landmark_id in frame1.keys():
            if landmark_id not in frame2:
                continue
                
            landmark1 = frame1[landmark_id]
            landmark2 = frame2[landmark_id]
            
            # Verifica a visibilidade
            if landmark1.visibility < self.min_visibility or landmark2.visibility < self.min_visibility:
                continue
                
            # Calcula a similaridade do landmark
            similarity = self._calculate_landmark_similarity(landmark1, landmark2)
            
            # Aplica os pesos
            weight = (weights1[str(landmark_id)] + weights2[str(landmark_id)]) / 2
            weighted_sum += similarity * weight
            total_weight += weight
            
            landmark_similarities[str(landmark_id)] = float(similarity)
            
        # Calcula a similaridade geral
        overall_similarity = float(weighted_sum / total_weight if total_weight > 0 else 0.0)
        
        return overall_similarity, landmark_similarities
        
    def _calculate_landmark_similarity(self, landmark1: PoseLandmark,
                                     landmark2: PoseLandmark) -> float:
        """
        Calcula a similaridade entre dois landmarks.
        
        Args:
            landmark1: Primeiro landmark
            landmark2: Segundo landmark
            
        Returns:
            float: Similaridade entre os landmarks (0.0 a 1.0)
        """
        # Calcula a distância euclidiana normalizada
        distance = np.sqrt(
            (landmark1.x - landmark2.x) ** 2 +
            (landmark1.y - landmark2.y) ** 2 +
            (landmark1.z - landmark2.z) ** 2
        )
        
        # Converte a distância para similaridade (0.0 a 1.0)
        similarity = 1.0 / (1.0 + distance)
        
        return similarity
        
    def _calculate_alignment_metrics(self, frame1: Dict[int, PoseLandmark],
                                   frame2: Dict[int, PoseLandmark]) -> Dict:
        """
        Calcula as métricas de alinhamento entre dois frames.
        
        Args:
            frame1: Landmarks do primeiro frame
            frame2: Landmarks do segundo frame
            
        Returns:
            Dict: Métricas de alinhamento
        """
        # Extrai as coordenadas dos landmarks
        coords1 = np.array([[l.x, l.y, l.z] for l in frame1.values()])
        coords2 = np.array([[l.x, l.y, l.z] for l in frame2.values()])
        
        # Calcula o centro de massa
        center1 = np.mean(coords1, axis=0)
        center2 = np.mean(coords2, axis=0)
        
        # Calcula a translação
        translation = center2 - center1
        
        # Calcula a escala
        scale1 = np.std(coords1)
        scale2 = np.std(coords2)
        scale = scale2 / scale1 if scale1 > 0 else 1.0
        
        # Calcula a rotação (simplificado)
        rotation = [0.0, 0.0, 0.0]  # TODO: Implementar cálculo de rotação
        
        return {
            "translation": translation.tolist(),
            "rotation": rotation,
            "scale": scale
        }
        
    def _calculate_overall_metrics(self, frame_comparisons: List[DanceComparison]) -> Dict:
        """
        Calcula as métricas gerais da comparação.
        
        Args:
            frame_comparisons: Lista de comparações de frames
            
        Returns:
            Dict: Métricas gerais
        """
        if not frame_comparisons:
            return {
                "average_similarity": 0.0,
                "min_similarity": 0.0,
                "max_similarity": 0.0,
                "std_similarity": 0.0,
                "alignment_quality": 0.0,
                "temporal_alignment": 0.0
            }
            
        # Extrai as similaridades
        similarities = [fc.similarity_score for fc in frame_comparisons]
        
        # Calcula as métricas
        average_similarity = np.mean(similarities)
        min_similarity = np.min(similarities)
        max_similarity = np.max(similarities)
        std_similarity = np.std(similarities)
        
        # Calcula a qualidade do alinhamento
        alignment_qualities = [
            np.mean([
                abs(m["translation"][0]),
                abs(m["translation"][1]),
                abs(m["translation"][2]),
                abs(m["rotation"][0]),
                abs(m["rotation"][1]),
                abs(m["rotation"][2]),
                abs(1.0 - m["scale"])
            ])
            for fc in frame_comparisons
            for m in [fc.alignment_metrics]
        ]
        alignment_quality = 1.0 - np.mean(alignment_qualities)
        
        # Calcula o alinhamento temporal
        temporal_alignment = 1.0 - (std_similarity / average_similarity if average_similarity > 0 else 0.0)
        
        return {
            "average_similarity": float(average_similarity),
            "min_similarity": float(min_similarity),
            "max_similarity": float(max_similarity),
            "std_similarity": float(std_similarity),
            "alignment_quality": float(alignment_quality),
            "temporal_alignment": float(temporal_alignment)
        }
