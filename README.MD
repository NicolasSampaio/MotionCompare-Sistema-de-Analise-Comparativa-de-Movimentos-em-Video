# Projeto TCC - Análise de Movimentos em Dança

## Visão Geral

Sistema de análise de movimentos em vídeo, com foco em comparação de performances de dança usando MediaPipe, OpenCV e ferramentas de ciência de dados em Python. O projeto permite extrair, analisar e comparar movimentos de dança em vídeos, gerando relatórios detalhados e visualizações.

## Configuração do Ambiente de Desenvolvimento

### Pré-requisitos

- Python 3.9 ou superior (recomendado: 3.11.x ou 3.12.x)
- pip (gerenciador de pacotes Python)
- Git (opcional, para controle de versão)

### Instalação

1. Clone o repositório:

   ```bash
   git clone [URL_DO_REPOSITÓRIO]
   cd tcc
   ```

2. Crie e ative o ambiente virtual:

   - **Windows:**
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **Linux/macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

   Ou use o script de configuração no Windows:
   ```bash
   .\setup.bat
   ```

### Verificação da Instalação

Para verificar se todas as dependências foram instaladas corretamente, execute:

```bash
pytest tests/test_imports.py
```

Para rodar todos os testes automatizados:

```bash
pytest tests/
```

## Uso da CLI

A ferramenta principal pode ser utilizada via linha de comando. Veja exemplos de comandos:

```bash
# Processar um vídeo
python -m src.analisador_cli -v video.mp4 --command process

# Comparar dois vídeos
python -m src.analisador_cli --command compare video1.mp4 video2.mp4

# Especificar arquivo de saída
python -m src.analisador_cli -v video.mp4 -o output.mp4 --command process

# Definir resolução de saída
python -m src.analisador_cli -v video.mp4 -r 1080p --command process

# Definir FPS de processamento
python -m src.analisador_cli -v video.mp4 -f 30 --command process

# Ativar modo verbose
python -m src.analisador_cli -v video.mp4 --verbose --command process

# Usar arquivo de configuração de parâmetros
python -m src.analisador_cli --command compare video1.mp4 video2.mp4 --config params.json
```

#### Opções Disponíveis

- `-v, --video`: Caminho do arquivo de vídeo a ser processado (obrigatório para process)
- `-o, --output`: Caminho do arquivo de saída (opcional)
- `-r, --resolution`: Resolução de saída do vídeo (padrão: 720p)
  - Opções: 480p, 720p, 1080p
- `-f, --fps`: FPS de processamento (opcional)
- `--verbose`: Ativa modo verbose para mais informações de debug
- `--skip-processing`: Pula o processamento do vídeo e carrega dados salvos
- `--config`: Caminho para arquivo JSON de parâmetros de comparação
- `--metric`: Métrica de distância para comparação (`euclidean`, `dtw`)
- `--tolerance`: Tolerância de similaridade (0-1)
- `--landmark-weights`: Pesos dos landmarks em JSON (ex: '{"shoulder": 0.8, "hip": 0.6}')
- `--temporal-sync`/`--no-temporal-sync`: Ativa/desativa sincronização temporal
- `--normalize`/`--no-normalize`: Ativa/desativa normalização
- `--storage-dir`: Diretório para armazenar dados de pose (padrão: data/pose)
- `--command`: `process` ou `compare` (obrigatório)
- `video1`, `video2`: Caminhos dos vídeos para comparação (obrigatório para compare)

#### Formatos Suportados

- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)

## Estrutura do Projeto

```
tcc/
├── docs/           # Documentação do projeto
├── examples/       # Exemplos de uso da API
├── src/            # Código fonte principal
│   ├── analisador_cli.py
│   ├── comparador_movimento.py
│   ├── pose_estimation.py
│   ├── pose_storage.py
│   ├── pose_models.py
│   ├── comparison_params.py
│   ├── comparison_results.py
│   ├── results_cache.py
│   ├── carregamento_dados.py
│   ├── gerador_relatorio.py
│   ├── utils.py
│   └── report/     # Módulo de relatórios e visualizações
│       ├── exporters/  # Exportadores (JSON, CSV)
│       └── visualizer/ # Visualizadores gráficos
├── tests/          # Testes automatizados
│   └── videos_teste/
├── data/           # Dados de pose e resultados
│   └── pose/
├── reports/        # Relatórios e resultados
├── requirements.txt # Dependências do projeto
└── README.md       # Este arquivo
```

Para detalhes completos, consulte [`docs/project-structure.md`](docs/project-structure.md).

## Exemplos de Uso da API

### Comparação de Vídeos

```python
from src.pose_estimation import PoseExtractor
from src.comparison_params import ComparisonParams, DistanceMetric
from src.comparador_movimento import DanceComparison

# Inicializa o extrator de pose
extractor = PoseExtractor()

# Processa os vídeos
video1_data = extractor.process_video("video1.mp4")
video2_data = extractor.process_video("video2.mp4")

# Configuração para dança contemporânea
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

# Realiza a comparação
comparison = DanceComparison(video1_data, video2_data, params)
similarity = comparison.get_similarity()
print(f"Similaridade: {similarity:.2f}")

# Carregando configuração de arquivo
params_from_file = ComparisonParams.load_from_file("config.json")
```

### Armazenamento e Cache

```python
from src.comparison_results import ComparisonResults
from src.pose_storage import PoseStorage
from src.results_cache import ResultsCache

# Criando um resultado de comparação
results = ComparisonResults(
    global_score=0.9,
    frame_scores=[0.8, 0.9, 1.0],
    temporal_alignment={"offset": 0, "scale": 1.0},
    landmark_details={"left_shoulder": {"score": 0.9}},
    metadata={"video1": "video1.mp4", "video2": "video2.mp4"}
)

# Salvando resultados em disco
pose_storage = PoseStorage("data/pose")
pose_storage.save_comparison_results("video1.mp4", "video2.mp4", results)

# Carregando resultados salvos
dados = pose_storage.load_comparison_results("video1.mp4", "video2.mp4")
print(dados.global_score)

# Usando o sistema de cache
cache = ResultsCache(cache_dir="cache")
cache.set("comparacao_v1_v2", results)
recuperado = cache.get("comparacao_v1_v2")
print(recuperado.to_json())
```

### Exportação de Relatórios

```python
from src.report.exporters import JSONExporter, CSVExporter

# Dados de análise
analysis_data = {
    "results": [
        {
            "id": 1,
            "name": "Movimento 1",
            "score": 0.95,
            "details": {"accuracy": 0.98, "smoothness": 0.92}
        },
        {
            "id": 2,
            "name": "Movimento 2",
            "score": 0.85,
            "details": {"accuracy": 0.87, "smoothness": 0.83}
        }
    ],
    "metadata": {
        "version": "1.0",
        "timestamp": "2024-03-19",
        "analysis_type": "comparison"
    }
}

# Exporta para JSON
json_exporter = JSONExporter(analysis_data)
json_exporter.export("output/analysis_results.json")

# Exporta para CSV
csv_exporter = CSVExporter(analysis_data)
csv_exporter.export("output/analysis_results.csv")
```

### Visualização de Resultados

```python
import matplotlib.pyplot as plt
from src.report.visualizer.plots import SimilarityPlotter

# Dados de comparação
comparison_data = {
    "global_score": 0.85,
    "frames": [
        {"frame_id": 1, "score": 0.9, "landmarks": {"left_shoulder": 0.95, "right_shoulder": 0.85}},
        {"frame_id": 2, "score": 0.8, "landmarks": {"left_shoulder": 0.85, "right_shoulder": 0.75}},
        {"frame_id": 3, "score": 0.85, "landmarks": {"left_shoulder": 0.90, "right_shoulder": 0.80}}
    ],
    "metadata": {
        "video1": "danca1.mp4",
        "video2": "danca2.mp4",
        "date": "2024-05-15"
    }
}

# Cria o visualizador
plotter = SimilarityPlotter(comparison_data)

# Plota o gráfico de similaridade ao longo do tempo
plotter.plot_similarity()

# Plota a comparação de um frame específico
plotter.plot_frame_comparison(frame_idx=1)

# Mostra os gráficos
plt.show()
```

## Scripts Utilitários

O projeto inclui scripts utilitários para facilitar a comparação de vídeos sem a necessidade de escrever código.

### comparar_videos.py

Este script realiza a comparação detalhada entre dois vídeos de dança, utilizando diretamente os componentes internos do sistema.

**Propósito:**
- Extrair poses de dois vídeos
- Armazenar os dados de pose em disco para uso futuro
- Comparar os movimentos entre os vídeos
- Exibir métricas detalhadas de similaridade

**Uso:**
```bash
python comparar_videos.py
```

**Parâmetros:**
O script utiliza valores padrão para os caminhos dos vídeos (definidos no código). Para personalizar, edite as variáveis no início da função `main()`:
- `video1_path`: Caminho para o primeiro vídeo
- `video2_path`: Caminho para o segundo vídeo

**Exemplo de personalização:**
```python
# Modifique estas linhas no script
video1_path = "caminho/para/seu/video1.mp4"
video2_path = "caminho/para/seu/video2.mp4"
```

### comparar_videos_simples.py

Uma versão simplificada que utiliza a interface de alto nível `AnalisadorCLI` para comparar vídeos com menos código.

**Propósito:**
- Fornecer uma interface simplificada para comparação de vídeos
- Utilizar a API de alto nível do sistema
- Gerar relatórios em formato JSON

**Uso:**
```bash
python comparar_videos_simples.py
```

**Parâmetros:**
Assim como o script anterior, utiliza valores padrão que podem ser modificados editando o código:
- `video1_path`: Caminho para o primeiro vídeo
- `video2_path`: Caminho para o segundo vídeo
- `output_path`: Caminho para salvar o relatório JSON (opcional)

**Exemplo de personalização:**
```python
# Modifique estas linhas no script
video1_path = "caminho/para/seu/video1.mp4"
video2_path = "caminho/para/seu/video2.mp4"
output_path = "caminho/para/relatorio.json"
```

**Diferenças entre os scripts:**
- `comparar_videos.py`: Mais detalhado, com acesso direto aos componentes internos do sistema
- `comparar_videos_simples.py`: Mais simples, utilizando a API de alto nível do sistema

Ambos os scripts salvam os dados de pose extraídos para reutilização futura, evitando o reprocessamento dos mesmos vídeos.

## Contribuindo

1. Siga os padrões definidos em [`docs/operational-guidelines.md`](docs/operational-guidelines.md) e [`docs/checklists/story-dod-checklist.md`](docs/checklists/story-dod-checklist.md).
2. Use PEP8, type hints, docstrings e mantenha o código testável.
3. Antes de abrir um PR, rode todos os testes e verifique se não há erros de lint (`flake8`) ou formatação (`black`).
4. Documente mudanças relevantes e siga o checklist de Definition of Done (DoD).
5. Consulte a documentação técnica e de API em [`docs/`](docs/).

## Documentação Adicional

- [Referência de API](docs/api-reference.md)
- [Modelos de Dados](docs/data-models.md)
- [Diretrizes Operacionais](docs/operational-guidelines.md)
- [Estrutura do Projeto](docs/project-structure.md)
- [Parâmetros de Comparação](docs/parametros_comparacao.md)
- [Arquitetura do Sistema](docs/Arquitetura_AnaliseDanca.md)
- [PRD - Product Requirements Document](docs/PRD_AnaliseDanca.md)
- [Checklist de DoD](docs/checklists/story-dod-checklist.md)
- [Tech Stack](docs/tech-stack.md)

## Epics e Stories

O projeto está organizado em epics e stories para facilitar o desenvolvimento:

- [Epic 1: Extração de Pose](docs/epic-1.md)
- [Epic 2: Comparação de Movimentos](docs/epic-2.md)
- [Epic 3: Visualização e Relatórios](docs/epic-3.md)
- [Epic 4: Interface de Usuário](docs/epic-4.md)
- [Epic 5: Otimização e Performance](docs/epic-5.md)
- [Epic 6: Integração e Implantação](docs/epic-6.md)

Para ver todas as stories, consulte o [índice de stories](docs/stories/stories-index.md).

---

Em caso de dúvidas, consulte a documentação ou abra uma issue.
