import pytest
import os
import json
from pathlib import Path
from src.pose_storage import PoseStorage, PoseData, PoseFrame
from src.pose_models import PoseLandmark
from datetime import datetime
import numpy as np
from src.comparison_results import ComparisonResults, DanceComparison

@pytest.fixture
def storage_dir(tmp_path):
    """Fixture que cria um diretório temporário para os testes."""
    return tmp_path / "pose_storage"

@pytest.fixture
def pose_storage(storage_dir):
    """Fixture que cria uma instância do PoseStorage."""
    return PoseStorage(storage_dir)

@pytest.fixture
def temp_video_files(tmp_path):
    """Fixture que cria arquivos de vídeo temporários para os testes."""
    video1 = tmp_path / "test_video.mp4"
    video2 = tmp_path / "video1.mp4"
    video3 = tmp_path / "video2.mp4"
    
    # Cria arquivos vazios para simular vídeos
    video1.touch()
    video2.touch()
    video3.touch()
    
    return {
        "test_video": str(video1),
        "video1": str(video2),
        "video2": str(video3)
    }

@pytest.fixture
def sample_landmarks():
    """Fixture que cria landmarks de exemplo."""
    return {
        0: PoseLandmark(x=0.1, y=0.2, z=0.3, visibility=0.9),
        1: PoseLandmark(x=0.4, y=0.5, z=0.6, visibility=0.8)
    }

@pytest.fixture
def sample_pose_data(sample_landmarks, temp_video_files):
    """Fixture que cria dados de pose de exemplo."""
    return PoseData(
        video_path=temp_video_files["test_video"],
        video_hash="test_hash",
        fps=30.0,
        resolution=(640, 480),
        total_frames=100,
        frames=[
            PoseFrame(
                frame_number=0,
                timestamp=0.0,
                landmarks=sample_landmarks
            ),
            PoseFrame(
                frame_number=1,
                timestamp=1/30.0,
                landmarks=sample_landmarks
            )
        ],
        created_at=datetime.now().isoformat()
    )

@pytest.fixture
def sample_comparison_results(temp_video_files):
    """Fixture que cria resultados de comparação de exemplo."""
    return ComparisonResults(
        video1_path=temp_video_files["video1"],
        video2_path=temp_video_files["video2"],
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
        video1_landmark_weights={
            "0": 1.0,
            "1": 1.0
        },
        video2_landmark_weights={
            "0": 1.0,
            "1": 1.0
        },
        frame_comparisons=[
            DanceComparison(
                frame_number=0,
                timestamp=0.0,
                similarity_score=0.95,
                landmark_similarities={
                    "0": 0.95,
                    "1": 0.95
                },
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
            "comparison_date": datetime.now().isoformat(),
            "comparison_duration": 1.0,
            "comparison_version": "1.0.0"
        }
    )

def test_pose_storage_initialization(pose_storage, storage_dir):
    """Testa a inicialização do PoseStorage."""
    assert pose_storage.storage_dir == storage_dir
    assert isinstance(pose_storage.cache, dict)
    assert len(pose_storage.cache) == 0

def test_generate_video_hash(pose_storage):
    """Testa a geração de hash para vídeos."""
    video_path = "test_video.mp4"
    hash1 = pose_storage._generate_video_hash(video_path)
    hash2 = pose_storage._generate_video_hash(video_path)
    
    assert isinstance(hash1, str)
    assert len(hash1) > 0
    assert hash1 == hash2  # Mesmo vídeo deve gerar mesmo hash

def test_validate_pose_data(pose_storage, sample_pose_data):
    """Testa a validação de dados de pose."""
    assert pose_storage._validate_pose_data(sample_pose_data)
    
    # Testa com dados inválidos
    invalid_data = PoseData(
        video_path="",
        video_hash="",
        fps=0.0,
        resolution=(0, 0),
        total_frames=0,
        frames=[],
        created_at=""
    )
    assert not pose_storage._validate_pose_data(invalid_data)

def test_save_and_load_pose_data(pose_storage, sample_pose_data):
    """Testa o salvamento e carregamento de dados de pose."""
    # Salva os dados
    assert pose_storage.save_pose_data(
        sample_pose_data.video_path,
        sample_pose_data.fps,
        sample_pose_data.resolution,
        sample_pose_data.total_frames,
        [f.landmarks for f in sample_pose_data.frames]
    )
    
    # Carrega os dados
    loaded_data = pose_storage.load_pose_data(sample_pose_data.video_path)
    assert loaded_data is not None
    assert loaded_data.video_path == sample_pose_data.video_path
    assert loaded_data.video_hash == sample_pose_data.video_hash
    assert loaded_data.fps == sample_pose_data.fps
    assert loaded_data.resolution == sample_pose_data.resolution
    assert loaded_data.total_frames == sample_pose_data.total_frames
    assert len(loaded_data.frames) == len(sample_pose_data.frames)

def test_get_pose_data(pose_storage, sample_pose_data):
    """Testa a obtenção de dados de pose no formato do comparador."""
    # Salva os dados
    assert pose_storage.save_pose_data(
        sample_pose_data.video_path,
        sample_pose_data.fps,
        sample_pose_data.resolution,
        sample_pose_data.total_frames,
        [f.landmarks for f in sample_pose_data.frames]
    )
    
    # Obtém os dados no formato do comparador
    frame_landmarks = pose_storage.get_pose_data(sample_pose_data.video_path)
    assert frame_landmarks is not None
    assert len(frame_landmarks) == sample_pose_data.total_frames
    assert frame_landmarks[0] == sample_pose_data.frames[0].landmarks
    assert frame_landmarks[1] == sample_pose_data.frames[1].landmarks

def test_save_and_load_comparison_results(pose_storage, sample_comparison_results):
    """Testa o salvamento e carregamento de resultados de comparação."""
    # Salva os resultados
    assert pose_storage.save_comparison_results(
        sample_comparison_results.video1_path,
        sample_comparison_results.video2_path,
        sample_comparison_results
    )
    
    # Carrega os resultados
    loaded_results = pose_storage.load_comparison_results(
        sample_comparison_results.video1_path,
        sample_comparison_results.video2_path
    )
    assert loaded_results is not None
    assert loaded_results.video1_path == sample_comparison_results.video1_path
    assert loaded_results.video2_path == sample_comparison_results.video2_path
    assert loaded_results.video1_fps == sample_comparison_results.video1_fps
    assert loaded_results.video2_fps == sample_comparison_results.video2_fps
    assert len(loaded_results.frame_comparisons) == len(sample_comparison_results.frame_comparisons)

def test_clear_cache(pose_storage, sample_pose_data):
    """Testa a limpeza do cache."""
    # Adiciona dados ao cache
    pose_storage.cache[sample_pose_data.video_hash] = sample_pose_data
    assert len(pose_storage.cache) > 0
    
    # Limpa o cache
    pose_storage.clear_cache()
    assert len(pose_storage.cache) == 0 
