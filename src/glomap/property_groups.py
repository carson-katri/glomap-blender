import bpy

class ViewGraphCalibrationPropertyGroup(bpy.types.PropertyGroup):
    # --ViewGraphCalib.thres_lower_ratio arg (=0.10000000000000001)
    thres_lower_ratio: bpy.props.FloatProperty(name="Threshold Lower Ratio", default=0.10000000000000001)
    # --ViewGraphCalib.thres_higher_ratio arg (=10)
    thres_higher_ratio: bpy.props.FloatProperty(name="Threshold Higher Ratio", default=10)
    # --ViewGraphCalib.thres_two_view_error arg (=2)
    thres_two_view_error: bpy.props.FloatProperty(name="Threshold Two View Error", default=2)

    def arguments(self):
        return [
            "--ViewGraphCalib.thres_lower_ratio", self.thres_lower_ratio,
            "--ViewGraphCalib.thres_higher_ratio", self.thres_higher_ratio,
            "--ViewGraphCalib.thres_two_view_error", self.thres_two_view_error,
        ]

class RelativePoseEstimationPropertyGroup(bpy.types.PropertyGroup):
    # --RelPoseEstimation.max_epipolar_error arg (=1)
    max_epipolar_error: bpy.props.FloatProperty(name="Max Epipolar Error", default=1)

    def arguments(self):
        return [
            "--RelPoseEstimation.max_epipolar_error", self.max_epipolar_error
        ]

class TrackEstablishmentPropertyGroup(bpy.types.PropertyGroup):
    # --TrackEstablishment.min_num_tracks_per_view arg (=-1)
    min_num_tracks_per_view: bpy.props.IntProperty(name="Min Tracks Per View", default=-1)
    # --TrackEstablishment.min_num_view_per_track arg (=3)
    min_num_view_per_track: bpy.props.IntProperty(name="Min View Per Track", default=3)
    # --TrackEstablishment.max_num_view_per_track arg (=100)
    max_num_view_per_track: bpy.props.IntProperty(name="Max View Per Track", default=100)
    # --TrackEstablishment.max_num_tracks arg (=10000000)
    max_num_tracks: bpy.props.IntProperty(name="Max Tracks", default=10000000)

    def arguments(self):
        return [
            "--TrackEstablishment.min_num_tracks_per_view", self.min_num_tracks_per_view,
            "--TrackEstablishment.min_num_view_per_track", self.min_num_view_per_track,
            "--TrackEstablishment.max_num_view_per_track", self.max_num_view_per_track,
            "--TrackEstablishment.max_num_tracks", self.max_num_tracks,
        ]

class GlobalPositioningPropertyGroup(bpy.types.PropertyGroup):
    # --GlobalPositioning.optimize_positions arg (=1)
    optimize_positions: bpy.props.BoolProperty(name="Optimize Positions", default=True)
    # --GlobalPositioning.optimize_points arg (=1)
    optimize_points: bpy.props.BoolProperty(name="Optimize Points", default=True)
    # --GlobalPositioning.optimize_scales arg (=1)
    optimize_scales: bpy.props.BoolProperty(name="Optimize Scales", default=True)
    # --GlobalPositioning.thres_loss_function arg (=0.10000000000000001)
    thres_loss_function: bpy.props.FloatProperty(name="Threshold Loss Function", default=0.10000000000000001)
    # --GlobalPositioning.max_num_iterations arg (=100)
    max_num_iterations: bpy.props.FloatProperty(name="Max Iterations", default=100)

    def arguments(self):
        return [
            "--GlobalPositioning.optimize_positions", self.optimize_positions,
            "--GlobalPositioning.optimize_points", self.optimize_points,
            "--GlobalPositioning.optimize_scales", self.optimize_scales,
            "--GlobalPositioning.thres_loss_function", self.thres_loss_function,
            "--GlobalPositioning.max_num_iterations", self.max_num_iterations,
        ]

class BundleAdjustmentPropertyGroup(bpy.types.PropertyGroup):
    # --BundleAdjustment.optimize_rotations arg (=1)
    optimize_rotations: bpy.props.BoolProperty(name="Optimize Rotations", default=True)
    # --BundleAdjustment.optimize_translation arg (=1)
    optimize_translation: bpy.props.BoolProperty(name="Optimize Translation", default=True)
    # --BundleAdjustment.optimize_intrinsics arg (=1)
    optimize_intrinsics: bpy.props.BoolProperty(name="Optimize Intrinsics", default=True)
    # --BundleAdjustment.optimize_principal_point arg (=0)
    optimize_principal_point: bpy.props.BoolProperty(name="Optimize Principal Point", default=False)
    # --BundleAdjustment.optimize_points arg (=1)
    optimize_points: bpy.props.BoolProperty(name="Optimize Points", default=True)
    # --BundleAdjustment.thres_loss_function arg (=1)
    thres_loss_function: bpy.props.FloatProperty(name="Threshold Loss Function", default=1)
    # --BundleAdjustment.max_num_iterations arg (=200)
    max_num_iterations: bpy.props.IntProperty(name="Max Iterations", default=200)

    def arguments(self):
        return [
            "--BundleAdjustment.optimize_rotations", self.optimize_rotations,
            "--BundleAdjustment.optimize_translation", self.optimize_translation,
            "--BundleAdjustment.optimize_intrinsics", self.optimize_intrinsics,
            "--BundleAdjustment.optimize_principal_point", self.optimize_principal_point,
            "--BundleAdjustment.optimize_points", self.optimize_points,
            "--BundleAdjustment.thres_loss_function", self.thres_loss_function,
            "--BundleAdjustment.max_num_iterations", self.max_num_iterations,
        ]

class TriangulationPropertyGroup(bpy.types.PropertyGroup):
    # --Triangulation.complete_max_reproj_error arg (=15)
    complete_max_reproj_error: bpy.props.FloatProperty(name="Complete Max Reprojection Error", default=15)
    # --Triangulation.merge_max_reproj_error arg (=15)
    merge_max_reproj_error: bpy.props.FloatProperty(name="Merge Max Reprojection Error", default=15)
    # --Triangulation.min_angle arg (=1)
    min_angle: bpy.props.FloatProperty(name="Min Angle", default=1)
    # --Triangulation.min_num_matches arg (=15)
    min_num_matches: bpy.props.IntProperty(name="Min Matches", default=15)

    def arguments(self):
        return [
            "--Triangulation.complete_max_reproj_error", self.complete_max_reproj_error,
            "--Triangulation.merge_max_reproj_error", self.merge_max_reproj_error,
            "--Triangulation.min_angle", self.min_angle,
            "--Triangulation.min_num_matches", self.min_num_matches,
        ]

class ThresholdsPropertyGroup(bpy.types.PropertyGroup):
    # --Thresholds.max_angle_error arg (=1)
    max_angle_error: bpy.props.FloatProperty(name="Max Angle Error", default=1)
    # --Thresholds.max_reprojection_error arg (=0.01)
    max_reprojection_error: bpy.props.FloatProperty(name="Max Reprojection Error", default=0.01)
    # --Thresholds.min_triangulation_angle arg (=1)
    min_triangulation_angle: bpy.props.FloatProperty(name="Min Triangulation Angle", default=1)
    # --Thresholds.max_epipolar_error_E arg (=1)
    max_epipolar_error_E: bpy.props.FloatProperty(name="Max Epipolar Error E", default=1)
    # --Thresholds.max_epipolar_error_F arg (=4)
    max_epipolar_error_F: bpy.props.FloatProperty(name="Max Epipolar Error F", default=4)
    # --Thresholds.max_epipolar_error_H arg (=4)
    max_epipolar_error_H: bpy.props.FloatProperty(name="Max Epipolar Error H", default=4)
    # --Thresholds.min_inlier_num arg (=30)
    min_inlier_num: bpy.props.IntProperty(name="Min Inlier", default=30)
    # --Thresholds.min_inlier_ratio arg (=0.25)
    min_inlier_ratio: bpy.props.FloatProperty(name="Min Inlier Ratio", default=0.25)
    # --Thresholds.max_rotation_error arg (=10)
    max_rotation_error: bpy.props.FloatProperty(name="Max Rotation Error", default=10)

    def arguments(self):
        return [
            "--Thresholds.max_angle_error", self.max_angle_error,
            "--Thresholds.max_reprojection_error", self.max_reprojection_error,
            "--Thresholds.min_triangulation_angle", self.min_triangulation_angle,
            "--Thresholds.max_epipolar_error_E", self.max_epipolar_error_E,
            "--Thresholds.max_epipolar_error_F", self.max_epipolar_error_F,
            "--Thresholds.max_epipolar_error_H", self.max_epipolar_error_H,
            "--Thresholds.min_inlier_num", self.min_inlier_num,
            "--Thresholds.min_inlier_ratio", self.min_inlier_ratio,
            "--Thresholds.max_rotation_error", self.max_rotation_error,
        ]

class GlomapPropertyGroup(bpy.types.PropertyGroup):
    # --GlobalPositioning.use_gpu 1 --BundleAdjustment.use_gpu
    use_gpu: bpy.props.BoolProperty(name="Use GPU", default=True)
    
    # --ba_iteration_num arg (=3)
    ba_iteration_num: bpy.props.IntProperty(name="Bundle Adjustment Iterations", default=3)
    # --retriangulation_iteration_num arg (=1)
    retriangulation_iteration_num: bpy.props.IntProperty(name="Retriangulation Iterations", default=1)
    # --skip_preprocessing arg (=0)
    use_preprocessing: bpy.props.BoolProperty(name="Preprocess", default=True)
    # --skip_view_graph_calibration arg (=0)
    use_view_graph_calibration: bpy.props.BoolProperty(name="View Graph Calibration", default=True)
    # --skip_relative_pose_estimation arg (=0)
    use_relative_pose_estimation: bpy.props.BoolProperty(name="Relative Pose Estimation", default=True)
    # --skip_rotation_averaging arg (=0)
    use_rotation_averaging: bpy.props.BoolProperty(name="Rotation Averaging", default=True)
    # --skip_global_positioning arg (=0)
    use_global_positioning: bpy.props.BoolProperty(name="Global Positioning", default=True)
    # --skip_bundle_adjustment arg (=0)
    use_bundle_adjustment: bpy.props.BoolProperty(name="Bundle Adjustment", default=True)
    # --skip_retriangulation arg (=0)
    use_retriangulation: bpy.props.BoolProperty(name="Retriangulation", default=True)
    # --skip_pruning arg (=1)
    use_pruning: bpy.props.BoolProperty(name="Prune", default=False)

    view_graph_calibration: bpy.props.PointerProperty(type=ViewGraphCalibrationPropertyGroup)
    relative_pose_estimation: bpy.props.PointerProperty(type=RelativePoseEstimationPropertyGroup)
    track_establishment: bpy.props.PointerProperty(type=TrackEstablishmentPropertyGroup)
    global_positioning: bpy.props.PointerProperty(type=GlobalPositioningPropertyGroup)
    bundle_adjustment: bpy.props.PointerProperty(type=BundleAdjustmentPropertyGroup)
    triangulation: bpy.props.PointerProperty(type=TriangulationPropertyGroup)
    thresholds: bpy.props.PointerProperty(type=ThresholdsPropertyGroup)

    def arguments(self):
        return [
            "--GlobalPositioning.use_gpu", self.use_gpu,
            "--BundleAdjustment.use_gpu", self.use_gpu,

            "--ba_iteration_num", self.ba_iteration_num,
            "--retriangulation_iteration_num", self.retriangulation_iteration_num,
            "--skip_preprocessing", not self.use_preprocessing,
            "--skip_view_graph_calibration", not self.use_view_graph_calibration,
            "--skip_relative_pose_estimation", not self.use_relative_pose_estimation,
            "--skip_rotation_averaging", not self.use_rotation_averaging,
            "--skip_global_positioning", not self.use_global_positioning,
            "--skip_bundle_adjustment", not self.use_bundle_adjustment,
            "--skip_retriangulation", not self.use_retriangulation,
            "--skip_pruning", not self.use_pruning,
            *self.view_graph_calibration.arguments(),
            *self.relative_pose_estimation.arguments(),
            *self.track_establishment.arguments(),
            *self.global_positioning.arguments(),
            *self.bundle_adjustment.arguments(),
            *self.triangulation.arguments(),
            *self.thresholds.arguments(),
        ]

def register():
    bpy.utils.register_class(ViewGraphCalibrationPropertyGroup)
    bpy.utils.register_class(RelativePoseEstimationPropertyGroup)
    bpy.utils.register_class(TrackEstablishmentPropertyGroup)
    bpy.utils.register_class(GlobalPositioningPropertyGroup)
    bpy.utils.register_class(BundleAdjustmentPropertyGroup)
    bpy.utils.register_class(TriangulationPropertyGroup)
    bpy.utils.register_class(ThresholdsPropertyGroup)
    bpy.utils.register_class(GlomapPropertyGroup)

    bpy.types.MovieClip.glomap = bpy.props.PointerProperty(type=GlomapPropertyGroup)

def unregister():
    bpy.utils.unregister_class(ViewGraphCalibrationPropertyGroup)
    bpy.utils.unregister_class(RelativePoseEstimationPropertyGroup)
    bpy.utils.unregister_class(TrackEstablishmentPropertyGroup)
    bpy.utils.unregister_class(GlobalPositioningPropertyGroup)
    bpy.utils.unregister_class(BundleAdjustmentPropertyGroup)
    bpy.utils.unregister_class(TriangulationPropertyGroup)
    bpy.utils.unregister_class(ThresholdsPropertyGroup)
    bpy.utils.unregister_class(GlomapPropertyGroup)