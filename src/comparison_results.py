from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import json
import logging
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class ComparisonResults:
    """
    Estrutura de dados para armazenar os resultados brutos da comparação de movimentos.

    Campos principais:
        - global_score (float): Score global de similaridade entre os vídeos.
        - frame_scores (List[float]): Scores de similaridade por frame.
        - temporal_alignment (dict): Detalhes da comparação temporal.
        - landmark_details (dict): Informações detalhadas por landmark.
        - metadata (dict): Metadados da análise (caminhos, datas, parâmetros, etc).
        - Outros campos: informações sobre vídeos, resoluções, pesos, métricas gerais, etc.

    Métodos principais:
        - to_dict(): Serializa os resultados para dicionário Python.
        - to_json(): Serializa os resultados para string JSON.
        - from_dict(data): Cria uma instância a partir de um dicionário.
        - from_json(json_str): Cria uma instância a partir de uma string JSON.
        - validate(): Valida a integridade dos dados.
        - log_results(): Registra os resultados no log do sistema.

    Exemplo de uso:
        >>> results = ComparisonResults(global_score=0.9, frame_scores=[0.8, 0.9], ...)
        >>> results.validate()
        True
        >>> json_str = results.to_json()
        >>> novo = ComparisonResults.from_json(json_str)
        >>> novo.global_score
        0.9
    """
    video1_path: str = ""
    video2_path: str = ""
    video1_fps: float = 0.0
    video2_fps: float = 0.0
    video1_resolution: tuple = (0, 0)
    video2_resolution: tuple = (0, 0)
    video1_total_frames: int = 0
    video2_total_frames: int = 0
    video1_processed_frames: int = 0
    video2_processed_frames: int = 0
    video1_landmarks_per_frame: int = 0
    video2_landmarks_per_frame: int = 0
    video1_landmark_weights: dict = None
    video2_landmark_weights: dict = None
    frame_comparisons: list = None
    overall_metrics: dict = None
    metadata: dict = None
    # Campos antigos para compatibilidade
    global_score: float = 0.0
    frame_scores: list = None
    temporal_alignment: dict = None
    landmark_details: dict = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.frame_scores is None:
            self.frame_scores = []
        if self.temporal_alignment is None:
            self.temporal_alignment = {}
        if self.landmark_details is None:
            self.landmark_details = {}
        if self.video1_landmark_weights is None:
            self.video1_landmark_weights = {}
        if self.video2_landmark_weights is None:
            self.video2_landmark_weights = {}
        if self.frame_comparisons is None:
            self.frame_comparisons = []
        if self.overall_metrics is None:
            self.overall_metrics = {}
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializa os resultados para um dicionário Python.
        """
        return asdict(self)

    def to_json(self) -> str:
        """
        Serializa os resultados para uma string JSON.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComparisonResults':
        """
        Cria uma instância de ComparisonResults a partir de um dicionário.
        """
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> 'ComparisonResults':
        """
        Cria uma instância de ComparisonResults a partir de uma string JSON.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def validate(self) -> bool:
        """
        Valida a integridade dos resultados.
        """
        try:
            # Validação básica dos campos
            if not isinstance(self.global_score, (int, float)):
                logger.error("global_score deve ser um número")
                return False

            if not isinstance(self.frame_scores, list):
                logger.error("frame_scores deve ser uma lista")
                return False

            if not all(isinstance(score, (int, float)) for score in self.frame_scores):
                logger.error("Todos os scores em frame_scores devem ser números")
                return False

            if not isinstance(self.temporal_alignment, dict):
                logger.error("temporal_alignment deve ser um dicionário")
                return False

            if not isinstance(self.landmark_details, dict):
                logger.error("landmark_details deve ser um dicionário")
                return False

            if not isinstance(self.metadata, dict):
                logger.error("metadata deve ser um dicionário")
                return False

            return True

        except Exception as e:
            logger.error(f"Erro na validação dos resultados: {str(e)}")
            return False

    def log_results(self):
        """
        Registra os resultados no log do sistema.
        """
        logger.info(f"Resultados da comparação - Score Global: {self.global_score}")
        logger.debug(f"Detalhes completos: {self.to_json()}")

@dataclass
class DanceComparison:
    """
    Estrutura de dados para armazenar a comparação de um frame entre dois vídeos.
    """
    frame_number: int = 0
    timestamp: float = 0.0
    similarity_score: float = 0.0
    landmark_similarities: dict = None
    alignment_metrics: dict = None

    def __post_init__(self):
        if self.landmark_similarities is None:
            self.landmark_similarities = {}
        if self.alignment_metrics is None:
            self.alignment_metrics = {
                "translation": [0.0, 0.0, 0.0],
                "rotation": [0.0, 0.0, 0.0],
                "scale": 1.0
            }
        # Garante que similarity_score seja um float
        self.similarity_score = float(self.similarity_score)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializa os resultados para um dicionário Python.
        """
        return asdict(self)

    def to_json(self) -> str:
        """
        Serializa os resultados para uma string JSON.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DanceComparison':
        """
        Cria uma instância de DanceComparison a partir de um dicionário.
        """
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> 'DanceComparison':
        """
        Cria uma instância de DanceComparison a partir de uma string JSON.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def validate(self) -> bool:
        """
        Valida a integridade dos resultados.
        """
        try:
            # Validação básica dos campos
            if not isinstance(self.similarity_score, (int, float)):
                logger.error("similarity_score deve ser um número")
                return False

            if not isinstance(self.landmark_similarities, dict):
                logger.error("landmark_similarities deve ser um dicionário")
                return False

            if not isinstance(self.alignment_metrics, dict):
                logger.error("alignment_metrics deve ser um dicionário")
                return False

            return True

        except Exception as e:
            logger.error(f"Erro na validação dos resultados: {str(e)}")
            return False

    def log_results(self):
        """
        Registra os resultados no log do sistema.
        """
        logger.info(f"Resultados da comparação - Similaridade: {self.similarity_score}")
        logger.debug(f"Detalhes completos: {self.to_json()}")

    def get_similarity(self) -> float:
        """
        Retorna o score de similaridade do frame.
        
        Returns:
            float: Score de similaridade (0.0 a 1.0)
        """
        return self.similarity_score

    def get_frame_scores(self) -> List[float]:
        """
        Retorna os scores de similaridade por landmark.
        
        Returns:
            List[float]: Lista de scores por landmark
        """
        return [float(score) for score in self.landmark_similarities.values()]

    def calculate_similarity(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """
        Calcula a similaridade entre dois frames.
        """
        # Implemente a lógica para calcular a similaridade entre dois frames
        # Retorne um valor entre 0 e 1
        pass

    def calculate_alignment(self, frame1: np.ndarray, frame2: np.ndarray) -> dict:
        """
        Calcula a alinhamento entre dois frames.
        """
        # Implemente a lógica para calcular o alinhamento entre dois frames
        # Retorne um dicionário com as métricas de alinhamento
        pass

    def calculate_landmark_similarity(self, landmark1: dict, landmark2: dict) -> float:
        """
        Calcula a similaridade entre dois landmarks.
        """
        # Implemente a lógica para calcular a similaridade entre dois landmarks
        # Retorne um valor entre 0 e 1
        pass

    def calculate_landmark_alignment(self, landmark1: dict, landmark2: dict) -> dict:
        """
        Calcula o alinhamento entre dois landmarks.
        """
        # Implemente a lógica para calcular o alinhamento entre dois landmarks
        # Retorne um dicionário com as métricas de alinhamento
        pass
