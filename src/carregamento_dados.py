import logging
from typing import Tuple, Optional, Dict, List
from pathlib import Path
import numpy as np
from dataclasses import dataclass

from .pose_storage import PoseStorage, PoseData, PoseFrame
from .pose_models import PoseLandmark

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class PoseDataValidationResult:
    """Resultado da validação dos dados de pose."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]

class PoseDataLoader:
    """Classe responsável por carregar e validar dados de pose de dois vídeos."""
    
    def __init__(self, storage_dir: str = "data/pose"):
        """
        Inicializa o carregador de dados.
        
        Args:
            storage_dir: Diretório onde os dados estão armazenados
        """
        self.storage = PoseStorage(storage_dir)
        logger.info("Carregador de dados de pose inicializado")

    def _validate_pose_data(self, data: PoseData) -> PoseDataValidationResult:
        """
        Valida os dados de pose de um vídeo.
        
        Args:
            data: Dados de pose a serem validados
            
        Returns:
            PoseDataValidationResult com o resultado da validação
        """
        errors = []
        warnings = []
        
        # Validação básica
        if not data.frames:
            errors.append("Nenhum frame encontrado nos dados")
            return PoseDataValidationResult(False, errors, warnings)
            
        # Validação de frames
        frame_numbers = [frame.frame_number for frame in data.frames]
        if len(frame_numbers) != len(set(frame_numbers)):
            errors.append("Frames duplicados encontrados")
            
        # Validação de timestamps
        timestamps = [frame.timestamp for frame in data.frames]
        if not all(t1 <= t2 for t1, t2 in zip(timestamps[:-1], timestamps[1:])):
            errors.append("Timestamps não estão em ordem crescente")
            
        # Validação de landmarks
        for frame in data.frames:
            if not frame.landmarks:
                warnings.append(f"Frame {frame.frame_number} não possui landmarks")
                continue
                
            for landmark_id, landmark in frame.landmarks.items():
                if not isinstance(landmark, PoseLandmark):
                    errors.append(f"Landmark inválido no frame {frame.frame_number}")
                    break
                    
                if not (0 <= landmark.visibility <= 1):
                    warnings.append(f"Visibilidade inválida no frame {frame.frame_number}, landmark {landmark_id}")
                    
        return PoseDataValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def _validate_compatibility(self, data1: PoseData, data2: PoseData) -> PoseDataValidationResult:
        """
        Valida a compatibilidade entre dois conjuntos de dados de pose.
        
        Args:
            data1: Primeiro conjunto de dados
            data2: Segundo conjunto de dados
            
        Returns:
            PoseDataValidationResult com o resultado da validação
        """
        errors = []
        warnings = []
        
        # Verifica se os conjuntos de landmarks são compatíveis
        if data1.frames and data2.frames:
            landmarks1 = set(data1.frames[0].landmarks.keys())
            landmarks2 = set(data2.frames[0].landmarks.keys())
            
            if landmarks1 != landmarks2:
                errors.append("Conjuntos de landmarks incompatíveis entre os vídeos")
                
            if len(data1.frames) != len(data2.frames):
                warnings.append("Número diferente de frames entre os vídeos")
                
        return PoseDataValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def load_pose_data(self, video_path1: str, video_path2: str) -> Tuple[Optional[PoseData], Optional[PoseData], PoseDataValidationResult]:
        """
        Carrega e valida os dados de pose de dois vídeos.
        
        Args:
            video_path1: Caminho do primeiro vídeo
            video_path2: Caminho do segundo vídeo
            
        Returns:
            Tuple contendo:
            - Dados de pose do primeiro vídeo (ou None se inválido)
            - Dados de pose do segundo vídeo (ou None se inválido)
            - Resultado da validação
        """
        try:
            # Carrega os dados
            data1 = self.storage.load_pose_data(video_path1)
            data2 = self.storage.load_pose_data(video_path2)
            
            if not data1 or not data2:
                return None, None, PoseDataValidationResult(
                    False,
                    ["Um ou ambos os arquivos de dados não foram encontrados"],
                    []
                )
            
            # Valida cada conjunto de dados individualmente
            validation1 = self._validate_pose_data(data1)
            validation2 = self._validate_pose_data(data2)
            
            if not validation1.is_valid or not validation2.is_valid:
                return None, None, PoseDataValidationResult(
                    False,
                    validation1.errors + validation2.errors,
                    validation1.warnings + validation2.warnings
                )
            
            # Valida compatibilidade entre os conjuntos
            compatibility = self._validate_compatibility(data1, data2)
            
            if not compatibility.is_valid:
                return None, None, compatibility
            
            # Combina todos os warnings
            all_warnings = validation1.warnings + validation2.warnings + compatibility.warnings
            
            return data1, data2, PoseDataValidationResult(True, [], all_warnings)
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados de pose: {str(e)}")
            return None, None, PoseDataValidationResult(
                False,
                [f"Erro ao carregar dados: {str(e)}"],
                []
            )
