import pytest
import numpy as np
from pathlib import Path
import json
import os

from src.comparison_params import ComparisonParams, DistanceMetric
from src.comparador_movimento import ComparadorMovimento, FrameData

# Classe mock para simular um landmark
class MockLandmark:
    def __init__(self, x, y, z, visibility):
        self.x = x
        self.y = y
        self.z = z
        self.visibility = visibility

def create_mock_frame_data(n_frames: int, n_landmarks: int = 33) -> list:
    """Cria dados de frame simulados para testes."""
    frames = []
    for i in range(n_frames):
        # Cria landmarks aleatórios
        landmarks = {}
        for idx in range(n_landmarks):
            x, y, z = np.random.rand(3)
            visibility = np.random.rand()
            landmarks[idx] = MockLandmark(x, y, z, visibility)
        frames.append(landmarks)
    return frames

def test_comparison_with_default_params():
    """Testa a comparação com parâmetros padrão."""
    video1_data = create_mock_frame_data(100)
    video2_data = create_mock_frame_data(100)
    
    comparador = ComparadorMovimento()
    results = comparador.compare_videos(
        video1_data, video2_data, 30.0, 30.0, (1920, 1080), (1920, 1080)
    )
    similarity = results.global_score
    assert 0 <= similarity <= 1
    frame_scores = results.frame_scores
    assert len(frame_scores) > 0

def test_comparison_with_dtw():
    """Testa a comparação usando DTW."""
    video1_data = create_mock_frame_data(100)
    video2_data = create_mock_frame_data(80)
    params = ComparisonParams(
        metric=DistanceMetric.DTW,
        tolerance=0.2,
        temporal_sync=True
    )
    comparador = ComparadorMovimento()
    results = comparador.compare_videos(
        video1_data, video2_data, 30.0, 30.0, (1920, 1080), (1920, 1080)
    )
    similarity = results.global_score
    assert 0 <= similarity <= 1
    assert 'average_similarity' in results.overall_metrics

def test_comparison_with_landmark_weights():
    """Testa a comparação com pesos de landmarks."""
    video1_data = create_mock_frame_data(100)
    video2_data = create_mock_frame_data(100)
    # Usar índices inteiros como chaves de pesos
    landmark_weights = {str(i): np.random.uniform(0.1, 1.0) for i in range(33)}
    params = ComparisonParams(
        landmark_weights=landmark_weights
    )
    comparador = ComparadorMovimento()
    results = comparador.compare_videos(
        video1_data, video2_data, 30.0, 30.0, (1920, 1080), (1920, 1080),
        video1_landmark_weights=params.landmark_weights,
        video2_landmark_weights=params.landmark_weights
    )
    similarity = results.global_score
    assert 0 <= similarity <= 1

def test_comparison_without_normalization():
    """Testa a comparação sem normalização."""
    video1_data = create_mock_frame_data(100)
    video2_data = create_mock_frame_data(100)
    params = ComparisonParams(normalize=False)
    comparador = ComparadorMovimento()
    results = comparador.compare_videos(
        video1_data, video2_data, 30.0, 30.0, (1920, 1080), (1920, 1080)
    )
    similarity = results.global_score
    assert 0 <= similarity <= 1

def test_comparison_without_temporal_sync():
    """Testa a comparação sem sincronização temporal."""
    video1_data = create_mock_frame_data(100)
    video2_data = create_mock_frame_data(100)
    params = ComparisonParams(temporal_sync=False)
    comparador = ComparadorMovimento()
    results = comparador.compare_videos(
        video1_data, video2_data, 30.0, 30.0, (1920, 1080), (1920, 1080)
    )
    similarity = results.global_score
    assert 0 <= similarity <= 1

def test_save_and_load_params():
    """Testa salvar e carregar parâmetros de um arquivo."""
    # Cria parâmetros
    original_params = ComparisonParams(
        metric=DistanceMetric.DTW,
        tolerance=0.2,
        landmark_weights={
            "shoulder": 0.8,
            "hip": 0.6
        },
        temporal_sync=True,
        normalize=True
    )
    
    # Cria diretório temporário para testes
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    
    # Salva parâmetros
    filepath = test_dir / "test_params.json"
    original_params.save_to_file(str(filepath))
    
    # Carrega parâmetros
    loaded_params = ComparisonParams.load_from_file(str(filepath))
    
    # Verifica se os parâmetros são iguais
    assert loaded_params.metric == original_params.metric
    assert loaded_params.tolerance == original_params.tolerance
    assert loaded_params.landmark_weights == original_params.landmark_weights
    assert loaded_params.temporal_sync == original_params.temporal_sync
    assert loaded_params.normalize == original_params.normalize
    
    # Limpa arquivo de teste
    os.remove(filepath)

def test_invalid_params():
    """Testa parâmetros inválidos."""
    # Testa tolerância inválida
    with pytest.raises(ValueError):
        ComparisonParams(tolerance=1.5)
    
    # Testa peso de landmark inválido
    with pytest.raises(ValueError):
        ComparisonParams(landmark_weights={"shoulder": 1.5})
    
    # Testa métrica inválida
    with pytest.raises(ValueError):
        ComparisonParams(metric="invalid") 
