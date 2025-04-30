#!/bin/bash

# if error stop script
set -e

# to test locally
#export PYTHONPATH=./

# for dockerfile
export PYTHONPATH=/app

echo "Container is starting..."

echo "Starting ollama service..."

# serve ollama and listen port
#ollama serve &

echo "Wait for ollama to start..."
sleep 10

MODELS=("gemma3:12b-it-q4_K_M" "gemma3")
for model in "${MODELS[@]}"; do
  echo "Downloading or upgrading: $model"
  retry_count=0
  max_retries=5
  until ollama pull "$model"; do
    if [ $retry_count -ge $max_retries ]; then
      echo "Error: Model $model could not be installed, tried for $max_retries times. Exiting."
      exit 1
    fi
    retry_count=$((retry_count+1))
    echo "Model $model could not be installed. Tried for $retry_count/$max_retries times. Trying again (after 5 seconds)..."
    sleep 5
  done
  echo "Model $model is ready."
done

echo "Wait for models to be ready..."
sleep 2

echo "Ollama and models are ready."

echo "Streamlit uygulaması başlatılıyor..."
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

echo "--- App is Live ---"