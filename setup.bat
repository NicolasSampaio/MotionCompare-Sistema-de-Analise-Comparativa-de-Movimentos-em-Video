@echo off
echo Criando ambiente virtual Python...
python -m venv venv

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Instalando dependências...
pip install -r requirements.txt

echo Configuração concluída!
echo Para ativar o ambiente virtual, execute: venv\Scripts\activate.bat 
