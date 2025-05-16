# Script para iniciar o ambiente de desenvolvimento

# Define variáveis de ambiente
$env:NODE_ENV = "development"

# Inicia o servidor Angular em uma nova janela
Start-Process powershell -ArgumentList "cd app-ui; npm start"

# Aguarda 10 segundos para o servidor Angular iniciar
Start-Sleep -Seconds 10

# Inicia o Electron
cd app-ui
npm run electron:start 
