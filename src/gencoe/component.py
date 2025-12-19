"""Component generation"""

import argparse

def create_parser(subparsers):
    parser = subparsers.add_parser(
        name='component',
        usage='%(prog)s name [-i INHERIT] [-h]',
        help='Generate anything needed for a new component'
    )

    parser.add_argument('name', type=str, help='The name of your new component')
    parser.add_argument('-i', '--inherit', type=str, choices=['Renderer'], default=None, help='The Component class that your new Component will inherit from')

def generate(args: argparse.Namespace):
    """Generate .hpp/.cpp files a new gamecoe::Component"""
    pass
