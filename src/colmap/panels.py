import bpy
from .operators import ColmapExtractFeaturesOperator, ColmapMatchFeaturesOperator, ColmapSolveOperator, ColmapSetupTrackingSceneOperator, ColmapRefreshCacheOperator, ColmapClearCacheOperator, ColmapClearFeatureExtractionOperator, ColmapClearFeatureMatchesOperator, ColmapClearReconstructionOperator, ColmapClearImagesOperator

class CLIP_PT_ColmapFeatureExtractionPanel(bpy.types.Panel):
    bl_space_type = 'CLIP_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "Track"
    bl_label = "COLMAP Feature Extraction"
    bl_idname = "CLIP_PT_ColmapFeatureExtractionPanel"
    
    @classmethod
    def poll(cls, context):
        return context.space_data.mode == 'TRACKING'

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        sc = context.space_data
        clip = sc.clip
        
        layout.prop(clip.colmap.extract_features, "camera_mode")

        row = layout.row(align=True)
        row.scale_y = 2.0
        row.operator(ColmapExtractFeaturesOperator.bl_idname)
        row.operator(ColmapRefreshCacheOperator.bl_idname, text="", icon="FILE_REFRESH")
        
        layout.operator(ColmapClearFeatureExtractionOperator.bl_idname, icon="TRASH")

        col = layout.column()
        col.alignment = 'RIGHT'
        col.label(text=f"Descriptors: {clip.colmap.cached_results.num_descriptors}")

class CLIP_PT_SiftExtractionOptionsPanel(bpy.types.Panel):
    bl_space_type = 'CLIP_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "Track"
    bl_parent_id = CLIP_PT_ColmapFeatureExtractionPanel.bl_idname
    bl_order = -1
    bl_options = {'DEFAULT_CLOSED'}
    bl_label = "SIFT"
    
    @classmethod
    def poll(cls, context):
        return context.space_data.mode == 'TRACKING'

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        sc = context.space_data
        clip = sc.clip
        
        layout.prop(clip.colmap.extract_features.sift_options, "max_num_features")
        layout.prop(clip.colmap.extract_features.sift_options, "first_octave")
        layout.prop(clip.colmap.extract_features.sift_options, "num_octaves")
        layout.prop(clip.colmap.extract_features.sift_options, "octave_resolution")
        layout.prop(clip.colmap.extract_features.sift_options, "peak_threshold")
        layout.prop(clip.colmap.extract_features.sift_options, "edge_threshold")
        layout.prop(clip.colmap.extract_features.sift_options, "estimate_affine_shape")
        layout.prop(clip.colmap.extract_features.sift_options, "max_num_orientations")
        layout.prop(clip.colmap.extract_features.sift_options, "upright")
        layout.prop(clip.colmap.extract_features.sift_options, "darkness_adaptivity")
        layout.prop(clip.colmap.extract_features.sift_options, "domain_size_pooling")
        layout.prop(clip.colmap.extract_features.sift_options, "dsp_min_scale")
        layout.prop(clip.colmap.extract_features.sift_options, "dsp_max_scale")
        layout.prop(clip.colmap.extract_features.sift_options, "dsp_num_scales")
        layout.prop(clip.colmap.extract_features.sift_options, "normalization")

class CLIP_PT_ColmapFeatureMatchingPanel(bpy.types.Panel):
    bl_space_type = 'CLIP_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "Track"
    bl_label = "COLMAP Feature Matching"
    bl_idname = "CLIP_PT_ColmapFeatureMatchingPanel"
    
    @classmethod
    def poll(cls, context):
        return context.space_data.mode == 'TRACKING'

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        sc = context.space_data
        clip = sc.clip

        layout.prop(clip.colmap.match_features, "matcher")

        match clip.colmap.match_features.matcher:
            case 'EXHAUSTIVE':
                layout.prop(clip.colmap.match_features.exhaustive, "block_size")
            case 'SPATIAL':
                layout.prop(clip.colmap.match_features.spatial, "ignore_z")
                layout.prop(clip.colmap.match_features.spatial, "max_num_neighbors")
                layout.prop(clip.colmap.match_features.spatial, "max_distance")
            case 'VOCABTREE':
                layout.prop(clip.colmap.match_features.vocab_tree, "num_images")
                layout.prop(clip.colmap.match_features.vocab_tree, "num_nearest_neighbors")
                layout.prop(clip.colmap.match_features.vocab_tree, "num_checks")
                layout.prop(clip.colmap.match_features.vocab_tree, "num_images_after_verification")
                layout.prop(clip.colmap.match_features.vocab_tree, "max_num_features")
                layout.prop(clip.colmap.match_features.vocab_tree, "vocab_tree_path")
                layout.prop(clip.colmap.match_features.vocab_tree, "match_list_path")
            case 'SEQUENTIAL':
                layout.prop(clip.colmap.match_features.sequential, "overlap")
                layout.prop(clip.colmap.match_features.sequential, "quadratic_overlap")
                layout.prop(clip.colmap.match_features.sequential, "expand_rig_images")
                
                layout.prop(clip.colmap.match_features.sequential, "loop_detection")
                col = layout.column()
                col.enabled = clip.colmap.match_features.sequential.loop_detection
                col.prop(clip.colmap.match_features.sequential, "loop_detection_period")
                col.prop(clip.colmap.match_features.sequential, "loop_detection_num_images")
                col.prop(clip.colmap.match_features.sequential, "loop_detection_num_nearest_neighbors")
                col.prop(clip.colmap.match_features.sequential, "loop_detection_num_checks")
                col.prop(clip.colmap.match_features.sequential, "loop_detection_num_images_after_verification")
                col.prop(clip.colmap.match_features.sequential, "loop_detection_max_num_features")
                
                layout.prop(clip.colmap.match_features.sequential, "vocab_tree_path")

        row = layout.row(align=True)
        row.scale_y = 2.0
        row.operator(ColmapMatchFeaturesOperator.bl_idname)
        row.operator(ColmapRefreshCacheOperator.bl_idname, text="", icon="FILE_REFRESH")
        
        layout.operator(ColmapClearFeatureMatchesOperator.bl_idname, icon="TRASH")

        col = layout.column()
        col.alignment = 'RIGHT'
        col.label(text=f"Matches: {clip.colmap.cached_results.num_matches}")
        col.label(text=f"Inlier Matches: {clip.colmap.cached_results.num_inlier_matches}")
        col.label(text=f"Matched Image Pairs: {clip.colmap.cached_results.num_matched_image_pairs}")
        col.label(text=f"Verified Image Pairs: {clip.colmap.cached_results.num_verified_image_pairs}")

class COLMAP_MT_ClearCacheMenu(bpy.types.Menu):
    bl_label = "Clear Cache"
    bl_idname = "COLMAP_MT_ClearCacheMenu"

    def draw(self, context):
        layout = self.layout
        layout.operator(ColmapClearCacheOperator.bl_idname)
        layout.operator(ColmapClearFeatureExtractionOperator.bl_idname)
        layout.operator(ColmapClearFeatureMatchesOperator.bl_idname)
        layout.operator(ColmapClearReconstructionOperator.bl_idname)
        layout.operator(ColmapClearImagesOperator.bl_idname)

class CLIP_PT_ColmapFootagePanel(bpy.types.Panel):
    bl_space_type = 'CLIP_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Footage"
    bl_label = "COLMAP Cache"
    bl_idname = "CLIP_PT_ColmapFootagePanel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        sc = context.space_data
        clip = sc.clip
        
        layout.prop(clip.colmap, "use_custom_directory")
        if clip.colmap.use_custom_directory:
            layout.prop(clip.colmap, "directory")

        layout.operator(ColmapRefreshCacheOperator.bl_idname, icon="FILE_REFRESH")
        
        layout.menu(COLMAP_MT_ClearCacheMenu.bl_idname)

class CLIP_PT_ColmapSolverPanel(bpy.types.Panel):
    bl_space_type = 'CLIP_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "Solve"
    bl_label = "COLMAP Solver"
    bl_idname = "CLIP_PT_ColmapSolverPanel"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return context.space_data.mode == 'TRACKING'

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        sc = context.space_data
        clip = sc.clip
        
        col = layout.column(align=True)
        col.scale_y = 2.0
        col.operator(ColmapSolveOperator.bl_idname, text="Solve Camera Motion")
        
        layout.operator(ColmapSetupTrackingSceneOperator.bl_idname, text="Setup Tracking Scene")
        
        layout.operator(ColmapClearReconstructionOperator.bl_idname, icon="TRASH")

class BaseColmapFeatureMatchingPanel(bpy.types.Panel):
    bl_space_type = 'CLIP_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "Track"
    bl_parent_id = CLIP_PT_ColmapFeatureMatchingPanel.bl_idname
    bl_order = -1
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return context.space_data.mode == 'TRACKING'

class CLIP_PT_SiftOptionsPanel(BaseColmapFeatureMatchingPanel):
    bl_label = "SIFT"

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        sc = context.space_data
        clip = sc.clip

        layout.prop(clip.colmap.match_features.sift_options, "use_gpu")
        layout.prop(clip.colmap.match_features.sift_options, "max_ratio")
        layout.prop(clip.colmap.match_features.sift_options, "max_distance")
        layout.prop(clip.colmap.match_features.sift_options, "cross_check")
        layout.prop(clip.colmap.match_features.sift_options, "max_num_matches")
        layout.prop(clip.colmap.match_features.sift_options, "guided_matching")
        layout.prop(clip.colmap.match_features.sift_options, "cpu_brute_force_matcher")

class CLIP_PT_VerificationOptionsPanel(BaseColmapFeatureMatchingPanel):
    bl_label = "Verification"
    bl_idname = "CLIP_PT_VerificationOptionsPanel"

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        sc = context.space_data
        clip = sc.clip

        layout.prop(clip.colmap.match_features.verification_options, "min_num_inliers")
        layout.prop(clip.colmap.match_features.verification_options, "min_E_F_inlier_ratio")
        layout.prop(clip.colmap.match_features.verification_options, "max_H_inlier_ratio")
        layout.prop(clip.colmap.match_features.verification_options, "watermark_min_inlier_ratio")
        layout.prop(clip.colmap.match_features.verification_options, "watermark_border_size")
        layout.prop(clip.colmap.match_features.verification_options, "detect_watermark")
        layout.prop(clip.colmap.match_features.verification_options, "multiple_ignore_watermark")
        layout.prop(clip.colmap.match_features.verification_options, "force_H_use")
        layout.prop(clip.colmap.match_features.verification_options, "compute_relative_pose")
        layout.prop(clip.colmap.match_features.verification_options, "multiple_models")

class CLIP_PT_RansacOptionsPanel(BaseColmapFeatureMatchingPanel):
    bl_label = "RANSAC"
    bl_space_type = 'CLIP_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "Track"
    bl_parent_id = CLIP_PT_VerificationOptionsPanel.bl_idname
    bl_order = -1
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        sc = context.space_data
        clip = sc.clip

        layout.prop(clip.colmap.match_features.verification_options.ransac, "max_error")
        layout.prop(clip.colmap.match_features.verification_options.ransac, "min_inlier_ratio")
        layout.prop(clip.colmap.match_features.verification_options.ransac, "confidence")
        layout.prop(clip.colmap.match_features.verification_options.ransac, "dyn_num_trials_multiplier")
        layout.prop(clip.colmap.match_features.verification_options.ransac, "min_num_trials")
        layout.prop(clip.colmap.match_features.verification_options.ransac, "max_num_trials")

def register():
    bpy.utils.register_class(CLIP_PT_ColmapFeatureExtractionPanel)
    bpy.utils.register_class(CLIP_PT_SiftExtractionOptionsPanel)
    
    bpy.utils.register_class(CLIP_PT_ColmapFeatureMatchingPanel)
    bpy.utils.register_class(CLIP_PT_SiftOptionsPanel)
    bpy.utils.register_class(CLIP_PT_VerificationOptionsPanel)
    bpy.utils.register_class(CLIP_PT_RansacOptionsPanel)

    bpy.utils.register_class(COLMAP_MT_ClearCacheMenu)
    bpy.utils.register_class(CLIP_PT_ColmapFootagePanel)
    bpy.utils.register_class(CLIP_PT_ColmapSolverPanel)

def unregister():
    bpy.utils.unregister_class(CLIP_PT_ColmapFeatureExtractionPanel)
    bpy.utils.unregister_class(CLIP_PT_SiftExtractionOptionsPanel)
    
    bpy.utils.unregister_class(CLIP_PT_ColmapFeatureMatchingPanel)
    bpy.utils.unregister_class(CLIP_PT_SiftOptionsPanel)
    bpy.utils.unregister_class(CLIP_PT_VerificationOptionsPanel)
    bpy.utils.unregister_class(CLIP_PT_RansacOptionsPanel)

    bpy.utils.unregister_class(COLMAP_MT_ClearCacheMenu)
    bpy.utils.unregister_class(CLIP_PT_ColmapFootagePanel)
    bpy.utils.unregister_class(CLIP_PT_ColmapSolverPanel)