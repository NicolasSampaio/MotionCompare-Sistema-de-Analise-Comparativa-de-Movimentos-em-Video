import json
import os
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
from pathlib import Path

from .pose_estimation import PoseLandmark

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class PoseFrame:
    """Classe para representar um frame com landmarks."""
    frame_number: int
    timestamp: float
    landmarks: Dict[int, PoseLandmark]

@dataclass
class PoseData:
    """Classe para representar os dados de pose de um vídeo."""
    video_path: str
    video_hash: str
    fps: float
    resolution: tuple
    total_frames: int
    frames: List[PoseFrame]
    created_at: str
    version: str = "1.0"

class PoseStorage:
    """Classe responsável por gerenciar o armazenamento dos dados de pose."""
    
    def __init__(self, storage_dir: str = "data/pose"):
        """
        Inicializa o sistema de armazenamento.
        
        Args:
            storage_dir: Diretório onde os dados serão armazenados
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.cache = {}
        logger.info(f"Sistema de armazenamento inicializado em: {self.storage_dir}")

    def _generate_video_hash(self, video_path: str) -> str:
        """Gera um hash único para o vídeo."""
        file_hash = hashlib.sha256()
        with open(video_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                file_hash.update(chunk)
        return file_hash.hexdigest()

    def _validate_pose_data(self, data: PoseData) -> bool:
        """Valida os dados de pose."""
        try:
            if not data.video_path or not os.path.exists(data.video_path):
                return False
            if not data.video_hash or len(data.video_hash) != 64:
                return False
            if not data.frames:
                return False
            if not all(isinstance(frame, PoseFrame) for frame in data.frames):
                return False
            return True
        except Exception as e:
            logger.error(f"Erro na validação dos dados: {str(e)}")
            return False

    def save_pose_data(self, video_path: str, fps: float, resolution: tuple, 
                      total_frames: int, frame_landmarks: List[Optional[Dict[int, PoseLandmark]]]) -> bool:
        """
        Salva os dados de pose em formato JSON.
        
        Args:
            video_path: Caminho do vídeo
            fps: Frames por segundo do vídeo
            resolution: Resolução do vídeo (width, height)
            total_frames: Total de frames no vídeo
            frame_landmarks: Lista de landmarks por frame
            
        Returns:
            bool: True se os dados foram salvos com sucesso
        """
        try:
            video_hash = self._generate_video_hash(video_path)
            
            # Converte os landmarks para o formato PoseFrame
            frames = []
            for frame_number, landmarks in enumerate(frame_landmarks):
                if landmarks is not None:
                    timestamp = frame_number / fps
                    frames.append(PoseFrame(
                        frame_number=frame_number,
                        timestamp=timestamp,
                        landmarks=landmarks
                    ))
            
            # Cria o objeto PoseData
            pose_data = PoseData(
                video_path=video_path,
                video_hash=video_hash,
                fps=fps,
                resolution=resolution,
                total_frames=total_frames,
                frames=frames,
                created_at=datetime.now().isoformat()
            )
            
            # Valida os dados
            if not self._validate_pose_data(pose_data):
                raise ValueError("Dados de pose inválidos")
            
            # Converte para JSON
            data_dict = asdict(pose_data)
            data_dict["frames"] = [
                {
                    "frame_number": f.frame_number,
                    "timestamp": f.timestamp,
                    "landmarks": {
                        str(k): asdict(v) for k, v in f.landmarks.items()
                    }
                }
                for f in pose_data.frames
            ]
            
            # Salva o arquivo
            output_path = self.storage_dir / f"{video_hash}.json"
            with open(output_path, "w") as f:
                json.dump(data_dict, f, indent=2)
            
            # Atualiza o cache
            self.cache[video_hash] = pose_data
            
            logger.info(f"Dados de pose salvos com sucesso em: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar dados de pose: {str(e)}")
            return False

    def load_pose_data(self, video_path: str) -> Optional[PoseData]:
        """
        Carrega os dados de pose de um vídeo.
        
        Args:
            video_path: Caminho do vídeo
            
        Returns:
            PoseData ou None se os dados não forem encontrados
        """
        try:
            video_hash = self._generate_video_hash(video_path)
            
            # Verifica o cache primeiro
            if video_hash in self.cache:
                return self.cache[video_hash]
            
            # Carrega do arquivo
            data_path = self.storage_dir / f"{video_hash}.json"
            if not data_path.exists():
                logger.warning(f"Dados de pose não encontrados para: {video_path}")
                return None
            
            with open(data_path, "r") as f:
                data_dict = json.load(f)
            
            # Converte de volta para objetos
            frames = []
            for frame_dict in data_dict["frames"]:
                landmarks = {
                    int(k): PoseLandmark(**v)
                    for k, v in frame_dict["landmarks"].items()
                }
                frames.append(PoseFrame(
                    frame_number=frame_dict["frame_number"],
                    timestamp=frame_dict["timestamp"],
                    landmarks=landmarks
                ))
            
            pose_data = PoseData(
                video_path=data_dict["video_path"],
                video_hash=data_dict["video_hash"],
                fps=data_dict["fps"],
                resolution=tuple(data_dict["resolution"]),
                total_frames=data_dict["total_frames"],
                frames=frames,
                created_at=data_dict["created_at"],
                version=data_dict.get("version", "1.0")
            )
            
            # Atualiza o cache
            self.cache[video_hash] = pose_data
            
            logger.info(f"Dados de pose carregados com sucesso de: {data_path}")
            return pose_data
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados de pose: {str(e)}")
            return None

    def clear_cache(self):
        """Limpa o cache de dados de pose."""
        self.cache.clear()
        logger.info("Cache de dados de pose limpo") 
