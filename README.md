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

Set the environment variable `A51_GAME_DATA` to the root of the PC game data (the directory which contains the file BOOT.DFS)


