# Network Issues Chat Agent
<p align="center">
  <img src="assets/joke.png" alt="Example Joke of Agent" width="65%">
</p>


- AI assistant, targeted multi-linguality
- When needed uses functions as tools
- Open source models are used (default gemma3:12b-it-q4_K_M (12b) for answering and gemma3 (4b) for selecting agent)
- Customizable and extensible framework for building intelligent conversational agents

<p align="center">
  <img src="assets/chat-agent-v2.png" alt="Chat Agent Diagram" width="60%">
</p>

## Features
* Multilingual Support 
    * (Prompts and pipelines optimized for Turkish and English.)
* Tool Integration
* Open-Source Models:
    * gemma3:12b-it-q4_K_M (12B): Default model for answering.
    * Gemma3 (4B): Used for agent selection to optimize performance.

## Prerequisites
* Python 3.13.3 is used.
* pip, brew, ollama
* internet connection to download models

Clone repo:
```bash
git clone https://github.com/rabiaedayilmaz/network-chatbot-agent.git
cd network-chatbot
```

Set up a virtual environment. (uv is cool)
```bash
curl -Ls https://astral.sh/uv/install.sh | sh
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```
or just `uv pip install -r <(uv pip compile pyproject.toml)`.

Also to use some tools, you need to install locally to machine:
```bash
brew install nmap
```

Install python dependencies:
```bash
export PYTHONPATH=.
pip install -r requirements.txt
```

Install ollama from official website, then:
```bash
brew install ollama
```

gemma3:12b-it-q4_K_M (8.1GB) is selected due to balancing its significant 12 billion parameter count for strong performance with the reduced memory and computational requirements provided by Q4_K_M quantization.
Gemma3 is used for efficient agent and tool selection, also 4B little model.
Download them using ollama.
```bash
ollama pull gemma3:12b-it-q4_K_M
ollama pull gemma3
```

Start the chat agent:
```bash
python3 main.py
```

To run tests:
```bash
pytest test/
```

Run web interface for testing via Streamlit (both local and api support):
```bash
streamlit run app.py
```

Run web interface for testing via Streamlit (only api support also deployment):
```bash
streamlit run app_to_deploy.py
```

To build container and deploy, one container is used for project app and other used for ollama models. 
(Total ~8GB containers, machine needs 16GB RAM)
```bash
docker-compose up
```

## Usage

| Example 1 | Example 2 |
|---------|---------|
| ![Video 1](assets/1111.gif) | ![Video 2](assets/2222.gif) |

Ask questions like:
* kalabalık alanlarda nasıl daha hızlı internete erişirim
* internet hız testi
* yıldız topolojisini açıklar mısın
* github.com için teşhis yap
* phishing saldırılarını nasıl tanırım
* ip adresim ne işe yarar
* modemim sık sık kopuyor

### Agents
There are 6 agents and each of them has own personality. Gemma3 will select appropriate agent and tools. Then, gemma3:12b-it-q4_K_M will answer your problem using them.
- Fixie: Support agent, can use RAG tools.
- Bytefix: Technical network agent, can use shell command tools (ping, tracerouter, nslookup) for given host or IP address.
- RouterX: Network engineer agent, makes suggestions.
- Sentinel: Security agent, makes suggestions.
- Hypernet: Speed optimizer agent, can use internet speed test tool.
- Prof. Ping: Instructor agent, can use topology drawing tool.

### Agent Samples

| Agent | Screenshot |
|-------|------------|
| **Bytefix** | ![](assets/sample_bytefix.png) |
| **Fixie** | ![](assets/sample_fixie.png) |
| **Hypernet** | ![](assets/sample_hypernet.png) |
| **Professor Ping** | ![](assets/sample_prof_ping.png) |
| **RouterX** | ![](assets/sample_routerx.png) |
| **Sentinel**| ![](assets/sample_sentinel.png) |


## Contributing
Contributions are welcome! To contribute:

- Fork the repository.
- Create a new branch (git checkout -b feature/your-feature).
- Commit your changes (git commit -m "Add your feature").
- Push to the branch (git push origin feature/your-feature).
- Open a pull request.

For any questions/suggestions [mail](edayilmxz@outlook.com) us! 

## Acknowledgments
* Ollama for providing an easy-to-use platform for running AI models.
* Google for their open-source Gemma models.