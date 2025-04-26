## Chatbot

- AI assistant specializing in European languages
- When needed uses function calls
- Open source model will be used (default phi4)

Setup and run:

```bash
git clone repo
cd repo
```

```bash
python3 -m venv .venv
source .venv/bin/activate
```

```bash
export PYTHONPATH=.
pip install -r requirements.txt
```

Install ollama from official website, then:
```bash
brew install ollama
```

```bash
ollama pull qwen2.5:14b
ollama pull llama3.2:1b
```

```bash
python3 main.py
```