import bpy
import subprocess
from pathlib import Path
import sys
import re

from ..utils import prepare_database, BlockingOperator

class GlomapSolveOperator(BlockingOperator):
    bl_idname = "colmap.glomap"
    bl_label = "Solve with GLOMAP"
    bl_description = "Solve camera motion with GLOMAP"

    parse_logs = False

    def prepare(self, context):
        sc = context.space_data
        clip = sc.clip

        database_path, images_path, reconstruction_path = prepare_database(clip)

        # path to the precompiled glomap executable
        if sys.platform.startswith('win'):
            executable = Path(__file__).parent / "../../glomap_subprocess/glomap.exe"
        elif sys.platform == 'darwin':
            executable = Path(__file__).parent / "../../glomap_subprocess/glomap.app/Contents/MacOS/glomap"
        else:
            executable = Path(__file__).parent / "../../glomap_subprocess/glomap.AppImage"
        
        return ([
            str(executable.resolve()),
            "mapper",
            "--database_path", str(database_path),
            "--output_path", str(reconstruction_path),
        ],)

    def execute_async(self, args):
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        progress_expression = re.compile(r"(\d+) \/ (\d+)")
        message_expression = re.compile(r"-+\nRunning ([\w\s]+) \.\.\.\n-+")
        buffer = ""
        for line in process.stdout:
            print(line, end='')
            buffer += line
            progress_match = progress_expression.search(buffer)
            message_match = message_expression.search(buffer)
            if message_match:
                self._message = message_match.group(1).title()
            if progress_match:
                self._progress_current = int(progress_match.group(1))
                self._progress_total = int(progress_match.group(2))
            if progress_match or message_match:
                buffer = ''
        process.wait()

        return {'FINISHED'}

def register():
    bpy.utils.register_class(GlomapSolveOperator)

def unregister():
    bpy.utils.unregister_class(GlomapSolveOperator)