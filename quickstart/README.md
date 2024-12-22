# GraphRAG QuickStart

This is a quickstart example of using GraphRAG-SDK with OpenAI's GPT-4 and FalkorDB.

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key

## Setup

1. Clone this repository:
```bash
git clone <repository-url>
cd quickstart
```

2. Create a `.env` file with your OpenAI API key:
```bash
echo "OPENAI_API_KEY=your_key_here" > .env
```

3. Start the services:
```bash
docker-compose up --build
```

4. In a new terminal, connect to the running container:
```bash
docker exec -it quickstart-graphrag-1 bash
```

5. Run the quickstart script:
```bash
python quickstart.py
```

The setup will:
- Start FalkorDB
- Build and start the GraphRAG application
- Drop you into a bash shell where you can run the quickstart script
- When you run the script, it will create a knowledge graph from movie data and run example queries

## Project Structure

```
quickstart/
├── docker-compose.yml   # Docker Compose configuration
├── Dockerfile          # Docker build instructions
├── requirements.txt    # Python dependencies
├── quickstart.py      # Main application code
└── README.md          # This file
```

## Configuration

- FalkorDB runs on ports 6379 (Redis protocol) and 3000 (HTTP)
- Data is persisted in a Docker volume
- You can interact directly with the Python environment in the container

## Customization

- Modify `quickstart.py` to change the URLs or queries
- Adjust the model in `quickstart.py` (e.g., change to different OpenAI models)
- Add authentication to FalkorDB by uncommenting username/password fields

## Exploring

Since you're dropped into a bash shell, you can:
- Run the quickstart script: `python quickstart.py`
- Explore the code: `ls`, `cat quickstart.py`
- Use Python interactively: `python`
- Install additional packages if needed: `pip install package_name`
