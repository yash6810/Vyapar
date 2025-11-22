#!/bin/bash

# This script starts all necessary backend services for the WhatsApp ARIA project.
# It is intended for development environments.
#
# Usage: ./start_all.sh
#
# Requires `tmux` for managing multiple terminal sessions.
# If tmux is not installed, you will need to run each command in a separate terminal manually.

# --- Configuration ---
# Set the Hugging Face model to use.
# For small models, consider: google/gemma-text-small-it
# For larger models, ensure your system has sufficient resources (especially GPU).
HF_MODEL=${HF_MODEL:-"google/gemma-text-small-it"}

# --- Function to check if a command exists ---
command_exists () {
    type "$1" &> /dev/null ;
}

# --- Check for tmux ---
if command_exists tmux; then
    echo "tmux found. Starting services in new tmux windows..."

    # Create a new tmux session if one doesn't exist
    tmux has-session -t whatsapp-aria 2>/dev/null
    if [ $? != 0 ]; then
        tmux new-session -d -s whatsapp-aria
    fi

    # Start HF server
    tmux new-window -t whatsapp-aria:1 -n "HF Server" "export HF_MODEL=$HF_MODEL && python backend/hf_server.py"
    echo "Started HF Server in tmux window 'HF Server' (session: whatsapp-aria)"

    # Start ASR service
    tmux new-window -t whatsapp-aria:2 -n "ASR Service" "python backend/asr_service.py"
    echo "Started ASR Service in tmux window 'ASR Service' (session: whatsapp-aria)"

    # Start Backend service
    tmux new-window -t whatsapp-aria:3 -n "Backend" "uvicorn backend.main:app --reload --port 8000"
    echo "Started Backend service in tmux window 'Backend' (session: whatsapp-aria)"

    # Optional: Start Gemini CLI in another window if needed
    # tmux new-window -t whatsapp-aria:4 -n "Gemini CLI" "cd gemini && gemini --config gemini_agent.yaml"
    # echo "Started Gemini CLI in tmux window 'Gemini CLI' (session: whatsapp-aria)"

    echo ""
    echo "All services are starting up. You can attach to the tmux session by running: tmux attach -t whatsapp-aria"
    echo "To switch between windows in tmux, use Ctrl+b then <window_number> (e.g., Ctrl+b 1 for HF Server)."
    echo "To detach from tmux, use Ctrl+b then d."
else
    echo "tmux not found. Please install tmux or run the following commands in separate terminal windows:"
    echo ""
    echo "--- Terminal 1: HF Server ---"
    echo "export HF_MODEL=$HF_MODEL"
    echo "python backend/hf_server.py"
    echo ""
    echo "--- Terminal 2: ASR Service ---"
    echo "python backend/asr_service.py"
    echo ""
    echo "--- Terminal 3: Backend Service ---"
    echo "uvicorn backend.main:app --reload --port 8000"
    echo ""
    # Optional: Gemini CLI
    # echo "--- Terminal 4: Gemini CLI (Optional) ---"
    # echo "cd gemini"
    # echo "gemini --config gemini_agent.yaml"
    # echo ""
    echo "Ensure you have activated your Python virtual environment before running these commands."
fi

echo "Setup complete. Please wait for services to fully start."
