import pytest
import numpy as np
from datetime import datetime

from src.comparador_movimento import ComparadorMovimento
from src.pose_models import PoseLandmark
from src.comparison_results import ComparisonResults, DanceComparison

@pytest.fixture
def comparador():
    """Fixture que cria uma instância do ComparadorMovimento."""
    return ComparadorMovimento(min_visibility=0.5)

@pytest.fixture
def sample_landmarks():
    """Fixture que cria landmarks de exemplo."""
    return {
        0: PoseLandmark(x=0.1, y=0.2, z=0.3, visibility=0.9),
        1: PoseLandmark(x=0.4, y=0.5, z=0.6, visibility=0.8)
    }

@pytest.fixture
def sample_video_landmarks(sample_landmarks):
    """Fixture que cria landmarks de vídeo de exemplo."""
    return [
        sample_landmarks,
        {
            0: PoseLandmark(x=0.11, y=0.21, z=0.31, visibility=0.9),
            1: PoseLandmark(x=0.41, y=0.51, z=0.61, visibility=0.8)
        },
        None,  # Frame sem landmarks
        sample_landmarks
    ]

def test_comparador_initialization(comparador):
    """Testa a inicialização do ComparadorMovimento."""
    assert comparador.min_visibility == 0.5

def test_compare_videos(comparador, sample_video_landmarks):
    """Testa a comparação de vídeos."""
    # Compara dois vídeos idênticos
    results = comparador.compare_videos(
        video1_landmarks=sample_video_landmarks,
        video2_landmarks=sample_video_landmarks,
        video1_fps=30.0,
        video2_fps=30.0,
        video1_resolution=(640, 480),
        video2_resolution=(640, 480)
    )
    
    assert isinstance(results, ComparisonResults)
    assert results.video1_fps == 30.0
    assert results.video2_fps == 30.0
    assert results.video1_resolution == (640, 480)
    assert results.video2_resolution == (640, 480)
    assert results.video1_total_frames == 4
    assert results.video2_total_frames == 4
    assert results.video1_processed_frames == 3
    assert results.video2_processed_frames == 3
    assert len(results.frame_comparisons) == 3  # Apenas frames com landmarks
    
    # Verifica as métricas gerais
    assert results.overall_metrics["average_similarity"] > 0.9  # Vídeos idênticos
    assert results.overall_metrics["min_similarity"] > 0.9
    assert results.overall_metrics["max_similarity"] > 0.9
    assert results.overall_metrics["std_similarity"] < 0.1
    assert results.overall_metrics["alignment_quality"] > 0.9
    assert results.overall_metrics["temporal_alignment"] > 0.9

def test_compare_frames(comparador, sample_landmarks):
    """Testa a comparação de frames."""
    # Cria um frame ligeiramente diferente
    frame2 = {
        0: PoseLandmark(x=0.11, y=0.21, z=0.31, visibility=0.9),
        1: PoseLandmark(x=0.41, y=0.51, z=0.61, visibility=0.8)
    }
    
    # Compara os frames
    similarity, landmark_similarities = comparador._compare_frames(
        frame1=sample_landmarks,
        frame2=frame2,
        weights1={"0": 1.0, "1": 1.0},
        weights2={"0": 1.0, "1": 1.0}
    )
    
    assert isinstance(similarity, float)
    assert 0.0 <= similarity <= 1.0
    assert similarity > 0.9  # Frames muito similares
    
    assert isinstance(landmark_similarities, dict)
    assert len(landmark_similarities) == 2
    assert all(0.0 <= s <= 1.0 for s in landmark_similarities.values())

def test_calculate_landmark_similarity(comparador):
    """Testa o cálculo de similaridade entre landmarks."""
    landmark1 = PoseLandmark(x=0.1, y=0.2, z=0.3, visibility=0.9)
    landmark2 = PoseLandmark(x=0.11, y=0.21, z=0.31, visibility=0.9)
    
    similarity = comparador._calculate_landmark_similarity(landmark1, landmark2)
    
    assert isinstance(similarity, float)
    assert 0.0 <= similarity <= 1.0
    assert similarity > 0.9  # Landmarks muito similares

def test_calculate_alignment_metrics(comparador, sample_landmarks):
    """Testa o cálculo de métricas de alinhamento."""
    # Cria um frame ligeiramente deslocado
    frame2 = {
        0: PoseLandmark(x=0.2, y=0.3, z=0.4, visibility=0.9),
        1: PoseLandmark(x=0.5, y=0.6, z=0.7, visibility=0.8)
    }
    
    metrics = comparador._calculate_alignment_metrics(sample_landmarks, frame2)
    
    assert isinstance(metrics, dict)
    assert "translation" in metrics
    assert "rotation" in metrics
    assert "scale" in metrics
    
    assert len(metrics["translation"]) == 3
    assert len(metrics["rotation"]) == 3
    assert isinstance(metrics["scale"], float)

def test_calculate_overall_metrics(comparador):
    """Testa o cálculo de métricas gerais."""
    # Cria comparações de frames de exemplo
    frame_comparisons = [
        DanceComparison(
            frame_number=0,
            timestamp=0.0,
            similarity_score=0.95,
            landmark_similarities={"0": 0.95, "1": 0.95},
            alignment_metrics={
                "translation": [0.0, 0.0, 0.0],
                "rotation": [0.0, 0.0, 0.0],
                "scale": 1.0
            }
        ),
        DanceComparison(
            frame_number=1,
            timestamp=1/30.0,
            similarity_score=0.90,
            landmark_similarities={"0": 0.90, "1": 0.90},
            alignment_metrics={
                "translation": [0.1, 0.1, 0.1],
                "rotation": [0.1, 0.1, 0.1],
                "scale": 1.1
            }
        )
    ]
    
    metrics = comparador._calculate_overall_metrics(frame_comparisons)
    
    assert isinstance(metrics, dict)
    assert "average_similarity" in metrics
    assert "min_similarity" in metrics
    assert "max_similarity" in metrics
    assert "std_similarity" in metrics
    assert "alignment_quality" in metrics
    assert "temporal_alignment" in metrics
    
    assert metrics["average_similarity"] == 0.925
    assert metrics["min_similarity"] == 0.90
    assert metrics["max_similarity"] == 0.95
    assert abs(metrics["std_similarity"] - 0.025) < 1e-10  # Usa uma tolerância para comparação de ponto flutuante
    assert 0.0 <= metrics["alignment_quality"] <= 1.0
    assert 0.0 <= metrics["temporal_alignment"] <= 1.0

def test_compare_videos_with_weights(comparador, sample_video_landmarks):
    """Testa a comparação de vídeos com pesos diferentes para os landmarks."""
    # Define pesos diferentes para os landmarks
    weights1 = {"0": 1.0, "1": 0.5}
    weights2 = {"0": 1.0, "1": 0.5}
    
    results = comparador.compare_videos(
        video1_landmarks=sample_video_landmarks,
        video2_landmarks=sample_video_landmarks,
        video1_fps=30.0,
        video2_fps=30.0,
        video1_resolution=(640, 480),
        video2_resolution=(640, 480),
        video1_landmark_weights=weights1,
        video2_landmark_weights=weights2
    )
    
    assert results.video1_landmark_weights == weights1
    assert results.video2_landmark_weights == weights2

def test_compare_videos_with_low_visibility(comparador):
    """Testa a comparação de vídeos com landmarks de baixa visibilidade."""
    # Cria landmarks com visibilidade baixa
    low_visibility_landmarks = {
        0: PoseLandmark(x=0.1, y=0.2, z=0.3, visibility=0.3),
        1: PoseLandmark(x=0.4, y=0.5, z=0.6, visibility=0.3)
    }

    # Cria landmarks com visibilidade alta
    high_visibility_landmarks = {
        0: PoseLandmark(x=0.1, y=0.2, z=0.3, visibility=0.9),
        1: PoseLandmark(x=0.4, y=0.5, z=0.6, visibility=0.9)
    }

    video1_landmarks = [low_visibility_landmarks]
    video2_landmarks = [high_visibility_landmarks]

    results = comparador.compare_videos(
        video1_landmarks=video1_landmarks,
        video2_landmarks=video2_landmarks,
        video1_fps=30.0,
        video2_fps=30.0,
        video1_resolution=(640, 480),
        video2_resolution=(640, 480)
    )

    # Como a visibilidade é menor que min_visibility, não deve haver comparações
    assert len(results.frame_comparisons) == 0
    assert results.overall_metrics["average_similarity"] == 0.0 
