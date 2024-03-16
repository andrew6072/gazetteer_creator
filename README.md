# Gazetteer Creator
The Gazetteer Creator is a tool designed to facilitate the creation of gazetteers for Named Entity Recognition (NER) tasks. It leverages the Wikidata search tool to compile comprehensive lists of named entities relevant to your NER projects.

## Getting Started
To begin using the Gazetteer Creator, follow these steps:

### Initialize the Environment
Run: `bash initialize_env.sh` then open new terminal

### Process the dataset (MultiCoNER, ViMQ, RDRS)
`process_multiconer.py --file <path to multiconer training file>`

`process_vimq.py --file <path to vimq training file>`

`process_rdrs.py --file <path to rdrs training file>`

### Run the Gazetteer Creation Script After initializing environment:
`bash make_gazetteer.sh <threshold> <limit> <lang> <dataset>`