import bpy
import mathutils
import math
from pathlib import Path
import subprocess

import pycolmap
import av
from PIL import Image

from .src.colmap import register as register_colmap
from .src.colmap import unregister as unregister_colmap

from .src.glomap import register as register_glomap
from .src.glomap import unregister as unregister_glomap

def register():
    register_colmap()
    register_glomap()

def unregister():
    unregister_colmap()
    unregister_glomap()

if __name__ == "__main__":
    register()