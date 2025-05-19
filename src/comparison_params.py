from dataclasses import dataclass, field
from typing import Dict, Optional
from enum import Enum
import json
from pathlib import Path

class DistanceMetric(Enum):
    EUCLIDEAN = "euclidean"
    DTW = "dtw"

@dataclass
class ComparisonParams:
    metric: DistanceMetric = DistanceMetric.EUCLIDEAN
    tolerance: float = 0.1
    landmark_weights: Dict[str, float] = field(default_factory=dict)
    temporal_sync: bool = True
    normalize: bool = True

    def __post_init__(self):
        """Valida os parâmetros após a inicialização."""
        self.validate()

    def validate(self) -> None:
        """Valida os parâmetros de comparação."""
        # Validação da métrica
        if isinstance(self.metric, str):
            try:
                self.metric = DistanceMetric(self.metric)
            except ValueError:
                raise ValueError(f"Métrica inválida: {self.metric}")
        elif not isinstance(self.metric, DistanceMetric):
            raise ValueError(f"Métrica inválida: {self.metric}")
        if not 0 <= self.tolerance <= 1:
            raise ValueError("Tolerância deve estar entre 0 e 1")
        
        if self.landmark_weights:
            for weight in self.landmark_weights.values():
                if not 0 <= weight <= 1:
                    raise ValueError("Pesos dos landmarks devem estar entre 0 e 1")

    def to_dict(self) -> dict:
        """Converte os parâmetros para um dicionário."""
        return {
            "metric": self.metric.value,
            "tolerance": self.tolerance,
            "landmark_weights": self.landmark_weights,
            "temporal_sync": self.temporal_sync,
            "normalize": self.normalize
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ComparisonParams':
        """Cria uma instância a partir de um dicionário."""
        if "metric" in data:
            data["metric"] = DistanceMetric(data["metric"])
        return cls(**data)

    def save_to_file(self, filepath: str) -> None:
        """Salva os parâmetros em um arquivo JSON."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load_from_file(cls, filepath: str) -> 'ComparisonParams':
        """Carrega os parâmetros de um arquivo JSON."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def __str__(self) -> str:
        """Retorna uma representação em string dos parâmetros."""
        return (
            f"Parâmetros de Comparação:\n"
            f"  Métrica: {self.metric.value}\n"
            f"  Tolerância: {self.tolerance}\n"
            f"  Pesos dos Landmarks: {self.landmark_weights}\n"
            f"  Sincronização Temporal: {self.temporal_sync}\n"
            f"  Normalização: {self.normalize}"
        ) 
