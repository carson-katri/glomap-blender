import bpy
from pathlib import Path
import shutil

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