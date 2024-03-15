#!/bin/bash
export CUDA_VISIBLE_DEVICES=0

REPO=$PWD

DATA_DIR=${1:-"$REPO/datasets/"}
THRESHOLD=${2:-0.75}
LIMIT=${3:-3}
LAN=${4:-"en"}
CORPUS=${5:-"multiconer"}

base_dir=${REPO}
train_file=${DATA_DIR}/${CORPUS}/${CORPUS}

# Ensure the train file exists
if [ ! -f "$train_file" ]; then
    echo "Train file does not exist: $train_file"
    exit 1
fi

# Execute the Python module with dynamic parameters
python -m make_gazetteer --data "$train_file" --threshold "$THRESHOLD" --limit "$LIMIT" --lang "$LAN"