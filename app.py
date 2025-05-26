import streamlit as st
import cv2
import tempfile
import os
from pathlib import Path
import mediapipe as mp
import logging
from datetime import datetime
from moviepy.editor import ImageSequenceClip

# Importações do projeto
from src.pose_estimation import PoseExtractor
from src.comparador_movimento import ComparadorMovimento
from src.pose_storage import PoseStorage
# from src.comparison_params import ComparisonParams  # Não usado na implementação atual
from src.gerador_relatorio import ReportGenerator
from src.comparison_results import DanceComparison

# Configuração da página
st.set_page_config(
    page_title="Comparador de Vídeos de Dança",
    page_icon="🎭",
    layout="wide"
)

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialização do MediaPipe Pose para preview
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Inicialização dos componentes do sistema
@st.cache_resource
def init_system_components():
    """Inicializa os componentes do sistema de comparação."""
    storage_dir = Path("data/pose")
    storage_dir.mkdir(parents=True, exist_ok=True)

    pose_storage = PoseStorage(storage_dir)
    pose_extractor = PoseExtractor()
    comparador = ComparadorMovimento()

    return pose_storage, pose_extractor, comparador

def process_video_frame_preview(frame):
    """Processa um frame do vídeo para preview e retorna o frame com o esqueleto desenhado."""
    try:
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
    except Exception as e:
        logger.error(f"Erro ao processar frame para preview: {str(e)}")
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

def create_preview_video(video_path, progress_bar, max_frames=150):
    """Cria um vídeo de preview com esqueleto desenhado (limitado para performance)."""
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Limita o número de frames para preview
    frames_to_process = min(total_frames, max_frames)
    frame_step = max(1, total_frames // frames_to_process)

    frames = []
    frame_count = 0

    for i in range(0, total_frames, frame_step):
        if frame_count >= max_frames:
            break

        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            break

        processed_frame = process_video_frame_preview(frame)
        processed_frame_bgr = cv2.cvtColor(processed_frame, cv2.COLOR_RGB2BGR)
        processed_frame_bgr = cv2.resize(processed_frame_bgr, (width, height))
        # MoviePy espera RGB
        frames.append(cv2.cvtColor(processed_frame_bgr, cv2.COLOR_BGR2RGB))

        frame_count += 1
        progress_bar.progress(frame_count / frames_to_process)

    cap.release()

    if not frames:
        return None

    # Salva o vídeo usando MoviePy (codec H264)
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
    clip = ImageSequenceClip(frames, fps=fps)
    clip.write_videofile(output_path, codec='libx264', audio=False, verbose=False, logger=None)
    return output_path

def fix_comparison_results(results):
    """
    Corrige os resultados de comparação, convertendo dicionários em objetos DanceComparison.

    Args:
        results: ComparisonResults que pode ter frame_comparisons como dicionários

    Returns:
        ComparisonResults com frame_comparisons corrigidos
    """
    if not results or not results.frame_comparisons:
        return results

    try:
        # Verifica se os frame_comparisons são dicionários e os converte para objetos
        fixed_frame_comparisons = []

        for fc in results.frame_comparisons:
            if isinstance(fc, dict):
                # Converte dicionário para objeto DanceComparison
                dance_comparison = DanceComparison(
                    frame_number=fc.get('frame_number', 0),
                    timestamp=fc.get('timestamp', 0.0),
                    similarity_score=fc.get('similarity_score', 0.0),
                    landmark_similarities=fc.get('landmark_similarities', {}),
                    alignment_metrics=fc.get('alignment_metrics', {})
                )
                fixed_frame_comparisons.append(dance_comparison)
            else:
                # Já é um objeto, mantém como está
                fixed_frame_comparisons.append(fc)

        # Atualiza os frame_comparisons
        results.frame_comparisons = fixed_frame_comparisons
        logger.info(f"Corrigidos {len(fixed_frame_comparisons)} frame comparisons")

    except Exception as e:
        logger.error(f"Erro ao corrigir frame_comparisons: {str(e)}")

    return results

def process_video_with_pose_extractor(video_path, pose_extractor, pose_storage):
    """Processa um vídeo usando o PoseExtractor do projeto."""
    try:
        # Verifica se já existe dados processados
        video_data = pose_storage.load_pose_data(video_path)
        if video_data is not None:
            logger.info(f"Dados de pose já existem para: {video_path}")
            return video_data

        # Processa o vídeo
        logger.info(f"Processando vídeo: {video_path}")
        success = pose_extractor.process_video(video_path)
        if not success:
            logger.error(f"Falha ao processar vídeo: {video_path}")
            return None

        # Obtém os landmarks processados
        landmarks = pose_extractor.get_landmarks()
        if not landmarks:
            logger.error(f"Nenhum landmark extraído do vídeo: {video_path}")
            return None

        # Obtém as informações do vídeo
        fps = pose_extractor.get_fps()
        resolution = pose_extractor.get_resolution()
        total_frames = pose_extractor.get_total_frames()

        # Salva os dados de pose
        success = pose_storage.save_pose_data(
            video_path=video_path,
            fps=fps,
            resolution=resolution,
            total_frames=total_frames,
            frame_landmarks=landmarks
        )

        if not success:
            logger.error(f"Falha ao salvar dados de pose: {video_path}")
            return None

        return pose_storage.load_pose_data(video_path)

    except Exception as e:
        logger.error(f"Erro ao processar vídeo: {str(e)}")
        return None

def display_comparison_results(results):
    """Exibe os resultados da comparação de forma organizada."""
    if not results:
        st.error("Nenhum resultado de comparação disponível.")
        return

    # Métricas principais
    st.subheader("📊 Métricas de Similaridade")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_sim = results.overall_metrics.get('average_similarity', 0.0)
        st.metric("Similaridade Média", f"{avg_sim:.2%}")

    with col2:
        min_sim = results.overall_metrics.get('min_similarity', 0.0)
        st.metric("Similaridade Mínima", f"{min_sim:.2%}")

    with col3:
        max_sim = results.overall_metrics.get('max_similarity', 0.0)
        st.metric("Similaridade Máxima", f"{max_sim:.2%}")

    with col4:
        alignment = results.overall_metrics.get('alignment_quality', 0.0)
        st.metric("Qualidade do Alinhamento", f"{alignment:.2%}")

    # Gráfico de similaridade por frame
    if results.frame_comparisons:
        st.subheader("📈 Similaridade por Frame")

        # Debug: mostra informações sobre os frame_comparisons
        logger.info(f"Processando {len(results.frame_comparisons)} frame comparisons")
        if results.frame_comparisons:
            first_fc = results.frame_comparisons[0]
            logger.info(f"Tipo do primeiro frame comparison: {type(first_fc)}")
            if isinstance(first_fc, dict):
                logger.info(f"Chaves do dicionário: {list(first_fc.keys())}")

        try:
            # Extrai dados dos frame comparisons (suporta tanto objetos quanto dicionários)
            frame_numbers = []
            similarity_scores = []

            for i, fc in enumerate(results.frame_comparisons):
                if hasattr(fc, 'frame_number'):
                    # É um objeto DanceComparison
                    frame_numbers.append(fc.frame_number)
                    similarity_scores.append(fc.similarity_score)
                elif isinstance(fc, dict):
                    # É um dicionário
                    frame_numbers.append(fc.get('frame_number', i))  # usa índice como fallback
                    similarity_scores.append(fc.get('similarity_score', 0.0))
                else:
                    logger.warning(f"Formato de frame comparison não reconhecido: {type(fc)}")
                    # Tenta usar como fallback
                    frame_numbers.append(i)
                    similarity_scores.append(0.0)
                    continue

            if frame_numbers and similarity_scores:
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(frame_numbers, similarity_scores, linewidth=2, color='#1f77b4')
                ax.fill_between(frame_numbers, similarity_scores, alpha=0.3, color='#1f77b4')
                ax.set_xlabel('Frame')
                ax.set_ylabel('Similaridade')
                ax.set_title('Evolução da Similaridade ao Longo do Tempo')
                ax.grid(True, alpha=0.3)
                ax.set_ylim(0, 1)

                st.pyplot(fig)

                # Estatísticas adicionais do gráfico
                st.write(f"📊 **Estatísticas do gráfico:** {len(frame_numbers)} frames analisados")
            else:
                st.warning("Nenhum dado de frame válido encontrado para o gráfico.")

                # Fallback: tenta usar frame_scores se disponível
                if hasattr(results, 'frame_scores') and results.frame_scores:
                    st.info("Usando dados alternativos para o gráfico...")
                    frame_numbers = list(range(len(results.frame_scores)))
                    similarity_scores = results.frame_scores

                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots(figsize=(12, 6))
                    ax.plot(frame_numbers, similarity_scores, linewidth=2, color='#ff7f0e')
                    ax.fill_between(frame_numbers, similarity_scores, alpha=0.3, color='#ff7f0e')
                    ax.set_xlabel('Frame')
                    ax.set_ylabel('Similaridade')
                    ax.set_title('Evolução da Similaridade ao Longo do Tempo (Dados Alternativos)')
                    ax.grid(True, alpha=0.3)
                    ax.set_ylim(0, 1)

                    st.pyplot(fig)
                    st.write(f"📊 **Estatísticas do gráfico:** {len(frame_numbers)} frames analisados (dados alternativos)")

        except Exception as e:
            st.error(f"Erro ao gerar gráfico de similaridade: {str(e)}")
            logger.error(f"Erro ao gerar gráfico: {str(e)}")

            # Fallback final: mostra informações básicas
            st.write(f"📊 **Frames analisados:** {len(results.frame_comparisons)}")
            if hasattr(results, 'frame_scores') and results.frame_scores:
                avg_score = sum(results.frame_scores) / len(results.frame_scores)
                st.write(f"📈 **Similaridade média dos frames:** {avg_score:.2%}")

                # Tenta mostrar um gráfico simples com frame_scores
                try:
                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots(figsize=(10, 4))
                    ax.plot(results.frame_scores, linewidth=2, color='#2ca02c')
                    ax.set_xlabel('Frame Index')
                    ax.set_ylabel('Similaridade')
                    ax.set_title('Similaridade por Frame (Fallback)')
                    ax.grid(True, alpha=0.3)
                    ax.set_ylim(0, 1)
                    st.pyplot(fig)
                except Exception as fallback_error:
                    logger.error(f"Erro no fallback do gráfico: {str(fallback_error)}")
                    st.write("⚠️ Não foi possível gerar o gráfico de similaridade.")

    # Detalhes técnicos
    with st.expander("🔧 Detalhes Técnicos"):
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Vídeo 1:**")
            st.write(f"- Resolução: {results.video1_resolution}")
            st.write(f"- FPS: {results.video1_fps}")
            st.write(f"- Total de frames: {results.video1_total_frames}")
            st.write(f"- Frames processados: {results.video1_processed_frames}")

        with col2:
            st.write("**Vídeo 2:**")
            st.write(f"- Resolução: {results.video2_resolution}")
            st.write(f"- FPS: {results.video2_fps}")
            st.write(f"- Total de frames: {results.video2_total_frames}")
            st.write(f"- Frames processados: {results.video2_processed_frames}")

def main():
    st.title("🎭 Comparador de Vídeos de Dança")
    st.markdown("Compare dois vídeos de dança e analise a similaridade dos movimentos usando detecção de pose avançada.")

    # Inicializa os componentes do sistema
    pose_storage, pose_extractor, comparador = init_system_components()

    # Inicializa variáveis de estado
    if 'video1_processed' not in st.session_state:
        st.session_state.video1_processed = None
    if 'video2_processed' not in st.session_state:
        st.session_state.video2_processed = None
    if 'video1_preview' not in st.session_state:
        st.session_state.video1_preview = None
    if 'video2_preview' not in st.session_state:
        st.session_state.video2_preview = None
    if 'comparison_results' not in st.session_state:
        st.session_state.comparison_results = None

    # Interface de upload de vídeos
    st.header("📹 Upload dos Vídeos")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Vídeo 1 (Referência)")
        uploaded_file1 = st.file_uploader(
            "Escolha o primeiro vídeo",
            type=['mp4', 'avi', 'mov', 'webm'],
            help="Formatos suportados: MP4, AVI, MOV, webm",
            key="video1"
        )

    with col2:
        st.subheader("Vídeo 2 (Comparação)")
        uploaded_file2 = st.file_uploader(
            "Escolha o segundo vídeo",
            type=['mp4', 'avi', 'mov', 'webm'],
            help="Formatos suportados: MP4, AVI, MOV, webm",
            key="video2"
        )

    # Processamento e preview dos vídeos
    video1_path = None
    video2_path = None

    if uploaded_file1 is not None:
        # Salva o primeiro vídeo temporariamente
        tfile1 = tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file1.name.split('.')[-1]}")
        tfile1.write(uploaded_file1.read())
        tfile1.close()
        video1_path = tfile1.name

        # Cria preview se ainda não foi criado
        if st.session_state.video1_preview is None:
            with st.spinner('Criando preview do Vídeo 1...'):
                progress_bar1 = st.progress(0)
                st.session_state.video1_preview = create_preview_video(video1_path, progress_bar1)

    if uploaded_file2 is not None:
        # Salva o segundo vídeo temporariamente
        tfile2 = tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file2.name.split('.')[-1]}")
        tfile2.write(uploaded_file2.read())
        tfile2.close()
        video2_path = tfile2.name

        # Cria preview se ainda não foi criado
        if st.session_state.video2_preview is None:
            with st.spinner('Criando preview do Vídeo 2...'):
                progress_bar2 = st.progress(0)
                st.session_state.video2_preview = create_preview_video(video2_path, progress_bar2)

    # Exibe os previews dos vídeos
    if st.session_state.video1_preview or st.session_state.video2_preview:
        st.header("👀 Preview dos Vídeos com Detecção de Pose")

        col1, col2 = st.columns(2)

        with col1:
            if st.session_state.video1_preview:
                st.subheader("Vídeo 1 (Referência)")
                st.video(st.session_state.video1_preview)

                # Informações do vídeo
                if uploaded_file1:
                    cap = cv2.VideoCapture(video1_path)
                    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    fps = int(cap.get(cv2.CAP_PROP_FPS))
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    cap.release()

                    st.write(f"📊 **Informações:**")
                    st.write(f"- Resolução: {width}x{height}")
                    st.write(f"- FPS: {fps}")
                    st.write(f"- Total de frames: {total_frames}")
                    st.write(f"- Formato: {uploaded_file1.name.split('.')[-1].upper()}")

        with col2:
            if st.session_state.video2_preview:
                st.subheader("Vídeo 2 (Comparação)")
                st.video(st.session_state.video2_preview)

                # Informações do vídeo
                if uploaded_file2:
                    cap = cv2.VideoCapture(video2_path)
                    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    fps = int(cap.get(cv2.CAP_PROP_FPS))
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    cap.release()

                    st.write(f"📊 **Informações:**")
                    st.write(f"- Resolução: {width}x{height}")
                    st.write(f"- FPS: {fps}")
                    st.write(f"- Total de frames: {total_frames}")
                    st.write(f"- Formato: {uploaded_file2.name.split('.')[-1].upper()}")

    # Botão para iniciar comparação
    if video1_path and video2_path:
        st.header("⚙️ Configurações de Comparação")

        # Informações sobre a comparação
        st.info("💡 A comparação usa algoritmos avançados de DTW (Dynamic Time Warping) para análise temporal precisa dos movimentos.")

        # Pesos dos landmarks
        with st.expander("🎯 Configuração de Pesos dos Landmarks"):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                shoulder_weight = st.slider("Ombros", 0.1, 1.0, 0.9, 0.1)
            with col2:
                hip_weight = st.slider("Quadris", 0.1, 1.0, 0.8, 0.1)
            with col3:
                knee_weight = st.slider("Joelhos", 0.1, 1.0, 0.7, 0.1)
            with col4:
                ankle_weight = st.slider("Tornozelos", 0.1, 1.0, 0.6, 0.1)

        # Botão de comparação
        if st.button("🚀 Iniciar Comparação", type="primary"):
            with st.spinner('Processando vídeos e realizando comparação...'):
                try:
                    # Processa os vídeos usando o PoseExtractor
                    st.info("Processando Vídeo 1...")
                    video1_data = process_video_with_pose_extractor(video1_path, pose_extractor, pose_storage)

                    if video1_data is None:
                        st.error("Falha ao processar o Vídeo 1")
                        return

                    st.info("Processando Vídeo 2...")
                    video2_data = process_video_with_pose_extractor(video2_path, pose_extractor, pose_storage)

                    if video2_data is None:
                        st.error("Falha ao processar o Vídeo 2")
                        return

                    # Verifica se já existe uma comparação
                    results = pose_storage.load_comparison_results(video1_path, video2_path)

                    # Corrige os resultados se necessário (converte dicionários para objetos)
                    if results is not None:
                        results = fix_comparison_results(results)
                        st.info("Comparação existente carregada do cache.")

                    if results is None:
                        st.info("Realizando comparação...")

                        # Obtém os landmarks no formato do comparador
                        video1_landmarks = pose_storage.get_pose_data(video1_path)
                        video2_landmarks = pose_storage.get_pose_data(video2_path)

                        if video1_landmarks is None or video2_landmarks is None:
                            st.error("Falha ao obter landmarks dos vídeos")
                            return

                        # Configura os pesos dos landmarks
                        landmark_weights = {
                            "shoulder": shoulder_weight,
                            "hip": hip_weight,
                            "knee": knee_weight,
                            "ankle": ankle_weight
                        }

                        # Compara os vídeos
                        results = comparador.compare_videos(
                            video1_landmarks=video1_landmarks,
                            video2_landmarks=video2_landmarks,
                            video1_fps=video1_data.fps,
                            video2_fps=video2_data.fps,
                            video1_resolution=video1_data.resolution,
                            video2_resolution=video2_data.resolution,
                            video1_landmark_weights=landmark_weights,
                            video2_landmark_weights=landmark_weights
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

                    # Armazena os resultados no estado da sessão
                    st.session_state.comparison_results = results
                    st.success("Comparação concluída com sucesso!")

                except Exception as e:
                    st.error(f"Erro durante a comparação: {str(e)}")
                    logger.error(f"Erro durante a comparação: {str(e)}")

    # Exibe os resultados da comparação
    if st.session_state.comparison_results:
        st.header("📊 Resultados da Comparação")
        display_comparison_results(st.session_state.comparison_results)

        # Geração de relatório
        with st.expander("📄 Relatório Detalhado"):
            try:
                report_generator = ReportGenerator(st.session_state.comparison_results)
                report = report_generator.generate()

                # Exibe o relatório formatado
                st.text(report._format_report())

                # Botão para download do relatório
                if st.button("💾 Baixar Relatório"):
                    report_content = report._format_report()
                    st.download_button(
                        label="📄 Download Relatório.txt",
                        data=report_content,
                        file_name=f"relatorio_comparacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )

            except Exception as e:
                st.error(f"Erro ao gerar relatório: {str(e)}")

    # Limpeza de arquivos temporários
    if video1_path:
        try:
            os.unlink(video1_path)
        except:
            pass

    if video2_path:
        try:
            os.unlink(video2_path)
        except:
            pass

if __name__ == "__main__":
    main()
