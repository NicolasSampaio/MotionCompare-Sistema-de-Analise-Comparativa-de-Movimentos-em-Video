# Modelos de Dados

## Visão Geral

Este documento define as estruturas de dados principais utilizadas no sistema de análise de dança. Os modelos são organizados por contexto e incluem suas regras de validação.

## Modelos Principais

### 1. Landmark (Ponto de Referência)

```python
class Landmark:
    x: float          # Coordenada X normalizada (0-1)
    y: float          # Coordenada Y normalizada (0-1)
    z: float          # Coordenada Z normalizada (0-1)
    visibility: float # Confiança da detecção (0-1)
```

**Regras de Validação:**

- Todas as coordenadas devem estar no intervalo [0, 1]
- Visibility deve estar no intervalo [0, 1]
- Valores nulos não são permitidos

### 2. PoseFrame (Frame de Pose)

```python
class PoseFrame:
    frame_number: int                    # Número sequencial do frame
    timestamp: float                     # Tempo do frame em segundos
    landmarks: Dict[str, Landmark]       # Dicionário de landmarks por nome
    confidence_score: float              # Score geral de confiança da detecção
```

**Regras de Validação:**

- frame_number deve ser não-negativo
- timestamp deve ser não-negativo
- landmarks não pode estar vazio
- confidence_score deve estar no intervalo [0, 1]

### 3. VideoAnalysis (Análise de Vídeo)

```python
class VideoAnalysis:
    video_path: str                      # Caminho do arquivo de vídeo
    fps: float                          # Frames por segundo do vídeo
    duration: float                     # Duração total em segundos
    frames: List[PoseFrame]             # Lista de frames analisados
    metadata: Dict[str, Any]            # Metadados adicionais do vídeo
```

**Regras de Validação:**

- video_path deve ser um caminho válido
- fps deve ser positivo
- duration deve ser positivo
- frames não pode estar vazio
- metadata pode ser vazio

### 4. ComparisonResult (Resultado da Comparação)

```python
class ComparisonResult:
    reference_video: VideoAnalysis       # Vídeo de referência
    target_video: VideoAnalysis         # Vídeo alvo
    similarity_score: float             # Score de similaridade geral
    frame_comparisons: List[Dict]       # Comparações por frame
    detailed_analysis: Dict[str, Any]   # Análise detalhada por aspecto
```

**Regras de Validação:**

- similarity_score deve estar no intervalo [0, 1]
- frame_comparisons deve ter o mesmo tamanho do menor vídeo
- detailed_analysis deve conter pelo menos um aspecto analisado

## Estruturas de Dados Auxiliares

### 1. FrameComparison (Comparação de Frame)

```python
class FrameComparison:
    frame_number: int                    # Número do frame
    similarity_score: float             # Score de similaridade do frame
    landmark_differences: Dict[str, float] # Diferenças por landmark
    confidence_score: float             # Confiança da comparação
```

### 2. AnalysisReport (Relatório de Análise)

```python
class AnalysisReport:
    comparison_result: ComparisonResult  # Resultado da comparação
    summary: str                        # Resumo textual da análise
    recommendations: List[str]          # Recomendações baseadas na análise
    timestamp: datetime                 # Data/hora da análise
```

## Validações Globais

1. **Consistência de Dados:**

   - Todos os frames devem ter o mesmo conjunto de landmarks
   - Timestamps devem ser sequenciais
   - FPS deve ser consistente em todo o vídeo

2. **Integridade de Arquivos:**

   - Verificar existência dos arquivos de vídeo
   - Validar formatos de arquivo suportados
   - Verificar permissões de acesso

3. **Performance:**
   - Limitar tamanho máximo de vídeos
   - Definir resolução máxima suportada
   - Estabelecer limites de memória para processamento

## Notas de Implementação

1. **Serialização:**

   - Todos os modelos devem ser serializáveis para JSON
   - Manter compatibilidade com pickle para cache
   - Implementar métodos de validação

2. **Cache:**

   - Definir estratégia de cache para landmarks
   - Implementar limpeza automática de cache
   - Manter metadados de cache

3. **Logging:**
   - Registrar validações falhas
   - Manter histórico de análises
   - Documentar exceções e erros
