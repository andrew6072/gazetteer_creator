import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Process vimq training data.', add_help=False)
    parser.add_argument('--file', type=str, help='Path to original training file of vimq')

    return parser.parse_args()