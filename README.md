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
pip install -r requirements.txt
```

```bash
ollama pull phi4
ollama pull llama3.2:1b
```

```bash
python3 main.py
```