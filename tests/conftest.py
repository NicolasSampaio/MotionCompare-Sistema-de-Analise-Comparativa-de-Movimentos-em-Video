import pytest
import numpy as np
import cv2
from pathlib import Path
import os

from src.pose_estimation import PoseExtractor
from src.pose_storage import PoseStorage
from src.comparador_movimento import ComparadorMovimento
from src.pose_models import PoseLandmark, PoseFrame, PoseData
from src.comparison_results import ComparisonResults, DanceComparison

@pytest.fixture
def test_video_path(tmp_path):
    """Cria um vídeo de teste."""
    video_path = tmp_path / "test_video.mp4"
    
    # Cria um vídeo simples
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(video_path), fourcc, 30.0, (640, 480))
    
    # Cria 30 frames
    for _ in range(30):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        out.write(frame)
    out.release()
    
    return str(video_path)

@pytest.fixture
def pose_extractor():
    """Cria um extrator de pose para testes."""
    return PoseExtractor()

@pytest.fixture
def pose_storage(tmp_path):
    """Cria um storage de pose para testes."""
    storage_dir = tmp_path / "pose_storage"
    storage_dir.mkdir(exist_ok=True)
    return PoseStorage(storage_dir=str(storage_dir))

@pytest.fixture
def comparador():
    """Cria um comparador de movimento para testes."""
    return ComparadorMovimento()

@pytest.fixture
def sample_pose_data():
    """Cria dados de pose de exemplo."""
    return PoseData(
        video_path="test_video.mp4",
        video_hash="test_hash",
        fps=30.0,
        resolution=(640, 480),
        total_frames=100,
        frames=[
            PoseFrame(
                frame_number=0,
                timestamp=0.0,
                landmarks={
                    0: PoseLandmark(x=0.1, y=0.2, z=0.3, visibility=0.9),
                    1: PoseLandmark(x=0.4, y=0.5, z=0.6, visibility=0.8)
                }
            ),
            PoseFrame(
                frame_number=1,
                timestamp=1/30.0,
                landmarks={
                    0: PoseLandmark(x=0.1, y=0.2, z=0.3, visibility=0.9),
                    1: PoseLandmark(x=0.4, y=0.5, z=0.6, visibility=0.8)
                }
            )
        ],
        created_at="2025-05-19T17:42:31.901614",
        version="1.0"
    )

@pytest.fixture
def sample_comparison_results():
    """Cria resultados de comparação de exemplo."""
    return ComparisonResults(
        video1_path="video1.mp4",
        video2_path="video2.mp4",
        video1_fps=30.0,
        video2_fps=30.0,
        video1_resolution=(640, 480),
        video2_resolution=(640, 480),
        video1_total_frames=100,
        video2_total_frames=100,
        video1_processed_frames=100,
        video2_processed_frames=100,
        video1_landmarks_per_frame=33,
        video2_landmarks_per_frame=33,
        video1_landmark_weights={"0": 1.0, "1": 1.0},
        video2_landmark_weights={"0": 1.0, "1": 1.0},
        frame_comparisons=[
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
            )
        ],
        overall_metrics={
            "average_similarity": 0.95,
            "min_similarity": 0.95,
            "max_similarity": 0.95,
            "std_similarity": 0.0,
            "alignment_quality": 1.0,
            "temporal_alignment": 1.0
        },
        metadata={
            "comparison_date": "2025-05-19T17:42:31.920754",
            "comparison_duration": 1.0,
            "comparison_version": "1.0.0"
        }
    ) 
