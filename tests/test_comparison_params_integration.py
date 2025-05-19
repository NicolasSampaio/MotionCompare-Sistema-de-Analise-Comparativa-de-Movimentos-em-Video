import pytest
import numpy as np
from pathlib import Path
import json
import os

from src.comparison_params import ComparisonParams, DistanceMetric
from src.comparador_movimento import DanceComparison, FrameData

def create_mock_frame_data(n_frames: int, n_landmarks: int = 33) -> list:
    """Cria dados de frame simulados para testes."""
    frames = []
    for i in range(n_frames):
        # Cria landmarks aleatórios
        landmarks = np.random.rand(n_landmarks, 3)
        # Cria confianças aleatórias
        confidence = np.random.rand(n_landmarks)
        frames.append(FrameData(
            landmarks=landmarks,
            confidence=confidence,
            timestamp=i/30.0  # Simula 30 FPS
        ))
    return frames

def test_comparison_with_default_params():
    """Testa a comparação com parâmetros padrão."""
    # Cria dados simulados
    video1_data = create_mock_frame_data(100)
    video2_data = create_mock_frame_data(100)
    
    # Cria comparador com parâmetros padrão
    comparison = DanceComparison(video1_data, video2_data)
    
    # Verifica se a comparação funciona
    similarity = comparison.get_similarity()
    assert 0 <= similarity <= 1
    
    # Verifica se os scores por frame existem
    frame_scores = comparison.get_frame_scores()
    assert len(frame_scores) > 0

def test_comparison_with_dtw():
    """Testa a comparação usando DTW."""
    # Cria dados simulados
    video1_data = create_mock_frame_data(100)
    video2_data = create_mock_frame_data(80)  # Diferente duração para testar DTW
    
    # Cria parâmetros com DTW
    params = ComparisonParams(
        metric=DistanceMetric.DTW,
        tolerance=0.2,
        temporal_sync=True
    )
    
    # Cria comparador
    comparison = DanceComparison(video1_data, video2_data, params)
    
    # Verifica se a comparação funciona
    similarity = comparison.get_similarity()
    assert 0 <= similarity <= 1
    
    # Verifica se o caminho de alinhamento existe
    result = comparison.compare()
    assert 'alignment_path' in result

def test_comparison_with_landmark_weights():
    """Testa a comparação com pesos de landmarks."""
    # Cria dados simulados
    video1_data = create_mock_frame_data(100)
    video2_data = create_mock_frame_data(100)
    
    # Cria parâmetros com pesos
    params = ComparisonParams(
        landmark_weights={
            "shoulder": 0.8,
            "hip": 0.6,
            "knee": 0.4
        }
    )
    
    # Cria comparador
    comparison = DanceComparison(video1_data, video2_data, params)
    
    # Verifica se a comparação funciona
    similarity = comparison.get_similarity()
    assert 0 <= similarity <= 1

def test_comparison_without_normalization():
    """Testa a comparação sem normalização."""
    # Cria dados simulados
    video1_data = create_mock_frame_data(100)
    video2_data = create_mock_frame_data(100)
    
    # Cria parâmetros sem normalização
    params = ComparisonParams(normalize=False)
    
    # Cria comparador
    comparison = DanceComparison(video1_data, video2_data, params)
    
    # Verifica se a comparação funciona
    similarity = comparison.get_similarity()
    assert 0 <= similarity <= 1

def test_comparison_without_temporal_sync():
    """Testa a comparação sem sincronização temporal."""
    # Cria dados simulados
    video1_data = create_mock_frame_data(100)
    video2_data = create_mock_frame_data(100)
    
    # Cria parâmetros sem sincronização temporal
    params = ComparisonParams(temporal_sync=False)
    
    # Cria comparador
    comparison = DanceComparison(video1_data, video2_data, params)
    
    # Verifica se a comparação funciona
    similarity = comparison.get_similarity()
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
