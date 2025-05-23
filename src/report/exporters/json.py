import json
from typing import Any, Dict
from pathlib import Path
from .base import BaseExporter

class JSONExporter(BaseExporter):
    """Exportador para formato JSON."""
    
    def export(self, output_path: str) -> None:
        """
        Exporta os dados para um arquivo JSON.
        
        Args:
            output_path: Caminho do arquivo JSON de saída
        """
        try:
            # Garante que o diretório de saída existe
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Exporta os dados com indentação para melhor legibilidade
            with open(output_path, 'w', encoding='utf-8') as f:
                try:
                    json.dump(self.data, f, indent=2, ensure_ascii=False, allow_nan=False)
                except (TypeError, ValueError) as e:
                    raise ValueError(f"Dados não serializáveis em JSON: {str(e)}")
            
            self._log_export(output_path, True)
            
        except Exception as e:
            self._log_export(output_path, False, e)
            raise
    
    def _validate_data(self) -> None:
        """
        Valida os dados específicos para exportação JSON.
        Além da validação básica, verifica se os dados são serializáveis em JSON.
        """
        super()._validate_data()
        
        # Tenta serializar os dados para garantir que são JSON-compatíveis
        try:
            json.dumps(self.data, allow_nan=False)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Dados não são serializáveis em JSON: {str(e)}") 
