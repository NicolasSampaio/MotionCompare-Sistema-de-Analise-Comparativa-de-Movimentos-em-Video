# Índice de Estórias do Projeto

Este arquivo indexa todas as Estórias de Usuário definidas para o projeto "Sistema de Análise Comparativa de Movimentos de Dança por Vídeo".

## Épico 1: Configuração do Ambiente e Processamento de Vídeo Base

- **Objetivo:** Estabelecer o ambiente de desenvolvimento Python, integrar a biblioteca MediaPipe e implementar a funcionalidade central de carregar um vídeo de entrada (via linha de comando) e extrair com sucesso a sequência de pontos-chave (pose estimation) desse vídeo, salvando esses dados de forma utilizável.

| ID  | Título da Estória                                     | Status    | Dependências | Link para Arquivo |
| :-- | :---------------------------------------------------- | :-------- | :----------- | :---------------- |
| 1.1 | Configuração do Ambiente de Desenvolvimento Python    | Concluída | Nenhuma      | `./story-1.1.md`  |
| 1.2 | Implementação da Entrada de Vídeo via CLI             | Concluída | 1.1          | `./story-1.2.md`  |
| 1.3 | Extração de Pontos-Chave (Pose Estimation) do Vídeo   | Concluída | 1.1, 1.2     | `./story-1.3.md`  |
| 1.4 | Armazenamento Estruturado dos Dados de Pose Extraídos | Concluída | 1.3          | `./story-1.4.md`  |

## Épico 2: Implementação da Lógica de Comparação de Movimentos

- **Objetivo:** Desenvolver o algoritmo principal que recebe as sequências de pontos-chave de dois vídeos (processados pelo Épico 1), realiza a comparação dos movimentos considerando dinâmica temporal e posicionamento estático, e implementa a capacidade de parametrizar a precisão desta análise.

| ID  | Título da Estória                                          | Status    | Dependências | Link para Arquivo |
| :-- | :--------------------------------------------------------- | :-------- | :----------- | :---------------- |
| 2.1 | Carregamento dos Dados de Pose para Dois Vídeos            | Concluída | 1.4          | `./story-2.1.md`  |
| 2.2 | Desenvolvimento do Algoritmo Central de Comparação         | Concluída | 2.1          | `./story-2.2.md`  |
| 2.3 | Implementação da Parametrização da Análise de Similaridade | Concluída | 2.2          | `./story-2.3.md`  |
| 2.4 | Disponibilização Interna dos Resultados Brutos             | Concluída | 2.2          | `./story-2.4.md`  |

## Épico 3: Geração e Apresentação de Resultados da Análise

- **Objetivo:** Implementar a funcionalidade que pega o resultado da comparação do Épico 2 e gera um relatório textual claro (via linha de comando) indicando o grau de semelhança e os pontos de concordância/divergência entre os vídeos.

| ID  | Título da Estória                                             | Status  | Dependências | Link para Arquivo |
| :-- | :------------------------------------------------------------ | :------ | :----------- | :---------------- |
| 3.1 | Acesso aos Resultados Detalhados da Comparação para Relatório | A Fazer | 2.4          | `./story-3.1.md`  |
| 3.2 | Formatação do Conteúdo do Relatório de Análise Comparativa    | A Fazer | 3.1          | `./story-3.2.md`  |
| 3.3 | Exibição do Relatório de Comparação na Linha de Comando       | A Fazer | 3.2          | `./story-3.3.md`  |
| 3.4 | Salvamento do Relatório de Comparação em Arquivo              | A Fazer | 3.2          | `./story-3.4.md`  |

**Nota:** O status das estórias deve ser atualizado neste índice conforme elas progridem (ex: A Fazer, Em Progresso, Revisão, Concluída). Os arquivos individuais de estória (`.story.md`) conterão os detalhes completos, incluindo descrição e Critérios de Aceitação.
