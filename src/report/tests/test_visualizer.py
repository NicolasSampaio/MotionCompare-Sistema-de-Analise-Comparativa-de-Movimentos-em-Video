import pytest
import numpy as np
from ..visualizer.base import BaseVisualizer
from ..visualizer.plots import PlotManager
from ..visualizer.cli import VisualizerCLI
from rich.prompt import Prompt

@pytest.fixture
def sample_report_data():
    """Fixture com dados de exemplo para testes."""
    return {
        'frames': [
            {
                'reference_pose': {
                    'keypoints': np.array([[0, 0], [1, 1], [2, 2]]),
                    'connections': [(0, 1), (1, 2)]
                },
                'comparison_pose': {
                    'keypoints': np.array([[0.1, 0.1], [1.1, 1.1], [2.1, 2.1]]),
                    'connections': [(0, 1), (1, 2)]
                },
                'metrics': {
                    'similarity': 0.95,
                    'distance': 0.1
                }
            },
            {
                'reference_pose': {
                    'keypoints': np.array([[0, 0], [1, 1], [2, 2]]),
                    'connections': [(0, 1), (1, 2)]
                },
                'comparison_pose': {
                    'keypoints': np.array([[0.2, 0.2], [1.2, 1.2], [2.2, 2.2]]),
                    'connections': [(0, 1), (1, 2)]
                },
                'metrics': {
                    'similarity': 0.90,
                    'distance': 0.2
                }
            }
        ],
        'similarity': {
            'matrix': np.array([[1.0, 0.8], [0.8, 1.0]]),
            'scores': [0.95, 0.90]
        }
    }

class DummyVisualizer(BaseVisualizer):
    def plot_similarity(self):
        pass
    def plot_frame_comparison(self, frame_idx: int):
        pass
    def show_frame_details(self, frame_idx: int):
        pass

def test_base_visualizer_initialization(sample_report_data):
    """Testa a inicialização do visualizador base."""
    visualizer = DummyVisualizer(sample_report_data)
    assert visualizer.total_frames == 2
    assert visualizer.current_frame == 0

def test_get_frame_data(sample_report_data):
    """Testa a obtenção de dados de um frame específico."""
    visualizer = DummyVisualizer(sample_report_data)
    
    # Teste frame válido
    frame_data = visualizer.get_frame_data(0)
    assert 'reference_pose' in frame_data
    assert 'comparison_pose' in frame_data
    assert 'metrics' in frame_data
    
    # Teste frame inválido
    with pytest.raises(IndexError):
        visualizer.get_frame_data(2)

def test_get_similarity_data(sample_report_data):
    """Testa a obtenção de dados de similaridade."""
    visualizer = DummyVisualizer(sample_report_data)
    similarity_data = visualizer.get_similarity_data()
    
    assert 'matrix' in similarity_data
    assert 'scores' in similarity_data
    assert isinstance(similarity_data['matrix'], np.ndarray)
    assert isinstance(similarity_data['scores'], list)

def test_plot_manager_initialization():
    """Testa a inicialização do gerenciador de plots."""
    plot_manager = PlotManager()
    assert hasattr(plot_manager, 'colors')
    assert len(plot_manager.colors) == 8

def test_visualizer_cli_initialization(sample_report_data):
    """Testa a inicialização do visualizador CLI."""
    cli = VisualizerCLI(sample_report_data)
    assert cli.running
    assert hasattr(cli, 'console')
    assert hasattr(cli, 'plot_manager')

def test_visualizer_cli_commands(sample_report_data, monkeypatch):
    """Testa os comandos do visualizador CLI."""
    cli = VisualizerCLI(sample_report_data)
    
    # Teste comando inválido
    with pytest.raises(ValueError):
        cli._handle_command('x')
    
    # Teste navegação
    cli._next_frame()
    assert cli.current_frame == 1
    
    cli._previous_frame()
    assert cli.current_frame == 0
    
    # Mock para Prompt.ask
    monkeypatch.setattr(Prompt, "ask", lambda *args, **kwargs: "0")
    
    # Teste navegação para frame específico
    cli._navigate_to_frame()
    assert cli.current_frame == 0  # Mantém o frame atual se inválido 
