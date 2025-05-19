#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import logging
from typing import List, Optional
import cv2
from tqdm import tqdm

from .pose_estimation import PoseExtractor

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
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

    # Configuração do nível de logging
    if parsed_args.verbose:
        logger.setLevel(logging.DEBUG)

    return parsed_args

def process_video(video_path: str, output_path: Optional[str] = None, 
                 resolution: str = '720p', fps: Optional[int] = None,
                 skip_processing: bool = False) -> bool:
    """
    Processa o vídeo e extrai os dados de pose.
    
    Args:
        video_path: Caminho do vídeo de entrada
        output_path: Caminho do vídeo de saída (opcional)
        resolution: Resolução de saída ('480p', '720p', '1080p')
        fps: FPS de processamento (opcional)
        skip_processing: Se True, pula o processamento e carrega os dados salvos
        
    Returns:
        bool: True se o processamento foi bem sucedido
    """
    try:
        # Inicializa o extrator de pose
        extractor = PoseExtractor()
        
        if skip_processing:
            logger.info("Carregando dados de pose salvos...")
            frame_landmarks = extractor.load_pose_data(video_path)
            if frame_landmarks is None:
                logger.error("Dados de pose não encontrados. Execute sem --skip-processing primeiro.")
                return False
            logger.info("Dados de pose carregados com sucesso!")
        else:
            logger.info("Processando vídeo...")
            frame_landmarks = extractor.process_video(
                video_path,
                progress_callback=lambda current, total: logger.info(f"Progresso: {current}/{total} frames")
            )
            if not frame_landmarks:
                logger.error("Erro ao processar vídeo")
                return False
            logger.info("Processamento concluído com sucesso!")
        
        # Se um arquivo de saída foi especificado, gera o vídeo com os landmarks
        if output_path:
            logger.info(f"Gerando vídeo de saída: {output_path}")
            
            # Abre o vídeo de entrada
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Não foi possível abrir o vídeo: {video_path}")
            
            # Obtém informações do vídeo
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            video_fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Define a resolução de saída
            if resolution == '480p':
                width, height = 854, 480
            elif resolution == '720p':
                width, height = 1280, 720
            elif resolution == '1080p':
                width, height = 1920, 1080
            
            # Define o FPS de saída
            if fps is None:
                fps = video_fps
            
            # Configura o writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            frame_count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Redimensiona o frame se necessário
                if frame.shape[1] != width or frame.shape[0] != height:
                    frame = cv2.resize(frame, (width, height))
                
                # Desenha os landmarks se disponíveis
                if frame_landmarks[frame_count]:
                    for landmark in frame_landmarks[frame_count].values():
                        x = int(landmark.x * width)
                        y = int(landmark.y * height)
                        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
                
                out.write(frame)
                frame_count += 1
            
            cap.release()
            out.release()
            logger.info("Vídeo de saída gerado com sucesso!")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro durante o processamento do vídeo: {str(e)}")
        return False

def main():
    """
    Função principal que processa os argumentos e inicia o processamento do vídeo.
    """
    try:
        args = parse_arguments()
        logger.info(f"Iniciando processamento do vídeo: {args.video}")
        logger.debug(f"Argumentos recebidos: {args}")

        success = process_video(
            video_path=args.video,
            output_path=args.output,
            resolution=args.resolution,
            fps=args.fps,
            skip_processing=args.skip_processing
        )

        if success:
            logger.info("Processamento concluído com sucesso!")
            sys.exit(0)
        else:
            logger.error("Erro durante o processamento")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Erro durante o processamento: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
