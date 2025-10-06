import bpy
from pathlib import Path
import shutil
import glob
import threading
import functools
import re

from PIL import Image
import av
import pycolmap

def clip_path(clip):
    """Get the path for a clip

    This can be a custom directory path, or the auto-generated path.

    The auto-generated path is a `BL_colmap/{clip_name}` directory next to the clip.
    """
    if clip.colmap.use_custom_directory:
        return Path(bpy.path.abspath(clip.colmap.directory)).resolve()
    else:
        path = Path(bpy.path.abspath(clip.filepath))
        return (path / "../BL_colmap" / path.name).resolve()

def prepare_database(clip):
    """Prepare the COLMAP database for a clip.

    If not already present, this will split the clip into an image sequence.

    Returns the path for the database and images
    """
    path = clip_path(clip)
    path.mkdir(parents=True, exist_ok=True)

    images_path = path / "frames"
    images_path.mkdir(parents=True, exist_ok=True)

    # split video into frames
    if not any(images_path.iterdir()):
        video_path = bpy.path.abspath(clip.filepath)
        container = av.open(video_path)
        for i, frame in enumerate(container.decode(video=0)):
            img = frame.to_ndarray(format="rgb24")
            Image.fromarray(img).save(images_path / f"{(i + 1):04d}.tiff")
    
    database_path = path / "database.db"
    reconstruction_path = path / "reconstruction"
    reconstruction_path.mkdir(parents=True, exist_ok=True)

    return database_path, images_path, reconstruction_path

def refresh_cache(clip):
    database_path, _, _ = prepare_database(clip)

    database = pycolmap.Database(database_path)

    clip.colmap.cached_results.num_descriptors = database.num_descriptors
    
    clip.colmap.cached_results.num_matches = database.num_matches
    clip.colmap.cached_results.num_inlier_matches = database.num_inlier_matches
    clip.colmap.cached_results.num_matched_image_pairs = database.num_matched_image_pairs
    clip.colmap.cached_results.num_verified_image_pairs = database.num_verified_image_pairs

    database.close()

def clear_feature_extraction(clip):
    database_path, _, _ = prepare_database(clip)

    database = pycolmap.Database(database_path)

    database.clear_images()
    database.clear_cameras()
    database.clear_keypoints()
    database.clear_descriptors()

    database.close()

    refresh_cache(clip)

def clear_feature_matches(clip):
    database_path, _, _ = prepare_database(clip)

    database = pycolmap.Database(database_path)
    
    database.clear_matches()
    database.clear_two_view_geometries()

    database.close()

    refresh_cache(clip)

def clear_reconstruction(clip):
    _, _, reconstruction_path = prepare_database(clip)

    shutil.rmtree(reconstruction_path)

def clear_images(clip):
    _, images_path, _ = prepare_database(clip)

    shutil.rmtree(images_path)

def clear_all(clip):
    database_path, _, _ = prepare_database(clip)

    database = pycolmap.Database(database_path)

    database.clear_all_tables()

    database.close()

    refresh_cache(clip)

    clear_reconstruction(clip)
    clear_images(clip)

class BlockingOperator(bpy.types.Operator):
    def prepare(self, context):
        pass
    def execute_async(self, args):
        pass
    
    parse_logs = True
    progress_expression = re.compile(r"Processed file \[(\d+)\/(\d+)\]")

    def _set_running(self, running):
        self._running = running
        BlockingOperator._running_lock[type(self)] = running

    def _is_running(self):
        return BlockingOperator._running_lock.get(type(self), False)

    _running = False

    _running_lock = {} # class state

    _log_pos = 0
    _log_partial_line = ""

    _progress_header = None
    _progress_current = 0
    _progress_total = 0

    _timer = None

    _clip = None

    _message = ""

    @classmethod
    def _draw_progress(cls, operator, self, context):
        if operator is None:
            return
        if operator._progress_total > 0:
            self.layout.label(text=operator._message)
            self.layout.progress(text=f"{operator._progress_current} / {operator._progress_total}", factor=operator._progress_current / operator._progress_total)

    @classmethod
    def _update_progress(cls, operator):
        if operator.parse_logs:
            log_paths = glob.glob(str(Path(bpy.app.tempdir) / "colmap_log_*"))
            if len(log_paths) > 0:
                with open(log_paths[0], "r", errors="ignore") as f:
                    f.seek(operator._log_pos)
                    operator._log_partial_line += f.read()
                    operator._log_pos = f.tell()
                    
                    progress_match = operator.progress_expression.search(operator._log_partial_line)
                    if progress_match:
                        operator._progress_current = int(progress_match.group(1))
                        operator._progress_total = int(progress_match.group(2))
                        operator._log_partial_line = ""
                        for area in bpy.context.screen.areas:
                            if area.type == 'CLIP_EDITOR':
                                area.tag_redraw()
        else:
            for area in bpy.context.screen.areas:
                if area.type == 'CLIP_EDITOR':
                    area.tag_redraw()
        if operator._running:
            return 0.1
        else:
            return None

    def modal(self, context, event):
        if self._running:
            return {'PASS_THROUGH'}
        else:
            if bpy.app.timers.is_registered(self._timer):
                bpy.app.timers.unregister(self._timer)
            bpy.types.CLIP_HT_header.remove(self._progress_header)
            self._progress_header = None
            self._log_partial_line = ""
            self._log_pos = 0
            self._set_running(False)
            for area in bpy.context.screen.areas:
                if area.type == 'CLIP_EDITOR':
                    area.tag_redraw()
            refresh_cache(self._clip)
            self._clip = None
            return {'FINISHED'}

    def execute(self, context):
        self._progress_total = 1 # get the progress bar to show right away
        self._clip = context.space_data.clip

        try:
            args = self.prepare(context)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            self._running = False
            return {'FINISHED'}

        def run(args):
            self.execute_async(args)
            self._running = False
        
        t = threading.Thread(target=run, args=args)
        t.start()

        return {'FINISHED'}
    
    def invoke(self, context, event):
        if self._is_running():
            self.report({'WARNING'}, f"'{self.bl_label}' is already running")
            return {'CANCELLED'}
        
        self._set_running(True)

        self._message = self.bl_label

        self._progress_header = functools.partial(BlockingOperator._draw_progress, self)
        bpy.types.CLIP_HT_header.append(self._progress_header)

        self._timer = functools.partial(BlockingOperator._update_progress, self)
        bpy.app.timers.register(self._timer, first_interval=0.1)

        self.execute(context)
        
        context.window_manager.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}