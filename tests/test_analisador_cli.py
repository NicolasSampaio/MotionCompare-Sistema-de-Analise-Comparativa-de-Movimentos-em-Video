import os
import pytest
import tempfile
from src.analisador_cli import validate_video_format, validate_file_path, parse_arguments

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

def test_validate_file_path():
    """Testa a validação de caminhos de arquivo."""
    # Criar um arquivo temporário para teste
    with tempfile.NamedTemporaryFile() as temp_file:
        # Arquivo existente e legível
        assert validate_file_path(temp_file.name) == True
        
        # Arquivo inexistente
        assert validate_file_path('arquivo_inexistente.mp4') == False

def test_parse_arguments():
    """Testa o parsing de argumentos da CLI."""
    # Teste com argumentos válidos
    args = parse_arguments(['-v', 'test.mp4'])
    assert args.video == 'test.mp4'
    assert args.resolution == '720p'  # valor padrão
    assert args.fps is None
    assert args.verbose is False

    # Teste com todos os argumentos
    args = parse_arguments([
        '-v', 'test.mp4',
        '-o', 'output.mp4',
        '-r', '1080p',
        '-f', '30',
        '--verbose'
    ])
    assert args.video == 'test.mp4'
    assert args.output == 'output.mp4'
    assert args.resolution == '1080p'
    assert args.fps == 30
    assert args.verbose is True

def test_parse_arguments_invalid():
    """Testa o parsing de argumentos inválidos."""
    # Arquivo não encontrado
    with pytest.raises(SystemExit):
        parse_arguments(['-v', 'arquivo_inexistente.mp4'])

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
