#!/bin/bash

export PYTHONPATH=.
chmod +x start.sh

# build app
docker build --no-cache -t network-chatbot-agent .

# Start Ollama in background
docker run -d --name ollama -v ollama:/root/.ollama -p 11434:11434 ollama/ollama

# wait ollama to start
sleep 10

echo "Pulling models..."

# pull models into the ollama container
docker exec ollama ollama pull gemma3:12b-it-q4_K_M
docker exec ollama ollama pull gemma3

echo "Starting app..."

# start app and conenct ollama
docker run --rm -p 8501:8501 --network="host" network-chatbot-agent
