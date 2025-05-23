import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Any, List, Tuple
import seaborn as sns

class PlotManager:
    """Gerenciador de plots para visualização de resultados de análise de dança."""
    
    def __init__(self):
        """Inicializa o gerenciador de plots com configurações padrão."""
        sns.set_theme()
        self.colors = plt.cm.Set2(np.linspace(0, 1, 8))
        
    def plot_similarity_heatmap(self, similarity_matrix: np.ndarray, 
                              title: str = "Matriz de Similaridade") -> None:
        """
        Plota um heatmap da matriz de similaridade.
        
        Args:
            similarity_matrix: Matriz numpy com valores de similaridade
            title: Título do gráfico
        """
        plt.figure(figsize=(10, 8))
        plt.imshow(similarity_matrix, cmap='viridis', aspect='auto')
        plt.colorbar(label='Similaridade')
        plt.title(title)
        plt.xlabel('Frame Referência')
        plt.ylabel('Frame Comparação')
        plt.tight_layout()
        
    def plot_similarity_line(self, similarity_scores: List[float], 
                           title: str = "Similaridade por Frame") -> None:
        """
        Plota um gráfico de linha mostrando a similaridade ao longo dos frames.
        
        Args:
            similarity_scores: Lista de scores de similaridade
            title: Título do gráfico
        """
        plt.figure(figsize=(12, 6))
        plt.plot(similarity_scores, color=self.colors[0], linewidth=2)
        plt.title(title)
        plt.xlabel('Frame')
        plt.ylabel('Score de Similaridade')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
    def plot_frame_comparison(self, frame_data: Dict[str, Any], 
                            title: str = "Comparação de Frame") -> None:
        """
        Plota a comparação detalhada de um frame específico.
        
        Args:
            frame_data: Dicionário com dados do frame
            title: Título do gráfico
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot referência
        self._plot_pose(ax1, frame_data['reference_pose'], 
                       title='Pose Referência', color=self.colors[0])
        
        # Plot comparação
        self._plot_pose(ax2, frame_data['comparison_pose'], 
                       title='Pose Comparação', color=self.colors[1])
        
        plt.suptitle(title)
        plt.tight_layout()
        
    def _plot_pose(self, ax: plt.Axes, pose_data: Dict[str, Any], 
                  title: str, color: Tuple[float, float, float, float]) -> None:
        """
        Plota uma pose específica em um subplot.
        
        Args:
            ax: Eixo matplotlib para plotagem
            pose_data: Dados da pose
            title: Título do subplot
            color: Cor para plotagem
        """
        keypoints = pose_data['keypoints']
        connections = pose_data.get('connections', [])
        
        # Plot keypoints
        ax.scatter(keypoints[:, 0], keypoints[:, 1], c=[color], s=50)
        
        # Plot connections
        for connection in connections:
            start_idx, end_idx = connection
            ax.plot([keypoints[start_idx, 0], keypoints[end_idx, 0]],
                   [keypoints[start_idx, 1], keypoints[end_idx, 1]],
                   color=color, linewidth=2)
            
        ax.set_title(title)
        ax.invert_yaxis()  # Inverte eixo Y para corresponder à imagem
        ax.set_aspect('equal')
        
    def show(self) -> None:
        """Mostra todos os plots ativos."""
        plt.show()
        
    def close_all(self) -> None:
        """Fecha todas as figuras ativas."""
        plt.close('all') 
