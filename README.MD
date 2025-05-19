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
