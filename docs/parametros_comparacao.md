# Parâmetros de Comparação

Este documento descreve os parâmetros disponíveis para configurar a análise de similaridade de movimentos.

## Parâmetros Disponíveis

### Métrica de Distância (`metric`)

Define o algoritmo usado para calcular a distância entre os movimentos.

- **euclidean**: Distância euclidiana padrão (padrão)
- **dtw**: Dynamic Time Warping, útil para movimentos com velocidades diferentes

### Tolerância (`tolerance`)

Define o limite de similaridade aceitável (0.0 a 1.0).

- Valores mais baixos (ex: 0.1) = comparação mais rigorosa
- Valores mais altos (ex: 0.5) = comparação mais flexível

### Pesos dos Landmarks (`landmark_weights`)

Define a importância de cada parte do corpo na comparação.

Exemplo:

```json
{
  "shoulder": 0.8,
  "hip": 0.7,
  "knee": 0.6,
  "ankle": 0.5
}
```

### Sincronização Temporal (`temporal_sync`)

- **true**: Considera a sincronização temporal dos movimentos
- **false**: Ignora a sincronização temporal

### Normalização (`normalize`)

- **true**: Normaliza os landmarks para compensar diferenças de escala
- **false**: Mantém as coordenadas originais

## Uso via Linha de Comando

### Arquivo de Configuração

Crie um arquivo JSON com os parâmetros desejados:

```json
{
  "metric": "dtw",
  "tolerance": 0.15,
  "landmark_weights": {
    "shoulder": 0.8,
    "hip": 0.7,
    "knee": 0.6,
    "ankle": 0.5
  },
  "temporal_sync": true,
  "normalize": true
}
```

Use o arquivo com o comando:

```bash
python analisador_cli.py -v video.mp4 --config config.json
```

### Argumentos Individuais

Também é possível definir os parâmetros individualmente:

```bash
python analisador_cli.py -v video.mp4 \
    --metric dtw \
    --tolerance 0.15 \
    --landmark-weights '{"shoulder": 0.8, "hip": 0.7}' \
    --temporal-sync \
    --normalize
```

## Exemplos de Configurações

### Configuração Padrão

```json
{
  "metric": "euclidean",
  "tolerance": 0.1,
  "landmark_weights": {},
  "temporal_sync": true,
  "normalize": true
}
```

### Configuração para Dança Contemporânea

```json
{
  "metric": "dtw",
  "tolerance": 0.2,
  "landmark_weights": {
    "shoulder": 0.9,
    "hip": 0.8,
    "knee": 0.7,
    "ankle": 0.6
  },
  "temporal_sync": true,
  "normalize": true
}
```

### Configuração para Movimentos Rápidos

```json
{
  "metric": "euclidean",
  "tolerance": 0.3,
  "landmark_weights": {
    "shoulder": 0.7,
    "hip": 0.8,
    "knee": 0.9,
    "ankle": 1.0
  },
  "temporal_sync": false,
  "normalize": true
}
```

## Dicas de Uso

1. Comece com a configuração padrão e ajuste conforme necessário
2. Use `temporal_sync: false` para movimentos muito rápidos
3. Ajuste os pesos dos landmarks para focar nas partes do corpo mais relevantes
4. Aumente a tolerância se estiver obtendo muitos falsos negativos
5. Use DTW para movimentos com velocidades diferentes
