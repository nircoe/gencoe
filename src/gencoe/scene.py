"""Scene generation"""

import argparse

def create_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]):
    parser = subparsers.add_parser(name='scene', help='Generate anything needed for a new scene')

    parser.add_argument('name', type=str, help='The name of your new scene')

def generate(args: argparse.Namespace):
    """Generate the assets/ subdirectories structure for a new gamecoe::Scene"""
    pass
