import argparse
import os

def parse_args():
    p = argparse.ArgumentParser(description='Make gazetteer configuration.', add_help=False)
    p.add_argument('--data', type=str, help='Path to the train data.', default=None)
    p.add_argument('--threshold', type=float, help='Threshold for similarity.', default=0.75)
    p.add_argument('--limit', type=int, help='Number of pages used to get topics for each entity.', default=3)
    p.add_argument('--lang', type=str, help='Language used for searching.', default="en")

    return p.parse_args()