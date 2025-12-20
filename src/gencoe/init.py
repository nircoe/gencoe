"""Initialize a gamecoe gamedev project"""

import argparse
from pathlib import Path
from textwrap import dedent

def create_parser(subparsers):
    parser = subparsers.add_parser(
        name='init', 
        usage='%(prog)s name [-p PATH] [-h]',
        help='Initialize a new gamecoe project'
    )

    parser.add_argument('name', type=str, help='The name of your new game project')
    parser.add_argument('-p', '--path', type=str, default=None, help='The directory path of your new game project')

def create_directories_structure(root: Path):
    root.mkdir(parents=True, exist_ok=True)
    (root / 'cmake').mkdir(exist_ok=True)
    (root / 'assets').mkdir(exist_ok=True)
    (root / 'assets' / 'audio' / 'general' / 'sfx').mkdir(parents=True, exist_ok=True)
    (root / 'assets' / 'audio' / 'general' / 'music').mkdir(parents=True, exist_ok=True)
    (root / 'assets' / 'textures' / 'general').mkdir(parents=True, exist_ok=True)
    (root / 'components' / 'include').mkdir(parents=True, exist_ok=True)
    (root / 'components' / 'src').mkdir(parents=True, exist_ok=True)

def generate_gamecoe_cmake(name: str, cmake_root: Path):
    gamecoe_cmake = cmake_root / 'gamecoe.cmake'
    git_tag = 'main' # TODO: Change to release tag in the future

    file_text = dedent(f'''
        function(fetch_gamecoe)
            message(STATUS "[{name}] Fetching gamecoe from source...")

            FetchContent_Declare(
                gamecoe
                GIT_REPOSITORY https://github.com/nircoe/gamecoe.git
                GIT_TAG {git_tag}
            )
            FetchContent_MakeAvailable(gamecoe)
        endfunction()
    ''').strip()

    gamecoe_cmake.write_text(file_text)

def generate_utils_cmake(name: str, cmake_root: Path):
    utils_cmake = cmake_root / 'utils.cmake'
    macro_name = name.upper().replace(' ', '_')

    file_text = dedent(f'''
        function(copy_directory_to_build_root exe dir)
            add_custom_command(TARGET ${{exe}} POST_BUILD
                COMMAND ${{CMAKE_COMMAND}} -E copy_directory
                ${{{macro_name}_SOURCE_ROOT_DIR}}/${{dir}} $<TARGET_FILE_DIR:${{exe}}>/${{dir}}
                COMMENT "[{name}] Copying ${{dir}} to build root"
                WORKING_DIRECTORY ${{CMAKE_BINARY_DIR}}
            )
        endfunction()
    ''').strip()

    utils_cmake.write_text(file_text)

def generate_config_cmake(name: str, cmake_root: Path):
    config_cmake = cmake_root / f'{name}_config.cmake'

    file_text = dedent(f'''
        include(${{CMAKE_CURRENT_LIST_DIR}}/gamecoe.cmake)
        include(${{CMAKE_CURRENT_LIST_DIR}}/utils.cmake)
    ''').strip()

    generate_gamecoe_cmake(name, cmake_root)
    generate_utils_cmake(name, cmake_root)
    config_cmake.write_text(file_text)

def generate_cmakelists(name: str, root: Path):
    cmake_lists = root / 'CMakeLists.txt'
    macro_name = name.upper().replace(' ', '_')

    file_text = dedent(f'''
        cmake_minimum_required(VERSION 3.20)
        project({name} LANGUAGES C CXX)
        set(CMAKE_CXX_STANDARD 20)
        set(CMAKE_CXX_STANDARD_REQUIRED ON)
        set(CMAKE_CXX_EXTENSIONS OFF)
        set({macro_name}_SOURCE_ROOT_DIR ${{CMAKE_CURRENT_SOURCE_DIR}})

        # Includes
        include(cmake/{name}_config.cmake)
        include(FetchContent)

        # Fetching libraries for {name}:
        # gamecoe
        fetch_gamecoe()

        # Creating {name} executable
        file(GLOB_RECURSE COMPONENTS components/src/*.cpp)
        add_executable({name} main.cpp ${{COMPONENTS}})

        target_include_directories({name} 
            PRIVATE 
                components/include
        )

        target_link_libraries({name}
            PRIVATE
                gamecoe
        )

        # Copy essential directories to build root
        copy_gamecoe_assets_to_build_root({name})
        copy_directory_to_build_root({name} "assets")
        
    ''').strip()

    cmake_lists.write_text(file_text)

def generate_main_cpp(name: str, root: Path):
    main_cpp = root / 'main.cpp'

    # TODO: change the example Component from Camera to other Component in the future
    file_text = dedent(f'''
        #include <gamecoe.hpp>

        // uncomment the next line if you want to use the gamecoe namespace
        // using namespace gamecoe; 

        int main()
        {{
            // Creating the gamecoe::Game object for {name}
            gamecoe::Game {name}("{name}", 800, 600, colorcoe::darkSlateGray());

            // Access the camera
            auto &camera = {name}.mainCamera();

            // Move the Main Camera GameObject
            auto &cameraTransform = camera.owner().transform();
            cameraTransform.translate({{3.0f, 3.0f, 5.0f}});
            cameraTransform.lookAt({{0.0f, 0.0f, 0.0f}});

            // Creating a new Scene
            auto &scene = {name}.createScene("SceneName");

            // Creating a new GameObject in a Scene
            auto &gameObject = scene.createGameObject("GameObjectName");

            // Set a Renderer to a GameObject
            gameObject.setRenderer(gamecoe::ShapeRenderer::cube(gameObject, colorcoe::maroon()));

            // Add a new Component to a GameObject (Camera in this example, can be any kind of Component, except Transform)
            // gameObject.addComponent<Camera>(std::make_unique<Camera>(gameObject));
            // or
            // auto cameraPtr = std::make_unique<Camera>(cameraGameObject);
            // gameObject.addComponent<Camera>(std::move(cameraPtr));

            // Get a Component reference of a GameObject
            // Transform - builtin Component, can get anytime
            auto &transform = gameObject.transform();
            // Renderer - optional Component, it will throw if you didn't set a Renderer before (via setRenderer() or addComponent<>())
            auto &renderer = gameObject.renderer();
            // Any other Component - it will throw if you didn't add this Component before (via addComponent<>())
            // Camera in this example, can be any other kind of Component
            // auto &camera = gameObject.getComponent<Camera>();

            // Load a scene
            {name}.loadScene("SceneName");
            // activate a scene
            {name}.activateScene("SceneName");

            // Play the game (starts the gameplay loop)
            {name}.play();

            return 0;
        }}
    ''').strip()

    main_cpp.write_text(file_text)

def generate(args: argparse.Namespace):
    """Generate a new empty gamecoe gamedev project"""
    name = args.name
    root = Path(args.path) / name if args.path else Path.cwd() / name
    
    create_directories_structure(root)
    generate_config_cmake(name, root / 'cmake')
    generate_cmakelists(name, root)
    generate_main_cpp(name, root)

    print(f'[gencoe] Created {name} - an empty gamecoe project at {root}')
    print('[gencoe] To proceed your gamedev journey, you can use gencoe:')
    print('[gencoe] gencoe scene <scene_name> - in order to create the essential directories for a new scene')
    print('[gencoe] gencoe component <component_name> - in order to generate component code files')