#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import logging
from typing import List, Optional, Tuple
import cv2
from tqdm import tqdm
import json
from pathlib import Path

from .pose_estimation import PoseExtractor
from .comparison_params import ComparisonParams, DistanceMetric
from .comparison_results import ComparisonResults
from .results_cache import ResultsCache
from .pose_storage import PoseStorage
from .comparador_movimento import ComparadorMovimento

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Formatos de vídeo suportados
SUPPORTED_FORMATS = ['.mp4', '.avi', '.mov']

def validate_video_format(file_path: str) -> bool:
    """
    Valida se o formato do arquivo de vídeo é suportado.
    
    Args:
        file_path (str): Caminho do arquivo de vídeo
        
    Returns:
        bool: True se o formato é suportado, False caso contrário
    """
    _, ext = os.path.splitext(file_path.lower())
    return ext in SUPPORTED_FORMATS

def validate_file_path(file_path: str) -> bool:
    """
    Valida se o arquivo existe e é acessível.
    
    Args:
        file_path (str): Caminho do arquivo
        
    Returns:
        bool: True se o arquivo é válido, False caso contrário
    """
    return os.path.isfile(file_path) and os.access(file_path, os.R_OK)

def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Configura e processa os argumentos da linha de comando.
    
    Args:
        args (Optional[List[str]]): Lista de argumentos da linha de comando
        
    Returns:
        argparse.Namespace: Argumentos processados
    """
    parser = argparse.ArgumentParser(
        description='Ferramenta de análise de vídeo via linha de comando',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python analisador_cli.py -v video.mp4
  python analisador_cli.py -v video.mp4 -o output.mp4 -r 720p
  python analisador_cli.py -v video.mp4 -f 30 --verbose
  python analisador_cli.py -v video.mp4 --config params.json
        """
    )

    parser.add_argument(
        '-v', '--video',
        required=True,
        help='Caminho do arquivo de vídeo a ser processado'
    )

    parser.add_argument(
        '-o', '--output',
        help='Caminho do arquivo de saída (opcional)'
    )

    parser.add_argument(
        '-r', '--resolution',
        choices=['480p', '720p', '1080p'],
        default='720p',
        help='Resolução de saída do vídeo (padrão: 720p)'
    )

    parser.add_argument(
        '-f', '--fps',
        type=int,
        help='FPS de processamento (opcional)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Ativa modo verbose para mais informações de debug'
    )

    parser.add_argument(
        '--skip-processing',
        action='store_true',
        help='Pula o processamento do vídeo e carrega os dados salvos'
    )

    # Novos argumentos para parâmetros de comparação
    parser.add_argument(
        '--config',
        help='Caminho para arquivo de configuração JSON com parâmetros de comparação'
    )

    parser.add_argument(
        '--metric',
        choices=['euclidean', 'dtw'],
        help='Métrica de distância para comparação'
    )

    parser.add_argument(
        '--tolerance',
        type=float,
        help='Tolerância de similaridade (0-1)'
    )

    parser.add_argument(
        '--landmark-weights',
        help='Pesos dos landmarks no formato JSON (ex: {"shoulder": 0.8, "hip": 0.6})'
    )

    parser.add_argument(
        '--temporal-sync',
        action='store_true',
        help='Ativar sincronização temporal'
    )

    parser.add_argument(
        '--no-temporal-sync',
        action='store_false',
        dest='temporal_sync',
        help='Desativar sincronização temporal'
    )

    parser.add_argument(
        '--normalize',
        action='store_true',
        help='Ativar normalização'
    )

    parser.add_argument(
        '--no-normalize',
        action='store_false',
        dest='normalize',
        help='Desativar normalização'
    )

    parser.add_argument(
        '--storage-dir',
        default="data/pose",
        help="Diretório para armazenar os dados de pose"
    )

    parser.add_argument(
        '--command',
        choices=['process', 'compare'],
        required=True,
        help="Comando a ser executado"
    )

    parser.add_argument(
        'video1',
        help="Caminho do primeiro vídeo para comparação"
    )

    parser.add_argument(
        'video2',
        help="Caminho do segundo vídeo para comparação"
    )

    parsed_args = parser.parse_args(args)

    # Validações
    if not validate_file_path(parsed_args.video):
        parser.error(f"Arquivo não encontrado ou sem permissão de leitura: {parsed_args.video}")

    if not validate_video_format(parsed_args.video):
        parser.error(f"Formato de vídeo não suportado. Formatos aceitos: {', '.join(SUPPORTED_FORMATS)}")

    if parsed_args.output and not validate_video_format(parsed_args.output):
        parser.error(f"Formato de saída não suportado. Formatos aceitos: {', '.join(SUPPORTED_FORMATS)}")

    if parsed_args.fps is not None and parsed_args.fps <= 0:
        parser.error("FPS deve ser um número positivo")

    # Validação dos parâmetros de comparação
    if parsed_args.config:
        if not validate_file_path(parsed_args.config):
            parser.error(f"Arquivo de configuração não encontrado: {parsed_args.config}")
        try:
            with open(parsed_args.config, 'r') as f:
                json.load(f)
        except json.JSONDecodeError:
            parser.error(f"Arquivo de configuração inválido: {parsed_args.config}")

    if parsed_args.tolerance is not None and not 0 <= parsed_args.tolerance <= 1:
        parser.error("Tolerância deve estar entre 0 e 1")

    if parsed_args.landmark_weights:
        try:
            weights = json.loads(parsed_args.landmark_weights)
            if not isinstance(weights, dict):
                parser.error("Pesos dos landmarks devem ser um objeto JSON")
            for weight in weights.values():
                if not isinstance(weight, (int, float)) or not 0 <= weight <= 1:
                    parser.error("Pesos dos landmarks devem estar entre 0 e 1")
        except json.JSONDecodeError:
            parser.error("Formato inválido para pesos dos landmarks")

    # Configuração do nível de logging
    if parsed_args.verbose:
        logger.setLevel(logging.DEBUG)

    return parsed_args

def get_comparison_params(args: argparse.Namespace) -> ComparisonParams:
    """
    Obtém os parâmetros de comparação a partir dos argumentos da linha de comando.
    
    Args:
        args (argparse.Namespace): Argumentos processados
        
    Returns:
        ComparisonParams: Parâmetros de comparação
    """
    if args.config:
        return ComparisonParams.load_from_file(args.config)
    
    params = ComparisonParams()
    
    if args.metric:
        params.metric = DistanceMetric(args.metric)
    if args.tolerance is not None:
        params.tolerance = args.tolerance
    if args.landmark_weights:
        params.landmark_weights = json.loads(args.landmark_weights)
    if args.temporal_sync is not None:
        params.temporal_sync = args.temporal_sync
    if args.normalize is not None:
        params.normalize = args.normalize
    
    return params

def process_video(video_path: str, output_path: Optional[str] = None, 
                 resolution: str = '720p', fps: Optional[int] = None,
                 skip_processing: bool = False,
                 comparison_params: Optional[ComparisonParams] = None) -> bool:
    """
    Processa o vídeo e extrai os dados de pose.
    
    Args:
        video_path: Caminho do vídeo de entrada
        output_path: Caminho do vídeo de saída (opcional)
        resolution: Resolução de saída ('480p', '720p', '1080p')
        fps: FPS de processamento (opcional)
        skip_processing: Se True, pula o processamento e carrega os dados salvos
        comparison_params: Parâmetros de comparação (opcional)
        
    Returns:
        bool: True se o processamento foi bem sucedido
    """
    try:
        # Inicializa o extrator de pose com os parâmetros de comparação
        extractor = PoseExtractor(comparison_params)
        
        # Verifica se já existem dados processados
        if skip_processing:
            try:
                extractor.load_processed_data(video_path)
                logger.info("Dados carregados com sucesso")
                return True
            except Exception as e:
                logger.error(f"Erro ao carregar dados processados: {str(e)}")
                return False
        
        # Processa o vídeo
        if not extractor.process_video(video_path, output_path, resolution, fps):
            return False
            
        # Salva os dados processados
        extractor.save_processed_data(video_path)
        logger.info("Dados processados salvos com sucesso")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao processar vídeo: {str(e)}")
        return False

def compare_videos(video1_path: str, video2_path: str,
                  comparison_params: Optional[ComparisonParams] = None) -> Optional[ComparisonResults]:
    """
    Compara dois vídeos usando os parâmetros especificados.
    
    Args:
        video1_path: Caminho do primeiro vídeo
        video2_path: Caminho do segundo vídeo
        comparison_params: Parâmetros de comparação (opcional)
        
    Returns:
        Optional[ComparisonResults]: Resultados da comparação ou None em caso de erro
    """
    try:
        # Inicializa o cache
        cache = ResultsCache()
        
        # Gera uma chave única para o cache baseada nos vídeos e parâmetros
        cache_key = f"{video1_path}_{video2_path}_{hash(str(comparison_params))}"
        
        # Tenta recuperar do cache
        cached_results = cache.get(cache_key)
        if cached_results is not None:
            logger.info("Resultados recuperados do cache")
            return cached_results
        
        # Processa os vídeos se necessário
        extractor = PoseExtractor(comparison_params)
        
        # Carrega ou processa o primeiro vídeo
        if not extractor.load_processed_data(video1_path):
            if not process_video(video1_path, comparison_params=comparison_params):
                return None
            extractor.load_processed_data(video1_path)
            
        # Carrega ou processa o segundo vídeo
        if not extractor.load_processed_data(video2_path):
            if not process_video(video2_path, comparison_params=comparison_params):
                return None
            extractor.load_processed_data(video2_path)
            
        # Realiza a comparação
        results = extractor.compare_videos()
        
        # Armazena no cache
        cache.set(cache_key, results)
        
        return results
        
    except Exception as e:
        logger.error(f"Erro ao comparar vídeos: {str(e)}")
        return None

def save_results(results: ComparisonResults, output_path: str) -> bool:
    """
    Salva os resultados em um arquivo JSON.
    
    Args:
        results: Resultados da comparação
        output_path: Caminho do arquivo de saída
        
    Returns:
        bool: True se os resultados foram salvos com sucesso
    """
    try:
        with open(output_path, 'w') as f:
            json.dump(results.to_dict(), f, indent=2)
        logger.info(f"Resultados salvos em: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar resultados: {str(e)}")
        return False

class AnalisadorCLI:
    def __init__(
        self,
        storage_dir: str = "data/pose",
        pose_storage: Optional[PoseStorage] = None,
        pose_extractor: Optional[PoseExtractor] = None,
        comparador: Optional[ComparadorMovimento] = None
    ):
        """
        Inicializa o analisador CLI.
        Args:
            storage_dir: Diretório para armazenar os dados de pose
            pose_storage: Instância de PoseStorage (injeção para testes)
            pose_extractor: Instância de PoseExtractor (injeção para testes)
            comparador: Instância de ComparadorMovimento (injeção para testes)
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.pose_storage = pose_storage or PoseStorage(self.storage_dir)
        self.pose_extractor = pose_extractor or PoseExtractor()
        self.comparador = comparador or ComparadorMovimento()
        
    def process_video(self, video_path: str, output_path: Optional[str] = None,
                     resolution: Optional[Tuple[int, int]] = None) -> bool:
        """
        Processa um vídeo para extrair os landmarks de pose.
        
        Args:
            video_path: Caminho do vídeo
            output_path: Caminho para salvar o vídeo processado (opcional)
            resolution: Resolução do vídeo processado (opcional)
            
        Returns:
            bool: True se o processamento foi bem-sucedido
        """
        try:
            # Verifica se o vídeo já foi processado
            if self.pose_storage.load_pose_data(video_path) is not None:
                logger.info(f"Vídeo já processado: {video_path}")
                return True
                
            # Processa o vídeo
            success = self.pose_extractor.process_video(
                video_path=video_path,
                output_path=output_path,
                resolution=resolution
            )
            
            if not success:
                logger.error(f"Falha ao processar vídeo: {video_path}")
                return False
                
            # Obtém os landmarks processados
            landmarks = self.pose_extractor.get_landmarks()
            if not landmarks:
                logger.error(f"Nenhum landmark extraído do vídeo: {video_path}")
                return False
                
            # Obtém as informações do vídeo
            fps = self.pose_extractor.get_fps()
            resolution = self.pose_extractor.get_resolution()
            total_frames = self.pose_extractor.get_total_frames()
            
            # Salva os dados de pose
            success = self.pose_storage.save_pose_data(
                video_path=video_path,
                fps=fps,
                resolution=resolution,
                total_frames=total_frames,
                frame_landmarks=landmarks
            )
            
            if not success:
                logger.error(f"Falha ao salvar dados de pose: {video_path}")
                return False
                
            logger.info(f"Vídeo processado com sucesso: {video_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar vídeo: {str(e)}")
            return False
            
    def compare_videos(self, video1_path: str, video2_path: str,
                      output_path: Optional[str] = None) -> Optional[ComparisonResults]:
        """
        Compara dois vídeos.
        
        Args:
            video1_path: Caminho do primeiro vídeo
            video2_path: Caminho do segundo vídeo
            output_path: Caminho para salvar os resultados (opcional)
            
        Returns:
            ComparisonResults ou None se a comparação falhar
        """
        try:
            # Verifica se os vídeos já foram processados
            video1_data = self.pose_storage.load_pose_data(video1_path)
            video2_data = self.pose_storage.load_pose_data(video2_path)
            
            if video1_data is None:
                logger.info(f"Processando primeiro vídeo: {video1_path}")
                if not self.process_video(video1_path):
                    return None
                video1_data = self.pose_storage.load_pose_data(video1_path)
                
            if video2_data is None:
                logger.info(f"Processando segundo vídeo: {video2_path}")
                if not self.process_video(video2_path):
                    return None
                video2_data = self.pose_storage.load_pose_data(video2_path)
                
            # Verifica se já existe uma comparação
            results = self.pose_storage.load_comparison_results(video1_path, video2_path)
            if results is not None:
                logger.info(f"Comparação já existe para: {video1_path} e {video2_path}")
                return results
                
            # Obtém os landmarks no formato do comparador
            video1_landmarks = self.pose_storage.get_pose_data(video1_path)
            video2_landmarks = self.pose_storage.get_pose_data(video2_path)
            
            if video1_landmarks is None or video2_landmarks is None:
                logger.error("Falha ao obter landmarks dos vídeos")
                return None
                
            # Compara os vídeos
            results = self.comparador.compare_videos(
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
            if output_path:
                success = self.pose_storage.save_comparison_results(
                    video1_path=video1_path,
                    video2_path=video2_path,
                    results=results
                )
                if not success:
                    logger.error(f"Falha ao salvar resultados da comparação: {output_path}")
                    
            logger.info(f"Vídeos comparados com sucesso: {video1_path} e {video2_path}")
            return results
            
        except Exception as e:
            logger.error(f"Erro ao comparar vídeos: {str(e)}")
            return None

def main():
    """Função principal do CLI."""
    args = parse_arguments()
    
    # Inicializa o analisador
    analisador = AnalisadorCLI(storage_dir=args.storage_dir)
    
    # Executa o comando
    if args.command == "process":
        success = analisador.process_video(
            video_path=args.video,
            output_path=args.output,
            resolution=tuple(args.resolution) if args.resolution else None
        )
        if not success:
            logger.error("Falha ao processar vídeo")
            return 1
            
    elif args.command == "compare":
        results = analisador.compare_videos(
            video1_path=args.video1,
            video2_path=args.video2,
            output_path=args.output
        )
        if results is None:
            logger.error("Falha ao comparar vídeos")
            return 1
            
        # Exibe os resultados
        print("\nResultados da Comparação:")
        print(f"Similaridade Média: {results.overall_metrics['average_similarity']:.2f}")
        print(f"Similaridade Mínima: {results.overall_metrics['min_similarity']:.2f}")
        print(f"Similaridade Máxima: {results.overall_metrics['max_similarity']:.2f}")
        print(f"Qualidade do Alinhamento: {results.overall_metrics['alignment_quality']:.2f}")
        print(f"Alinhamento Temporal: {results.overall_metrics['temporal_alignment']:.2f}")
        
    else:
        logger.error("Comando inválido")
        return 1
        
    return 0
    
if __name__ == "__main__":
    exit(main())
