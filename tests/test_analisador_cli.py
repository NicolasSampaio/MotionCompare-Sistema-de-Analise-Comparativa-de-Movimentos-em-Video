import os
import pytest
import tempfile
import json
from src.analisador_cli import (
    validate_video_format,
    validate_file_path,
    parse_arguments,
    get_comparison_params,
    process_video,
    compare_videos,
    save_results
)
from src.comparison_params import ComparisonParams, DistanceMetric
from src.comparison_results import ComparisonResults
from pathlib import Path
from unittest.mock import Mock, patch
from src.analisador_cli import AnalisadorCLI
from src.pose_models import PoseLandmark
from src.pose_storage import PoseStorage
from src.pose_estimation import PoseExtractor
from src.comparador_movimento import ComparadorMovimento

@pytest.fixture
def sample_video_path(tmp_path):
    """Fixture que cria um arquivo de vídeo de teste."""
    video_path = tmp_path / "test_video.mp4"
    video_path.touch()
    return str(video_path)

@pytest.fixture
def sample_config_path(tmp_path):
    """Fixture que cria um arquivo de configuração de teste."""
    config = {
        "metric": "euclidean",
        "tolerance": 0.8,
        "landmark_weights": {
            "shoulder": 0.8,
            "hip": 0.6
        },
        "temporal_sync": True,
        "normalize": True
    }
    config_path = tmp_path / "test_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f)
    return str(config_path)

def test_validate_video_format():
    """Testa a validação de formatos de vídeo suportados."""
    # Formatos válidos
    assert validate_video_format('video.mp4') == True
    assert validate_video_format('video.avi') == True
    assert validate_video_format('video.mov') == True
    
    # Formatos inválidos
    assert validate_video_format('video.txt') == False
    assert validate_video_format('video.pdf') == False
    assert validate_video_format('video') == False

def test_validate_file_path(sample_video_path):
    """Testa a validação de caminhos de arquivo."""
    # Arquivo existente e legível
    assert validate_file_path(sample_video_path) == True
        
    # Arquivo inexistente
    assert validate_file_path('nonexistent_file.mp4') == False

def test_parse_arguments(sample_video_path, tmp_path):
    """Testa o parsing de argumentos."""
    # Cria um arquivo de configuração temporário
    config_path = tmp_path / "test_config.json"
    config_data = {
        "metric": "euclidean",
        "tolerance": 0.2,
        "landmark_weights": {
            "shoulder": 0.8,
            "hip": 0.6
        },
        "temporal_sync": True,
        "normalize": True
    }
    with open(config_path, "w") as f:
        json.dump(config_data, f)

    args = parse_arguments([
        "-v", sample_video_path,
        "--command", "compare",
        sample_video_path,
        sample_video_path,
        "--config", str(config_path)
    ])
    
    assert args.command == "compare"
    assert args.video == sample_video_path
    assert args.video1 == sample_video_path
    assert args.video2 == sample_video_path
    assert args.config == str(config_path)

def test_parse_arguments_invalid():
    """Testa o parsing de argumentos inválidos."""
    with pytest.raises(SystemExit):
        parse_arguments([])  # Falta o comando

    with pytest.raises(SystemExit):
        parse_arguments(["--command", "compare"])  # Falta os vídeos

    with pytest.raises(SystemExit):
        parse_arguments(["--command", "compare", "video1.mp4"])  # Falta o segundo vídeo

    # Formato de vídeo não suportado
    with pytest.raises(SystemExit):
        parse_arguments(['-v', 'video.txt'])

    # FPS inválido
    with pytest.raises(SystemExit):
        parse_arguments(['-v', 'test.mp4', '-f', '-1'])

    # Resolução inválida
    with pytest.raises(SystemExit):
        parse_arguments(['-v', 'test.mp4', '-r', '4k'])

def test_parse_arguments_missing_required():
    """Testa o parsing quando argumentos obrigatórios estão faltando."""
    with pytest.raises(SystemExit):
        parse_arguments([])  # Falta o argumento -v 

def test_parse_arguments_with_config(sample_video_path, tmp_path):
    """Testa o parsing de argumentos com arquivo de configuração."""
    # Cria um arquivo de configuração temporário
    config_path = tmp_path / "test_config.json"
    config_data = {
        "metric": "euclidean",
        "tolerance": 0.2,
        "landmark_weights": {
            "shoulder": 0.8,
            "hip": 0.6
        },
        "temporal_sync": True,
        "normalize": True
    }
    with open(config_path, "w") as f:
        json.dump(config_data, f)

    # Testa o parsing com o arquivo de configuração
    args = parse_arguments([
        "-v", sample_video_path,
        "--command", "compare",
        sample_video_path,
        sample_video_path,
        "--config", str(config_path)
    ])

    assert args.command == "compare"
    assert args.video == sample_video_path
    assert args.video1 == sample_video_path
    assert args.video2 == sample_video_path
    assert args.config == str(config_path)

def test_get_comparison_params(tmp_path):
    """Testa a leitura dos parâmetros de comparação do arquivo de configuração."""
    # Cria um arquivo de configuração temporário
    config_path = tmp_path / "test_config.json"
    config_data = {
        "metric": DistanceMetric.EUCLIDEAN.value,
        "tolerance": 0.2,
        "landmark_weights": {
            "shoulder": 0.8,
            "hip": 0.6
        },
        "temporal_sync": True,
        "normalize": True
    }
    with open(config_path, "w") as f:
        json.dump(config_data, f)

    # Cria um objeto Namespace com os argumentos necessários
    args = Mock()
    args.config = str(config_path)
    args.metric = DistanceMetric.EUCLIDEAN.value
    args.tolerance = 0.2
    args.landmark_weights = {"shoulder": 0.8, "hip": 0.6}
    args.temporal_sync = True
    args.normalize = True

    # Testa a leitura dos parâmetros
    params = get_comparison_params(args)
    assert params.metric == DistanceMetric.EUCLIDEAN
    assert params.tolerance == 0.2
    assert params.landmark_weights["shoulder"] == 0.8
    assert params.landmark_weights["hip"] == 0.6
    assert params.temporal_sync is True
    assert params.normalize is True

def test_process_video(sample_video_path, tmp_path):
    """Testa o processamento de vídeo."""
    output_path = str(tmp_path / "output.mp4")
    assert process_video(
        sample_video_path,
        output_path=output_path,
        resolution="720p",
        fps=30,
        skip_processing=True
    ) is True

def test_compare_videos(sample_video_path):
    """Testa a comparação de vídeos."""
    results = compare_videos(sample_video_path, sample_video_path)
    assert results is not None
    assert isinstance(results, ComparisonResults)
    assert results.global_score is not None
    assert len(results.frame_scores) > 0

def test_save_results(tmp_path):
    """Testa o salvamento de resultados."""
    results = ComparisonResults(
        global_score=0.85,
        frame_scores=[0.8, 0.85, 0.9],
        temporal_alignment={"type": "euclidean"},
        landmark_details={},
        metadata={}
    )
    output_path = str(tmp_path / "results.json")
    assert save_results(results, output_path) is True
    assert os.path.exists(output_path)
    
    # Verifica se o arquivo contém os dados corretos
    with open(output_path, 'r') as f:
        saved_data = json.load(f)
        assert saved_data["global_score"] == 0.85
        assert saved_data["frame_scores"] == [0.8, 0.85, 0.9]

@pytest.fixture
def storage_dir(tmp_path):
    """Fixture que cria um diretório temporário para os testes."""
    return tmp_path / "pose_storage"

@pytest.fixture
def analisador(storage_dir):
    """Fixture que cria uma instância do AnalisadorCLI."""
    return AnalisadorCLI(storage_dir=str(storage_dir))

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

@pytest.fixture
def mock_pose_extractor():
    """Fixture que cria um mock do PoseExtractor."""
    extractor = Mock()
    extractor.process_video.return_value = True
    extractor.get_landmarks.return_value = [
        {
            0: PoseLandmark(x=0.1, y=0.2, z=0.3, visibility=0.9),
            1: PoseLandmark(x=0.4, y=0.5, z=0.6, visibility=0.8)
        }
    ]
    extractor.get_fps.return_value = 30.0
    extractor.get_resolution.return_value = (640, 480)
    extractor.get_total_frames.return_value = 100
    return extractor

@pytest.fixture
def mock_pose_storage():
    """Fixture que cria um mock do PoseStorage."""
    storage = Mock()
    storage.load_pose_data.return_value = None
    storage.save_pose_data.return_value = True
    storage.get_pose_data.return_value = [
        {
            0: PoseLandmark(x=0.1, y=0.2, z=0.3, visibility=0.9),
            1: PoseLandmark(x=0.4, y=0.5, z=0.6, visibility=0.8)
        }
    ]
    storage.load_comparison_results.return_value = None
    storage.save_comparison_results.return_value = True
    return storage

@pytest.fixture
def mock_comparador():
    """Fixture que cria um mock do ComparadorMovimento."""
    comparador = Mock()
    comparador.compare_videos.return_value = ComparisonResults(
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
        frame_comparisons=[],
        overall_metrics={
            "average_similarity": 0.95,
            "min_similarity": 0.90,
            "max_similarity": 1.0,
            "std_similarity": 0.05,
            "alignment_quality": 0.95,
            "temporal_alignment": 0.95
        },
        metadata={
            "comparison_date": "2024-01-01T00:00:00",
            "comparison_duration": 1.0,
            "comparison_version": "1.0.0"
        }
    )
    return comparador

def test_analisador_initialization(analisador, storage_dir):
    """Testa a inicialização do AnalisadorCLI."""
    assert analisador.storage_dir == storage_dir
    assert isinstance(analisador.pose_storage, PoseStorage)
    assert isinstance(analisador.pose_extractor, PoseExtractor)
    assert isinstance(analisador.comparador, ComparadorMovimento)

@patch('src.analisador_cli.PoseExtractor')
@patch('src.analisador_cli.PoseStorage')
def test_process_video(mock_pose_storage, mock_pose_extractor, sample_video_path, storage_dir):
    """Testa o processamento de vídeo."""
    # Configura os mocks
    mock_pose_extractor.return_value = mock_pose_extractor
    mock_pose_storage.return_value = mock_pose_storage
    mock_pose_extractor.process_video.return_value = True
    mock_pose_storage.load_pose_data.return_value = None
    mock_pose_storage.save_pose_data.return_value = True

    # Cria o analisador após os patches
    from src.analisador_cli import AnalisadorCLI
    analisador = AnalisadorCLI(storage_dir=str(storage_dir))

    # Testa processamento bem-sucedido
    success = analisador.process_video(
        video_path=sample_video_path,
        output_path="output.mp4",
        resolution=(640, 480)
    )
    assert success
    mock_pose_extractor.process_video.assert_called_once_with(
        video_path=sample_video_path,
        output_path="output.mp4",
        resolution=(640, 480)
    )
    mock_pose_storage.save_pose_data.assert_called_once()

    # Testa quando o vídeo já foi processado
    mock_pose_storage.load_pose_data.return_value = Mock()
    success = analisador.process_video(sample_video_path)
    assert success
    mock_pose_extractor.process_video.assert_called_once()  # Não deve ser chamado novamente

    # Testa falha no processamento
    mock_pose_extractor.process_video.return_value = False
    mock_pose_storage.load_pose_data.return_value = None
    success = analisador.process_video(sample_video_path)
    assert not success

@patch('src.analisador_cli.PoseExtractor')
@patch('src.analisador_cli.PoseStorage')
@patch('src.analisador_cli.ComparadorMovimento')
def test_compare_videos(mock_comparador, mock_pose_storage, mock_pose_extractor, sample_video_path, storage_dir):
    """Testa a comparação de vídeos."""
    # Configura os mocks
    mock_pose_extractor.return_value = mock_pose_extractor
    mock_pose_storage.return_value = mock_pose_storage
    mock_comparador.return_value = mock_comparador
    mock_pose_extractor.process_video.return_value = True
    mock_pose_extractor.get_fps.return_value = 30.0
    mock_pose_extractor.get_resolution.return_value = (640, 480)
    mock_pose_extractor.get_total_frames.return_value = 100
    # Retorno válido para get_pose_data
    mock_pose_storage.get_pose_data.return_value = [
        {
            0: PoseLandmark(x=0.1, y=0.2, z=0.3, visibility=0.9),
            1: PoseLandmark(x=0.4, y=0.5, z=0.6, visibility=0.8)
        }
    ]
    comparison_result_obj = ComparisonResults(
        video1_path=sample_video_path,
        video2_path=sample_video_path,
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
        frame_comparisons=[],
        overall_metrics={
            "average_similarity": 0.95,
            "min_similarity": 0.90,
            "max_similarity": 1.0,
            "std_similarity": 0.05,
            "alignment_quality": 0.95,
            "temporal_alignment": 0.95
        },
        metadata={
            "comparison_date": "2024-01-01T00:00:00",
            "comparison_duration": 1.0,
            "comparison_version": "1.0.0"
        }
    )
    # Simula ciclo: 1a chamada None, depois sempre objeto simulado
    pose_data_mock = type('PoseData', (), {
        'fps': 30.0,
        'resolution': (640, 480),
        'total_frames': 100
    })()
    def load_pose_data_side_effect(*args, **kwargs):
        if load_pose_data_side_effect.counter < 1:
            load_pose_data_side_effect.counter += 1
            return None
        return pose_data_mock
    load_pose_data_side_effect.counter = 0
    mock_pose_storage.load_pose_data.side_effect = load_pose_data_side_effect
    mock_pose_storage.save_pose_data.return_value = True
    # Simula ciclo: 1a chamada None, depois sempre ComparisonResults
    def load_comparison_results_side_effect(*args, **kwargs):
        if load_comparison_results_side_effect.counter < 1:
            load_comparison_results_side_effect.counter += 1
            return None
        return comparison_result_obj
    load_comparison_results_side_effect.counter = 0
    mock_pose_storage.load_comparison_results.side_effect = load_comparison_results_side_effect
    mock_comparador.compare_videos.return_value = comparison_result_obj

    # Cria o analisador com injeção dos mocks
    from src.analisador_cli import AnalisadorCLI
    analisador = AnalisadorCLI(
        storage_dir=str(storage_dir),
        pose_storage=mock_pose_storage,
        pose_extractor=mock_pose_extractor,
        comparador=mock_comparador
    )

    # Testa comparação bem-sucedida
    results = analisador.compare_videos(
        video1_path=sample_video_path,
        video2_path=sample_video_path,
        output_path="results.json"
    )
    assert isinstance(results, ComparisonResults)
    assert results.video1_path == sample_video_path
    assert results.video2_path == sample_video_path
    mock_pose_storage.save_comparison_results.assert_called_once()

    # Reseta o mock antes do próximo teste
    mock_comparador.compare_videos.reset_mock()

    # Testa quando a comparação já existe
    results = analisador.compare_videos(sample_video_path, sample_video_path)
    assert isinstance(results, ComparisonResults)
    mock_comparador.compare_videos.assert_not_called()  # Não deve ser chamado

    # Configura o mock para retornar None no teste de falha
    mock_pose_storage.load_comparison_results.side_effect = lambda *a, **kw: None

    # Testa falha na comparação
    mock_pose_storage.get_pose_data.return_value = None
    results = analisador.compare_videos(sample_video_path, sample_video_path)
    assert results is None

def test_process_video_with_invalid_path(analisador):
    """Testa o processamento de vídeo com caminho inválido."""
    success = analisador.process_video("nonexistent.mp4")
    assert not success

def test_compare_videos_with_invalid_path(analisador):
    """Testa a comparação de vídeos com caminho inválido."""
    results = analisador.compare_videos("nonexistent1.mp4", "nonexistent2.mp4")
    assert results is None

def test_process_video_with_exception(analisador, mock_pose_extractor, mock_pose_storage):
    """Testa o processamento de vídeo com exceção."""
    # Configura o mock para lançar uma exceção
    mock_pose_extractor.process_video.side_effect = Exception("Test error")
    
    success = analisador.process_video("test_video.mp4")
    assert not success

def test_compare_videos_with_exception(analisador, mock_pose_extractor, mock_pose_storage, mock_comparador):
    """Testa a comparação de vídeos com exceção."""
    # Configura o mock para lançar uma exceção
    mock_comparador.compare_videos.side_effect = Exception("Test error")
    
    results = analisador.compare_videos("video1.mp4", "video2.mp4")
    assert results is None
