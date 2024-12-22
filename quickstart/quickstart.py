from dotenv import load_dotenv
import os
import time
import json
import logging

# Import our local helper override
import helpers

# Monkey patch the graphrag_sdk helper function
import graphrag_sdk.helpers
graphrag_sdk.helpers.map_dict_to_cypher_properties = helpers.map_dict_to_cypher_properties

from graphrag_sdk.source import URL
from graphrag_sdk import KnowledgeGraph, Ontology
from graphrag_sdk.models.openai import OpenAiGenerativeModel
from graphrag_sdk.model_config import KnowledgeGraphModelConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Wait for FalkorDB to be ready
logger.info("Waiting for FalkorDB to be ready...")
time.sleep(10)  # Simple wait for services to be up

# Define your URLs
urls = [
    "https://www.rottentomatoes.com/m/side_by_side_2012",
    "https://www.rottentomatoes.com/m/matrix",
    "https://www.rottentomatoes.com/m/matrix_revolutions",
    "https://www.rottentomatoes.com/m/matrix_reloaded",
    "https://www.rottentomatoes.com/m/speed_1994",
    "https://www.rottentomatoes.com/m/john_wick_chapter_4"
]

try:
    # Convert URLs to source objects
    sources = [URL(url) for url in urls]

    # Initialize the OpenAI model
    model = OpenAiGenerativeModel(model_name="gpt-4o")

    # Create ontology from sources
    logger.info("Creating ontology...")
    ontology = Ontology.from_sources(
        sources=sources,
        model=model,
    )

    # Save the ontology to disk
    logger.info("Saving ontology...")
    with open("ontology.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(ontology.to_json(), indent=2))

    # Create Knowledge Graph
    logger.info("Creating knowledge graph...")
    kg = KnowledgeGraph(
        name="movie_knowledge",
        model_config=KnowledgeGraphModelConfig.with_model(model),
        ontology=ontology,
        host="falkordb",  # Using Docker service name
        port=6379,
        # username="your_username",  # Optional
        # password="your_password"   # Optional
    )

    # Process the sources
    logger.info("Processing sources...")
    kg.process_sources(sources)

    # Start a conversation
    logger.info("Starting chat session...")
    chat = kg.chat_session()

    # Ask questions
    logger.info("\nAsking: Who is the director of the movie The Matrix?")
    response = chat.send_message("Who is the director of the movie The Matrix?")
    print("Response:", response['response'])

    logger.info("\nAsking: How is this director connected to Keanu Reeves?")
    response = chat.send_message("How is this director connected to Keanu Reeves?")
    print("Response:", response['response'])

except Exception as e:
    logger.error(f"An error occurred: {str(e)}")
    raise