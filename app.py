import streamlit as st
import cv2
import numpy as np
import tempfile
import os
from pathlib import Path
import mediapipe as mp
from PIL import Image
import time
from moviepy.editor import ImageSequenceClip

# Configuração da página
st.set_page_config(
    page_title="Visualizador de Pose",
    page_icon="🎥",
    layout="wide"
)

# Inicialização do MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def process_video_frame(frame):
    """Processa um frame do vídeo e retorna o frame com o esqueleto desenhado."""
    # Converte BGR para RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Processa o frame
    results = pose.process(frame_rgb)
    
    # Desenha o esqueleto se detectado
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame_rgb,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )
    
    return frame_rgb

def process_entire_video(video_path, progress_bar):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    frames = []
    debug_frame_saved = False

    for i in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break

        processed_frame = process_video_frame(frame)
        processed_frame_bgr = cv2.cvtColor(processed_frame, cv2.COLOR_RGB2BGR)
        processed_frame_bgr = cv2.resize(processed_frame_bgr, (width, height))
        # MoviePy espera RGB
        frames.append(cv2.cvtColor(processed_frame_bgr, cv2.COLOR_BGR2RGB))

        if not debug_frame_saved:
            cv2.imwrite("debug_frame.jpg", processed_frame_bgr)
            debug_frame_saved = True

        progress_bar.progress((i + 1) / total_frames)

    cap.release()

    # Salva o vídeo usando MoviePy (codec H264)
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
    clip = ImageSequenceClip(frames, fps=fps)
    clip.write_videofile(output_path, codec='libx264', audio=False, verbose=False, logger=None)
    return output_path

def main():
    st.title("Visualizador de Pose")
    
    # Inicializa variáveis de estado
    if 'processed_video' not in st.session_state:
        st.session_state.processed_video = None
    
    # Upload do vídeo
    uploaded_file = st.file_uploader(
        "Escolha um vídeo",
        type=['mp4', 'avi', 'mov', 'webm'],
        help="Formatos suportados: MP4, AVI, MOV, webm"
    )
    
    if uploaded_file is not None:
        # Salva o arquivo temporariamente
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}")
        tfile.write(uploaded_file.read())
        tfile.close()
        
        # Abre o vídeo para obter informações
        cap = cv2.VideoCapture(tfile.name)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        cap.release()
        
        # Processa o vídeo se ainda não foi processado
        if st.session_state.processed_video is None:
            with st.spinner('Processando vídeo...'):
                progress_bar = st.progress(0)
                st.session_state.processed_video = process_entire_video(tfile.name, progress_bar)
                st.success('Vídeo processado com sucesso!')
        
        # Interface de controle
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write("Controles de reprodução:")
            st.video(st.session_state.processed_video)
        
        with col2:
            st.write(f"Total de frames: {total_frames}")
            st.write(f"FPS: {fps}")
            st.write(f"Formato: {uploaded_file.name.split('.')[-1].upper()}")
        
        # Limpeza
        try:
            os.unlink(tfile.name)
        except:
            pass  # Ignora erros de deleção do arquivo temporário

if __name__ == "__main__":
    main() 
