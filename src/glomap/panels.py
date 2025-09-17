import bpy

from .operators import GlomapSolveOperator
from ..colmap.operators import ColmapSetupTrackingSceneOperator

class CLIP_PT_GlomapSolverPanel(bpy.types.Panel):
    bl_space_type = 'CLIP_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "Solve"
    bl_label = "GLOMAP Solver"
    bl_idname = "CLIP_PT_GlomapSolverPanel"
    
    @classmethod
    def poll(cls, context):
        return context.space_data.mode == 'TRACKING'

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        sc = context.space_data
        clip = sc.clip
        
        layout.prop(clip.colmap, "use_custom_directory")
        if clip.colmap.use_custom_directory:
            layout.prop(clip.colmap, "directory")
        
        layout.prop(clip.glomap, "use_gpu")
        layout.prop(clip.glomap, "ba_iteration_num")
        layout.prop(clip.glomap, "retriangulation_iteration_num")
        layout.prop(clip.glomap, "use_preprocessing")
        layout.prop(clip.glomap, "use_rotation_averaging")
        layout.prop(clip.glomap, "use_pruning")

        col = layout.column(align=True)
        col.scale_y = 2.0
        col.operator(GlomapSolveOperator.bl_idname, text="Solve Camera Motion")
        
        layout.operator(ColmapSetupTrackingSceneOperator.bl_idname, text="Setup Tracking Scene")

class BaseGlomapPanel(bpy.types.Panel):
    bl_space_type = 'CLIP_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "Solve"
    bl_parent_id = CLIP_PT_GlomapSolverPanel.bl_idname
    bl_order = -1
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return context.space_data.mode == 'TRACKING'

class CLIP_PT_ViewGraphCalibration(BaseGlomapPanel):
    bl_label = "View Graph Calibration"

    def draw_header(self, context):
        self.layout.prop(context.space_data.clip.glomap, "use_view_graph_calibration", text="")

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        sc = context.space_data
        clip = sc.clip

        layout.enabled = clip.glomap.use_view_graph_calibration

        layout.prop(clip.glomap.view_graph_calibration, "thres_lower_ratio")
        layout.prop(clip.glomap.view_graph_calibration, "thres_higher_ratio")
        layout.prop(clip.glomap.view_graph_calibration, "thres_two_view_error")

class CLIP_PT_RelativePoseEstimation(BaseGlomapPanel):
    bl_label = "Relative Pose Estimation"

    def draw_header(self, context):
        self.layout.prop(context.space_data.clip.glomap, "use_relative_pose_estimation", text="")

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        sc = context.space_data
        clip = sc.clip

        layout.enabled = clip.glomap.use_relative_pose_estimation

        layout.prop(clip.glomap.relative_pose_estimation, "max_epipolar_error")

class CLIP_PT_TrackEstablishment(BaseGlomapPanel):
    bl_label = "Track Establishment"

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        sc = context.space_data
        clip = sc.clip

        layout.prop(clip.glomap.track_establishment, "min_num_tracks_per_view")
        layout.prop(clip.glomap.track_establishment, "min_num_view_per_track")
        layout.prop(clip.glomap.track_establishment, "max_num_view_per_track")
        layout.prop(clip.glomap.track_establishment, "max_num_tracks")

class CLIP_PT_GlobalPositioning(BaseGlomapPanel):
    bl_label = "Global Positioning"

    def draw_header(self, context):
        self.layout.prop(context.space_data.clip.glomap, "use_global_positioning", text="")

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        sc = context.space_data
        clip = sc.clip

        layout.enabled = clip.glomap.use_global_positioning

        layout.prop(clip.glomap.global_positioning, "optimize_positions")
        layout.prop(clip.glomap.global_positioning, "optimize_points")
        layout.prop(clip.glomap.global_positioning, "optimize_scales")
        layout.prop(clip.glomap.global_positioning, "thres_loss_function")
        layout.prop(clip.glomap.global_positioning, "max_num_iterations")

class CLIP_PT_BundleAdjustment(BaseGlomapPanel):
    bl_label = "Bundle Adjustment"

    def draw_header(self, context):
        self.layout.prop(context.space_data.clip.glomap, "use_bundle_adjustment", text="")

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        sc = context.space_data
        clip = sc.clip

        layout.enabled = clip.glomap.use_bundle_adjustment

        layout.prop(clip.glomap.bundle_adjustment, "optimize_rotations")
        layout.prop(clip.glomap.bundle_adjustment, "optimize_translation")
        layout.prop(clip.glomap.bundle_adjustment, "optimize_intrinsics")
        layout.prop(clip.glomap.bundle_adjustment, "optimize_principal_point")
        layout.prop(clip.glomap.bundle_adjustment, "optimize_points")
        layout.prop(clip.glomap.bundle_adjustment, "thres_loss_function")
        layout.prop(clip.glomap.bundle_adjustment, "max_num_iterations")

class CLIP_PT_Triangulation(BaseGlomapPanel):
    bl_label = "Triangulation"

    def draw_header(self, context):
        self.layout.prop(context.space_data.clip.glomap, "use_retriangulation", text="")

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        sc = context.space_data
        clip = sc.clip

        layout.enabled = clip.glomap.use_retriangulation

        layout.prop(clip.glomap.triangulation, "complete_max_reproj_error")
        layout.prop(clip.glomap.triangulation, "merge_max_reproj_error")
        layout.prop(clip.glomap.triangulation, "min_angle")
        layout.prop(clip.glomap.triangulation, "min_num_matches")

class CLIP_PT_Thresholds(BaseGlomapPanel):
    bl_label = "Thresholds"

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        sc = context.space_data
        clip = sc.clip

        layout.prop(clip.glomap.thresholds, "max_angle_error")
        layout.prop(clip.glomap.thresholds, "max_reprojection_error")
        layout.prop(clip.glomap.thresholds, "min_triangulation_angle")
        layout.prop(clip.glomap.thresholds, "max_epipolar_error_E")
        layout.prop(clip.glomap.thresholds, "max_epipolar_error_F")
        layout.prop(clip.glomap.thresholds, "max_epipolar_error_H")
        layout.prop(clip.glomap.thresholds, "min_inlier_num")
        layout.prop(clip.glomap.thresholds, "min_inlier_ratio")
        layout.prop(clip.glomap.thresholds, "max_rotation_error")

def register():
    bpy.utils.register_class(CLIP_PT_GlomapSolverPanel)
    
    bpy.utils.register_class(CLIP_PT_ViewGraphCalibration)
    bpy.utils.register_class(CLIP_PT_RelativePoseEstimation)
    bpy.utils.register_class(CLIP_PT_TrackEstablishment)
    bpy.utils.register_class(CLIP_PT_GlobalPositioning)
    bpy.utils.register_class(CLIP_PT_BundleAdjustment)
    bpy.utils.register_class(CLIP_PT_Triangulation)
    bpy.utils.register_class(CLIP_PT_Thresholds)

def unregister():
    bpy.utils.unregister_class(CLIP_PT_GlomapSolverPanel)

    bpy.utils.unregister_class(CLIP_PT_ViewGraphCalibration)
    bpy.utils.unregister_class(CLIP_PT_RelativePoseEstimation)
    bpy.utils.unregister_class(CLIP_PT_TrackEstablishment)
    bpy.utils.unregister_class(CLIP_PT_GlobalPositioning)
    bpy.utils.unregister_class(CLIP_PT_BundleAdjustment)
    bpy.utils.unregister_class(CLIP_PT_Triangulation)
    bpy.utils.unregister_class(CLIP_PT_Thresholds)