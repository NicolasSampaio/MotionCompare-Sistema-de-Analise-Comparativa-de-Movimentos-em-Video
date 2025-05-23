# História 3.3: Visualização Interativa dos Resultados

## Status: Review

## Story

- Como usuário do sistema de análise comparativa de dança
- Quero visualizar os resultados da análise de forma interativa via CLI
- Para que eu possa explorar e entender melhor os detalhes da comparação

## Acceptance Criteria (ACs)

1. Visualização gráfica básica implementada usando matplotlib
2. Navegação por frames via CLI implementada
3. Documentação de uso completa
4. Testes de visualização implementados

## Tasks / Subtasks

- [x] Implementar visualização gráfica básica (AC: 1)
  - [x] Criar classe Visualizer
  - [x] Implementar gráficos de similaridade
  - [x] Implementar gráficos de comparação por frame
  - [x] Adicionar testes unitários

- [x] Implementar navegação por frames (AC: 2)
  - [x] Criar interface de navegação CLI
  - [x] Implementar comandos de navegação
  - [x] Adicionar visualização detalhada por frame
  - [x] Implementar testes de navegação

- [x] Criar documentação de uso (AC: 3)
  - [x] Documentar comandos de visualização
  - [x] Criar exemplos de uso
  - [x] Adicionar screenshots/exemplos
  - [x] Documentar atalhos e dicas

- [x] Implementar testes de visualização (AC: 4)
  - [x] Criar testes de integração
  - [x] Implementar testes de interface
  - [x] Adicionar testes de performance

## Dev Technical Guidance

### Estrutura de Arquivos
```
src/
└── report/
    ├── visualizer/
    │   ├── base.py        # Classe base abstrata
    │   ├── cli.py         # Interface CLI
    │   ├── plots.py       # Funções de plotagem
    │   └── README.md      # Documentação
    └── tests/
        ├── test_visualizer.py
        ├── test_cli.py
        └── test_plots.py
```

### Dependências
- Python 3.8+
- Resultados das histórias 3.1 e 3.2
- matplotlib
- numpy
- rich (para CLI interativa)
- pytest (para testes)

### Considerações de Implementação

1. **Visualização Gráfica:**
   - Usar matplotlib para gráficos básicos
   - Implementar temas consistentes
   - Otimizar para diferentes tamanhos de terminal

2. **Interface CLI:**
   - Usar rich para interface interativa
   - Implementar comandos intuitivos
   - Suportar atalhos de teclado

3. **Navegação:**
   - Implementar sistema de paginação
   - Permitir zoom em frames específicos
   - Adicionar filtros e busca

4. **Performance:**
   - Otimizar renderização de gráficos
   - Implementar cache de dados
   - Considerar lazy loading

### Exemplo de Uso

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

## Story Progress Notes

### Agent Model Used: Claude 3.7 Sonnet

### Completion Notes List
- Implementada visualização gráfica básica com matplotlib
- Interface CLI interativa implementada com rich
- Documentação completa criada
- Testes unitários e de integração implementados
- Sistema de navegação por frames implementado
- Cache de dados implementado para melhor performance

### Change Log
- 2024-03-19: Criação inicial da história
- 2024-03-20: Implementação completa da história
  - Criada estrutura base do visualizador
  - Implementada interface CLI
  - Adicionados testes
  - Criada documentação
