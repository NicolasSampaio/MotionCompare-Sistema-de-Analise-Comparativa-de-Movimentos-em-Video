# História 3.1: Geração de Relatório Textual de Análise

## Status: Draft

## Story

- Como usuário do sistema de análise comparativa de dança
- Quero receber um relatório textual detalhado da análise
- Para que eu possa entender facilmente as similaridades e diferenças entre os vídeos comparados

## Acceptance Criteria (ACs)

1. Relatório inclui score de similaridade global
2. Relatório apresenta análise por frame (ou agrupamento)
3. Pontos de concordância e divergência destacados
4. Recomendações automáticas baseadas nos resultados
5. Relatório salvo em arquivo e exibido na CLI
6. Testes de geração de relatório

## Tasks / Subtasks

- [ ] Implementar estrutura base do relatório (AC: 1, 2)
  - [ ] Criar classe ReportGenerator
  - [ ] Implementar formatação do score global
  - [ ] Implementar formatação da análise por frame
  - [ ] Adicionar testes unitários

- [ ] Implementar análise de concordância/divergência (AC: 3)
  - [ ] Desenvolver algoritmo de identificação de pontos críticos
  - [ ] Implementar formatação dos pontos destacados
  - [ ] Adicionar testes unitários

- [ ] Implementar sistema de recomendações (AC: 4)
  - [ ] Desenvolver lógica de análise para recomendações
  - [ ] Implementar formatação das recomendações
  - [ ] Adicionar testes unitários

- [ ] Implementar sistema de saída (AC: 5)
  - [ ] Desenvolver salvamento em arquivo
  - [ ] Implementar exibição na CLI
  - [ ] Adicionar testes de integração

- [ ] Implementar testes de geração (AC: 6)
  - [ ] Criar testes de integração
  - [ ] Implementar testes de performance
  - [ ] Adicionar testes de casos de borda

## Dev Technical Guidance

### Estrutura de Arquivos
```
src/
└── report/
    ├── generator.py      # Classe principal de geração
    ├── formatters.py     # Formatadores específicos
    ├── analyzers.py      # Análises e recomendações
    └── tests/
        ├── test_generator.py
        ├── test_formatters.py
        └── test_analyzers.py
```

### Dependências
- Python 3.8+
- Resultados da história 2.4 (ComparisonResults)
- rich (para formatação CLI)

### Considerações de Implementação

1. **Formatação do Relatório:**
   - Usar rich para formatação colorida na CLI
   - Estruturar relatório em seções claras
   - Implementar formatação consistente

2. **Análise de Dados:**
   - Utilizar thresholds configuráveis para pontos críticos
   - Implementar agrupamento inteligente de frames
   - Considerar performance para vídeos longos

3. **Sistema de Recomendações:**
   - Baseado em thresholds e padrões identificados
   - Focado em pontos de melhoria
   - Priorizar recomendações mais relevantes

4. **Testes:**
   - Cobertura mínima de 80%
   - Testar diferentes cenários de dados
   - Validar formatação e conteúdo

### Exemplo de Uso

```python
from src.report.generator import ReportGenerator
from src.comparison.results import ComparisonResults

# Carregar resultados da comparação
results = ComparisonResults.from_file("comparison_results.json")

# Gerar relatório
generator = ReportGenerator(results)
report = generator.generate()

# Salvar e exibir
report.save("analysis_report.txt")
report.display()
```

## Story Progress Notes

### Agent Model Used: Claude 3.7 Sonnet

### Completion Notes List
- Implementar validação de dados de entrada
- Considerar internacionalização futura
- Documentar padrões de formatação

### Change Log
- 2024-03-19: Criação inicial da história 
