```plaintext
{raiz_do_projeto}/
├── .git/
├── .gitignore
├── venv/                     # Ambiente virtual Python (recomendado)
├── docs/
│   ├── PRD_AnaliseDanca.md
│   └── Arquitetura_AnaliseDanca.md # Este documento
├── reports/                  # Diretório para salvar os relatórios de comparação
├── src/                      # Código fonte principal
│   ├── __init__.py
│   ├── analisador_cli.py     # Ponto de entrada, AnalisadorCLI
│   ├── carregamento_dados.py # CarregadorDadosPose
│   ├── comparador_movimento.py # ComparadorMovimento
│   ├── gerador_relatorio.py  # GeradorRelatorio
│   └── utils.py              # (Opcional) Funções utilitárias
├── tests/
│   └── videos_teste/         # Para seus vídeos de teste
│       ├── video_ref_01.mp4
│       └── video_teste_01.mp4
├── requirements.txt          # Dependências Python
└── README.md                 # Instruções do projeto
```
