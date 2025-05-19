# Projeto TCC

## Configuração do Ambiente de Desenvolvimento

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git (opcional, para controle de versão)

### Instalação

1. Clone o repositório (se estiver usando Git):

   ```bash
   git clone [URL_DO_REPOSITÓRIO]
   cd tcc
   ```

2. Execute o script de setup:

   - No Windows:
     ```bash
     setup.bat
     ```
   - No Linux/macOS:
     ```bash
     python -m venv venv
     source venv/bin/activate
     pip install -r requirements.txt
     ```

3. Ative o ambiente virtual:
   - No Windows:
     ```bash
     venv\Scripts\activate
     ```
   - No Linux/macOS:
     ```bash
     source venv/bin/activate
     ```

### Uso da CLI

A ferramenta de análise de vídeo pode ser utilizada através da linha de comando. Aqui estão os principais comandos e opções disponíveis:

#### Comandos Básicos

```bash
# Processar um vídeo com configurações padrão
python src/analisador_cli.py -v video.mp4

# Especificar arquivo de saída
python src/analisador_cli.py -v video.mp4 -o output.mp4

# Definir resolução de saída
python src/analisador_cli.py -v video.mp4 -r 1080p

# Definir FPS de processamento
python src/analisador_cli.py -v video.mp4 -f 30

# Ativar modo verbose para mais informações
python src/analisador_cli.py -v video.mp4 --verbose
```

#### Opções Disponíveis

- `-v, --video`: Caminho do arquivo de vídeo a ser processado (obrigatório)
- `-o, --output`: Caminho do arquivo de saída (opcional)
- `-r, --resolution`: Resolução de saída do vídeo (padrão: 720p)
  - Opções: 480p, 720p, 1080p
- `-f, --fps`: FPS de processamento (opcional)
- `--verbose`: Ativa modo verbose para mais informações de debug

#### Formatos Suportados

- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)

### Verificação da Instalação

Para verificar se todas as dependências foram instaladas corretamente, execute:

```bash
pytest tests/test_imports.py
```

### Solução de Problemas

#### Problemas comuns e soluções:

1. **Erro ao instalar MediaPipe**:

   - Certifique-se de ter o Python 3.8 ou superior
   - Atualize o pip: `python -m pip install --upgrade pip`

2. **Erro ao instalar OpenCV**:

   - No Windows: Instale o Visual C++ Build Tools
   - No Linux: Instale as dependências de desenvolvimento: `sudo apt-get install python3-dev`

3. **Erro de permissão**:
   - No Linux/macOS: Use `sudo` para comandos que requerem privilégios de administrador
   - No Windows: Execute o PowerShell como administrador

### Estrutura do Projeto

```
tcc/
├── docs/           # Documentação do projeto
├── src/            # Código fonte
├── tests/          # Testes automatizados
├── reports/        # Relatórios e resultados
├── requirements.txt # Dependências do projeto
└── README.md       # Este arquivo
```
