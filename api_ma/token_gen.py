import os
import sys
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import argparse
import re
from utils.logging_config import logger
import warnings


warnings.filterwarnings("ignore")

# Load environment variables
try:
    load_dotenv("config.env")
    load_dotenv("tokens.env")
except Exception as e:
    logger.error(f"Failed to load environment variables: {e}")
    sys.exit(1)

fernet_key = os.getenv("FERNET_KEY")
if fernet_key is None:
    logger.error("FERNET_KEY environment variable is not set.")
    sys.exit(1)

try:
    cipher_suite = Fernet(fernet_key)
except Exception as e:
    logger.error(f"Failed to create cipher suite: {e}")
    sys.exit(1)

def encrypt_string(input_string, cipher_suite):
    try:
        # Encrypt the input string
        encrypted_text = cipher_suite.encrypt(input_string.encode())
        return encrypted_text
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        sys.exit(1)

def write_token_to_env(key: str, value: str):
    env_file = "tokens.env"
    
    try:
        # Read the current contents of the config file
        with open(env_file, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        logger.error(f"{env_file} not found. Creating a new one.")
        lines = []
    except Exception as e:
        logger.error(f"Failed to read {env_file}: {e}")
        sys.exit(1)

    # Check if the key already exists, and update if necessary
    key_pattern = re.compile(rf"^{re.escape(key)}=")  # Regex to match the key
    key_exists = False
    
    for i, line in enumerate(lines):
        if key_pattern.match(line):
            lines[i] = f"{key}={value}\n"  # Update the line with the new value
            key_exists = True
            break

    # If the key does not exist, add it to the end
    if not key_exists:
        lines.append(f"{key}={value}\n")

    try:
        # Write the updated lines back to the config file
        with open(env_file, 'w') as file:
            file.writelines(lines)
    except Exception as e:
        logger.error(f"Failed to write to {env_file}: {e}")
        sys.exit(1)

def generate_token(input_string):
    try:
        token = encrypt_string(input_string, cipher_suite).decode()
        write_token_to_env(input_string, token)
        return {"token": token}
    except Exception as e:
        logger.error(f"Token generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a token.")
    parser.add_argument("text", type=str, help="The text to encrypt and generate a token for.")
    args = parser.parse_args()
    
    result = generate_token(args.text)
    logger.info(f"Token generated successfully: {result['token']}")