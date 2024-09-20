import os
from dotenv import load_dotenv
from utils.logging_config import logger
from cryptography.fernet import Fernet
import asyncio
from watchdog.observers import Observer
from utils.file_watcher import TokenFileHandler
from core.token_manager import update_current_valid_token, update_cipher_suite
from watchdog.observers.polling import PollingObserver

fernet_key = None
API_KEY = None



async def load_configuration():
    global fernet_key, API_KEY
    
    try:
        load_dotenv("config.env")
        load_dotenv("tokens.env")
    except Exception as e:
        logger.error(f"Failed to load environment variables: {e}")
        raise
    
    try:
        fernet_key = os.getenv("FERNET_KEY")
        API_KEY = os.getenv("API_KEY")
        
        if fernet_key is None:
            raise ValueError("FERNET_KEY environment variable is not set.")
        
        if API_KEY is None:
            raise ValueError("API_KEY environment variable is not set.")
        
        cipher_suite = Fernet(fernet_key)
        update_cipher_suite(cipher_suite)
        logger.info("Configuration loaded successfully.")
    
    except ValueError as ve:
        logger.error(ve)
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during configuration loading: {e}")
        raise

async def initialize_tokens():
    env_file = "tokens.env"
    new_tokens = {}

    try:
        # Open the tokens.env file and read lines
        with open(env_file, 'r') as file:
            lines = file.readlines()

        for line in lines:
            line = line.strip()
            if line and '=' in line:  # Only process non-empty lines with key-value pairs
                key, value = line.split('=', 1)  # Split only on the first '='
                new_tokens[key.strip()] = value.strip()
                logger.info(f"Loaded token: {key.strip()} into current_valid_token ")

        if not new_tokens:
            logger.warning("No tokens found in tokens.env")
        
        update_current_valid_token(new_tokens)

    except FileNotFoundError:
        logger.error(f"{env_file} not found.")
    except Exception as e:
        logger.error(f"An error occurred while reading tokens: {e}")



async def start_file_watcher():
    event_handler = TokenFileHandler(initialize_tokens, load_configuration)
    observer = PollingObserver()
    observer.schedule(event_handler, path='/app', recursive=False)
    observer.start()

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
