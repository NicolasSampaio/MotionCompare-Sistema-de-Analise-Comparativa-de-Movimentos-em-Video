"""
Exemplo de uso dos exportadores de relatórios.
"""

import os
from pathlib import Path
from src.report.exporters import JSONExporter, CSVExporter

def main():
    # Dados de exemplo
    sample_data = {
        "results": [
            {
                "id": 1,
                "name": "Movimento 1",
                "score": 0.95,
                "details": {
                    "accuracy": 0.98,
                    "smoothness": 0.92
                }
            },
            {
                "id": 2,
                "name": "Movimento 2",
                "score": 0.85,
                "details": {
                    "accuracy": 0.87,
                    "smoothness": 0.83
                }
            }
        ],
        "metadata": {
            "version": "1.0",
            "timestamp": "2024-03-19",
            "analysis_type": "comparison"
        }
    }
    
    # Cria diretório de saída
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Exporta para JSON
    json_path = output_dir / "analysis_results.json"
    json_exporter = JSONExporter(sample_data)
    json_exporter.export(str(json_path))
    print(f"Arquivo JSON exportado: {json_path}")
    
    # Exporta para CSV
    csv_path = output_dir / "analysis_results.csv"
    csv_exporter = CSVExporter(sample_data)
    csv_exporter.export(str(csv_path))
    print(f"Arquivo CSV exportado: {csv_path}")

if __name__ == "__main__":
    main() 
