# Gazetteer Creator
The Gazetteer Creator is a tool designed to facilitate the creation of gazetteers for Named Entity Recognition (NER) tasks. It leverages the Wikidata search tool to compile comprehensive lists of named entities relevant to your NER projects.

## Getting Started
To begin using the Gazetteer Creator, follow these steps:

### Initialize the Environment
Run: `bash initialize_env.sh` then open new terminal

### Process the dataset (MultiCoNER, ViMQ, RDRS)
`python datasets/process_multiconer.py --file <path to multiconer training conll file>`

`python datasets/process_vimq.py --file <path to vimq training json file>`

`python datasets/process_rdrs.py --dir <path to dir containing 5 folds of RDRS (in form "~RDRS-main/data/interim")>`

### Run the Gazetteer Creation Script After initializing environment:
`bash make_gazetteer.sh <threshold> <limit> <lang> <dataset>`