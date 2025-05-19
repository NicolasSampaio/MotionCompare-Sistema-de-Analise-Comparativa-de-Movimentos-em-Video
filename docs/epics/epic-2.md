# Épico 2: Implementação da Lógica de Comparação de Movimentos

## Objetivo

Desenvolver o algoritmo principal que recebe as sequências de pontos-chave de dois vídeos (processados pelo Épico 1), realiza a comparação dos movimentos considerando dinâmica temporal e posicionamento estático, e implementa a capacidade de parametrizar a precisão desta análise.

## Contexto

Este épico é responsável por transformar os dados brutos extraídos dos vídeos em uma análise comparativa significativa, permitindo avaliar o grau de similaridade entre execuções de dança.

## Histórias

### 2.1 Carregamento dos Dados de Pose para Dois Vídeos

**Objetivo:** Implementar a funcionalidade de carregar e validar os dados de pose extraídos de dois vídeos distintos.

**Critérios de Aceitação:**

- [ ] Leitura dos arquivos de dados de pose (JSON) gerados no Épico 1
- [ ] Validação da integridade e formato dos dados
- [ ] Verificação de compatibilidade entre os conjuntos de dados
- [ ] Logging de erros e inconsistências
- [ ] Testes unitários para casos de dados inválidos

**Dependências:**

- 1.4 (Armazenamento Estruturado dos Dados de Pose Extraídos)

### 2.2 Desenvolvimento do Algoritmo Central de Comparação

**Objetivo:** Desenvolver o algoritmo que compara as sequências de pontos-chave dos dois vídeos, considerando aspectos temporais e espaciais.

**Critérios de Aceitação:**

- [ ] Implementação do cálculo de similaridade quadro a quadro
- [ ] Consideração de variações temporais (sincronização)
- [ ] Métricas de distância configuráveis (ex: Euclidiana, DTW)
- [ ] Geração de score de similaridade global e por frame
- [ ] Logging detalhado do processo de comparação
- [ ] Testes unitários e de integração

**Dependências:**

- 2.1 (Carregamento dos Dados de Pose)

### 2.3 Implementação da Parametrização da Análise de Similaridade

**Objetivo:** Permitir que o usuário configure parâmetros da análise de similaridade (ex: tolerância, métrica, peso de landmarks).

**Critérios de Aceitação:**

- [ ] CLI aceita parâmetros customizados para análise
- [ ] Parâmetros validados e documentados
- [ ] Testes para diferentes configurações
- [ ] Documentação de exemplos de uso

**Dependências:**

- 2.2 (Algoritmo Central de Comparação)

### 2.4 Disponibilização Interna dos Resultados Brutos

**Objetivo:** Disponibilizar os resultados detalhados da comparação para uso em etapas posteriores (ex: geração de relatório).

**Critérios de Aceitação:**

- [ ] Estrutura de dados para resultados brutos definida
- [ ] Resultados acessíveis via API interna ou módulo
- [ ] Testes de acesso e integridade dos dados
- [ ] Documentação da estrutura de resultados

**Dependências:**

- 2.2 (Algoritmo Central de Comparação)

## Considerações Técnicas

### Stack Tecnológica

- Python 3.8+
- NumPy
- JSON
- Estruturas de dados do projeto (ver data-models.md)

### Estrutura de Arquivos

```
src/
├── comparison/
│   ├── loader.py
│   ├── algorithm.py
│   ├── params.py
│   └── results.py
└── utils/
    └── logging.py
```

### Padrões de Implementação

1. **Validação de Dados:**

   - Checagem de integridade e formato
   - Mensagens de erro claras
   - Logging apropriado

2. **Performance:**

   - Algoritmo otimizado para grandes volumes de dados
   - Uso eficiente de memória
   - Testes de performance

3. **Testes:**
   - Testes unitários e de integração
   - Casos de borda (ex: vídeos de durações diferentes)

## Métricas de Sucesso

1. **Qualidade:**

   - Cobertura de testes > 80%
   - Zero erros de linting
   - Documentação completa

2. **Performance:**

   - Comparação eficiente para vídeos longos
   - Uso de memória controlado

3. **Usabilidade:**
   - Parâmetros de análise fáceis de configurar
   - Mensagens de erro claras
   - Documentação clara

## Riscos e Mitigações

1. **Risco:** Diferenças de duração entre vídeos

   - **Mitigação:** Sincronização automática e padding

2. **Risco:** Dados de pose inconsistentes

   - **Mitigação:** Validação robusta e logging

3. **Risco:** Performance insuficiente
   - **Mitigação:** Otimização do algoritmo e uso de NumPy

## Critérios de Conclusão do Épico

1. Todas as histórias completadas e testadas
2. Documentação atualizada
3. Testes de integração passando
4. Review de código concluído
5. Performance validada
6. Estrutura de resultados documentada
