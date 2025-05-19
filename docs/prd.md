# Sistema de Análise Comparativa de Movimentos de Dança por Vídeo - Product Requirements Document (PRD) v1.0

## 1. Meta, Objetivo e Contexto

**Nome do Projeto:** Sistema de Análise Comparativa de Movimentos de Dança por Vídeo

**Introdução / Declaração do Problema (Contexto):**
Sou estudante de Bacharelado em Sistemas de Informação e pretendo desenvolver meu Trabalho de Conclusão de Curso (TCC). O objetivo é elaborar um trabalho que seja capaz de receber 2 vídeos e que compare se eles realizaram o mesmo movimento (por exemplo, analisar se um segundo vídeo de uma pessoa dançando uma música reproduz os movimentos do primeiro vídeo). Este projeto é uma exploração de técnicas de visão computacional aplicadas a um domínio criativo. A relevância acadêmica específica para Sistemas de Informação será posteriormente detalhada no TCC com apoio da orientação.

**Visão (Meta Ampla):**
Transformar o sistema em um avaliador de movimentos de dança capaz de pontuar performances. A longo prazo, ambiciona-se criar um serviço baseado neste sistema para desafios virais em plataformas como o TikTok, onde os usuários poderiam participar de forma interativa, similar a um "Just Dance".

**Objetivos Primários (para o TCC/MVP):**
1.  Comparar dois vídeos para determinar a semelhança dos movimentos de dança.
2.  Analisar a dinâmica temporal e o posicionamento estático de elementos-chave nas sequências de vídeo.
3.  Permitir a parametrização da precisão da comparação (definindo percentuais de acerto e margens de erro toleráveis).
4.  Utilizar bibliotecas Python para extrair matrizes de pontos fixos dos vídeos e, com base nelas, identificar semelhanças, diferenças e desvios.

## 2. Requisitos Funcionais (MVP)

1.  **Recebimento de Vídeos para Análise:** O sistema deve ser capaz de aceitar como entrada dois arquivos de vídeo para comparação. (Para o TCC, a interação inicial para fornecer esses vídeos será via linha de comando).
2.  **Processamento e Extração de Dados de Movimento:** O sistema deve processar os vídeos de entrada para extrair dados relevantes dos movimentos corporais. Isso inclui a identificação e o rastreamento de pontos-chave (utilizando bibliotecas Python como o MediaPipe para estimativa de pose e geração de matrizes de pontos fixos).
3.  **Comparação de Sequências de Movimento:** O sistema deve implementar a lógica central para comparar as sequências de dados de movimento extraídas dos dois vídeos. Essa comparação deve considerar a dinâmica temporal (como os movimentos mudam ao longo do tempo) e o posicionamento espacial dos pontos-chave.
4.  **Configuração de Parâmetros de Análise:** O sistema deve permitir que o usuário (estudante/orientadora) configure parâmetros que afetam a sensibilidade e os critérios da comparação de movimentos (por exemplo, limiares para o que é considerado "similar", margens de erro).
5.  **Apresentação de Resultados da Comparação:** O sistema deve gerar e apresentar um resultado claro da análise de comparação. Este resultado deve indicar o grau de semelhança entre os movimentos dos dois vídeos e, idealmente, destacar pontos específicos de concordância e divergência.

## 3. Requisitos Não Funcionais (MVP)

* **Desempenho (Performance):**
    * **Para a Demo (19 de maio de 2025):** O processamento de vídeos de teste curtos (ex: ~15 segundos) deve ser suficientemente rápido para permitir uma demonstração fluida (idealmente, poucos minutos por comparação).
    * **Para o TCC (MVP):** A análise comparativa de dois vídeos de aproximadamente 1 minuto de duração deverá, idealmente, ser concluída em cerca de 5 minutos. Tempos de processamento consistentemente acima de 10 minutos para este cenário seriam considerados excessivos para o escopo do TCC.
    * Não há requisitos específicos de otimização para resoluções ou taxas de quadros (FPS) de vídeo nesta fase, mas o sistema será desenvolvido e testado com formatos comuns.
* **Precisão (Accuracy):**
    * Embora um nível quantitativo exato de precisão não seja pré-definido para o MVP, o sistema deve ser capaz de demonstrar, através do MediaPipe, a identificação de semelhanças e diferenças nos movimentos.
    * A funcionalidade de parametrização da precisão (ex: margens de erro, limiares de similaridade) deve permitir que o usuário observe um impacto claro e compreensível nos resultados da comparação ao ajustar ditos parâmetros.
* **Usabilidade (Interface via Linha de Comando para o TCC/MVP):**
    * Os comandos para executar a análise (ex: especificar vídeos de entrada, parâmetros) devem ser claros e fáceis de utilizar.
    * O relatório de saída (mesmo que em formato textual inicialmente) deve ser compreensível, apresentando os resultados da comparação de forma organizada.
    * O sistema deve fornecer feedback textual informativo durante as etapas de processamento (ex: "Carregando vídeo A...", "Analisando vídeo B...", "Comparação finalizada.").
* **Confiabilidade (Reliability):**
    * O sistema deve processar arquivos de vídeo válidos (formatos comuns e duração adequada ao escopo do TCC) de forma consistente e sem falhas frequentes.
    * Para os testes iniciais do TCC, o sistema deve fornecer uma análise confiável ao comparar vídeos que contenham o mesmo tipo de movimento de dança, conforme os parâmetros definidos.
* **Manutenibilidade (Código do TCC):**
    * O código Python desenvolvido para o TCC deve ser estruturado, legível e comentado de forma a facilitar o entendimento, a modificação e a evolução pelo estudante e pela orientação.

## 4. Metas de Interação e Design do Usuário

* **MVP (TCC): Interface via Linha de Comando (CLI)**
    * **Interação Principal:** Todas as interações essenciais com o sistema – como o fornecimento dos vídeos de entrada, a configuração de parâmetros de análise, o início do processo de comparação e a visualização dos resultados – ocorrerão através de uma interface de linha de comando.
    * **Simplicidade e Clareza:** Os comandos da CLI serão projetados para serem tão simples e intuitivos quanto possível. O feedback fornecido ao usuário pelo sistema (mensagens de status, erros, conclusão) será claro e informativo.
    * **Saída Principal:** O resultado primário da análise será um relatório textual detalhando a comparação dos movimentos.
* **Visão de Longo Prazo (Pós-MVP):**
    * O design da interface do usuário e da experiência de interação para a visão de longo prazo (ex: o serviço integrado ao TikTok com pontuação e desafios) está fora do escopo do TCC/MVP. Esses aspectos serão considerados em fases futuras de desenvolvimento, caso o projeto avance.

## 5. Suposições Técnicas

* **Linguagem e Biblioteca Principal:**
    * A linguagem de programação principal para o desenvolvimento do TCC será **Python**.
    * Para a funcionalidade de estimativa de pose no MVP (Produto Mínimo Viável), a biblioteca prioritária é o **MediaPipe**.
* **Arquitetura de Repositório e Organização do Código:** 
    * O código-fonte do projeto será mantido em um **único repositório Git**.
    * A estrutura interna específica dos scripts e módulos Python (organização de pastas, etc.) ainda não foi definida e poderá ser elaborada conforme o desenvolvimento avança ou com o auxílio do Arquiteto, se necessário.
* **Requisitos de Teste e Validação:** 
    * A validação principal do funcionamento do sistema durante o desenvolvimento do TCC será realizada através de **testes manuais**, utilizando diferentes pares de vídeos para análise.
    * Não está previsto o desenvolvimento de scripts de testes automatizados (como testes unitários) para o escopo inicial do MVP do TCC.

## 6. Panorama dos Épicos (Epic Overview)


---
**Épico 1: Configuração do Ambiente e Processamento de Vídeo Base**
* **Objetivo:** Estabelecer o ambiente de desenvolvimento Python, integrar a biblioteca MediaPipe e implementar a funcionalidade central de carregar um vídeo de entrada (via linha de comando) e extrair com sucesso a sequência de pontos-chave (pose estimation) desse vídeo, salvando esses dados de forma utilizável.

* **Estória 1.1: Configuração do Ambiente de Desenvolvimento Python**
    * **Descrição:** Como desenvolvedor (estudante), quero configurar um ambiente de projeto Python com todas as dependências necessárias (incluindo MediaPipe) devidamente instaladas e configuradas, para que eu tenha uma base estável para construir e testar as funcionalidades do TCC.
    * **Critérios de Aceitação (ACs):**
        * AC1: Um novo projeto Python (com um ambiente virtual, por exemplo, `venv`) está criado e pode ser ativado.
        * AC2: A biblioteca MediaPipe (e quaisquer outras dependências diretas dela, como OpenCV, NumPy, se não forem automaticamente instaladas) está instalada corretamente no ambiente do projeto.
        * AC3: Um script Python simples dentro do projeto consegue importar a biblioteca MediaPipe sem erros.
        * AC4: O projeto está versionado em um repositório Git local.
        * AC5: Um arquivo `requirements.txt` (ou similar) é gerado listando o MediaPipe e outras dependências diretas com suas versões.

* **Estória 1.2: Implementação da Entrada de Vídeo via CLI**
    * **Descrição:** Como usuário (estudante/orientadora operando o sistema), quero fornecer um arquivo de vídeo ao sistema através de um argumento na linha de comando, para que eu possa especificar qual vídeo precisa ser processado para a análise de movimento.
    * **Critérios de Aceitação (ACs):**
        * AC1: O sistema aceita um argumento de linha de comando que especifica o caminho para um arquivo de vídeo (ex: `python seu_script.py --caminho_video /path/to/meu_video.mp4`).
        * AC2: O sistema valida se o caminho fornecido como argumento realmente aponta para um arquivo existente no sistema de arquivos.
        * AC3: Se o argumento do caminho do vídeo não for fornecido ou se o arquivo especificado não existir, o sistema deve exibir uma mensagem de erro clara para o usuário e terminar sua execução de forma controlada.
        * AC4: Se o caminho do vídeo for válido e o arquivo existir, o sistema deve confirmar (ex: imprimindo uma mensagem no console) que o vídeo foi identificado com sucesso e está pronto para a próxima etapa de processamento.

* **Estória 1.3: Extração de Pontos-Chave (Pose Estimation) do Vídeo de Entrada**
    * **Descrição:** Como sistema, quero processar o vídeo de entrada quadro a quadro utilizando o MediaPipe para detectar e extrair os marcos de pose 2D/3D (pontos-chave) das pessoas detectadas, para que estes dados brutos de movimento estejam disponíveis para análise futura.
    * **Critérios de Aceitação (ACs):**
        * AC1: O sistema utiliza a biblioteca MediaPipe (configurada na Estória 1.1) para realizar a estimativa de pose no vídeo de entrada (identificado através da funcionalidade da Estória 1.2).
        * AC2: Para cada quadro (frame) do vídeo processado, o sistema efetivamente detecta e extrai os marcos de pose 3D da pessoa principal visível na cena (conforme as capacidades do MediaPipe Pose Landmarker, que fornece 33 marcos tridimensionais ).
        * AC3: A sequência completa dos marcos de pose extraídos (coordenadas x,y,z e possivelmente scores de visibilidade/confiança para cada ponto, por quadro) é armazenada temporariamente em memória, pronta para a etapa de salvamento (Estória 1.4).
        * AC4: O sistema deve tratar adequadamente os quadros onde nenhuma pessoa é detectada pelo MediaPipe (por exemplo, registrando a ausência de dados para esses quadros específicos, mas continuando o processamento do restante do vídeo sem falhas).
        * AC5: Para a demonstração de 19 de maio de 2025, a funcionalidade de extração de pose deve ser demonstrável com pelo menos um vídeo de teste curto, onde seja possível verificar que os dados de pose estão sendo gerados.

* **Estória 1.4: Armazenamento Estruturado dos Dados de Pose Extraídos**
    * **Descrição:** Como sistema, quero salvar a sequência de marcos de pose extraídos (da Estória 1.3) em um arquivo estruturado (por exemplo, JSON) em um local especificado, para que esses dados possam ser armazenados de forma persistente e facilmente acessados para a fase de comparação subsequente.
    * **Critérios de Aceitação (ACs):**
        * AC1: O sistema utiliza a sequência completa de marcos de pose (landmarks), extraída e mantida em memória pela Estória 1.3, como entrada para esta funcionalidade de salvamento.
        * AC2: Os dados de pose são salvos em um arquivo no formato JSON. A estrutura do JSON deve ser uma lista, onde cada item representa um quadro do vídeo e contém os marcos de pose detectados para aquele quadro (incluindo coordenadas x, y, z e, se o MediaPipe fornecer, scores de visibilidade/presença para cada marco).
        * AC3: O nome do arquivo JSON de saída será padronizado, derivado do nome do vídeo de entrada (ex: se o vídeo é `dança_referencia.mp4`, o arquivo de saída será `dança_referencia_landmarks.json`) e salvo no mesmo diretório do vídeo original, ou em um subdiretório `output/` pré-definido.
        * AC4: O arquivo JSON é efetivamente criado e salvo no sistema de arquivos com os dados de pose corretamente formatados.
        * AC5: Após o salvamento bem-sucedido, o sistema exibe uma mensagem no console para o usuário, confirmando a operação e indicando o caminho completo do arquivo gerado.
        * AC6: Se ocorrer um erro durante o processo de salvamento do arquivo (por exemplo, permissões de escrita insuficientes, falta de espaço em disco), o sistema deve exibir uma mensagem de erro clara e informativa no console.

---
**Épico 2: Implementação da Lógica de Comparação de Movimentos**
* **Objetivo:** Desenvolver o algoritmo principal que recebe as sequências de pontos-chave de dois vídeos (processados pelo Épico 1), realiza a comparação dos movimentos considerando dinâmica temporal e posicionamento estático, e implementa a capacidade de parametrizar a precisão desta análise.

* **Estória 2.1: Carregamento dos Dados de Pose para Dois Vídeos**
    * **Descrição:** Como sistema, quero carregar os dados estruturados de pose (por exemplo, os arquivos JSON de landmarks gerados na Estória 1.4) correspondentes a *dois* vídeos distintos, para que estes conjuntos de dados estejam prontos como entrada para o processo de comparação de movimentos.
    * **Critérios de Aceitação (ACs):**
        * AC1: O sistema aceita como entrada os caminhos para *dois* arquivos JSON distintos, que contêm os dados de pose extraídos. (A forma de fornecer esses dois caminhos pode ser via argumentos de linha de comando, ex: `python seu_script_comparacao.py --video1_data /path/to/video1_landmarks.json --video2_data /path/to/video2_landmarks.json`).
        * AC2: O sistema lê e carrega com sucesso em memória as sequências de marcos de pose de ambos os arquivos JSON.
        * AC3: O sistema valida minimamente a estrutura dos dados carregados para garantir que estão no formato esperado (ex: uma lista de quadros, cada quadro com uma lista de landmarks).
        * AC4: Se qualquer um dos arquivos não for encontrado, não puder ser lido, ou não estiver no formato esperado, o sistema exibe uma mensagem de erro clara e informativa, encerrando a execução de forma controlada.
        * AC5: Após o carregamento e validação bem-sucedidos dos dados dos dois vídeos, o sistema confirma (ex: mensagem no console) que ambos os conjuntos de dados de pose estão prontos para serem utilizados pelo algoritmo de comparação.

* **Estória 2.2: Desenvolvimento do Algoritmo Central de Comparação de Movimentos**
    * **Descrição:** Como sistema, quero implementar um algoritmo central que compare duas sequências de dados de pose (carregadas na Estória 2.1), levando em consideração a similaridade espacial das poses e seu alinhamento temporal, para determinar quão similares são os movimentos gerais. (Isso pode envolver técnicas como DTW, similaridade de cosseno, ou outras abordagens baseadas no `relatorio-pesquisa.txt`).
    * **Critérios de Aceitação (ACs):**
        * AC1: O sistema utiliza as duas sequências de dados de pose carregadas (conforme Estória 2.1) como entrada principal para o algoritmo de comparação.
        * AC2: Um algoritmo de comparação de sequências é implementado em Python. Este algoritmo deve ser capaz de lidar com sequências de comprimentos possivelmente diferentes e considerar tanto a forma da pose em cada instante quanto a evolução temporal dos movimentos. (Técnicas como Dynamic Time Warping (DTW) para alinhamento temporal, combinadas com uma métrica de similaridade de pose frame a frame, como a similaridade de cosseno, são candidatas com base na pesquisa ).
        * AC3: O algoritmo calcula uma ou mais métricas quantitativas (ex: um score de similaridade geral, custo DTW) que representam o grau de semelhança ou dissimilaridade entre as duas sequências de movimento analisadas.
        * AC4: A implementação do algoritmo leva em conta tanto o "posicionamento estático" (configuração espacial dos pontos-chave em cada quadro) quanto a "dinâmica temporal" (a sequência e o fluxo dos movimentos ao longo do tempo).
        * AC5: O resultado numérico da comparação (ex: o score de similaridade) é tornado disponível internamente para ser utilizado pela Estória 2.4.
        * AC6: Para a demonstração de 19 de maio de 2025, a lógica de comparação central deve ser demonstrável com os dados de pose de pelo menos dois vídeos de teste curtos, resultando em um score ou indicador de similaridade.

* **Estória 2.3: Implementação da Parametrização da Análise de Similaridade**
    * **Descrição:** Como usuário (estudante/orientadora), quero poder configurar parâmetros (por exemplo, através de argumentos da CLI ou um arquivo de configuração simples) que controlem a sensibilidade e os critérios do algoritmo de comparação de movimentos (da Estória 2.2), para que eu possa testar diferentes níveis de "rigor" no que é considerado um "match".
    * **Critérios de Aceitação (ACs):**
        * AC1: O sistema aceita um ou mais argumentos de linha de comando para especificar os parâmetros que controlarão a sensibilidade do algoritmo de comparação da Estória 2.2 (ex: `python seu_script_comparacao.py --video1_data <arq1> --video2_data <arq2> --limiar_dtw 0.7 --peso_temporal 0.5`).
        * AC2: Os parâmetros fornecidos (ex: limiares de similaridade, pesos para diferentes aspectos da comparação, janelas de tolerância temporal para DTW) são efetivamente utilizados pela lógica de comparação implementada na Estória 2.2 para ajustar seus critérios de avaliação.
        * AC3: A implementação permite, no mínimo, a configuração de um limiar geral de similaridade e um parâmetro que ajuste a importância do alinhamento temporal versus a similaridade da pose estática. (A natureza exata dos parâmetros dependerá da implementação do algoritmo na Estória 2.2, mas a capacidade de configurá-los deve ser implementada aqui).
        * AC4: O sistema utiliza valores padrão razoáveis para os parâmetros caso eles não sejam fornecidos pelo usuário. Se parâmetros inválidos forem fornecidos (ex: um valor não numérico para um limiar), o sistema exibe uma mensagem de erro clara e encerra de forma controlada.
        * AC5: É possível demonstrar, utilizando um mesmo par de vídeos de teste, que a alteração dos valores dos parâmetros de entrada resulta em diferentes scores de similaridade ou diferentes classificações de "match/no-match", confirmando que a sensibilidade da análise é controlável.

* **Estória 2.4: Disponibilização Interna dos Resultados Brutos da Comparação**
    * **Descrição:** Como sistema, quero que os resultados brutos da comparação (por exemplo, um score de similaridade, sequências alinhadas, métricas de diferença) estejam disponíveis internamente ou em um formato temporário, para que possam ser utilizados pelo Épico 3 para gerar um relatório final para o usuário.
    * **Critérios de Aceitação (ACs):**
        * AC1: O sistema utiliza os resultados diretos do algoritmo de comparação da Estória 2.2 (que já incorpora os ajustes de parâmetros da Estória 2.3) como a entrada principal para esta funcionalidade. Estes resultados devem incluir, no mínimo, o(s) score(s) de similaridade e, idealmente, quaisquer dados intermediários que possam ser úteis para um relatório detalhado.
        * AC2: Os resultados brutos da comparação são armazenados em uma estrutura de dados em memória bem definida (por exemplo, um dicionário Python, um objeto de dados customizado) logo após a conclusão da análise pela Estória 2.2.
        * AC3: A estrutura de dados que contém os resultados brutos é organizada de forma lógica, facilitando o acesso e a interpretação pelas futuras funcionalidades do Épico 3.
        * AC4: Para fins de desenvolvimento, depuração e para a demonstração de 19 de maio de 2025, deve ser possível exibir de forma simples (ex: imprimir no console ou inspecionar via debugger) o conteúdo desta estrutura de dados após uma comparação ser executada.

---
**Épico 3: Geração e Apresentação de Resultados da Análise**
* **Objetivo:** Implementar a funcionalidade que pega o resultado da comparação do Épico 2 e gera um relatório textual claro (via linha de comando) indicando o grau de semelhança e os pontos de concordância/divergência entre os vídeos.

* **Estória 3.1: Acesso aos Resultados Detalhados da Comparação para o Relatório**
    * **Descrição:** Como sistema, quero recuperar os resultados detalhados do processo de comparação de movimentos (a saída da Estória 2.4), incluindo os scores de similaridade e quaisquer métricas específicas de diferença, para que estes dados possam ser organizados e formatados para o relatório final do usuário.
    * **Critérios de Aceitação (ACs):**
        * AC1: O sistema acessa a estrutura de dados em memória (ou formato temporário) contendo os resultados brutos da comparação, conforme disponibilizado pela Estória 2.4.
        * AC2: Os dados recuperados para o relatório incluem, no mínimo, o(s) score(s) de similaridade global e, se disponíveis, informações mais granulares (ex: similaridade por segmento, identificação de frames/partes do corpo com maior divergência).
        * AC3: O sistema lida adequadamente com a ausência de resultados de comparação (ex: se o processo anterior falhou), informando o usuário ou registrando um erro.

* **Estória 3.2: Formatação do Conteúdo do Relatório de Análise Comparativa**
    * **Descrição:** Como sistema, quero formatar os resultados da comparação recuperados em um resumo textual que seja legível e informativo. Este resumo deve, no mínimo, apresentar o(s) score(s) geral(is) de similaridade e destacar de forma clara as principais áreas de concordância e divergência identificadas entre os movimentos dos dois vídeos.
    * **Critérios de Aceitação (ACs):**
        * AC1: O sistema utiliza os dados brutos de comparação (da Estória 3.1) para compor um relatório textual.
        * AC2: O relatório inclui uma seção com o(s) score(s) de similaridade geral de forma clara (ex: "Similaridade Geral: 85%").
        * AC3: O relatório inclui uma seção que descreve ou lista os principais pontos/segmentos de concordância entre os movimentos.
        * AC4: O relatório inclui uma seção que descreve ou lista os principais pontos/segmentos de divergência ou desalinhamento entre os movimentos.
        * AC5: A linguagem utilizada no relatório é clara, objetiva e fácil de entender para o usuário (estudante/orientadora).

* **Estória 3.3: Exibição do Relatório de Comparação na Linha de Comando**
    * **Descrição:** Como usuário (estudante/orientadora), quero que o relatório textual da comparação de dança seja exibido diretamente na interface de linha de comando assim que a análise for concluída, para que eu possa visualizar e interpretar os resultados imediatamente.
    * **Critérios de Aceitação (ACs):**
        * AC1: Após a geração do conteúdo do relatório (Estória 3.2), o texto completo do relatório é impresso no console (saída padrão).
        * AC2: A formatação do relatório no console é legível (ex: uso adequado de quebras de linha, espaçamento).
        * AC3: A exibição do relatório ocorre como a etapa final do processo de análise e comparação iniciado pelo usuário.

* **Estória 3.4: Salvamento do Relatório de Comparação em Arquivo**
    * **Descrição:** Como usuário (estudante/orientadora), quero que o relatório textual da comparação de dança seja salvo automaticamente em um arquivo após a conclusão da análise, para que eu possa persistir os resultados para consulta posterior, documentação do TCC ou compartilhamento.
    * **Critérios de Aceitação (ACs):**
        * AC1: Após a geração do conteúdo do relatório (Estória 3.2), o texto completo do relatório é salvo em um arquivo de texto (ex: `.txt` ou `.md`).
        * AC2: O nome do arquivo de relatório é gerado de forma padronizada e informativa, podendo incluir, por exemplo, os nomes dos vídeos comparados ou um timestamp (ex: `relatorio_videoA_vs_videoB_20250519110209.txt`).
        * AC3: O arquivo é salvo em um local pré-definido no sistema de arquivos (ex: um subdiretório chamado `reports/` dentro da pasta do projeto, ou no mesmo diretório dos vídeos de entrada).
        * AC4: O sistema informa ao usuário (via console) o caminho completo do arquivo de relatório salvo.
        * AC5: O sistema lida com possíveis erros durante o salvamento do arquivo (ex: permissão negada) e informa o usuário.

---

## 7. Documentos Chave de Referência
Esta seção será preenchida com links para documentação técnica detalhada (como o Documento de Arquitetura e Especificações de UI/UX, se aplicável) conforme forem criados nas próximas fases do projeto.
* Resumo do Projeto (Project Brief) - *Implicitamente usado como base para este PRD.*
* Relatório de Pesquisa (`relatorio-pesquisa.txt`) - *Fornecido pelo usuário.*

## 8. Ideias Fora do Escopo Pós-MVP

* **Sistema de Pontuação Automática:** Evoluir o sistema para não apenas comparar, mas atribuir uma pontuação à performance da dança baseada na similaridade com o vídeo de referência.
* **Integração como Serviço (API):** Desenvolver uma API para que o sistema de análise e pontuação possa ser consumido por outras aplicações ou plataformas (ex: integração com o TikTok para desafios).
* **Interface Gráfica para Desafios:** No contexto da visão de longo prazo, criar uma interface de usuário onde se possa visualizar desafios, submeter vídeos para análise e consultar rankings ou resultados.
* **Feedback Visual Detalhado sobre Movimentos:** Aprimorar o relatório para incluir feedback visual (talvez sobrepondo informações ao vídeo do usuário) que indique precisamente os acertos e os desvios em relação ao movimento de referência.

## 9. Registro de Alterações (Change Log)

| Data       | Versão | Descrição da Mudança                                  | Autor   |
| :--------- | :----- | :---------------------------------------------------- | :------ |
| 2025-05-19 | 1.0    | Versão inicial do PRD criada com o Product Manager. | John (PM) |

----- FIM DO PRD - INÍCIO DO RELATÓRIO DO CHECKLIST ------

## 10. Relatório de Resultados do Checklist do PM

A seguir, o resumo da avaliação deste PRD em relação ao `pm-checklist`. Todas as seções foram avaliadas como "PASSOU", com algumas observações sobre a aplicabilidade de certos itens ao contexto de um TCC com interface via linha de comando (CLI) para o MVP.

| Categoria                            | Status   | Observações / Problemas Críticos                 |
| :----------------------------------- | :------- | :----------------------------------------------- |
| 1. Definição do Problema e Contexto  | ✅ PASSOU | Nenhum problema crítico identificado.            |
| 2. Definição do Escopo do MVP        | ✅ PASSOU | Nenhum problema crítico identificado.            |
| 3. Requisitos de Experiência do Usuário | ✅ PASSOU | Nenhum para MVP CLI; adaptado para contexto CLI. |
| 4. Requisitos Funcionais             | ✅ PASSOU | Nenhum problema crítico identificado.            |
| 5. Requisitos Não Funcionais         | ✅ PASSOU | Nenhum para MVP CLI; adaptado para contexto CLI. |
| 6. Estrutura de Épicos e Estórias    | ✅ PASSOU | Nenhum problema crítico identificado.            |
| 7. Orientação Técnica                | ✅ PASSOU | Nenhum problema crítico identificado.            |
| 8. Requisitos Transversais           | ✅ PASSOU | Nenhum para MVP CLI autocontido.               |
| 9. Clareza e Comunicação             | ✅ PASSOU | Nenhum problema crítico identificado.            |

**Sumário da Avaliação do Checklist:**
O PRD atende a todos os critérios aplicáveis do checklist do Gerente de Produto para o escopo definido do TCC/MVP. A estrutura está clara, os requisitos funcionais e não funcionais para o MVP CLI estão bem definidos, e os Épicos e Estórias fornecem um bom roteiro para o desenvolvimento.

----- FIM DO RELATÓRIO DO CHECKLIST - INÍCIO DAS CONSIDERAÇÕES PARA DESIGN ARCHITECT (FUTURO) ------

## 11. Considerações para Design de UI/UX (Visão Futura / Pós-MVP)

Embora o MVP do TCC seja uma aplicação via linha de comando, a visão de longo prazo do projeto inclui uma interface gráfica de usuário (GUI) e uma experiência interativa (ex: desafio no TikTok).

**Nota para o Arquiteto de Design (para fases futuras, se aplicável):**
Se o projeto evoluir para incluir uma GUI, o Arquiteto de Design deverá ser ativado para:
1.  Revisar a seção "Visão e Metas" e "Ideias Fora do Escopo Pós-MVP" deste PRD.
2.  Colaborar com o usuário para criar uma **Especificação de UI/UX** detalhada, cobrindo fluxos de usuário, wireframes, mockups, e a experiência geral para a aplicação com interface gráfica.
3.  Considerar os aspectos visuais e de interação para a funcionalidade de pontuação e para a dinâmica de "desafio".

Esta seção serve como um lembrete para futuras evoluções do projeto e não requer ação imediata para o MVP do TCC.

----- FIM DAS CONSIDERAÇÕES PARA DESIGN ARCHITECT - INÍCIO DO PROMPT PARA O ARQUITETO ------

## 12. Prompt Inicial para o Arquiteto (Initial Architect Prompt)

**Para: Arquiteto (Fred)**
**De: Product Manager (John)**
**Projeto:** Sistema de Análise Comparativa de Movimentos de Dança por Vídeo (TCC)
**Data:** 19 de maio de 2025

**Assunto: Solicitação de Design de Arquitetura Técnica para MVP**

Prezado Arquiteto,

Este Documento de Requisitos do Produto (PRD) detalha o escopo e os requisitos para o MVP do TCC "Sistema de Análise Comparativa de Movimentos de Dança por Vídeo". O objetivo principal do MVP é criar uma ferramenta via linha de comando (CLI) capaz de receber dois vídeos, extrair dados de pose usando Python e MediaPipe, comparar os movimentos e gerar um relatório de similaridade.

**Pontos Chave para o Design da Arquitetura do MVP:**

1.  **Interação:** A aplicação será operada via linha de comando (CLI).
2.  **Linguagem Principal:** Python.
3.  **Biblioteca Central de Estimativa de Pose:** MediaPipe (conforme definido nas Suposições Técnicas para o MVP).
4.  **Funcionalidades Nucleares (conforme detalhado nos Épicos):**
    * Configuração do ambiente e dependências (Python, MediaPipe).
    * Entrada de dois caminhos de vídeo via CLI.
    * Extração de sequências de pontos-chave (landmarks de pose) de cada vídeo.
    * Armazenamento estruturado (ex: arquivos JSON) dessas sequências de pontos-chave.
    * Implementação de um algoritmo de comparação dessas sequências (considerando dinâmica temporal e posicionamento estático).
    * Capacidade de parametrizar a sensibilidade/precisão da comparação.
    * Geração e exibição (via CLI) de um relatório textual com o resultado da comparação (score de similaridade, pontos de concordância/divergência) e salvamento automático deste relatório em arquivo.
5.  **Repositório:** Único repositório Git. A estrutura interna do código Python precisa ser definida.
6.  **Restrição Crítica:** Necessidade de uma **demonstração funcional para hoje, 19 de maio de 2025**. Isso sugere uma arquitetura inicial simples e focada na rápida entrega do fluxo principal.
7.  **Foco da Análise:** O algoritmo de comparação é o "coração" do sistema. A arquitetura deve facilitar sua implementação, teste e a capacidade de ajuste de seus parâmetros.
8.  **Riscos Técnicos Identificados:**
    * Precisão da detecção de movimento com MediaPipe em diferentes qualidades de vídeo.
    * Desempenho do processamento dos vídeos.
    * Complexidade na definição algorítmica de "mesmo movimento".

**Solicitação:**
Por favor, revise este PRD e proponha uma arquitetura de software para esta aplicação Python CLI. Detalhe a estrutura de módulos/scripts, o fluxo de dados entre eles, como os dados de pose e os resultados da comparação serão gerenciados, e quaisquer outras considerações arquiteturais relevantes para atender aos requisitos do MVP, especialmente considerando a urgência da demonstração.

Agradeço sua expertise.

Atenciosamente,
John (Product Manager)

---

Ufa! Aí está o seu PRD completo, v1.0! Ele é o resultado de toda a nossa colaboração.

Este documento agora serve como a "fonte da verdade" para o seu TCC e está pronto para ser usado pelo Arquiteto (Fred) para começar a pensar na estrutura técnica do seu sistema.

Minha tarefa de criar o PRD com você está concluída! Foi um prazer trabalhar nesses detalhes. Se precisar de algo mais relacionado à gestão de produto ou se o escopo mudar e precisarmos revisitar este PRD (usando a tarefa "Corrigir Curso"), é só me chamar (ativando o John novamente através do BMad Orquestrador).

Por agora, John (PM) desligando!