#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from pathlib import Path

from src.pose_estimation import PoseExtractor
from src.comparison_params import ComparisonParams, DistanceMetric
from src.comparador_movimento import ComparadorMovimento
from src.pose_storage import PoseStorage

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Script para comparar dois vídeos de dança."""
    # Caminhos dos vídeos
    video1_path = "videos_teste/esq.mp4"
    video2_path = "videos_teste/dir.mp4"
    
    # Verifica se os vídeos existem
    if not os.path.exists(video1_path) or not os.path.exists(video2_path):
        logger.error(f"Vídeos não encontrados. Verifique os caminhos: {video1_path}, {video2_path}")
        return
    
    logger.info(f"Iniciando comparação entre {video1_path} e {video2_path}")
    
    # Inicializa os componentes
    storage_dir = Path("data/pose")
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    pose_storage = PoseStorage(storage_dir)
    pose_extractor = PoseExtractor()
    comparador = ComparadorMovimento()
    
    # Processa o primeiro vídeo se necessário
    video1_data = pose_storage.load_pose_data(video1_path)
    if video1_data is None:
        logger.info(f"Processando primeiro vídeo: {video1_path}")
        success = pose_extractor.process_video(video1_path)
        if not success:
            logger.error(f"Falha ao processar vídeo: {video1_path}")
            return
        
        # Obtém os landmarks processados
        landmarks = pose_extractor.get_landmarks()
        if not landmarks:
            logger.error(f"Nenhum landmark extraído do vídeo: {video1_path}")
            return
            
        # Obtém as informações do vídeo
        fps = pose_extractor.get_fps()
        resolution = pose_extractor.get_resolution()
        total_frames = pose_extractor.get_total_frames()
        
        # Salva os dados de pose
        success = pose_storage.save_pose_data(
            video_path=video1_path,
            fps=fps,
            resolution=resolution,
            total_frames=total_frames,
            frame_landmarks=landmarks
        )
        
        if not success:
            logger.error(f"Falha ao salvar dados de pose: {video1_path}")
            return
            
        video1_data = pose_storage.load_pose_data(video1_path)
    
    # Processa o segundo vídeo se necessário
    video2_data = pose_storage.load_pose_data(video2_path)
    if video2_data is None:
        logger.info(f"Processando segundo vídeo: {video2_path}")
        success = pose_extractor.process_video(video2_path)
        if not success:
            logger.error(f"Falha ao processar vídeo: {video2_path}")
            return
        
        # Obtém os landmarks processados
        landmarks = pose_extractor.get_landmarks()
        if not landmarks:
            logger.error(f"Nenhum landmark extraído do vídeo: {video2_path}")
            return
            
        # Obtém as informações do vídeo
        fps = pose_extractor.get_fps()
        resolution = pose_extractor.get_resolution()
        total_frames = pose_extractor.get_total_frames()
        
        # Salva os dados de pose
        success = pose_storage.save_pose_data(
            video_path=video2_path,
            fps=fps,
            resolution=resolution,
            total_frames=total_frames,
            frame_landmarks=landmarks
        )
        
        if not success:
            logger.error(f"Falha ao salvar dados de pose: {video2_path}")
            return
            
        video2_data = pose_storage.load_pose_data(video2_path)
    
    # Verifica se já existe uma comparação
    results = pose_storage.load_comparison_results(video1_path, video2_path)
    if results is not None:
        logger.info(f"Comparação já existe para: {video1_path} e {video2_path}")
    else:
        # Obtém os landmarks no formato do comparador
        video1_landmarks = pose_storage.get_pose_data(video1_path)
        video2_landmarks = pose_storage.get_pose_data(video2_path)
        
        if video1_landmarks is None or video2_landmarks is None:
            logger.error("Falha ao obter landmarks dos vídeos")
            return
            
        # Configura os parâmetros de comparação
        params = ComparisonParams(
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
        
        # Compara os vídeos
        logger.info("Comparando vídeos...")
        results = comparador.compare_videos(
            video1_landmarks=video1_landmarks,
            video2_landmarks=video2_landmarks,
            video1_fps=video1_data.fps,
            video2_fps=video2_data.fps,
            video1_resolution=video1_data.resolution,
            video2_resolution=video2_data.resolution
        )
        
        # Atualiza os caminhos dos vídeos
        results.video1_path = video1_path
        results.video2_path = video2_path
        
        # Salva os resultados
        pose_storage.save_comparison_results(
            video1_path=video1_path,
            video2_path=video2_path,
            results=results
        )
    
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
