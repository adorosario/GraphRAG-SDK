# GraphRAG Researcher

A tool to build and query knowledge graphs from website content using GraphRAG-SDK.

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key

## Setup

1. Clone this repository and navigate to the directory:
```bash
cd quickstart
```

2. Create a `.env` file with your OpenAI API key:
```bash
echo "OPENAI_API_KEY=your_key_here" > .env
```

3. Start the FalkorDB service:
```bash
docker-compose up -d
```

4. Open a shell in the GraphRAG container:
```bash
docker-compose exec graphrag bash
```

5. Run the researcher with the sitemap:
```bash
python researcher.py https://adorosario.github.io/small-sitemap.xml
```

## Using the Chat Interface

Once the knowledge graph is built, you'll enter an interactive chat session where you can:
- Ask questions about the content from the processed URLs
- Type 'clear' to reset the chat history
- Type 'exit' to end the session

## Logs and Artifacts

Each run creates:
- A unique run ID based on timestamp and URL
- Logs in `logs/researcher_[run_id].log`
- Artifacts in `runs/[run_id]/`
- A unique knowledge graph named `kg_[run_id]`

## Example Questions

You can ask questions like:
- "What topics are covered in these pages?"
- "Can you summarize the main points from each URL?"
- "What are the connections between different concepts mentioned?"
