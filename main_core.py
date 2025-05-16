import json
import sys
import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, Any

# Inicializa os módulos do MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def process_frame(frame_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processa um frame de vídeo e retorna os landmarks detectados.
    
    Args:
        frame_data: Dicionário contendo os dados do frame
        
    Returns:
        Dicionário com os landmarks detectados
    """
    try:
        # Converte o frame para numpy array
        frame = np.array(frame_data['frame'], dtype=np.uint8)
        
        # Processa o frame com MediaPipe
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(frame_rgb)
            
            if results.pose_landmarks:
                # Converte os landmarks para um formato serializável
                landmarks = []
                for landmark in results.pose_landmarks.landmark:
                    landmarks.append({
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z,
                        'visibility': landmark.visibility
                    })
                return {'success': True, 'landmarks': landmarks}
            
            return {'success': False, 'error': 'Nenhum landmark detectado'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def main():
    """
    Função principal que processa mensagens do Electron.
    """
    while True:
        try:
            # Lê a mensagem do stdin
            message = sys.stdin.readline()
            if not message:
                break
                
            # Processa a mensagem
            data = json.loads(message)
            response = process_frame(data)
            
            # Envia a resposta
            print(json.dumps(response))
            sys.stdout.flush()
            
        except Exception as e:
            error_response = {'success': False, 'error': str(e)}
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == '__main__':
    main() 
