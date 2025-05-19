import pytest
from pathlib import Path
import json
import os
from datetime import datetime

from src.carregamento_dados import PoseDataLoader, PoseDataValidationResult
from src.pose_storage import PoseData, PoseFrame
from src.pose_models import PoseLandmark

@pytest.fixture
def temp_storage_dir(tmp_path):
    """Fixture para criar um diretório temporário para os testes."""
    storage_dir = tmp_path / "pose_data"
    storage_dir.mkdir()
    return storage_dir

@pytest.fixture
def sample_pose_data():
    """Fixture para criar dados de pose de exemplo."""
    landmarks = {
        0: PoseLandmark(x=0.1, y=0.2, z=0.3, visibility=0.9),
        1: PoseLandmark(x=0.4, y=0.5, z=0.6, visibility=0.8)
    }
    
    frames = [
        PoseFrame(frame_number=0, timestamp=0.0, landmarks=landmarks),
        PoseFrame(frame_number=1, timestamp=0.033, landmarks=landmarks)
    ]
    
    return PoseData(
        video_path="test_video1.mp4",
        video_hash="test_hash_1",
        fps=30.0,
        resolution=(1920, 1080),
        total_frames=2,
        frames=frames,
        created_at=datetime.now().isoformat()
    )

@pytest.fixture
def sample_pose_data_2():
    """Fixture para criar dados de pose de exemplo para o segundo vídeo."""
    landmarks = {
        0: PoseLandmark(x=0.2, y=0.3, z=0.4, visibility=0.95),
        1: PoseLandmark(x=0.5, y=0.6, z=0.7, visibility=0.85)
    }
    
    frames = [
        PoseFrame(frame_number=0, timestamp=0.0, landmarks=landmarks),
        PoseFrame(frame_number=1, timestamp=0.033, landmarks=landmarks)
    ]
    
    return PoseData(
        video_path="test_video2.mp4",
        video_hash="test_hash_2",
        fps=30.0,
        resolution=(1920, 1080),
        total_frames=2,
        frames=frames,
        created_at=datetime.now().isoformat()
    )

def test_load_pose_data_success(temp_storage_dir, sample_pose_data, sample_pose_data_2):
    """Testa o carregamento bem-sucedido de dados de pose."""
    # Salva os dados de exemplo
    loader = PoseDataLoader(str(temp_storage_dir))
    
    # Salva os dados de exemplo
    data_path1 = temp_storage_dir / f"{sample_pose_data.video_hash}.json"
    data_path2 = temp_storage_dir / f"{sample_pose_data_2.video_hash}.json"
    
    with open(data_path1, "w") as f:
        json.dump({
            "video_path": sample_pose_data.video_path,
            "video_hash": sample_pose_data.video_hash,
            "fps": sample_pose_data.fps,
            "resolution": sample_pose_data.resolution,
            "total_frames": sample_pose_data.total_frames,
            "frames": [
                {
                    "frame_number": frame.frame_number,
                    "timestamp": frame.timestamp,
                    "landmarks": {
                        str(k): {"x": v.x, "y": v.y, "z": v.z, "visibility": v.visibility}
                        for k, v in frame.landmarks.items()
                    }
                }
                for frame in sample_pose_data.frames
            ],
            "created_at": sample_pose_data.created_at,
            "version": sample_pose_data.version
        }, f)
    
    with open(data_path2, "w") as f:
        json.dump({
            "video_path": sample_pose_data_2.video_path,
            "video_hash": sample_pose_data_2.video_hash,
            "fps": sample_pose_data_2.fps,
            "resolution": sample_pose_data_2.resolution,
            "total_frames": sample_pose_data_2.total_frames,
            "frames": [
                {
                    "frame_number": frame.frame_number,
                    "timestamp": frame.timestamp,
                    "landmarks": {
                        str(k): {"x": v.x, "y": v.y, "z": v.z, "visibility": v.visibility}
                        for k, v in frame.landmarks.items()
                    }
                }
                for frame in sample_pose_data_2.frames
            ],
            "created_at": sample_pose_data_2.created_at,
            "version": sample_pose_data_2.version
        }, f)
    
    # Testa o carregamento
    data1, data2, validation = loader.load_pose_data(
        sample_pose_data.video_path,
        sample_pose_data_2.video_path
    )
    
    assert data1 is not None
    assert data2 is not None
    assert validation.is_valid
    assert len(validation.errors) == 0
    assert len(validation.warnings) == 0

def test_load_pose_data_missing_files(temp_storage_dir):
    """Testa o carregamento quando os arquivos não existem."""
    loader = PoseDataLoader(str(temp_storage_dir))
    data1, data2, validation = loader.load_pose_data("nonexistent1.mp4", "nonexistent2.mp4")
    
    assert data1 is None
    assert data2 is None
    assert not validation.is_valid
    assert len(validation.errors) > 0

def test_load_pose_data_invalid_data(temp_storage_dir):
    """Testa o carregamento com dados inválidos."""
    loader = PoseDataLoader(str(temp_storage_dir))
    
    # Cria um arquivo com dados inválidos
    invalid_data = {
        "video_path": "test.mp4",
        "video_hash": "test_hash",
        "fps": "invalid",  # FPS inválido
        "resolution": [1920, 1080],
        "total_frames": 2,
        "frames": [],
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }
    
    data_path = temp_storage_dir / "test_hash.json"
    with open(data_path, "w") as f:
        json.dump(invalid_data, f)
    
    data1, data2, validation = loader.load_pose_data("test.mp4", "test2.mp4")
    
    assert data1 is None
    assert data2 is None
    assert not validation.is_valid
    assert len(validation.errors) > 0

def test_load_pose_data_incompatible_landmarks(temp_storage_dir, sample_pose_data):
    """Testa o carregamento com landmarks incompatíveis."""
    loader = PoseDataLoader(str(temp_storage_dir))
    
    # Cria uma cópia dos dados com landmarks diferentes, mas com dois frames
    landmarks_incompat = {
        2: PoseLandmark(x=0.1, y=0.2, z=0.3, visibility=0.9),
        3: PoseLandmark(x=0.4, y=0.5, z=0.6, visibility=0.8)
    }
    frames_incompat = [
        PoseFrame(frame_number=0, timestamp=0.0, landmarks=landmarks_incompat),
        PoseFrame(frame_number=1, timestamp=0.033, landmarks=landmarks_incompat)
    ]
    incompatible_data = PoseData(
        video_path="test_video2.mp4",
        video_hash="test_hash_2",
        fps=30.0,
        resolution=(1920, 1080),
        total_frames=2,
        frames=frames_incompat,
        created_at=datetime.now().isoformat()
    )
    
    # Salva os dados
    data_path1 = temp_storage_dir / f"{sample_pose_data.video_hash}.json"
    data_path2 = temp_storage_dir / f"{incompatible_data.video_hash}.json"
    
    with open(data_path1, "w") as f:
        json.dump({
            "video_path": sample_pose_data.video_path,
            "video_hash": sample_pose_data.video_hash,
            "fps": sample_pose_data.fps,
            "resolution": sample_pose_data.resolution,
            "total_frames": sample_pose_data.total_frames,
            "frames": [
                {
                    "frame_number": frame.frame_number,
                    "timestamp": frame.timestamp,
                    "landmarks": {
                        str(k): {"x": v.x, "y": v.y, "z": v.z, "visibility": v.visibility}
                        for k, v in frame.landmarks.items()
                    }
                }
                for frame in sample_pose_data.frames
            ],
            "created_at": sample_pose_data.created_at,
            "version": sample_pose_data.version
        }, f)
    
    with open(data_path2, "w") as f:
        json.dump({
            "video_path": incompatible_data.video_path,
            "video_hash": incompatible_data.video_hash,
            "fps": incompatible_data.fps,
            "resolution": incompatible_data.resolution,
            "total_frames": incompatible_data.total_frames,
            "frames": [
                {
                    "frame_number": frame.frame_number,
                    "timestamp": frame.timestamp,
                    "landmarks": {
                        str(k): {"x": v.x, "y": v.y, "z": v.z, "visibility": v.visibility}
                        for k, v in frame.landmarks.items()
                    }
                }
                for frame in frames_incompat
            ],
            "created_at": incompatible_data.created_at,
            "version": incompatible_data.version
        }, f)
    
    data1, data2, validation = loader.load_pose_data(
        sample_pose_data.video_path,
        incompatible_data.video_path
    )
    
    assert not validation.is_valid
    assert any("incompatíveis" in error for error in validation.errors) 
