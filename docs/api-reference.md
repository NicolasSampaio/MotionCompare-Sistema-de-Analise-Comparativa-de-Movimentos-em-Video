# Referência da Interface de Linha de Comando (CLI)

## Visão Geral

Este documento descreve a interface de linha de comando (CLI) do sistema de análise de dança. A CLI é a principal interface de interação com o sistema, permitindo a execução de análises de vídeo e geração de relatórios.

## Comandos Principais

### 1. Análise de Vídeo

```bash
python main.py analyze --reference <caminho_video_referencia> --target <caminho_video_alvo> [opções]
```

**Parâmetros Obrigatórios:**

- `--reference`: Caminho para o vídeo de referência
- `--target`: Caminho para o vídeo alvo a ser comparado

**Opções:**

- `--output`: Caminho para salvar o relatório (padrão: `./reports/analysis_<timestamp>.txt`)
- `--verbose`: Ativa modo detalhado de logging
- `--debug`: Ativa modo de depuração
- `--config`: Caminho para arquivo de configuração personalizado

**Exemplo:**

```bash
python main.py analyze --reference videos/referencia.mp4 --target videos/alvo.mp4 --output reports/analise_001.txt
```

### 2. Visualização de Resultados

```bash
python main.py view --report <caminho_relatorio> [opções]
```

**Parâmetros Obrigatórios:**

- `--report`: Caminho para o arquivo de relatório

**Opções:**

- `--format`: Formato de saída (texto/json) (padrão: texto)
- `--detail`: Nível de detalhe (baixo/médio/alto) (padrão: médio)

**Exemplo:**

```bash
python main.py view --report reports/analise_001.txt --format json --detail alto
```

### 3. Configuração do Sistema

```bash
python main.py config [opções]
```

**Opções:**

- `--show`: Mostra configurações atuais
- `--set`: Define uma configuração específica
- `--reset`: Restaura configurações padrão
- `--export`: Exporta configurações para arquivo
- `--import`: Importa configurações de arquivo

**Exemplo:**

```bash
python main.py config --set fps=30 --set max_video_size=100MB
```

## Formatos de Arquivo

### 1. Arquivo de Configuração (JSON)

```json
{
  "video": {
    "max_size_mb": 100,
    "supported_formats": ["mp4", "avi", "mov"],
    "fps": 30
  },
  "analysis": {
    "confidence_threshold": 0.7,
    "landmark_threshold": 0.5,
    "cache_enabled": true
  },
  "output": {
    "default_format": "text",
    "default_path": "./reports"
  }
}
```

### 2. Formato do Relatório (TXT)

```
=== Relatório de Análise de Dança ===
Data: 2024-03-19 15:30:00

Vídeo de Referência: videos/referencia.mp4
Vídeo Alvo: videos/alvo.mp4

Score de Similaridade: 0.85

Análise por Frame:
Frame 1: 0.90
Frame 2: 0.85
...

Recomendações:
1. Melhorar alinhamento dos braços
2. Ajustar timing do movimento X
...
```

### 3. Formato do Relatório (JSON)

```json
{
  "metadata": {
    "timestamp": "2024-03-19T15:30:00",
    "reference_video": "videos/referencia.mp4",
    "target_video": "videos/alvo.mp4"
  },
  "analysis": {
    "overall_score": 0.85,
    "frame_analysis": [
      {
        "frame": 1,
        "score": 0.9,
        "landmark_differences": {
          "left_shoulder": 0.05,
          "right_shoulder": 0.03
        }
      }
    ]
  },
  "recommendations": [
    "Melhorar alinhamento dos braços",
    "Ajustar timing do movimento X"
  ]
}
```

## Códigos de Retorno

- `0`: Sucesso
- `1`: Erro de argumentos inválidos
- `2`: Erro de arquivo não encontrado
- `3`: Erro de formato de arquivo não suportado
- `4`: Erro de processamento de vídeo
- `5`: Erro de análise
- `6`: Erro de geração de relatório
- `7`: Erro de configuração

## Tratamento de Erros

1. **Erros de Entrada:**

   - Validação de caminhos de arquivo
   - Verificação de formatos suportados
   - Validação de parâmetros numéricos

2. **Erros de Processamento:**

   - Tratamento de falhas na detecção de pose
   - Recuperação de erros de análise
   - Logging de erros críticos

3. **Erros de Saída:**
   - Verificação de permissões de escrita
   - Validação de formato de relatório
   - Backup de relatórios existentes

## Notas de Implementação

1. **Validação de Entrada:**

   - Todos os parâmetros são validados antes do processamento
   - Mensagens de erro são claras e informativas
   - Sugestões de correção são fornecidas quando possível

2. **Performance:**

   - Processamento assíncrono de vídeos grandes
   - Cache de resultados intermediários
   - Limpeza automática de arquivos temporários

3. **Segurança:**
   - Validação de caminhos de arquivo
   - Sanitização de entrada
   - Controle de acesso a arquivos
