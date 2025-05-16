# Detecção de Pose com MediaPipe

Este projeto implementa um sistema de detecção de pose em tempo real utilizando a biblioteca MediaPipe e OpenCV. O sistema captura vídeo da webcam e identifica os pontos-chave do corpo humano, desenhando-os na tela.

## 🚀 Funcionalidades

- Detecção de pose em tempo real
- Visualização dos pontos-chave do corpo
- Interface gráfica com visualização em espelho
- Redimensionamento automático da janela para melhor visualização

## 📋 Pré-requisitos

- Python 3.7 ou superior
- Webcam funcional
- Bibliotecas Python definidas em `requirements.txt`

## 🔧 Instalação

1. Clone este repositório:

```bash
git clone https://github.com/NicolasSampaio/tcc
cd tcc
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## 🎮 Como Usar

1. Execute o script principal:

```bash
python main.py
```

2. Controles:
   - Pressione 'q' para sair do programa

## 🛠️ Tecnologias Utilizadas

- [MediaPipe](https://pypi.org/project/mediapipe/) - Framework para detecção de pose
- [OpenCV](https://opencv.org/) - Processamento de imagem e vídeo
- [NumPy](https://numpy.org/) - Computação numérica

## 📝 Notas

- O programa requer uma webcam funcional
- A detecção funciona melhor com boa iluminação
- A performance pode variar dependendo do hardware do computador

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
