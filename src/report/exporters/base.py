from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class BaseExporter(ABC):
    """Classe base abstrata para exportadores de relatórios."""
    
    def __init__(self, data: Dict[str, Any]):
        """
        Inicializa o exportador com os dados a serem exportados.
        
        Args:
            data: Dicionário contendo os dados do relatório
        """
        self.data = data
        self._validate_data()
    
    @abstractmethod
    def export(self, output_path: str) -> None:
        """
        Exporta os dados para o formato específico.
        
        Args:
            output_path: Caminho do arquivo de saída
        """
        pass
    
    def _validate_data(self) -> None:
        """
        Valida os dados antes da exportação.
        Levanta ValueError se os dados forem inválidos.
        """
        if not isinstance(self.data, dict):
            raise ValueError("Os dados devem ser um dicionário")
        
        if not self.data:
            raise ValueError("Os dados não podem estar vazios")
    
    def _log_export(self, output_path: str, success: bool, error: Optional[Exception] = None) -> None:
        """
        Registra informações sobre a exportação.
        
        Args:
            output_path: Caminho do arquivo exportado
            success: Se a exportação foi bem-sucedida
            error: Exceção ocorrida, se houver
        """
        if success:
            logger.info(f"Exportação concluída com sucesso: {output_path}")
        else:
            logger.error(f"Erro na exportação para {output_path}: {str(error)}") 
