import csv
from typing import Any, Dict, List
from pathlib import Path
from .base import BaseExporter

class CSVExporter(BaseExporter):
    """Exportador para formato CSV."""
    
    def export(self, output_path: str) -> None:
        """
        Exporta os dados para um arquivo CSV.
        
        Args:
            output_path: Caminho do arquivo CSV de saída
        """
        try:
            # Garante que o diretório de saída existe
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Prepara os dados para CSV
            headers, rows = self._prepare_csv_data()
            
            # Exporta os dados
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(rows)
            
            self._log_export(output_path, True)
            
        except Exception as e:
            self._log_export(output_path, False, e)
            raise
    
    def _prepare_csv_data(self) -> tuple[List[str], List[Dict[str, Any]]]:
        """
        Prepara os dados para o formato CSV.
        
        Returns:
            Tuple contendo a lista de cabeçalhos e a lista de linhas
        """
        if not isinstance(self.data, dict):
            raise ValueError("Os dados devem ser um dicionário")
        
        # Se houver 'results' e for lista, exporta como tabela
        results = self.data.get('results', None)
        if isinstance(results, list):
            if not results:
                return [], []
            headers = list(results[0].keys())
            return headers, results
        
        # Caso contrário, exporta o próprio dicionário
        headers = list(self.data.keys())
        return headers, [self.data]
    
    def _validate_data(self) -> None:
        """
        Valida os dados específicos para exportação CSV.
        Verifica se os dados têm uma estrutura adequada para CSV.
        """
        super()._validate_data()
        
        # Verifica se os dados têm uma estrutura adequada para CSV
        if 'results' in self.data and not isinstance(self.data['results'], list):
            raise ValueError("O campo 'results' deve ser uma lista") 
