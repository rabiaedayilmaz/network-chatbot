## Chatbot

- AI assistant, targeted multi-linguality
- When needed uses functions as tools
- Open source models are used (default qwen2.5 (14b) for answering and gemma3 (4b) for selecting agent)

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

QWen2.5 14B is selected due to long contexts up to 128K tokens, plus multilingual capabilities for over 29 languages.
```bash
ollama pull qwen2.5:14b
ollama pull gemma3
```

```bash
python3 main.py
```