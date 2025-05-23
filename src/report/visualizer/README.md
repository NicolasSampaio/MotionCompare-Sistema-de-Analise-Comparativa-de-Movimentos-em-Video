# Visualizador de Análise de Dança

Este módulo fornece uma interface interativa via CLI para visualização dos resultados da análise comparativa de dança.

## Requisitos

- Python 3.8+
- matplotlib
- numpy
- rich

## Instalação

```bash
pip install matplotlib numpy rich
```

## Uso

```python
from src.report.visualizer.cli import VisualizerCLI
from src.report.generator import ReportGenerator

# Gerar relatório
generator = ReportGenerator(results)
report = generator.generate()

# Iniciar visualização interativa
visualizer = VisualizerCLI(report)
visualizer.start()
```

## Comandos Disponíveis

- `s`: Mostrar gráfico de similaridade
- `f`: Navegar para um frame específico
- `n`: Próximo frame
- `p`: Frame anterior
- `d`: Mostrar detalhes do frame atual
- `q`: Sair

## Visualizações

### Gráfico de Similaridade
- Heatmap da matriz de similaridade
- Gráfico de linha mostrando a similaridade por frame

### Comparação de Frames
- Visualização lado a lado das poses
- Métricas detalhadas de comparação
- Navegação interativa entre frames

## Exemplos

### Visualização de Similaridade
```python
# Mostrar gráfico de similaridade
visualizer.plot_similarity()
```

### Navegação entre Frames
```python
# Mostrar detalhes de um frame específico
visualizer.show_frame_details(frame_idx=0)

# Navegar para o próximo frame
visualizer._next_frame()

# Navegar para o frame anterior
visualizer._previous_frame()
```

## Dicas

1. Use o comando `s` para ter uma visão geral da similaridade entre as sequências
2. Navegue entre frames usando `n` e `p` para análise detalhada
3. Use `f` para ir diretamente para um frame específico
4. Pressione `q` para sair do visualizador

## Estrutura do Código

```
src/report/visualizer/
├── base.py        # Classe base abstrata
├── cli.py         # Interface CLI
├── plots.py       # Funções de plotagem
└── README.md      # Documentação
```

## Contribuindo

1. Siga o padrão de código existente
2. Adicione testes para novas funcionalidades
3. Atualize a documentação conforme necessário
4. Use type hints e docstrings 
