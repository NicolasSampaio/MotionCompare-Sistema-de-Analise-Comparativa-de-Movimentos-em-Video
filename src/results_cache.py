import os
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from .comparison_results import ComparisonResults

logger = logging.getLogger(__name__)

class ResultsCache:
    """
    Sistema de cache para armazenar e recuperar resultados de comparação.
    """
    def __init__(self, cache_dir: str = "cache", max_age_hours: int = 24):
        self.cache_dir = cache_dir
        self.max_age = timedelta(hours=max_age_hours)
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """Garante que o diretório de cache existe."""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            logger.info(f"Diretório de cache criado: {self.cache_dir}")

    def _get_cache_path(self, key: str) -> str:
        """Retorna o caminho do arquivo de cache para uma chave específica."""
        return os.path.join(self.cache_dir, f"{key}.json")

    def _is_cache_valid(self, cache_path: str) -> bool:
        """Verifica se o cache ainda é válido baseado na idade do arquivo."""
        if not os.path.exists(cache_path):
            return False

        file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        age = datetime.now() - file_time
        return age <= self.max_age

    def get(self, key: str) -> Optional[ComparisonResults]:
        """
        Recupera resultados do cache se existirem e forem válidos.
        """
        cache_path = self._get_cache_path(key)
        
        if not self._is_cache_valid(cache_path):
            logger.debug(f"Cache inválido ou inexistente para chave: {key}")
            return None

        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
                results = ComparisonResults.from_dict(data)
                if results.validate():
                    logger.info(f"Resultados recuperados do cache para chave: {key}")
                    return results
                else:
                    logger.warning(f"Resultados inválidos encontrados no cache para chave: {key}")
                    return None
        except Exception as e:
            logger.error(f"Erro ao recuperar cache para chave {key}: {str(e)}")
            return None

    def set(self, key: str, results: ComparisonResults) -> bool:
        """
        Armazena resultados no cache.
        """
        if not results.validate():
            logger.error("Tentativa de armazenar resultados inválidos no cache")
            return False

        cache_path = self._get_cache_path(key)
        try:
            with open(cache_path, 'w') as f:
                json.dump(results.to_dict(), f)
            logger.info(f"Resultados armazenados no cache para chave: {key}")
            return True
        except Exception as e:
            logger.error(f"Erro ao armazenar cache para chave {key}: {str(e)}")
            return False

    def clear(self, key: Optional[str] = None):
        """
        Limpa o cache para uma chave específica ou todo o cache.
        """
        if key:
            cache_path = self._get_cache_path(key)
            if os.path.exists(cache_path):
                os.remove(cache_path)
                logger.info(f"Cache limpo para chave: {key}")
        else:
            for file in os.listdir(self.cache_dir):
                if file.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, file))
            logger.info("Todo o cache foi limpo") 
