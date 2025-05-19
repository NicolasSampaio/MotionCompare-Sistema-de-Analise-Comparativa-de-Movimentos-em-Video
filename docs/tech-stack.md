## Seleções Definitivas da Pilha Tecnológica

| Categoria          | Tecnologia          | Versão / Detalhes                      | Descrição / Propósito                                             | Justificativa (Opcional)                             |
| :----------------- | :------------------ | :------------------------------------- | :---------------------------------------------------------------- | :--------------------------------------------------- |
| **Linguagens**     | Python              | 3.9+ (Recomendado: 3.11.x)             | Linguagem principal para desenvolvimento.                         | Bibliotecas de CV/dados; familiaridade.              |
| **Bibliotecas CV** | MediaPipe (Google)  | Última estável via PyPI (ex: `0.10.x`) | Usado no pré-processamento para gerar arquivos JSON de landmarks. | Facilidade, licença Apache 2.0, desempenho para MVP. |
|                    | OpenCV (cv2)        | Última estável (dependência comum)     | Manipulação de vídeo (na etapa de pré-processamento).             | Interoperabilidade.                                  |
| **Dados**          | NumPy               | Última estável                         | Manipulação de arrays numéricos (landmarks).                      | Fundamental para dados em Python.                    |
| **CLI**            | `argparse` (Python) | Módulo padrão Python                   | Análise de argumentos da CLI.                                     | Integrado, simples para MVP.                         |
| **Versionamento**  | Git                 | Última estável                         | Controle de versão.                                               | Padrão da indústria.                                 |
| **Empacotamento**  | `requirements.txt`  | N/A                                    | Especificação de dependências Python.                             | Método padrão Python.                                |

**Nota:** Versões exatas devem ser fixadas no `requirements.txt` durante a configuração do ambiente (Estória 1.1 do PRD).
