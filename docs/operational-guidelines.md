## Padrões de Codificação

- **Linguagem Principal:** Python (3.9+).
- **Guia de Estilo e Linter:** PEP 8. Recomenda-se Black (formatação) e Flake8 (linting).
- **Convenções de Nomenclatura:** `snake_case` para variáveis/funções/módulos, `PascalCase` para classes, `UPPER_SNAKE_CASE` para constantes.
- **Type Hints:** Fortemente recomendado para todas as definições de função/método.
- **Docstrings:** Mandatório para módulos, classes e funções públicas (ex: Google Style).
- **Gerenciamento de Dependências:** `pip` e `requirements.txt` com versões fixadas.
- **Idiomas Python:** Uso de construções idiomáticas, `with` para recursos.

## Estratégia Geral de Testes

- **Ferramentas (MVP):** Execução direta de scripts Python, observação manual de saídas, conjunto de vídeos de teste.
- **Testes Unitários/Integração (MVP):** Não automatizados formalmente. Validação manual da lógica dos módulos e interações durante o desenvolvimento e testes E2E manuais.
- **Testes de Ponta a Ponta (E2E) (MVP):** Execução completa do CLI com vídeos de teste, análise manual da plausibilidade do relatório. A demo de 19 de maio de 2025 será um teste E2E prático.
- **Gerenciamento de Dados de Teste:** Seleção de vídeos de teste pelo estudante; arquivos JSON de landmarks gerados serão os dados de teste para comparação.

## Estratégia de Tratamento de Erros

- **Abordagem Geral:** Exceções Python, mensagens de erro claras no console, encerramento controlado.
- **Logging (MVP):** `print()` para status/erros; módulo `logging` (nível ERROR) para depuração mais crítica.
- **Padrões Específicos:** Validação de caminhos de arquivo, formato JSON, parâmetros CLI. Tratamento de falhas na detecção de pose (pelo MediaPipe na fase de pré-processamento) e no algoritmo de comparação, informando o usuário. Erros ao salvar relatório serão notificados, mas a exibição no console será tentada.

## Melhores Práticas de Segurança

- **Validação de Entrada:** Validar caminhos de arquivo, tratar exceções de JSON malformado, validar parâmetros da CLI.
- **Segurança de Dependências:** Usar PyPI oficial, manter dependências atualizadas (com versões fixadas para TCC).
- **Tratamento de Erros:** Não expor detalhes sensíveis em mensagens de erro ao usuário.
- **Ambiente de Desenvolvimento:** Uso de `venv`, não versionar informações sensíveis.
- **Dados de Vídeo:** Manusear vídeos de teste com respeito à privacidade.
