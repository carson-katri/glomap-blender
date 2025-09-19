import bpy
import mathutils
import math
import os
import threading
import queue
from pathlib import Path
import glob
import re

import pycolmap

from ..utils import prepare_database, refresh_cache, clear_feature_extraction, clear_feature_matches, clear_reconstruction, clear_images, clear_all, BlockingOperator

class ColmapExtractFeaturesOperator(BlockingOperator):
    bl_idname = "colmap.extract_features"
    bl_label = "Extract Features"
    bl_description = "Automatically find features to track across all frames"

    def prepare(self, context):
        sc = context.space_data
        clip = sc.clip

        database_path, images_path, _ = prepare_database(clip)

        return (clip.colmap.extract_features.build(database_path, images_path),)

    def execute_async(self, args):
        return pycolmap.extract_features(**args)

class ColmapMatchFeaturesOperator(BlockingOperator):
    bl_idname = "colmap.match_features"
    bl_label = "Match Features"
    bl_description = "Match features between frames"

    progress_expression = re.compile(r"Matching \w+ \[(\d+)\/(\d+)")

    def prepare(self, context):
        sc = context.space_data
        clip = sc.clip

        database_path, _, _ = prepare_database(clip)

        matcher, args = clip.colmap.match_features.build(database_path)

        match matcher:
            case 'EXHAUSTIVE':
                return ((matcher, args),)
            case 'SPATIAL':
                return ((matcher, args),)
            case 'VOCABTREE':
                return ((matcher, args),)
            case 'SEQUENTIAL':
                return ((matcher, args),)

    def execute_async(self, args):
        matcher, kwargs = args
        match matcher:
            case 'EXHAUSTIVE':
                return pycolmap.match_exhaustive(**kwargs)
            case 'SPATIAL':
                return pycolmap.match_spatial(**kwargs)
            case 'VOCABTREE':
                return pycolmap.match_vocabtree(**kwargs)
            case 'SEQUENTIAL':
                return pycolmap.match_sequential(**kwargs)

class ColmapSolveOperator(BlockingOperator):
    bl_idname = "colmap.solve"
    bl_label = "Solve"
    bl_description = "Solve camera motion with COLMAP. This is slower than GLOMAP and should only be used if GLOMAP fails"

    parse_logs = False

    def prepare(self, context):
        sc = context.space_data
        clip = sc.clip
        
        database_path, image_path, reconstruction_path = prepare_database(clip)

        return ({
            'database_path': database_path,
            'image_path': image_path,
            'output_path': reconstruction_path,
            'options': clip.colmap.incremental_pipeline.build()
        },)

    def execute_async(self, args):
        self._progress_total = len(os.listdir(args['image_path']))
        def initial_image_pair_callback():
            self._progress_current = 0
        def next_image_callback():
            self._progress_current += 1
        pycolmap.incremental_mapping(
            **args,
            initial_image_pair_callback=initial_image_pair_callback,
            next_image_callback=next_image_callback,
        )

        return {'FINISHED'}

class ColmapSetupTrackingSceneOperator(bpy.types.Operator):
    bl_idname = "colmap.setup_tracking_scene"
    bl_label = "Setup Tracking Scene"
    bl_description = "Load the tracking data as a Camera and point cloud"

    def execute(self, context):
        sc = context.space_data
        clip = sc.clip

        _, _, reconstruction_path = prepare_database(clip)

        reconstruction = pycolmap.Reconstruction(reconstruction_path / "0")

        root_empty = bpy.data.objects.new("Track Root", None)
        bpy.context.collection.objects.link(root_empty)

        # create point cloud
        positions = []
        colors = []
        for point in reconstruction.points3D.values():
            positions.append(point.xyz.tolist())
            colors.append((point.color / 255.0).tolist()) # NOTE: GLOMAP doesn't produce colors yet, COLMAP's mapper does
        mesh = bpy.data.meshes.new("Track Point Cloud")
        obj = bpy.data.objects.new("Track Point Cloud", mesh)
        bpy.context.collection.objects.link(obj)
        
        obj.parent = root_empty
        obj.hide_render = True

        mesh.from_pydata(positions, [], [])  # only verts, no edges/faces
        mesh.update()
        color_layer = mesh.color_attributes.new(name="Color", domain='POINT', type='BYTE_COLOR')
        for i, c in enumerate(colors):
            color_layer.data[i].color = (*c, 1.0)  # RGBA
        
        obj.lock_location = (True, True, True)
        obj.lock_rotation = (True, True, True)
        obj.lock_scale = (True, True, True)

        # create camera
        camera = bpy.data.cameras.new("Track Camera")
        camera.show_background_images = True
        bg = camera.background_images.new()
        bg.source = 'MOVIE_CLIP'
        bg.clip = clip

        camera_obj = bpy.data.objects.new("Track Camera", camera)
        camera_obj.rotation_mode = 'QUATERNION'
        bpy.context.collection.objects.link(camera_obj)
        camera_obj.parent = root_empty

        context.scene.camera = camera_obj

        for _, image in reconstruction.images.items():
            # images are always named as {frame}.tiff
            frame = int(os.path.splitext(os.path.basename(image.name))[0])

            # convert focal length to mm
            camera.lens = image.camera.focal_length_x * (camera.sensor_width / image.camera.width)

            # get cam -> world transform
            world_from_cam = image.cam_from_world().inverse()

            # build Blender 4x4 matrix from pycolmap rotation & translation
            # world_from_cam.rotation.matrix() is a 3x3 numpy array-like
            R = world_from_cam.rotation.matrix()
            t = world_from_cam.translation  # numpy (3,)

            rot_mat = mathutils.Matrix((
                (float(R[0,0]), float(R[0,1]), float(R[0,2])),
                (float(R[1,0]), float(R[1,1]), float(R[1,2])),
                (float(R[2,0]), float(R[2,1]), float(R[2,2])),
            ))
            mat = rot_mat.to_4x4()
            mat.translation = mathutils.Vector((float(t[0]), float(t[1]), float(t[2])))

            # convert COLMAP camera axes (x right, y down, z front) to Blender camera axes (x right, y up, z back)
            # rotating 180° about X flips Y and Z (equivalent to diag(1,-1,-1))
            flip_x180 = mathutils.Matrix.Rotation(math.pi, 4, 'X')
            blender_world_mat = mat @ flip_x180

            # apply transform
            camera_obj.matrix_world = blender_world_mat

            # insert keyframe for transform
            camera.keyframe_insert(data_path="lens", frame=frame)
            camera_obj.keyframe_insert(data_path="location", frame=frame)
            camera_obj.keyframe_insert(data_path="rotation_quaternion", frame=frame)

        return {'FINISHED'}

class ColmapSetOriginOperator(bpy.types.Operator):
    bl_idname = "colmap.set_origin"
    bl_label = "Set Origin"
    bl_description = "Set selected vertex as origin by moving the camera and point cloud in 3D space"

    def execute(self, context):
        camera = context.scene.camera
        track_root = camera.parent
        active_object = context.active_object

        was_edit_mode = active_object.mode == 'EDIT'
        if was_edit_mode:
            bpy.ops.object.mode_set(mode='OBJECT')

        selected_vertex = next((v for v in active_object.data.vertices if v.select == True), None)
        if selected_vertex is None:
            self.report({'ERROR'}, "Select a vertex to mark the scene origin point")
            return {'FINISHED'}

        vert_world = active_object.matrix_world @ selected_vertex.co
        translation = mathutils.Matrix.Translation(-vert_world)
        
        track_root.matrix_world = translation @ track_root.matrix_world

        if was_edit_mode:
            bpy.ops.object.mode_set(mode='EDIT')
        
        return {'FINISHED'}

class ColmapRefreshCacheOperator(bpy.types.Operator):
    bl_idname = "colmap.refresh_cache"
    bl_label = "Refresh Cached Stats"
    bl_description = "Refresh result values from the COLMAP database"

    def execute(self, context):
        sc = context.space_data
        clip = sc.clip

        refresh_cache(clip)

        return {'FINISHED'}

class ColmapClearCacheOperator(bpy.types.Operator):
    bl_idname = "colmap.clear_cache"
    bl_label = "Clear Cache"
    bl_description = "Clear all cached data"

    def execute(self, context):
        sc = context.space_data
        clip = sc.clip

        clear_all(clip)

        return {'FINISHED'}

class ColmapClearFeatureExtractionOperator(bpy.types.Operator):
    bl_idname = "colmap.clear_feature_extraction"
    bl_label = "Clear Feature Extraction"
    bl_description = "Clear all extracted features"

    def execute(self, context):
        sc = context.space_data
        clip = sc.clip

        clear_feature_extraction(clip)

        return {'FINISHED'}

class ColmapClearFeatureMatchesOperator(bpy.types.Operator):
    bl_idname = "colmap.clear_feature_matches"
    bl_label = "Clear Feature Matches"
    bl_description = "Clear all feature matches"

    def execute(self, context):
        sc = context.space_data
        clip = sc.clip

        clear_feature_matches(clip)

        return {'FINISHED'}

class ColmapClearReconstructionOperator(bpy.types.Operator):
    bl_idname = "colmap.clear_reconstruction"
    bl_label = "Clear Reconstruction"
    bl_description = "Clear all reconstruction data"

    def execute(self, context):
        sc = context.space_data
        clip = sc.clip

        clear_reconstruction(clip)

        return {'FINISHED'}

class ColmapClearImagesOperator(bpy.types.Operator):
    bl_idname = "colmap.clear_images"
    bl_label = "Clear Images"
    bl_description = "Clear all split frames"

    def execute(self, context):
        sc = context.space_data
        clip = sc.clip

        clear_images(clip)

        return {'FINISHED'}

def register():
    bpy.utils.register_class(ColmapExtractFeaturesOperator)
    
    bpy.utils.register_class(ColmapMatchFeaturesOperator)
    
    bpy.utils.register_class(ColmapSolveOperator)
    
    bpy.utils.register_class(ColmapSetupTrackingSceneOperator)
    
    bpy.utils.register_class(ColmapRefreshCacheOperator)

    bpy.utils.register_class(ColmapSetOriginOperator)

    bpy.utils.register_class(ColmapClearCacheOperator)
    bpy.utils.register_class(ColmapClearFeatureExtractionOperator)
    bpy.utils.register_class(ColmapClearFeatureMatchesOperator)
    bpy.utils.register_class(ColmapClearReconstructionOperator)
    bpy.utils.register_class(ColmapClearImagesOperator)

def unregister():
    bpy.utils.unregister_class(ColmapExtractFeaturesOperator)
    
    bpy.utils.unregister_class(ColmapMatchFeaturesOperator)
    
    bpy.utils.unregister_class(ColmapSolveOperator)
    
    bpy.utils.unregister_class(ColmapSetupTrackingSceneOperator)

    bpy.utils.unregister_class(ColmapRefreshCacheOperator)

    bpy.utils.unregister_class(ColmapSetOriginOperator)
    
    bpy.utils.unregister_class(ColmapClearCacheOperator)
    bpy.utils.unregister_class(ColmapClearFeatureExtractionOperator)
    bpy.utils.unregister_class(ColmapClearFeatureMatchesOperator)
    bpy.utils.unregister_class(ColmapClearReconstructionOperator)
    bpy.utils.unregister_class(ColmapClearImagesOperator)