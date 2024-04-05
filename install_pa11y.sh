#!/bin/bash

# Verificar si nvm está instalado, si no lo está, instalarlo
if ! command -v nvm &> /dev/null; then
    echo "Instalando nvm..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
fi

# Cargar nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Instalar Node.js y npm con las versiones específicas
echo "Instalando Node.js y npm..."
nvm install 18.20.0
nvm use 18.20.0

# Instalar pa11y
echo "Instalando pa11y..."
npm install -g pa11y

# Verificar la instalación
echo "Verificando la instalación..."
pa11y --version

echo "¡pa11y se ha instalado correctamente!"
