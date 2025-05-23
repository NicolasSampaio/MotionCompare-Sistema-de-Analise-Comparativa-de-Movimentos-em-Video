#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from pathlib import Path

from src.analisador_cli import AnalisadorCLI

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Script simples para comparar dois vídeos de dança usando o AnalisadorCLI."""
    # Caminhos dos vídeos
    video1_path = "videos_teste/sapatoA.mp4"
    video2_path = "videos_teste/sapatoB.mp4"
    
    # Verifica se os vídeos existem
    if not os.path.exists(video1_path) or not os.path.exists(video2_path):
        logger.error(f"Vídeos não encontrados. Verifique os caminhos: {video1_path}, {video2_path}")
        return
    
    logger.info(f"Iniciando comparação entre {video1_path} e {video2_path}")
    
    # Inicializa o analisador CLI
    analisador = AnalisadorCLI(storage_dir="data/pose")
    
    # Compara os vídeos
    results = analisador.compare_videos(
        video1_path=video1_path,
        video2_path=video2_path,
        output_path="reports/comparacao_resultado.json"
    )
    
    if results is None:
        logger.error("Falha ao comparar vídeos")
        return
    
    # Exibe os resultados
    print("\nResultados da Comparação:")
    print(f"Similaridade Média: {results.overall_metrics['average_similarity']:.2f}")
    print(f"Similaridade Mínima: {results.overall_metrics['min_similarity']:.2f}")
    print(f"Similaridade Máxima: {results.overall_metrics['max_similarity']:.2f}")
    print(f"Qualidade do Alinhamento: {results.overall_metrics['alignment_quality']:.2f}")
    print(f"Alinhamento Temporal: {results.overall_metrics['temporal_alignment']:.2f}")
    
    logger.info("Comparação concluída com sucesso!")

if __name__ == "__main__":
    main()
