"""Component generation"""

import argparse
from pathlib import Path
from textwrap import dedent, indent
import re
import os

INHERIT_OPTIONS = {
    'Renderer': 'gamecoe/entity/renderer/renderer.hpp'
}

def create_parser(subparsers):
    parser = subparsers.add_parser(
        name='component',
        usage='%(prog)s name [-i INHERIT] [-n NAMESPACE] [-f FILENAME] [-h]',
        help='Generate anything needed for a new component'
    )

    parser.add_argument('name', type=str, help='Component class name (recommended: PascalCase)')
    parser.add_argument('-i', '--inherit', type=str, default=None, help='Base Component class to inherit from')
    parser.add_argument('-n', '--namespace', type=str, default=None, help='Namespace for the Component class (default: none)')
    parser.add_argument('-f', '--filename', type=str, default=None, help='Filename for .hpp/.cpp files (default: class name in snake_case)')

def pascal_to_snake_case(name: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

def get_inherit_include_path(inherit: str) -> str:
    if inherit in INHERIT_OPTIONS:
        return f'#include <{INHERIT_OPTIONS[inherit]}>'
    
    # custom inherit (user made Component)
    # TODO: search for the relevant {inherit}.hpp file path and insert it automatically
    return dedent(f'''
        // Uncomment the next line and update it with your {inherit} .hpp file path
        // #include "{inherit}.hpp"
    ''').strip()

def generate_hpp(name: str, hpp: Path, inherit: str = None, namespace: str = None, gamecoe: bool = False):
    inherit = inherit if inherit else f'Component<{name}>'

    renderer_method = dedent('''
        // Called once per frame while the GameObject is active and owns a Renderer
        virtual void render() const override;
    ''').strip() if inherit == 'Renderer' else ''

    file_text = dedent('''
        #pragma once

        #include <gamecoe/entity/component.hpp>
    ''').strip() + '\n'

    if inherit:
        file_text += f'{get_inherit_include_path(inherit)}\n'

    if namespace:
        file_text += '\n' + dedent(f'''
            namespace {namespace}
            {{
        ''').strip() + '\n'

    class_code = dedent(f'''
        class {name} : public {inherit}
        {{
            // Add {name} Component private members here (variables and methods)
        
        public:
            static constexpr const char* TYPE_NAME = "{name}";

            {name}(GameObject &owner); // Component "default" Constructor
            // Add any additional {name} Constructors here. Ensure you pass "GameObject &owner" to the {inherit} Constructor

            // Remove the "= delete" if you would like to implement copy/move semantics for {name}
            {name}(const {name}&) = delete;
            {name}& operator=(const {name}&) = delete;
            {name}({name}&&) = delete;
            {name}& operator=({name}&&) = delete;

            virtual ~{name}() override;

            // Component life cycle methods:

            // Called once when initializing the GameObject, or when adding the {name} Component to an initialized GameObject
            virtual void initialize() override;

            // Called at the beginning of each Scene containing the owner GameObject, or when adding the {name} Component mid-Scene
            virtual void begin() override;

            // Called when the owner GameObject is activated, or when adding the {name} Component to an active GameObject
            virtual void activate() override;

            // Called when the owner GameObject is deactivated
            virtual void deactivate() override;

            // Called once per frame while the owner GameObject is active
            virtual void update() override;
    
            {renderer_method}

            // Add {name} Component public members here (variables and methods)
        }};
    ''').strip()

    if namespace:
        class_code = indent(class_code, '    ')

    file_text += f'\n{class_code}\n'

    if namespace:
        file_text += f'}} // namespace {namespace}\n'

    hpp.write_text(file_text)

    print(f'[gencoe] Created Component files for "{name}":')
    print(f'  - {hpp.relative_to(Path.cwd())}')

def generate_cpp(name: str, hpp: Path, cpp: Path, inherit: str = None, namespace: str = None, gamecoe: bool = False):
    inherit = inherit if inherit else f'Component<{name}>'
    root = Path.cwd()
    hpp = hpp.relative_to(root / 'include') if gamecoe else hpp.relative_to(root / 'assets' / 'components' / 'include')
    hpp = f'<{hpp}>' if gamecoe else f'"{hpp}"'

    renderer_method = dedent(f'''
        // Called once per frame while the GameObject is active and owns a Renderer
        void {name}::render() const
        {{
            // Implement here
        }}
    ''').strip() if inherit == 'Renderer' else ''

    file_text = f'#include {hpp}\n'

    if namespace:
        file_text += '\n' + dedent(f'''
            namespace {namespace}
            {{
        ''').strip() + '\n'

    impl_code = dedent(f'''
        // {name} constructor
        {name}::{name}(GameObject &owner) : {inherit}(owner) // Initialize {name} private members here
        {{ 
            // Implement here
        }}

        // Add any additional {name} Constructors here. Ensure you pass "GameObject &owner" to the {inherit} Constructor

        /* Uncomment and implement those methods if you would like copy semantics for {name} class
        {name}::{name}(const {name}&)
        {{
            // Implement here
        }}

        {name}& {name}::operator=(const {name}&)
        {{
            // Implement here
        }}
        */

        /* Uncomment and implement those methods if you would like move semantics for {name} class
        {name}::{name}({name}&&)
        {{
            // Implement here
        }}

        {name}& {name}::operator=({name}&&)
        {{
            // Implement here
        }}
        */

        // {name} destructor
        {name}::~{name}()
        {{
            // Implement here
        }}

        // Component life cycle methods:

        // Called once when initializing the GameObject, or when adding the {name} Component to an initialized GameObject
        void {name}::initialize()
        {{
            // Implement here
        }}

        // Called at the beginning of each Scene containing the owner GameObject, or when adding the {name} Component mid-Scene
        void {name}::begin()
        {{
            // Implement here
        }}

        // Called when the owner GameObject is activated, or when adding the {name} Component to an active GameObject
        void {name}::activate() 
        {{
            // Implement here

            m_active = true;
        }}
        
        // Called when the owner GameObject is deactivated
        void {name}::deactivate() 
        {{
            // Implement here

            m_active = false;
        }}

        // Called once per frame while the owner GameObject is active
        void {name}::update()
        {{
            // Implement here
        }}

        {renderer_method}
    
        // Add {name} Component public member method implementations here

    ''')

    if namespace:
        impl_code = indent(impl_code, '    ')

    file_text += f'\n{impl_code}\n'

    if namespace:
        file_text += f'}} // namespace {namespace}\n'

    cpp.write_text(file_text)

    print(f'  - {cpp.relative_to(Path.cwd())}')

def generate(args: argparse.Namespace):
    """Generate .hpp/.cpp files for a new gamecoe::Component"""

    name = args.name
    inherit = args.inherit
    namespace = args.namespace
    filename = args.filename
    gamecoe = os.environ.get('GAMECOE') is not None # for internal gamecoe development
    root = Path.cwd()

    if not filename:
        filename = pascal_to_snake_case(name)
    
    if not gamecoe and not (root / 'assets' / 'components' / 'include').exists():
        print('[gencoe] Error: Not in a gamecoe project root directory')
        print('[gencoe] Run "gencoe component <name>" from your game project root directory')
        return
    
    if gamecoe and not (root / 'include' / 'gamecoe' / 'entity' / 'renderer').exists():
        print('[gencoe] Error: Not in gamecoe root directory (Internal gamecoe development)')
        print('[gencoe] Run "gencoe component <name>" from your gamecoe root directory')
        return
    
    if inherit and inherit not in INHERIT_OPTIONS:
        print(f'[gencoe] Warning: {inherit} is not a built-in gamecoe Component')
        print(f'[gencoe] Warning: Ensure the {inherit} Component exists and include its header manually')

    hpp_path = (root / 'include' / 'gamecoe' / 'entity') if gamecoe else (root / 'assets' / 'components' / 'include')
    hpp_path = (hpp_path / inherit.lower()) if inherit else hpp_path
    hpp_path.mkdir(parents=True, exist_ok=True)
    hpp_path = hpp_path / f'{filename}.hpp'
    generate_hpp(name, hpp_path, inherit, namespace)

    cpp_path = (root / 'src' / 'gamecoe' / 'entity') if gamecoe else (root / 'assets' / 'components' / 'src')
    cpp_path = (cpp_path / inherit.lower()) if inherit else cpp_path
    cpp_path.mkdir(parents=True, exist_ok=True)
    cpp_path = cpp_path / f'{filename}.cpp'
    generate_cpp(name, hpp_path, cpp_path, inherit, namespace)

    print(f'[gencoe] {name} Component files are ready for implementation')
