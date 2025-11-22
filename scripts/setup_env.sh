#!/bin/bash

# This script sets up the Python virtual environment and installs dependencies
# for the WhatsApp ARIA project.
#
# Usage: ./setup_env.sh

echo "Setting up Python virtual environment..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    python -m venv .venv
    echo "Virtual environment created at ./.venv"
else
    echo "Virtual environment already exists at ./.venv"
fi

# Activate virtual environment
# Note: 'source' command is for bash/zsh. For fish shell, use 'source .venv/bin/activate.fish'
# For Windows (Command Prompt), use '.venv\Scripts\activate.bat'
# For Windows (PowerShell), use '.venv\Scripts\Activate.ps1'
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "Virtual environment activated."
elif [ -f ".venv/Scripts/Activate.ps1" ]; then
    # For PowerShell users, this might need to be run manually in PowerShell
    echo "For PowerShell, please run '.venv\Scripts\Activate.ps1' manually."
elif [ -f ".venv/Scripts/activate.bat" ]; then
    # For Command Prompt users, this might need to be run manually
    echo "For Command Prompt, please run '.venv\Scripts\activate.bat' manually."
else
    echo "Could not find a suitable activation script. Please activate your virtual environment manually."
fi


echo "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt

echo "Setup complete."
echo "Remember to activate your virtual environment in each new terminal session."
