from abc import ABC, abstractmethod
from typing import Dict, Any, List
import matplotlib.pyplot as plt
import numpy as np

class BaseVisualizer(ABC):
    """Classe base abstrata para visualização de resultados de análise de dança."""
    
    def __init__(self, report_data: Dict[str, Any]):
        """
        Inicializa o visualizador com os dados do relatório.
        
        Args:
            report_data: Dicionário contendo os dados do relatório de análise
        """
        self.report_data = report_data
        self.current_frame = 0
        self.total_frames = len(report_data.get('frames', []))
        
    @abstractmethod
    def plot_similarity(self) -> None:
        """Plota o gráfico de similaridade entre as sequências."""
        pass
    
    @abstractmethod
    def plot_frame_comparison(self, frame_idx: int) -> None:
        """
        Plota a comparação detalhada de um frame específico.
        
        Args:
            frame_idx: Índice do frame a ser visualizado
        """
        pass
    
    @abstractmethod
    def show_frame_details(self, frame_idx: int) -> None:
        """
        Mostra detalhes específicos de um frame.
        
        Args:
            frame_idx: Índice do frame a ser visualizado
        """
        pass
    
    def get_frame_data(self, frame_idx: int) -> Dict[str, Any]:
        """
        Retorna os dados de um frame específico.
        
        Args:
            frame_idx: Índice do frame desejado
            
        Returns:
            Dicionário com os dados do frame
        """
        if 0 <= frame_idx < self.total_frames:
            return self.report_data['frames'][frame_idx]
        raise IndexError(f"Frame {frame_idx} fora dos limites (0-{self.total_frames-1})")
    
    def get_similarity_data(self) -> Dict[str, Any]:
        """
        Retorna os dados de similaridade do relatório.
        
        Returns:
            Dicionário com os dados de similaridade
        """
        return self.report_data.get('similarity', {}) 
