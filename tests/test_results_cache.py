import pytest
import os
import shutil
from datetime import datetime, timedelta
from src.results_cache import ResultsCache
from src.comparison_results import ComparisonResults

@pytest.fixture
def cache_dir(tmp_path):
    """Fixture que cria um diretório temporário para os testes de cache."""
    cache_path = tmp_path / "test_cache"
    cache_path.mkdir()
    yield str(cache_path)
    shutil.rmtree(str(cache_path))

@pytest.fixture
def results_cache(cache_dir):
    """Fixture que cria uma instância do ResultsCache para testes."""
    return ResultsCache(cache_dir=cache_dir, max_age_hours=1)

@pytest.fixture
def sample_results():
    """Fixture que cria um conjunto de resultados de exemplo."""
    return ComparisonResults(
        global_score=0.85,
        frame_scores=[0.8, 0.85, 0.9],
        temporal_alignment={"offset": 0, "scale": 1.0},
        landmark_details={
            "left_shoulder": {"score": 0.9, "confidence": 0.95}
        },
        metadata={"video1": "dance1.mp4"}
    )

def test_cache_initialization(cache_dir):
    """Testa a inicialização do cache."""
    cache = ResultsCache(cache_dir=cache_dir)
    assert os.path.exists(cache_dir)
    assert cache.cache_dir == cache_dir

def test_cache_set_get(results_cache, sample_results):
    """Testa o armazenamento e recuperação de resultados do cache."""
    # Teste de armazenamento
    assert results_cache.set("test_key", sample_results) is True
    
    # Teste de recuperação
    cached_results = results_cache.get("test_key")
    assert cached_results is not None
    assert cached_results.global_score == sample_results.global_score
    assert cached_results.frame_scores == sample_results.frame_scores

def test_cache_invalidation(results_cache, sample_results):
    """Testa a invalidação do cache após o tempo máximo."""
    # Configura o cache com tempo máximo de 1 hora
    cache = ResultsCache(cache_dir=results_cache.cache_dir, max_age_hours=1)
    
    # Armazena resultados
    cache.set("test_key", sample_results)
    
    # Simula cache expirado modificando a data do arquivo
    cache_path = os.path.join(cache.cache_dir, "test_key.json")
    old_time = datetime.now() - timedelta(hours=2)
    os.utime(cache_path, (old_time.timestamp(), old_time.timestamp()))
    
    # Tenta recuperar resultados expirados
    cached_results = cache.get("test_key")
    assert cached_results is None

def test_cache_clear(results_cache, sample_results):
    """Testa a limpeza do cache."""
    # Armazena alguns resultados
    results_cache.set("key1", sample_results)
    results_cache.set("key2", sample_results)
    
    # Limpa uma chave específica
    results_cache.clear("key1")
    assert results_cache.get("key1") is None
    assert results_cache.get("key2") is not None
    
    # Limpa todo o cache
    results_cache.clear()
    assert results_cache.get("key2") is None

def test_cache_invalid_data(results_cache):
    """Testa o comportamento do cache com dados inválidos."""
    # Tenta armazenar resultados inválidos
    invalid_results = ComparisonResults(
        global_score="invalid",  # Deveria ser float
        frame_scores=[0.8],
        temporal_alignment={},
        landmark_details={},
        metadata={}
    )
    
    assert results_cache.set("invalid_key", invalid_results) is False
    assert results_cache.get("invalid_key") is None 
