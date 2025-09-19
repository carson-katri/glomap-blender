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
    log_path = Path(bpy.app.tempdir) / "colmap_log_"
    pycolmap.logging.set_log_destination(pycolmap.logging.Level.INFO, log_path)

    register_glomap()
    register_colmap()

def unregister():
    unregister_glomap()
    unregister_colmap()

if __name__ == "__main__":
    register()