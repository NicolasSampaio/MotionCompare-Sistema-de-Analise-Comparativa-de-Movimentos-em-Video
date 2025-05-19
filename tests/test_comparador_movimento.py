import pytest
import numpy as np
from src.comparador_movimento import DanceComparison, FrameData

@pytest.fixture
def sample_frame_data():
    """Fixture para criar dados de frame de exemplo."""
    landmarks = np.array([
        [0, 0, 0],
        [1, 1, 1],
        [2, 2, 2]
    ])
    confidence = np.array([0.9, 0.8, 0.7])
    return FrameData(landmarks=landmarks, confidence=confidence, timestamp=0.0)

@pytest.fixture
def sample_video_data(sample_frame_data):
    """Fixture para criar dados de vídeo de exemplo."""
    return [sample_frame_data] * 3

def test_frame_distance(sample_frame_data):
    """Testa o cálculo de distância entre frames."""
    frame1 = sample_frame_data
    frame2 = FrameData(
        landmarks=frame1.landmarks + 1,
        confidence=frame1.confidence,
        timestamp=0.0
    )
    
    comparison = DanceComparison([frame1], [frame2], normalize=False)
    distance = comparison._frame_distance(frame1, frame2)
    
    assert isinstance(distance, float)
    assert distance > 0

def test_normalize_scale(sample_video_data):
    """Testa a normalização de escala."""
    comparison = DanceComparison(sample_video_data, sample_video_data)
    comparison._normalize_scale()
    
    for frame in comparison.video1:
        # Verifica se o centro está próximo de zero
        assert np.allclose(np.mean(frame.landmarks, axis=0), 0, atol=1e-6)
        # Verifica se a escala está normalizada
        assert np.max(np.abs(frame.landmarks)) <= 1

def test_compare_euclidean(sample_video_data):
    """Testa a comparação usando distância euclidiana."""
    comparison = DanceComparison(sample_video_data, sample_video_data)
    result = comparison._compare_euclidean()
    
    assert 'global_score' in result
    assert 'frame_scores' in result
    assert 'metric' in result
    assert result['metric'] == 'euclidean'
    assert len(result['frame_scores']) == len(sample_video_data)

def test_compare_dtw(sample_video_data):
    """Testa a comparação usando DTW."""
    comparison = DanceComparison(sample_video_data, sample_video_data)
    result = comparison._compare_dtw()
    
    assert 'global_score' in result
    assert 'frame_scores' in result
    assert 'metric' in result
    assert 'alignment_path' in result
    assert result['metric'] == 'dtw'

def test_get_global_score(sample_video_data):
    """Testa o cálculo do score global."""
    comparison = DanceComparison(sample_video_data, sample_video_data)
    score = comparison.get_global_score()
    
    assert isinstance(score, float)
    assert score >= 0

def test_get_frame_scores(sample_video_data):
    """Testa o cálculo dos scores por frame."""
    comparison = DanceComparison(sample_video_data, sample_video_data)
    scores = comparison.get_frame_scores()
    
    assert isinstance(scores, list)
    assert len(scores) == len(sample_video_data)
    assert all(isinstance(score, float) for score in scores)

def test_invalid_metric(sample_video_data):
    """Testa o comportamento com métrica inválida."""
    comparison = DanceComparison(sample_video_data, sample_video_data)
    
    with pytest.raises(ValueError):
        comparison.compare(metric='invalid_metric')

def test_different_length_videos():
    """Testa o comportamento com vídeos de comprimentos diferentes."""
    video1 = [FrameData(
        landmarks=np.array([[0, 0, 0]]),
        confidence=np.array([0.9]),
        timestamp=0.0
    )] * 3
    
    video2 = [FrameData(
        landmarks=np.array([[0, 0, 0]]),
        confidence=np.array([0.9]),
        timestamp=0.0
    )] * 5
    
    comparison = DanceComparison(video1, video2)
    result = comparison.compare(metric='dtw')
    
    assert 'alignment_path' in result
    assert len(result['alignment_path']) > 0 
