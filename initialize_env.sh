#!/bin/bash

# Define variables
VENV_DIR=".venv"
SPACY_PACKAGE="spacy"
SPACY_MODEL="en_core_web_lg"

# Check if the virtual environment directory exists
if [ -d "$VENV_DIR" ]; then
    echo "$VENV_DIR directory already exists. Skipping virtual environment creation."
else
    # Create a virtual environment if it does not exist
    python -m venv $VENV_DIR || { echo "Failed to create virtual environment"; exit 1; }
fi

# Activate the virtual environment
source $VENV_DIR/bin/activate || { echo "Failed to activate virtual environment"; exit 1; }

# Install dependencies from requirements.txt
pip install -r requirements.txt || { echo "Failed to install dependencies from requirements.txt"; exit 1; }

# Upgrade spacy to the latest version
pip install -U $SPACY_PACKAGE || { echo "Failed to upgrade $SPACY_PACKAGE"; exit 1; }

# Download the spacy model
python -m spacy download $SPACY_MODEL || { echo "Failed to download spacy model $SPACY_MODEL"; exit 1; }

# Run the Python script with error handling
python datasets/process_dataset.py || { echo "Failed to run datasets/process_dataset.py"; exit 1; }