from dotenv import load_dotenv
import os
import time
import json
import logging
import argparse
import hashlib
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

# Import our local helper override
import helpers

# Monkey patch the graphrag_sdk helper function
import graphrag_sdk.helpers
graphrag_sdk.helpers.map_dict_to_cypher_properties = helpers.map_dict_to_cypher_properties

from graphrag_sdk.source import Source
from graphrag_sdk import KnowledgeGraph, Ontology
from graphrag_sdk.models.openai import OpenAiGenerativeModel
from graphrag_sdk.model_config import KnowledgeGraphModelConfig

def setup_logging(run_id):
    """Set up logging to file only"""
    logger = logging.getLogger('researcher')
    logger.setLevel(logging.DEBUG)
    
    Path('logs').mkdir(exist_ok=True)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler(f'logs/researcher_{run_id}.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    return logger

def parse_sitemap(sitemap_url):
    """Parse sitemap and return list of URLs"""
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        urls = []
        for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
            urls.append(url.text)
        
        return urls
    except Exception as e:
        raise Exception(f"Failed to parse sitemap: {str(e)}")

def generate_run_id(sitemap_url):
    """Generate a unique run ID based on sitemap URL and timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    url_hash = hashlib.md5(sitemap_url.encode()).hexdigest()[:6]
    return f"{timestamp}_{url_hash}"

def fetch_and_save_html(url, save_dir, logger):
    """Fetch URL content and save as HTML file"""
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        response.raise_for_status()
        
        # Create a filename from URL
        filename = hashlib.md5(url.encode()).hexdigest() + '.html'
        filepath = save_dir / filename
        
        # Save HTML content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        logger.info(f"Successfully saved {url} to {filename}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to fetch URL {url}: {str(e)}")
        return None

def interactive_chat_session(chat, logger):
    """Run an interactive chat session with the knowledge graph"""
    print("\nChat session ready. Type 'exit' to end or 'clear' to reset history.")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'exit':
                print("\nEnding chat session...")
                break
            
            if user_input.lower() == 'clear':
                chat = kg.chat_session()
                print("\nChat history cleared.")
                continue
            
            if not user_input:
                continue
                
            logger.info(f"User Query: {user_input}")
            response = chat.send_message(user_input)
            logger.info(f"Assistant Response: {response['response']}")
            
            print("\nAssistant:", response['response'])
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nEnding chat session...")
            break
        except Exception as e:
            logger.error(f"Error in chat session: {e}")
            print(f"\nAn error occurred. Check logs for details.")

def main():
    parser = argparse.ArgumentParser(description='Research and build knowledge graph from sitemap URLs')
    parser.add_argument('sitemap_url', help='URL to the sitemap')
    args = parser.parse_args()

    run_id = generate_run_id(args.sitemap_url)
    logger = setup_logging(run_id)
    logger.info(f"Starting new research run with ID: {run_id}")
    
    try:
        load_dotenv()
        time.sleep(10)  # Wait for FalkorDB

        # Parse sitemap
        urls = parse_sitemap(args.sitemap_url)
        logger.info(f"Found {len(urls)} URLs in sitemap")

        print(f"Building knowledge graph from {len(urls)} URLs...")
        
        # Create directories for this run
        run_dir = Path(f'runs/{run_id}')
        html_dir = run_dir / 'html'
        html_dir.mkdir(parents=True, exist_ok=True)
        
        # Download and save HTML files
        sources = []
        successful_downloads = 0
        
        for url in urls:
            filepath = fetch_and_save_html(url, html_dir, logger)
            if filepath:
                # Create source from HTML file
                sources.append(Source(str(filepath)))
                successful_downloads += 1
                print(f"Downloaded {successful_downloads}/{len(urls)} URLs", end='\r')

        print(f"\nSuccessfully downloaded {successful_downloads} URLs")
        
        if not sources:
            print("No URLs were successfully downloaded. Check the logs for details.")
            return

        # Initialize model and create knowledge graph
        model = OpenAiGenerativeModel(model_name="gpt-4o")
        
        # Create ontology from sources
        logger.info("Creating ontology...")
        ontology = Ontology.from_sources(sources=sources, model=model)
        
        # Save ontology
        ontology_path = run_dir / 'ontology.json'
        with open(ontology_path, "w", encoding="utf-8") as file:
            file.write(json.dumps(ontology.to_json(), indent=2))

        # Create knowledge graph
        kg = KnowledgeGraph(
            name=f"kg_{run_id}",
            model_config=KnowledgeGraphModelConfig.with_model(model),
            ontology=ontology,
            host="falkordb",
            port=6379
        )

        # Process sources
        logger.info(f"Processing {len(sources)} sources...")
        kg.process_sources(sources)

        print("\nKnowledge graph ready!")
        
        # Start chat session
        chat = kg.chat_session()
        interactive_chat_session(chat, logger)

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        print(f"\nAn error occurred. Check logs in logs/researcher_{run_id}.log")

# The researcher.py script is the main entry point for our research process. It fetches URLs from a sitemap, downloads the HTML content, processes the content to build an ontology, and creates a knowledge graph. It then starts an interactive chat session with the knowledge graph.
    
if __name__ == "__main__":
    main()

