import pytest
import os
import json
from pathlib import Path
from src.pose_storage import PoseStorage, PoseData, PoseFrame
from src.pose_estimation import PoseLandmark

@pytest.fixture
def storage():
    """Fixture para criar uma instância do PoseStorage."""
    storage_dir = "test_data/pose"
    storage = PoseStorage(storage_dir)
    yield storage
    # Limpa os dados de teste após os testes
    if os.path.exists(storage_dir):
        for file in os.listdir(storage_dir):
            os.remove(os.path.join(storage_dir, file))
        os.rmdir(storage_dir)

@pytest.fixture
def sample_landmarks():
    """Fixture para criar landmarks de exemplo."""
    return {
        0: PoseLandmark(x=0.1, y=0.2, z=0.3, visibility=0.9),
        1: PoseLandmark(x=0.4, y=0.5, z=0.6, visibility=0.8)
    }

@pytest.fixture
def sample_frame_landmarks(sample_landmarks):
    """Fixture para criar frame_landmarks de exemplo."""
    return [sample_landmarks, None, sample_landmarks]

def test_init(storage):
    """Testa a inicialização do PoseStorage."""
    assert storage.storage_dir.exists()
    assert isinstance(storage.cache, dict)
    assert len(storage.cache) == 0

def test_generate_video_hash(storage, tmp_path):
    """Testa a geração de hash para vídeo."""
    # Cria um arquivo de teste
    test_file = tmp_path / "test.mp4"
    test_file.write_bytes(b"test content")
    
    hash1 = storage._generate_video_hash(str(test_file))
    hash2 = storage._generate_video_hash(str(test_file))
    
    assert len(hash1) == 64
    assert hash1 == hash2

def test_validate_pose_data(storage, sample_landmarks, tmp_path):
    """Testa a validação de dados de pose."""
    # Cria um arquivo de vídeo de teste
    test_video = tmp_path / "test.mp4"
    test_video.write_bytes(b"test content")
    
    # Cria dados de pose válidos
    valid_data = PoseData(
        video_path=str(test_video),
        video_hash=storage._generate_video_hash(str(test_video)),
        fps=30.0,
        resolution=(1920, 1080),
        total_frames=100,
        frames=[
            PoseFrame(
                frame_number=0,
                timestamp=0.0,
                landmarks=sample_landmarks
            )
        ],
        created_at="2024-01-01T00:00:00"
    )
    
    assert storage._validate_pose_data(valid_data)
    
    # Testa dados inválidos
    invalid_data = PoseData(
        video_path="nonexistent.mp4",
        video_hash="invalid",
        fps=30.0,
        resolution=(1920, 1080),
        total_frames=100,
        frames=[],
        created_at="2024-01-01T00:00:00"
    )
    
    assert not storage._validate_pose_data(invalid_data)

def test_save_and_load_pose_data(storage, sample_frame_landmarks, tmp_path):
    """Testa o salvamento e carregamento de dados de pose."""
    # Cria um arquivo de vídeo de teste
    test_video = tmp_path / "test.mp4"
    test_video.write_bytes(b"test content")
    
    # Salva os dados
    success = storage.save_pose_data(
        video_path=str(test_video),
        fps=30.0,
        resolution=(1920, 1080),
        total_frames=3,
        frame_landmarks=sample_frame_landmarks
    )
    
    assert success
    
    # Carrega os dados
    loaded_data = storage.load_pose_data(str(test_video))
    
    assert loaded_data is not None
    assert loaded_data.video_path == str(test_video)
    assert loaded_data.fps == 30.0
    assert loaded_data.resolution == (1920, 1080)
    assert loaded_data.total_frames == 3
    assert len(loaded_data.frames) == 2  # Apenas frames com landmarks
    
    # Verifica o conteúdo dos frames
    frame = loaded_data.frames[0]
    assert frame.frame_number == 0
    assert frame.timestamp == 0.0
    assert len(frame.landmarks) == 2
    assert frame.landmarks[0].x == 0.1
    assert frame.landmarks[0].y == 0.2
    assert frame.landmarks[0].z == 0.3
    assert frame.landmarks[0].visibility == 0.9

def test_clear_cache(storage, sample_frame_landmarks, tmp_path):
    """Testa a limpeza do cache."""
    # Cria um arquivo de vídeo de teste
    test_video = tmp_path / "test.mp4"
    test_video.write_bytes(b"test content")
    
    # Salva e carrega dados para popular o cache
    storage.save_pose_data(
        video_path=str(test_video),
        fps=30.0,
        resolution=(1920, 1080),
        total_frames=3,
        frame_landmarks=sample_frame_landmarks
    )
    storage.load_pose_data(str(test_video))
    
    assert len(storage.cache) > 0
    
    # Limpa o cache
    storage.clear_cache()
    
    assert len(storage.cache) == 0 
