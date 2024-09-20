import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import datasets
import argparse
import os
import sys
from utils.logging_config import logger
from dotenv import load_dotenv
import re
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

try:
    load_dotenv('config.env')
    embedding_model = os.getenv("sentence_model_path")
except Exception as e:
    logger.error(f" {e}")
    sys.exit(1)
    



config_file = "config.env"

st = SentenceTransformer(embedding_model)

def check_existing_name(name_data, config_file):
    """Check if the dataset name already exists in the configuration file."""
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            for line in f:
                if line.startswith(f"{name_data}_DATASET_PATH="):
                    return True
    return False

def prompt_user_for_override(name_data):
    """Prompt the user to decide whether to override existing dataset path."""
    while True:
        user_input = input(f"The name '{name_data}' already exists. Do you want to override it? (y/n): ").strip().lower()
        if user_input in ['y', 'n']:
            return user_input == 'y'
        print("Invalid input. Please enter 'y' or 'n'.")
        

def validate_path(path_data):
    """Validate if the provided dataset path exists."""
    if not os.path.isfile(path_data):
        logger.error(f"The provided path '{path_data}' is not a valid file.")
        raise FileNotFoundError(f"The provided path '{path_data}' is not a valid file.")
        

def update_config(name_data, path_data, faiss_path):
    """Update or add entries in the configuration file with new dataset path and FAISS index."""
    updated_lines = []
    dataset_path_updated = False
    faiss_index_updated = False

    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            for line in f:
                if line.startswith(f"{name_data}_DATASET_PATH="):
                    updated_lines.append(f"{name_data}_DATASET_PATH={path_data}\n")
                    dataset_path_updated = True
                elif line.startswith(f"{name_data}_FAISS_INDEX="):
                    updated_lines.append(f"{name_data}_FAISS_INDEX={faiss_path}\n")
                    faiss_index_updated = True
                else:
                    updated_lines.append(line)

    # If the dataset path was not updated, add it
    if not dataset_path_updated:
        updated_lines.append(f"{name_data}_DATASET_PATH={path_data}\n")
    
    # If the FAISS index was not updated, add it
    if not faiss_index_updated:
        updated_lines.append(f"{name_data}_FAISS_INDEX={faiss_path}\n")

    # Write the updated lines back to the config file
    with open(config_file, "w") as f:
        f.writelines(updated_lines)

def generate_embeddings(name_data, path_data):

    try:
            
        validate_path(path_data)
    
        # Check if the name_data already exists
        while True:
            if check_existing_name(name_data, config_file):
                if not prompt_user_for_override(name_data):
                    name_data = input("Please provide another name or type 'exit' to quit: ").strip()
                    if name_data.lower() == 'exit':
                        print("Exiting the program.")
                        return
                    continue  # Recheck the new name
                
        # Load the dataset and generate embeddings
            df = datasets.load_dataset("json", data_files=[path_data], split="train")
            embeddings = st.encode(df["text"], convert_to_numpy=True)
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            
            # Add the embeddings to the index
            index.add(embeddings)
            
            # Write the embeddings index to disk
            faiss_path = f"./embeddings/{name_data}.faiss" 
            
            faiss.write_index(index, faiss_path)
            
            # Append the dataset path to the config file
            update_config(name_data, path_data, faiss_path)
            logger.info(f"Embeddings of the dataset '{name_data}' have been generated successfully.")
            break

    except Exception as e:
        logger.error(f"An error occurred while generating embeddings: {e}")
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate embeddings of a dataset.")
    parser.add_argument("name_data", type=str, help="The name of the dataset.")
    parser.add_argument("path_data", type=str, help="The path of the dataset.")
    args = parser.parse_args()
    
    generate_embeddings(args.name_data, args.path_data)