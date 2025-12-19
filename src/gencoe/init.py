"""Initialize a gamecoe gamedev project"""

import argparse

def create_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]):
    parser = subparsers.add_parser(name='init', help='Initialize a new gamecoe project')

    parser.add_argument('name', type=str, help='The name of your new game project')
    parser.add_argument('-p', '--path', type=str, default=None, help='The directory path of your new game project')

def generate(args: argparse.Namespace):
    """Generate a new empty gamecoe gamedev project"""
    pass
