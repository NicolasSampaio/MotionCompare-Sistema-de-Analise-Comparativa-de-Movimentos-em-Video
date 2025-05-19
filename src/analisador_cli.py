#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import logging
from typing import List, Optional

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

def main():
    """
    Função principal que processa os argumentos e inicia o processamento do vídeo.
    """
    try:
        args = parse_arguments()
        logger.info(f"Iniciando processamento do vídeo: {args.video}")
        logger.debug(f"Argumentos recebidos: {args}")

        # TODO: Implementar o processamento do vídeo aqui
        # Por enquanto apenas logamos os argumentos recebidos
        logger.info("Processamento do vídeo iniciado com sucesso!")

    except Exception as e:
        logger.error(f"Erro durante o processamento: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
