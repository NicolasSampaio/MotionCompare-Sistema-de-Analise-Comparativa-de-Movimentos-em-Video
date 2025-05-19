import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import logging
from dataclasses import dataclass
from scipy.spatial.distance import euclidean
from scipy.signal import resample
from scipy.optimize import linear_sum_assignment
import mediapipe as mp

from .comparison_params import ComparisonParams, DistanceMetric

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

class DanceComparison:
    """Classe principal para comparação de movimentos de dança."""
    
    def __init__(self, video1_data: List[FrameData], video2_data: List[FrameData], 
                 comparison_params: Optional[ComparisonParams] = None):
        """
        Inicializa o comparador de dança.
        
        Args:
            video1_data: Lista de FrameData do primeiro vídeo
            video2_data: Lista de FrameData do segundo vídeo
            comparison_params: Parâmetros de comparação (opcional)
        """
        self.video1 = video1_data
        self.video2 = video2_data
        self.comparison_params = comparison_params or ComparisonParams()
        self.mp_pose = mp.solutions.pose
        
        if self.comparison_params.normalize:
            self._normalize_videos()
        logger.info("Inicializado comparador de dança com dois vídeos")
        
    def _normalize_videos(self) -> None:
        """Normaliza os vídeos para comparação."""
        # Normalização temporal
        if self.comparison_params.temporal_sync:
            self._normalize_temporal()
        # Normalização espacial
        self._normalize_spatial()
        
    def _normalize_temporal(self) -> None:
        """Normaliza os vídeos temporalmente usando DTW."""
        # Implementação do DTW para alinhamento temporal
        cost_matrix = self._compute_cost_matrix()
        path = self._compute_dtw_path(cost_matrix)
        self._align_videos(path)
        
    def _normalize_spatial(self) -> None:
        """Normaliza os vídeos espacialmente."""
        # Normalização de escala
        self._normalize_scale()
        # Normalização de orientação
        self._normalize_orientation()
        
    def _normalize_scale(self) -> None:
        """Normaliza a escala dos vídeos."""
        for video in [self.video1, self.video2]:
            for frame in video:
                # Calcula o centro de massa
                center = np.mean(frame.landmarks, axis=0)
                # Normaliza em relação ao centro
                frame.landmarks -= center
                # Normaliza a escala
                scale = np.max(np.abs(frame.landmarks))
                if scale > 0:
                    frame.landmarks /= scale
                    
    def _normalize_orientation(self) -> None:
        """Normaliza a orientação dos vídeos."""
        # Implementação da normalização de orientação
        # usando PCA ou alinhamento de eixos principais
        pass
        
    def _compute_cost_matrix(self) -> np.ndarray:
        """Computa a matriz de custo para DTW."""
        n = len(self.video1)
        m = len(self.video2)
        cost_matrix = np.zeros((n, m))
        
        for i in range(n):
            for j in range(m):
                cost_matrix[i, j] = self._frame_distance(
                    self.video1[i], self.video2[j]
                )
                
        return cost_matrix
        
    def _frame_distance(self, frame1: FrameData, frame2: FrameData) -> float:
        """Calcula a distância entre dois frames."""
        # Aplica os pesos dos landmarks se definidos
        weights = np.ones_like(frame1.confidence)
        if self.comparison_params.landmark_weights:
            for idx, landmark_name in enumerate(self.mp_pose.PoseLandmark):
                weight = self.comparison_params.landmark_weights.get(landmark_name.name.lower(), 1.0)
                weights[idx] = weight
        
        # Combina com os pesos de confiança
        weights *= np.minimum(frame1.confidence, frame2.confidence)
        
        return np.sum(weights * np.linalg.norm(
            frame1.landmarks - frame2.landmarks, axis=1
        ))
        
    def _compute_dtw_path(self, cost_matrix: np.ndarray) -> List[Tuple[int, int]]:
        """Computa o caminho DTW."""
        n, m = cost_matrix.shape
        dtw_matrix = np.zeros((n + 1, m + 1))
        dtw_matrix.fill(np.inf)
        dtw_matrix[0, 0] = 0
        
        # Preenche a matriz DTW
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                dtw_matrix[i, j] = cost_matrix[i-1, j-1] + min(
                    dtw_matrix[i-1, j],    # Inserção
                    dtw_matrix[i, j-1],    # Deleção
                    dtw_matrix[i-1, j-1]   # Substituição
                )
                
        # Backtrack para encontrar o caminho
        path = []
        i, j = n, m
        while i > 0 and j > 0:
            path.append((i-1, j-1))
            if i == 1:
                j -= 1
            elif j == 1:
                i -= 1
            else:
                min_idx = np.argmin([
                    dtw_matrix[i-1, j],
                    dtw_matrix[i, j-1],
                    dtw_matrix[i-1, j-1]
                ])
                if min_idx == 0:
                    i -= 1
                elif min_idx == 1:
                    j -= 1
                else:
                    i -= 1
                    j -= 1
                    
        return list(reversed(path))
        
    def _align_videos(self, path: List[Tuple[int, int]]) -> None:
        """Alinha os vídeos usando o caminho DTW."""
        # Implementação do alinhamento dos vídeos
        pass
        
    def compare(self) -> Dict:
        """
        Compara os dois vídeos usando os parâmetros configurados.
        
        Returns:
            Dicionário com resultados da comparação
        """
        if self.comparison_params.metric == DistanceMetric.EUCLIDEAN:
            return self._compare_euclidean()
        elif self.comparison_params.metric == DistanceMetric.DTW:
            return self._compare_dtw()
        else:
            raise ValueError(f"Métrica {self.comparison_params.metric} não suportada")
            
    def _compare_euclidean(self) -> Dict:
        """Compara os vídeos usando distância euclidiana."""
        frame_scores = []
        for frame1, frame2 in zip(self.video1, self.video2):
            score = self._frame_distance(frame1, frame2)
            frame_scores.append(score)
            
        return {
            'global_score': np.mean(frame_scores),
            'frame_scores': frame_scores,
            'metric': 'euclidean',
            'similarity': 1.0 - min(1.0, np.mean(frame_scores) / self.comparison_params.tolerance)
        }
        
    def _compare_dtw(self) -> Dict:
        """Compara os vídeos usando DTW."""
        cost_matrix = self._compute_cost_matrix()
        path = self._compute_dtw_path(cost_matrix)
        
        # Calcula scores por frame
        frame_scores = []
        for i, j in path:
            frame_scores.append(cost_matrix[i, j])
            
        return {
            'global_score': np.mean(frame_scores),
            'frame_scores': frame_scores,
            'metric': 'dtw',
            'alignment_path': path,
            'similarity': 1.0 - min(1.0, np.mean(frame_scores) / self.comparison_params.tolerance)
        }
        
    def get_global_score(self) -> float:
        """Retorna o score global de similaridade."""
        return self.compare()['global_score']
        
    def get_frame_scores(self) -> List[float]:
        """Retorna os scores por frame."""
        return self.compare()['frame_scores']
        
    def get_similarity(self) -> float:
        """Retorna o valor de similaridade normalizado (0-1)."""
        return self.compare()['similarity']
