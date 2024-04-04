#!/bin/bash
REPO=$PWD

DATA_DIR="${REPO}/datasets/"
THRESHOLD=${1:-0.80}
LIMIT=${2:-3}
LAN=${3:-"en"}
CORPUS=${4:-"multiconer"}

base_dir=${REPO}
train_file=${DATA_DIR}/${CORPUS}/${CORPUS}

# Ensure the train file exists
if [ ! -f "$train_file" ]; then
    echo "Train file does not exist: $train_file"
    exit 1
fi

# Execute the Python module with dynamic parameters
python -m make_gazetteer --data "$train_file" --threshold "$THRESHOLD" --limit "$LIMIT" --lang "$LAN"