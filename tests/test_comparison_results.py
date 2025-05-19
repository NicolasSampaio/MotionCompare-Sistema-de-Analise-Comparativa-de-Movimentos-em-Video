import pytest
from datetime import datetime
from src.comparison_results import ComparisonResults

@pytest.fixture
def sample_results():
    return ComparisonResults(
        global_score=0.85,
        frame_scores=[0.8, 0.85, 0.9],
        temporal_alignment={"offset": 0, "scale": 1.0},
        landmark_details={
            "left_shoulder": {"score": 0.9, "confidence": 0.95},
            "right_shoulder": {"score": 0.85, "confidence": 0.92}
        },
        metadata={
            "video1": "dance1.mp4",
            "video2": "dance2.mp4",
            "timestamp": datetime.now().isoformat()
        }
    )

def test_comparison_results_creation(sample_results):
    assert isinstance(sample_results, ComparisonResults)
    assert sample_results.global_score == 0.85
    assert len(sample_results.frame_scores) == 3
    assert "left_shoulder" in sample_results.landmark_details

def test_comparison_results_serialization(sample_results):
    # Teste de serialização para dicionário
    result_dict = sample_results.to_dict()
    assert isinstance(result_dict, dict)
    assert result_dict["global_score"] == 0.85

    # Teste de serialização para JSON
    json_str = sample_results.to_json()
    assert isinstance(json_str, str)
    assert "global_score" in json_str

def test_comparison_results_deserialization(sample_results):
    # Teste de deserialização a partir de dicionário
    result_dict = sample_results.to_dict()
    new_results = ComparisonResults.from_dict(result_dict)
    assert new_results.global_score == sample_results.global_score
    assert new_results.frame_scores == sample_results.frame_scores

    # Teste de deserialização a partir de JSON
    json_str = sample_results.to_json()
    new_results = ComparisonResults.from_json(json_str)
    assert new_results.global_score == sample_results.global_score
    assert new_results.frame_scores == sample_results.frame_scores

def test_comparison_results_validation(sample_results):
    assert sample_results.validate() is True

    # Teste com dados inválidos
    invalid_results = ComparisonResults(
        global_score="invalid",  # Deveria ser float
        frame_scores=[0.8, 0.85, 0.9],
        temporal_alignment={"offset": 0, "scale": 1.0},
        landmark_details={
            "left_shoulder": {"score": 0.9, "confidence": 0.95}
        },
        metadata={"video1": "dance1.mp4"}
    )
    assert invalid_results.validate() is False

def test_comparison_results_timestamp():
    results = ComparisonResults(
        global_score=0.85,
        frame_scores=[0.8],
        temporal_alignment={},
        landmark_details={},
        metadata={}
    )
    assert results.timestamp is not None
    assert isinstance(results.timestamp, str) 
