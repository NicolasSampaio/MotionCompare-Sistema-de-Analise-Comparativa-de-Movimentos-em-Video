import pytest
from src.comparison_params import ComparisonParams, DistanceMetric
import json
import os
from pathlib import Path

def test_default_params():
    params = ComparisonParams()
    assert params.metric == DistanceMetric.EUCLIDEAN
    assert params.tolerance == 0.1
    assert params.landmark_weights == {}
    assert params.temporal_sync is True
    assert params.normalize is True

def test_custom_params():
    params = ComparisonParams(
        metric=DistanceMetric.DTW,
        tolerance=0.5,
        landmark_weights={"shoulder": 0.8, "hip": 0.6},
        temporal_sync=False,
        normalize=False
    )
    assert params.metric == DistanceMetric.DTW
    assert params.tolerance == 0.5
    assert params.landmark_weights == {"shoulder": 0.8, "hip": 0.6}
    assert params.temporal_sync is False
    assert params.normalize is False

def test_validation():
    # Teste de tolerância inválida
    with pytest.raises(ValueError):
        ComparisonParams(tolerance=1.5)

    # Teste de peso de landmark inválido
    with pytest.raises(ValueError):
        ComparisonParams(landmark_weights={"shoulder": 1.5})

def test_to_dict():
    params = ComparisonParams(
        metric=DistanceMetric.DTW,
        tolerance=0.5,
        landmark_weights={"shoulder": 0.8}
    )
    data = params.to_dict()
    assert data["metric"] == "dtw"
    assert data["tolerance"] == 0.5
    assert data["landmark_weights"] == {"shoulder": 0.8}

def test_from_dict():
    data = {
        "metric": "dtw",
        "tolerance": 0.5,
        "landmark_weights": {"shoulder": 0.8}
    }
    params = ComparisonParams.from_dict(data)
    assert params.metric == DistanceMetric.DTW
    assert params.tolerance == 0.5
    assert params.landmark_weights == {"shoulder": 0.8}

def test_save_and_load():
    # Criar diretório temporário para testes
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    
    filepath = test_dir / "test_params.json"
    
    # Criar e salvar parâmetros
    original_params = ComparisonParams(
        metric=DistanceMetric.DTW,
        tolerance=0.5,
        landmark_weights={"shoulder": 0.8}
    )
    original_params.save_to_file(str(filepath))
    
    # Carregar parâmetros
    loaded_params = ComparisonParams.load_from_file(str(filepath))
    
    # Verificar se são iguais
    assert loaded_params.metric == original_params.metric
    assert loaded_params.tolerance == original_params.tolerance
    assert loaded_params.landmark_weights == original_params.landmark_weights
    
    # Limpar arquivo de teste
    os.remove(filepath) 
