# Projeto TCC

## Visão Geral

Sistema de análise de movimentos em vídeo, com foco em comparação de performances de dança usando MediaPipe, OpenCV e ferramentas de ciência de dados em Python.

## Configuração do Ambiente de Desenvolvimento

### Pré-requisitos

- Python 3.9 ou superior (recomendado: 3.11.x)
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
├── src/            # Código fonte principal
│   ├── analisador_cli.py
│   ├── comparador_movimento.py
│   ├── pose_estimation.py
│   ├── pose_storage.py
│   ├── comparison_results.py
│   ├── results_cache.py
│   └── ...
├── tests/          # Testes automatizados
│   └── videos_teste/
├── reports/        # Relatórios e resultados
├── requirements.txt # Dependências do projeto
└── README.md       # Este arquivo
```

Para detalhes completos, consulte [`docs/project-structure.md`](docs/project-structure.md).

## Exemplo de Uso da API Interna

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

## Contribuindo

1. Siga os padrões definidos em [`docs/operational-guidelines.md`](docs/operational-guidelines.md) e [`docs/checklists/story-dod-checklist.txt`](docs/checklists/story-dod-checklist.txt).
2. Use PEP8, type hints, docstrings e mantenha o código testável.
3. Antes de abrir um PR, rode todos os testes e verifique se não há erros de lint (`flake8`) ou formatação (`black`).
4. Documente mudanças relevantes e siga o checklist de Definition of Done (DoD).
5. Consulte a documentação técnica e de API em [`docs/`](docs/).

## Documentação Adicional

- [Referência de API](docs/api-reference.md)
- [Modelos de Dados](docs/data-models.md)
- [Diretrizes Operacionais](docs/operational-guidelines.md)
- [Estrutura do Projeto](docs/project-structure.md)
- [Checklist de DoD](docs/checklists/story-dod-checklist.txt)
- [Tech Stack](docs/tech-stack.md)

---

Em caso de dúvidas, consulte a documentação ou abra uma issue.
