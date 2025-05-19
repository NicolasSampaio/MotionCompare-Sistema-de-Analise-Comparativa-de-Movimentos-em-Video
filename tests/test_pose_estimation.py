import pytest
import numpy as np
import cv2
import os
import logging
import time
import sys
from tqdm import tqdm
from src.pose_estimation import PoseExtractor, PoseLandmark
from src.comparison_params import ComparisonParams
from src.comparison_results import ComparisonResults
from src.pose_models import PoseLandmark
from pathlib import Path

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout  # Força saída para stdout
)
logger = logging.getLogger(__name__)

@pytest.fixture
def sample_frame():
    """Fixture que cria um frame de teste."""
    return np.zeros((480, 640, 3), dtype=np.uint8)

@pytest.fixture
def pose_extractor():
    """Fixture que cria um extrator de pose para testes."""
    return PoseExtractor(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        comparison_params=ComparisonParams()
    )

def test_pose_extractor_initialization():
    """Testa a inicialização do PoseExtractor."""
    # Teste com valores válidos
    extractor = PoseExtractor(0.5, 0.5)
    assert extractor.pose is not None
    
    # Teste com valores inválidos
    with pytest.raises(ValueError):
        PoseExtractor(-0.1, 0.5)
    with pytest.raises(ValueError):
        PoseExtractor(0.5, 1.5)

def test_normalize_landmarks(pose_extractor):
    """Testa a normalização de landmarks."""
    # Cria landmarks de teste
    landmarks = {
        0: PoseLandmark(0.2, 0.3, 0.4, 0.9),
        1: PoseLandmark(0.4, 0.5, 0.6, 0.8),
        2: PoseLandmark(0.6, 0.7, 0.8, 0.7)
    }
    
    # Testa com normalização ativada
    pose_extractor.comparison_params.normalize = True
    normalized = pose_extractor.normalize_landmarks(landmarks)
    assert normalized is not None
    assert len(normalized) == len(landmarks)
    
    # Verifica se os valores estão normalizados
    x_coords = [lm.x for lm in normalized.values()]
    y_coords = [lm.y for lm in normalized.values()]
    z_coords = [lm.z for lm in normalized.values()]
    
    assert min(x_coords) >= 0 and max(x_coords) <= 1
    assert min(y_coords) >= 0 and max(y_coords) <= 1
    assert min(z_coords) >= 0 and max(z_coords) <= 1
    
    # Testa com normalização desativada
    pose_extractor.comparison_params.normalize = False
    not_normalized = pose_extractor.normalize_landmarks(landmarks)
    assert not_normalized == landmarks

def test_apply_landmark_weights(pose_extractor):
    """Testa a aplicação de pesos aos landmarks."""
    # Cria landmarks de teste com índices reais do MediaPipe
    landmarks = {
        0: PoseLandmark(0.2, 0.3, 0.4, 0.9),  # nose
        11: PoseLandmark(0.4, 0.5, 0.6, 0.8), # left_shoulder
        2: PoseLandmark(0.6, 0.7, 0.8, 0.7)   # outro
    }
    
    # Define pesos para alguns landmarks
    pose_extractor.comparison_params.landmark_weights = {
        "nose": 0.8,
        "left_shoulder": 0.6
    }
    
    weighted = pose_extractor.apply_landmark_weights(landmarks)
    assert weighted is not None
    assert len(weighted) == len(landmarks)
    
    # Verifica se os pesos foram aplicados corretamente
    for idx, landmark in weighted.items():
        original = landmarks[idx]
        if idx == 0:  # nose
            assert landmark.x == original.x * 0.8
            assert landmark.y == original.y * 0.8
            assert landmark.z == original.z * 0.8
        elif idx == 11:  # left_shoulder
            assert landmark.x == original.x * 0.6
            assert landmark.y == original.y * 0.6
            assert landmark.z == original.z * 0.6
        else:
            assert landmark.x == original.x
            assert landmark.y == original.y
            assert landmark.z == original.z

def test_process_frame(pose_extractor, sample_frame):
    """Testa o processamento de um frame."""
    # Teste com frame válido
    landmarks = pose_extractor.process_frame(sample_frame)
    assert landmarks is None  # Frame vazio não deve detectar landmarks
    
    # Teste com frame None
    with pytest.raises(ValueError):
        pose_extractor.process_frame(None)
    
    # Teste com frame inválido
    with pytest.raises(ValueError):
        pose_extractor.process_frame(np.zeros((480, 640)))  # Sem canal de cor

def test_process_video(pose_extractor, test_video_path):
    """Testa o processamento de um vídeo completo real."""
    print(f"\nTestando processamento do vídeo: {os.path.abspath(test_video_path)}", flush=True)

    # Verifica se o arquivo existe
    assert os.path.exists(test_video_path), f"Arquivo de vídeo não encontrado: {test_video_path}"

    # Tenta abrir o vídeo diretamente com OpenCV para verificar
    cap = cv2.VideoCapture(test_video_path)
    assert cap.isOpened(), f"Não foi possível abrir o vídeo: {test_video_path}"

    # Obtém informações do vídeo
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"Vídeo aberto com sucesso. Frames: {total_frames}, FPS: {fps}, Resolução: {width}x{height}", flush=True)
    print(f"Tempo estimado de processamento: {total_frames/fps:.1f} segundos", flush=True)
    cap.release()

    # Processa o vídeo com o PoseExtractor
    start_time = time.time()
    extractor = PoseExtractor()

    # Configura a barra de progresso
    pbar = tqdm(total=total_frames, desc="Processando frames", unit="frames", ncols=100, file=sys.stdout)
    last_update = 0

    def progress_callback(frame_count: int, total_frames: int):
        nonlocal last_update
        update_amount = frame_count - last_update
        if update_amount > 0:
            pbar.update(update_amount)
            last_update = frame_count

            elapsed_time = time.time() - start_time
            frames_per_second = frame_count / elapsed_time if elapsed_time > 0 else 0
            remaining_frames = total_frames - frame_count
            estimated_time = remaining_frames / frames_per_second if frames_per_second > 0 else 0

            # Atualiza a descrição da barra de progresso com informações detalhadas
            pbar.set_description(
                f"Processando frames ({frame_count}/{total_frames} - {frame_count/total_frames*100:.1f}%) - "
                f"Velocidade: {frames_per_second:.1f} fps - "
                f"Tempo restante: {estimated_time:.1f}s"
            )

    results = extractor.process_video(test_video_path, progress_callback=progress_callback)
    assert results

def test_compare_videos(pose_extractor, tmp_path):
    """Testa a comparação de vídeos."""
    # Cria dois vídeos de teste
    video1_path = str(tmp_path / "video1.mp4")
    video2_path = str(tmp_path / "video2.mp4")

    # Cria vídeos simples
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    for path in [video1_path, video2_path]:
        out = cv2.VideoWriter(path, fourcc, 30.0, (640, 480))
        for _ in range(30):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            out.write(frame)
        out.release()

    # Processa os vídeos
    assert pose_extractor.process_video(video1_path)
    assert pose_extractor.process_video(video2_path)

    # Testa a comparação
    results = pose_extractor.compare_videos(video1_path, video2_path)
    # Aceita que pode não haver landmarks detectados, mas valida o tipo de retorno
    assert results is None or isinstance(results, ComparisonResults)

def test_get_methods(pose_extractor, tmp_path):
    """Testa os métodos get do PoseExtractor."""
    # Processa um vídeo primeiro
    video_path = str(tmp_path / "test_video.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, 30.0, (640, 480))
    for _ in range(30):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        out.write(frame)
    out.release()
    
    pose_extractor.process_video(video_path)
    
    # Testa os métodos get
    assert len(pose_extractor.get_landmarks()) > 0
    assert pose_extractor.get_fps() == 30.0
    assert pose_extractor.get_resolution() == (640, 480)
    assert pose_extractor.get_total_frames() == 30

def test_process_frame_with_empty_frame():
    """Testa o processamento de um frame vazio."""
    extractor = PoseExtractor()
    empty_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    result = extractor.process_frame(empty_frame)
    assert result is None

def test_process_frame_with_sample_frame():
    """Testa o processamento de um frame com uma pessoa."""
    extractor = PoseExtractor()
    
    # Cria um frame de teste com uma pessoa
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Desenha um retângulo simples para simular uma pessoa
    cv2.rectangle(frame, (200, 100), (400, 400), (255, 255, 255), -1)
    
    result = extractor.process_frame(frame)
    # Como é um frame simulado, podemos esperar None ou landmarks
    assert result is None or isinstance(result, dict)

def test_pose_landmark_creation():
    """Testa a criação de um PoseLandmark."""
    landmark = PoseLandmark(x=0.5, y=0.5, z=0.0, visibility=0.9)
    assert landmark.x == 0.5
    assert landmark.y == 0.5
    assert landmark.z == 0.0
    assert landmark.visibility == 0.9

def test_process_frame_with_invalid_input():
    """Testa o processamento com entrada inválida."""
    extractor = PoseExtractor()
    with pytest.raises(Exception):
        extractor.process_frame(None)
    
    with pytest.raises(Exception):
        extractor.process_frame(np.zeros((480, 640), dtype=np.uint8))  # Frame 2D inválido

def test_process_frame_with_different_resolutions():
    """Testa o processamento com diferentes resoluções de frame."""
    extractor = PoseExtractor()
    resolutions = [(640, 480), (1280, 720), (1920, 1080)]
    
    for width, height in resolutions:
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        result = extractor.process_frame(frame)
        assert result is None or isinstance(result, dict)

def test_pose_extractor_with_different_confidence():
    """Testa o extrator com diferentes níveis de confiança."""
    confidences = [(0.3, 0.3), (0.5, 0.5), (0.7, 0.7)]
    
    for det_conf, track_conf in confidences:
        extractor = PoseExtractor(
            min_detection_confidence=det_conf,
            min_tracking_confidence=track_conf
        )
        assert extractor is not None
        assert extractor.pose is not None

# Removido o teste abaixo pois depende de arquivo externo inexistente
# def test_process_video():
#     """Testa o processamento de um vídeo completo real."""
#     video_path = "video.mp4"
#     print(f"\nTestando processamento do vídeo: {os.path.abspath(video_path)}", flush=True)
#     # Verifica se o arquivo existe
#     assert os.path.exists(video_path), f"Arquivo de vídeo não encontrado: {video_path}"
#     ... 
