"""Component generation"""

import argparse
from pathlib import Path
from textwrap import dedent, indent
import re
import os
from jinja2 import Environment, PackageLoader

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
    parser.add_argument('-i', '--inherit', type=str, default=None, help='Base Component class to inherit from (default: Component)')
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
    gamecoe_prefix = '' if gamecoe else 'gamecoe::'
    original_inherit = inherit
    if inherit:
        inherit = f'{gamecoe_prefix}{inherit}' if inherit in INHERIT_OPTIONS else inherit
    else:
        inherit = f'{gamecoe_prefix}Component<{name}>'

    renderer_method = '\n\n' + dedent('''
        // Called once per frame while the GameObject is active and owns a Renderer
        virtual void render() const override;
    ''').strip() if inherit == f'{gamecoe_prefix}Renderer' else ''
    renderer_method = indent(renderer_method, '    ')

    file_text = dedent('''
#pragma once

#include <gamecoe/entity/component.hpp>
    ''').strip() + '\n'

    if inherit != f'{gamecoe_prefix}Component<{name}>':
        file_text += f'{get_inherit_include_path(original_inherit)}\n'

    if namespace:
        file_text += '\n' + dedent(f'''
namespace {namespace}
{{
        ''').strip()

    class_code = dedent(f'''
class {name} : public {inherit}
{{
    // Add {name} Component private members here (variables and methods)

public:
    static constexpr const char* TYPE_NAME = "{name}";

    {name}({gamecoe_prefix}GameObject &owner); // Component "default" Constructor
    // Add any additional {name} Constructors here. Ensure you pass "GameObject &owner" to the {inherit} Constructor

    // Remove the "= delete" if you would like to implement copy/move semantics for {name}
    {name}(const {name} &other) = delete;
    {name}& operator=(const {name} &other) = delete;
    {name}({name} &&other) = delete;
    {name}& operator=({name} &&other) = delete;

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
    virtual void update() override;{renderer_method}

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
    gamecoe_prefix = '' if gamecoe else 'gamecoe::'
    if inherit:
        inherit = f'{gamecoe_prefix}{inherit}' if inherit in INHERIT_OPTIONS else inherit
    else:
        inherit = f'{gamecoe_prefix}Component<{name}>'
    root = Path.cwd()
    hpp = hpp.relative_to(root / 'include') if gamecoe else hpp.relative_to(root / 'components' / 'include')
    hpp = f'<{hpp}>' if gamecoe else f'"{hpp}"'

    renderer_method = '\n\n' + dedent(f'''
    // Called once per frame while the GameObject is active and owns a Renderer
    void {name}::render() const
    {{
        // Implement here
    }}
    ''').strip() if inherit == f'{gamecoe_prefix}Renderer' else ''

    file_text = dedent(f'''
#include {hpp}
#include <gamecoe/entity/game_object.hpp>
    ''').strip() + '\n'

    if namespace:
        file_text += '\n' + dedent(f'''
namespace {namespace}
{{
        ''').strip()

    impl_code = dedent(f'''
// {name} constructor
{name}::{name}({gamecoe_prefix}GameObject &owner) : {inherit}(owner) // Initialize {name} private members here
{{ 
    // Implement here
}}

// Add any additional {name} Constructors here. Ensure you pass "GameObject &owner" to the {inherit} Constructor

/* Uncomment and implement those methods if you would like copy semantics for {name} class
{name}::{name}(const {name} &other)
{{
    // Implement here
}}

{name}& {name}::operator=(const {name} &other)
{{
    // Implement here
}}
*/

/* Uncomment and implement those methods if you would like move semantics for {name} class
{name}::{name}({name} &&other)
{{
    // Implement here
}}

{name}& {name}::operator=({name} &&other)
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
}}{renderer_method}

// Add {name} Component public member method implementations here
    ''')

    if namespace:
        impl_code = indent(impl_code, '    ')

    file_text += f'{impl_code}'

    if namespace:
        file_text += f'\n}} // namespace {namespace}\n'

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

    if gamecoe:
        namespace = 'gamecoe'

    if not filename:
        filename = pascal_to_snake_case(name)
    
    if not gamecoe and not (root / 'components' / 'include').exists():
        print('[gencoe] Error: Not in a gamecoe project root directory')
        print('[gencoe] Run "gencoe component <name>" from your game project root directory')
        return
    
    if gamecoe and not (root / 'include' / 'gamecoe' / 'entity' / 'renderer').exists():
        print('[gencoe] Error: Not in gamecoe root directory (Internal gamecoe development)')
        print('[gencoe] Run "GAMECOE=1 gencoe component <name>" from your gamecoe root directory')
        return
    
    if inherit and inherit not in INHERIT_OPTIONS:
        print(f'[gencoe] Warning: {inherit} is not a built-in gamecoe Component')
        print(f'[gencoe] Warning: Ensure the {inherit} Component exists and include its header manually')

    hpp_path = (root / 'include' / 'gamecoe' / 'entity') if gamecoe else (root / 'components' / 'include')
    hpp_path = (hpp_path / inherit.lower()) if inherit else hpp_path
    hpp_path.mkdir(parents=True, exist_ok=True)
    hpp_path = hpp_path / f'{filename}.hpp'
    generate_hpp(name, hpp_path, inherit, namespace, gamecoe)

    cpp_path = (root / 'src' / 'gamecoe' / 'entity') if gamecoe else (root / 'components' / 'src')
    cpp_path = (cpp_path / inherit.lower()) if inherit else cpp_path
    cpp_path.mkdir(parents=True, exist_ok=True)
    cpp_path = cpp_path / f'{filename}.cpp'
    generate_cpp(name, hpp_path, cpp_path, inherit, namespace, gamecoe)

    print(f'[gencoe] {name} Component files are ready for implementation')
    print('[gencoe] Make sure you reconfigure your project CMake before building it next time')
