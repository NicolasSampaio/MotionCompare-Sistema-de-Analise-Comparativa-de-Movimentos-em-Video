# Alterações Temporárias

## História 2.1: Carregamento dos Dados de Pose para Dois Vídeos

### Arquivos Criados

- `src/carregamento_dados.py`: Implementação do carregamento e validação de dados de pose
- `tests/test_carregamento_dados.py`: Testes unitários para o carregamento de dados

### Arquivos Modificados

- Nenhum arquivo foi modificado

### Status

- [x] Implementação concluída
- [x] Testes implementados
- [x] Documentação atualizada

## História 2.3: Implementação da Parametrização da Análise de Similaridade

### Arquivos Criados

- `src/comparison_params.py`: Implementação dos parâmetros de comparação
- `tests/test_comparison_params.py`: Testes unitários para os parâmetros
- `tests/test_comparison_params_integration.py`: Testes de integração
- `examples/config.json`: Exemplo de configuração
- `examples/comparacao_exemplo.py`: Exemplo de uso
- `docs/parametros_comparacao.md`: Documentação dos parâmetros

### Arquivos Modificados

- `src/analisador_cli.py`: Adicionado suporte aos parâmetros de comparação
- `src/pose_estimation.py`: Adicionado suporte aos parâmetros de comparação
- `src/comparador_movimento.py`: Atualizado para usar os parâmetros
- `requirements.txt`: Adicionadas novas dependências

### Status

- [x] Implementação concluída
- [x] Testes implementados
- [x] Documentação atualizada
- [x] Exemplos criados

## História 3.1: Geração de Relatório Textual de Análise

### Arquivos Criados

- `src/gerador_relatorio.py`: Implementação do gerador de relatório
- `src/tests/test_gerador_relatorio.py`: Testes unitários para o gerador de relatório

### Arquivos Modificados

- `requirements.txt`: Adicionada dependência rich para formatação CLI
- `docs/stories/story-3.1.md`: Atualizado status e progresso da história

### Status

- [x] Implementação concluída
- [x] Testes implementados
- [x] Documentação atualizada
- [x] Dependências atualizadas
