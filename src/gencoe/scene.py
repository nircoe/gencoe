"""Scene generation"""

import argparse
import re
from pathlib import Path

def create_parser(subparsers):
    parser = subparsers.add_parser(
        name='scene', 
        usage='%(prog)s name [-h]',
        help='Generate anything needed for a new scene'
    )

    parser.add_argument('name', type=str, help='The name of your new scene')

def create_directories_structure(name: str):
    root = Path.cwd()
    (root / 'assets' / 'audio' / name / 'sfx').mkdir(parents=True, exist_ok=True)
    (root / 'assets' / 'audio' / name / 'music').mkdir(parents=True, exist_ok=True)
    (root / 'assets' / 'textures' / name).mkdir(parents=True, exist_ok=True)

    print(f'[gencoe] Created scene directories for "{name}":')
    print(f'  - assets/audio/{name}/sfx/')
    print(f'  - assets/audio/{name}/music/')
    print(f'  - assets/textures/{name}/\n')

def get_project_name() -> str:
    """Extract project name from CMakeLists.txt if exists"""

    cmakelists = Path.cwd() / 'CMakeLists.txt'
    if cmakelists.exists():    
        content = cmakelists.read_text()
        match = re.search(r'project\s*\(\s*(\w+)', content)
        if match:
            return match.group(1)
    
    return '<your gamecoe::Game object>'

def generate(args: argparse.Namespace):
    """Generate the assets/ subdirectories structure for a new gamecoe::Scene"""

    name = args.name

    if not (Path.cwd() / 'assets' / 'audio' / 'general').exists():
        print('[gencoe] Error: Not in a gamecoe project root directory')
        print('[gencoe] Run "gencoe scene <name>" from your game project root directory')
        return

    create_directories_structure(name)

    print(f'[gencoe] Add the following code in order to create the Scene "{name}":')
    print(f'auto &{name} = {get_project_name()}.createScene("{name}");')
