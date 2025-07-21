# Lens Flare Project

A 3D OpenGL implementation of lens flare effects in Python, featuring dynamic light source visibility detection and smooth transitions.

> **Note**: The visuals are kept simple, the project focuses on implementing mathematically accurate lens flare detection and occlusion algorithms rather than photorealistic rendering.


## Features

- **Real-time lens flare rendering** with multiple flare types
- **Dynamic occlusion detection** using depth buffer and ray-casting
- **Smooth visibility transitions** based on light source obstruction
- **Interactive 3D camera** with full movement and rotation controls
- **Textured 3D scene** with rotating objects

## Demo

The application renders a 3D scene with a rotating textured cube, ground plane, and a light source that produces lens flare effects when visible to the camera. The lens flares dynamically fade in/out based on occlusion by scene objects.

## Architecture

The project is structured into four main modules:

- **`main.py`** - Main application loop and input handling
- **`graphics.py`** - 3D rendering and texture management
- **`lens_flare.py`** - Lens flare effects and visibility detection
- **`math_utils.py`** - 3D mathematics and ray-casting algorithms

## How It Works

1. **Visibility Detection**: Uses field of view checking and depth buffer testing
2. **Occlusion Handling**: Ray-casting algorithm detects object interference
3. **Dynamic Rendering**: Lens flares scale and fade based on light visibility
4. **Smooth Transitions**: Gradual opacity changes for realistic effects

## Controls

### Camera Movement
- `W/A/S/D` - Move forward/left/backward/right
- `Q/E` - Move up/down

### Camera Rotation
- `Arrow keys` - Rotate camera view

### Debug
- `Space` - Show debug information
- `ESC` - Exit application


