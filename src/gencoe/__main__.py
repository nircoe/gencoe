"""gencoe CLI entry point"""

import argparse
from . import init, scene, component

def create_parser():
    parser = argparse.ArgumentParser(
        prog='gencoe', 
        description='A Generator for gamecoe, Generates anything you need for a new project, scene or component',
        epilog='See gencoe <command> --help for command-specific options'
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    init.create_parser(subparsers)
    scene.create_parser(subparsers)
    component.create_parser(subparsers)

    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()

    if args.command == 'init':
        init.generate(args)
    elif args.command == 'scene':
        scene.generate(args)
    elif args.command == 'component':
        component.generate(args)

if __name__ == "__main__":
    main()
