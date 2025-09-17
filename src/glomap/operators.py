import bpy
import subprocess
from pathlib import Path

from ..utils import prepare_database

class GlomapSolveOperator(bpy.types.Operator):
    bl_idname = "colmap.glomap"
    bl_label = "Solve with GLOMAP"
    bl_description = "Solve camera motion with GLOMAP"

    def execute(self, context):
        sc = context.space_data
        clip = sc.clip

        database_path, images_path, reconstruction_path = prepare_database(clip)

        # path to the precompiled glomap executable
        executable = Path(__file__).parent / "../../glomap_subprocess/glomap"

        subprocess.run([
            executable,
            "mapper",
            "--database_path", database_path,
            "--output_path", reconstruction_path
        ])

        return {'FINISHED'}

def register():
    bpy.utils.register_class(GlomapSolveOperator)

def unregister():
    bpy.utils.unregister_class(GlomapSolveOperator)