import pytest
import numpy as np
import cv2
import os
import logging
import time
import sys
from tqdm import tqdm
from src.pose_estimation import PoseExtractor, PoseLandmark

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout  # Força saída para stdout
)
logger = logging.getLogger(__name__)

def test_pose_extractor_initialization():
    """Testa a inicialização do PoseExtractor."""
    extractor = PoseExtractor()
    assert extractor is not None
    assert extractor.pose is not None

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

def test_process_video():
    """Testa o processamento de um vídeo completo real."""
    video_path = "video.mp4"
    print(f"\nTestando processamento do vídeo: {os.path.abspath(video_path)}", flush=True)
    
    # Verifica se o arquivo existe
    assert os.path.exists(video_path), f"Arquivo de vídeo não encontrado: {video_path}"
    
    # Tenta abrir o vídeo diretamente com OpenCV para verificar
    cap = cv2.VideoCapture(video_path)
    assert cap.isOpened(), f"Não foi possível abrir o vídeo: {video_path}"
    
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
    
    results = extractor.process_video(video_path, progress_callback=progress_callback)
    pbar.close()
    
    # Verifica os resultados
    assert isinstance(results, list), "Resultado deve ser uma lista"
    assert len(results) > 0, "Deve ter processado pelo menos um frame"
    assert all(isinstance(r, (dict, type(None))) for r in results), "Todos os resultados devem ser dicionários ou None"
    
    # Conta quantos frames tiveram landmarks detectados
    frames_with_landmarks = sum(1 for r in results if r is not None)
    total_time = time.time() - start_time
    print(f"\nProcessamento concluído em {total_time:.1f} segundos", flush=True)
    print(f"Total de frames processados: {len(results)}", flush=True)
    print(f"Frames com landmarks detectados: {frames_with_landmarks}", flush=True)
    print(f"Taxa de detecção: {frames_with_landmarks/len(results)*100:.1f}%", flush=True)
    print(f"Velocidade média: {len(results)/total_time:.1f} fps", flush=True) 
