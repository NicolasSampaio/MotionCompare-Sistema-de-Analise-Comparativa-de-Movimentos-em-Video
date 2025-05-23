import json
import csv
from typing import Any, Dict, List
from pathlib import Path

class Validator:
    """Classe base para validadores de formato."""
    
    @staticmethod
    def validate_file_exists(file_path: str) -> None:
        """
        Valida se o arquivo existe.
        
        Args:
            file_path: Caminho do arquivo a ser validado
            
        Raises:
            FileNotFoundError: Se o arquivo não existir
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

class JSONValidator(Validator):
    """Validador para arquivos JSON."""
    
    @staticmethod
    def validate(file_path: str) -> Dict[str, Any]:
        """
        Valida um arquivo JSON.
        
        Args:
            file_path: Caminho do arquivo JSON
            
        Returns:
            Dados do arquivo JSON validado
            
        Raises:
            json.JSONDecodeError: Se o arquivo não for um JSON válido
            FileNotFoundError: Se o arquivo não existir
        """
        JSONValidator.validate_file_exists(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Arquivo JSON inválido: {str(e)}", e.doc, e.pos)

class CSVValidator(Validator):
    """Validador para arquivos CSV."""
    
    @staticmethod
    def validate(file_path: str) -> List[Dict[str, Any]]:
        """
        Valida um arquivo CSV.
        
        Args:
            file_path: Caminho do arquivo CSV
            
        Returns:
            Lista de dicionários com os dados do CSV
            
        Raises:
            csv.Error: Se o arquivo não for um CSV válido
            FileNotFoundError: Se o arquivo não existir
        """
        CSVValidator.validate_file_exists(file_path)
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                # Verifica se todas as linhas têm o mesmo número de colunas
                expected_fields = reader.fieldnames
                for i, row in enumerate(rows):
                    if set(row.keys()) != set(expected_fields):
                        raise csv.Error(f"Linha {i+2} com número de colunas diferente do cabeçalho")
                return rows
        except csv.Error as e:
            raise csv.Error(f"Arquivo CSV inválido: {str(e)}") 
