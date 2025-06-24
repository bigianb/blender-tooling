# blender-tooling
Various scripts to deal with Blender.

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/65675b8bec754ba6a8f93daa19dce7aa)](https://app.codacy.com/gh/bigianb/blender-tooling/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

In general, open the folder in VSCode.

# Python version

The Blender python module (bpy) currently requires python version 3.11
It's easier to create a virtual environment using python 3.11 and install bpy into it.

see https://docs.python.org/3/tutorial/venv.html

## For example on a Mac
```
python3.11 -m venv venv       
source venv/bin/activate
pip install -r requirements.txt
```

Blender API: https://docs.blender.org/api/current/index.html

# Area 51
You will need the Area 51 game data. Many people have this because it was distributed for free by the US Army.

Set the environment variable `A51_GAME_DATA` to the root of the PC game data (the directory which contains the file BOOT.DFS).
Set the environment variable `A51_DOOM_DATA` to where the mod will be written. If your doom base directory is at /xxx/yyy/base then set I suggest setting this to /xxx/yyy/a51mod. 

Running Dreamland in VSCode will create a blend file in maps in the `A51_DOOM_DATA` directory.
The exporter currently expects to find the textures in the textures directory. Right now you need to use something like DFSViewer to populate this (just export all to that location) but eventually the python script will create them.

## Export to gltf
Use the blender export to create a .glb file in the same location as the blend file. You need to ensure that you select custom properties are selected in the export options.

## Build the map

In RBDOOM-BFG open the console and type
```
dmap DREAMLND.glb
```

You can then run the map with

```
map DREAMLND.glb
```

# Some links for reading blender levels into RBDOOM3-BFG

https://dmeat.itch.io/stack-rock-dungeon

https://modwiki.dhewm3.org/RBDoom3BFG-Blender-Mapping




