#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import logging
from pathlib import Path

# Adiciona o diretório src ao PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from src.pose_estimation import PoseExtractor
from src.comparison_params import ComparisonParams, DistanceMetric
from src.comparador_movimento import DanceComparison, FrameData

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Exemplo de uso dos parâmetros de comparação."""
    # Caminhos dos vídeos
    video1_path = "video1.mp4"
    video2_path = "video2.mp4"
    
    # Verifica se os vídeos existem
    if not os.path.exists(video1_path) or not os.path.exists(video2_path):
        logger.error("Vídeos não encontrados. Por favor, forneça os caminhos corretos.")
        return
    
    # Inicializa o extrator de pose
    extractor = PoseExtractor()
    
    # Processa os vídeos
    logger.info("Processando vídeo 1...")
    video1_data = extractor.process_video(video1_path)
    
    logger.info("Processando vídeo 2...")
    video2_data = extractor.process_video(video2_path)
    
    # Exemplo 1: Configuração padrão
    logger.info("\nExemplo 1: Configuração padrão")
    params1 = ComparisonParams()
    comparison1 = DanceComparison(video1_data, video2_data, params1)
    similarity1 = comparison1.get_similarity()
    logger.info(f"Similaridade: {similarity1:.2f}")
    
    # Exemplo 2: Configuração para dança contemporânea
    logger.info("\nExemplo 2: Configuração para dança contemporânea")
    params2 = ComparisonParams(
        metric=DistanceMetric.DTW,
        tolerance=0.2,
        landmark_weights={
            "shoulder": 0.9,
            "hip": 0.8,
            "knee": 0.7,
            "ankle": 0.6
        },
        temporal_sync=True,
        normalize=True
    )
    comparison2 = DanceComparison(video1_data, video2_data, params2)
    similarity2 = comparison2.get_similarity()
    logger.info(f"Similaridade: {similarity2:.2f}")
    
    # Exemplo 3: Configuração para movimentos rápidos
    logger.info("\nExemplo 3: Configuração para movimentos rápidos")
    params3 = ComparisonParams(
        metric=DistanceMetric.EUCLIDEAN,
        tolerance=0.3,
        landmark_weights={
            "shoulder": 0.7,
            "hip": 0.8,
            "knee": 0.9,
            "ankle": 1.0
        },
        temporal_sync=False,
        normalize=True
    )
    comparison3 = DanceComparison(video1_data, video2_data, params3)
    similarity3 = comparison3.get_similarity()
    logger.info(f"Similaridade: {similarity3:.2f}")
    
    # Exemplo 4: Carregando configuração de arquivo
    logger.info("\nExemplo 4: Carregando configuração de arquivo")
    config_path = "examples/config.json"
    if os.path.exists(config_path):
        params4 = ComparisonParams.load_from_file(config_path)
        comparison4 = DanceComparison(video1_data, video2_data, params4)
        similarity4 = comparison4.get_similarity()
        logger.info(f"Similaridade: {similarity4:.2f}")
    else:
        logger.warning(f"Arquivo de configuração não encontrado: {config_path}")

if __name__ == "__main__":
    main() 
