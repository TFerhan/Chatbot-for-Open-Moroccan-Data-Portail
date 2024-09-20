#!/bin/bash

install_git_lfs() {
    if command -v apt-get > /dev/null; then
        echo "Installing Git LFS using apt-get..."
        apt-get update
        apt-get install -y git-lfs
    elif command -v yum > /dev/null; then
        echo "Installing Git LFS using yum..."
        yum install -y git-lfs
    else
        echo "Error: Neither apt-get nor yum found. Cannot install Git LFS."
        exit 1
    fi

    git lfs install || { echo "Failed to initialize Git LFS."; exit 1; }
}

if ! command -v git-lfs > /dev/null; then
    install_git_lfs
else
    echo "Git LFS is already installed."
fi

echo "Downloading the Spacy french model..."
python -m spacy download fr_core_news_md || { echo "Failed to download Spacy model."; exit 1; }

# Create the models directory if it doesn't already exist

mkdir -p models || { echo "Failed to create models directory."; exit 1; }
pushd models || exit

# Clone the repositories if they don't already exist
echo "Cloning model repositories..."

declare -A repos=(
  ["opus-mt-ar-fr"]="https://huggingface.co/Helsinki-NLP/opus-mt-ar-fr"
  ["finetuned_camb_intents"]="https://huggingface.co/tferhan/finetuned_camb_intents"
  ["paraphrase-multilingual-MiniLM-L12-v2"]="https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

for repo in "${!repos[@]}"; do
  if [ ! -d "$repo" ]; then
    git clone "${repos[$repo]}" "$repo" || { echo "Failed to clone $repo"; exit 1; }
  else
    echo "$repo already exists, skipping clone."
  fi
done

# Navigate into each directory and remove files if they exist
cleanup_files() {
  local dir="$1"
  shift
  cd "$dir" || exit
  for file in "$@"; do
    if [ -f "$file" ]; then
      rm "$file"
      echo "Removed $file in $dir."
    else
      echo "$file does not exist in $dir, skipping removal."
    fi
  done
  cd .. || exit
}

cleanup_files "opus-mt-ar-fr" "tf_model.h5"
cleanup_files "paraphrase-multilingual-MiniLM-L12-v2" "tf_model.h5" "model.safetensors"

popd || exit

echo "Setup completed successfully!"