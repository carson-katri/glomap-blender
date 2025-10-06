import bpy
import pycolmap

class SiftExtractionOptionsPropertyGroup(bpy.types.PropertyGroup):
    max_num_features: bpy.props.IntProperty(name="Max Features", default=8192, description="Maximum number of features to detect, keeping larger-scale features")
    first_octave: bpy.props.IntProperty(name="First Octave", default=-1, description="First octave in the pyramid, i.e. -1 upsamples the image by one level")
    num_octaves: bpy.props.IntProperty(name="Num Octave", default=4)
    octave_resolution: bpy.props.IntProperty(name="Octave Resolution", default=3, description="Number of levels per octave")
    peak_threshold: bpy.props.FloatProperty(name="Peak Threshold", default=0.006666666666666667, description="Peak threshold for detection")
    edge_threshold: bpy.props.FloatProperty(name="Edge Threshold", default=10.0, description="Edge threshold for detection")
    estimate_affine_shape: bpy.props.BoolProperty(name="Edge Threshold", default=False, description="Estimate affine shape of SIFT features in the form of oriented ellipses as opposed to original SIFT which estimates oriented disks")
    max_num_orientations: bpy.props.IntProperty(name="Max Orientations", default=2, description="Maximum number of orientations per keypoint if not estimate_affine_shape")
    upright: bpy.props.BoolProperty(name="Upright", default=False, description="Fix the orientation to 0 for upright features")
    darkness_adaptivity: bpy.props.BoolProperty(name="Darkness Adaptivity", default=False, description="Whether to adapt the feature detection depending on the image darkness. only available on GPU")
    domain_size_pooling: bpy.props.BoolProperty(name="Domain Size Pooling", default=False, description="“Domain-Size Pooling in Local Descriptors and NetworkArchitectures”, J. Dong and S. Soatto, CVPR 2015")
    dsp_min_scale: bpy.props.FloatProperty(name="DSP Min Scale", default=0.16666666666666666)
    dsp_max_scale: bpy.props.FloatProperty(name="DSP Max Scale", default=3.0)
    dsp_num_scales: bpy.props.IntProperty(name="DSP Scales", default=10)
    normalization: bpy.props.EnumProperty(
        name="Normalization",
        items=[
            ('L1_ROOT', 'L1 Root', 'L1-normalizes each descriptor followed by element-wise square rooting. This normalization is usually better than standard L2-normalization. See ‘Three things everyone should know to improve object retrieval’, Relja Arandjelovic and Andrew Zisserman, CVPR 2012'),
            ('L2', 'L2', 'Each vector is L2-normalized'),
        ],
        default="L1_ROOT",
        description="L1_ROOT or L2 descriptor normalization"
    )

    def build(self):
        return pycolmap.SiftExtractionOptions(
            max_num_features=self.max_num_features,
            first_octave=self.first_octave,
            num_octaves=self.num_octaves,
            octave_resolution=self.octave_resolution,
            peak_threshold=self.peak_threshold,
            edge_threshold=self.edge_threshold,
            estimate_affine_shape=self.estimate_affine_shape,
            max_num_orientations=self.max_num_orientations,
            upright=self.upright,
            darkness_adaptivity=self.darkness_adaptivity,
            domain_size_pooling=self.domain_size_pooling,
            dsp_min_scale=self.dsp_min_scale,
            dsp_max_scale=self.dsp_max_scale,
            dsp_num_scales=self.dsp_num_scales,
            normalization=self.normalization
        )

class ExtractFeaturesPropertyGroup(bpy.types.PropertyGroup):
    estimate_camera: bpy.props.BoolProperty(name="Estimate Camera", description="Allow COLMAP to estimate the camera poses", default=True)

    camera_mode: bpy.props.EnumProperty(
        name="Camera Mode",
        items=[
            ('AUTO', 'Auto', 'Automatic camera mode'),
            ('SINGLE', 'Single', 'Single camera mode'),
            ('PER_FOLDER', 'Per-Folder', 'Per-folder camera mode'),
            ('PER_IMAGE', 'Per-Image', 'Per-image camera mode'),
        ]
    )

    # SiftExtractionOptions
    sift_options: bpy.props.PointerProperty(type=SiftExtractionOptionsPropertyGroup)

    def build(self, database_path, image_path, clip):
        if not self.estimate_camera:
            camera = clip.tracking.camera
            pixel_width = camera.sensor_width / clip.size[0]
            pixel_height = pixel_width * camera.pixel_aspect

            # the value is always in mm, even if the UI shows it in px
            fx = camera.focal_length / pixel_width
            fy = camera.focal_length / pixel_height

            cx = clip.size[0] / 2 + (camera.principal_point[0] * clip.size[0] / 2)
            cy = clip.size[1] / 2 + (camera.principal_point[1] * clip.size[1] / 2)

            reader_options = pycolmap.ImageReaderOptions(
                camera_model="SIMPLE_RADIAL",
                camera_params=f"{(fx + fy) / 2.0}, {cx}, {cy}, 0.0"
            )
        else:
            reader_options = pycolmap.ImageReaderOptions()

        return {
            'database_path': database_path,
            'image_path': image_path,
            'camera_mode': pycolmap.CameraMode(self.camera_mode),
            'reader_options': reader_options,
            'sift_options': self.sift_options.build()
        }

class RansacOptionsPropertyGroup(bpy.types.PropertyGroup):
    max_error: bpy.props.FloatProperty(name="Max Error", default=4.0)
    min_inlier_ratio: bpy.props.FloatProperty(name="Min Inlier Ratio", default=0.01)
    confidence: bpy.props.FloatProperty(name="Confidence", default=0.9999)
    dyn_num_trials_multiplier: bpy.props.FloatProperty(name="Dyn Num Trials Multiplier", default=3.0)
    min_num_trials: bpy.props.IntProperty(name="Min Num Trials", default=1000)
    max_num_trials: bpy.props.IntProperty(name="Max Num Trials", default=100000)

    def build(self):
        return pycolmap.RANSACOptions(
            max_error=self.max_error,
            min_inlier_ratio=self.min_inlier_ratio,
            confidence=self.confidence,
            dyn_num_trials_multiplier=self.dyn_num_trials_multiplier,
            min_num_trials=self.min_num_trials,
            max_num_trials=self.max_num_trials
        )

class SiftMatchingOptionsPropertyGroup(bpy.types.PropertyGroup):
    use_gpu: bpy.props.BoolProperty(name="Use GPU", default=True)
    max_ratio: bpy.props.FloatProperty(name="Max Ratio", default=0.8, description="Maximum distance ratio between first and second best match")
    max_distance: bpy.props.FloatProperty(name="Max Distance", default=0.7, description="Maximum distance to best match")
    cross_check: bpy.props.BoolProperty(name="Cross Check", default=True, description="Whether to enable cross checking in matching")
    max_num_matches: bpy.props.IntProperty(name="Max Matches", default=32768, description="Maximum number of matches")
    guided_matching: bpy.props.BoolProperty(name="Guided Matching", default=False, description="Whether to perform guided matching, if geometric verification succeeds")
    cpu_brute_force_matcher: bpy.props.BoolProperty(name="CPU Brute Force Matcher", default=False, description="Whether to use brute-force instead of faiss based CPU matching")

    def build(self):
        return pycolmap.SiftMatchingOptions(
            use_gpu=self.use_gpu,
            max_ratio=self.max_ratio,
            max_distance=self.max_distance,
            cross_check=self.cross_check,
            max_num_matches=self.max_num_matches,
            guided_matching=self.guided_matching,
            cpu_brute_force_matcher=self.cpu_brute_force_matcher
        )

class TwoViewGeometryOptionsPropertyGroup(bpy.types.PropertyGroup):
    min_num_inliers: bpy.props.IntProperty(name="Min Inliers", default=15)
    min_E_F_inlier_ratio: bpy.props.FloatProperty(name="Min E/F Inlier Ratio", default=0.95)
    max_H_inlier_ratio: bpy.props.FloatProperty(name="Max H Inlier Ratio", default=0.8)
    watermark_min_inlier_ratio: bpy.props.FloatProperty(name="Watermark Min Inlier Ratio", default=0.7)
    watermark_border_size: bpy.props.FloatProperty(name="Watermark Border Size", default=0.1)
    detect_watermark: bpy.props.BoolProperty(name="Detect Watermark", default=True)
    multiple_ignore_watermark: bpy.props.BoolProperty(name="Multiple Ignore Watermark", default=True)
    force_H_use: bpy.props.BoolProperty(name="Force H Use", default=False)
    compute_relative_pose: bpy.props.BoolProperty(name="Compute Relative Pose", default=False)
    multiple_models: bpy.props.BoolProperty(name="Multiple Models", default=False)

    # RANSACOptions
    ransac: bpy.props.PointerProperty(type=RansacOptionsPropertyGroup)

    def build(self):
        return pycolmap.TwoViewGeometryOptions(
            min_num_inliers=self.min_num_inliers,
            min_E_F_inlier_ratio=self.min_E_F_inlier_ratio,
            max_H_inlier_ratio=self.max_H_inlier_ratio,
            watermark_min_inlier_ratio=self.watermark_min_inlier_ratio,
            watermark_border_size=self.watermark_border_size,
            detect_watermark=self.detect_watermark,
            multiple_ignore_watermark=self.multiple_ignore_watermark,
            force_H_use=self.force_H_use,
            compute_relative_pose=self.compute_relative_pose,
            multiple_models=self.multiple_models,
            ransac=self.ransac.build()
        )

class ExhaustiveMatchingOptionsPropertyGroup(bpy.types.PropertyGroup):
    block_size: bpy.props.IntProperty(name="Block Size", default=50)

    def build(self):
        return pycolmap.ExhaustiveMatchingOptions(
            block_size=self.block_size
        )

class SpatialMatchingOptionsPropertyGroup(bpy.types.PropertyGroup):
    ignore_z: bpy.props.BoolProperty(name="Ignore Z", default=True, description='Whether to ignore the Z-component of the location prior')
    max_num_neighbors: bpy.props.IntProperty(name="Max Neighbors", default=50, description='The maximum number of nearest neighbors to match')
    max_distance: bpy.props.FloatProperty(name="Max Distance", default=100.0, description='The maximum distance between the query and nearest neighbor [meters]')

    def build(self):
        return pycolmap.SpatialMatchingOptions(
            ignore_z=self.ignore_z,
            max_num_neighbors=self.max_num_neighbors,
            max_distance=self.max_distance,
        )

class VocabTreeMatchingOptionsPropertyGroup(bpy.types.PropertyGroup):
    num_images: bpy.props.IntProperty(name="Images", default=100, description='Number of images to retrieve for each query image')
    num_nearest_neighbors: bpy.props.IntProperty(name="Nearest Neighbors", default=5, description='Number of nearest neighbors to retrieve per query feature')
    num_checks: bpy.props.IntProperty(name="Checks", default=64, description='Number of nearest-neighbor checks to use in retrieval')
    num_images_after_verification: bpy.props.IntProperty(name="Images After Verification", default=0, description='How many images to return after spatial verification. Set to 0 to turn off spatial verification')
    max_num_features: bpy.props.IntProperty(name="Max Features", default=-1, description='The maximum number of features to use for indexing an image')
    match_list_path: bpy.props.StringProperty(name="Match List Path", default="", description='Optional path to file with specific image names to match', subtype="DIR_PATH")
    vocab_tree_path: bpy.props.StringProperty(name="Vocab Tree Path", default="https://github.com/colmap/colmap/releases/download/3.11.1/vocab_tree_faiss_flickr100K_words256K.bin", description='Path to the vocabulary tree')
    vocab_tree_name: bpy.props.StringProperty(name="Vocab Tree Name", default="vocab_tree_faiss_flickr100K_words256K.bin", description='Name of the vocabulary tree, only required if Vocab Tree Path is a URL')
    vocab_tree_hash: bpy.props.StringProperty(name="Vocab Tree Hash", default="96ca8ec8ea60b1f73465aaf2c401fd3b3ca75cdba2d3c50d6a2f6f760f275ddc", description='SHA256 hash of the vocabulary tree, only required if Vocab Tree Path is a URL')

    def build(self):
        kwargs = {
            'num_images': self.num_images,
            'num_nearest_neighbors': self.num_nearest_neighbors,
            'num_checks': self.num_checks,
            'num_images_after_verification': self.num_images_after_verification,
            'max_num_features': self.max_num_features,
            'match_list_path': self.match_list_path
        }
        if self.vocab_tree_path.strip() != "":
            if self.vocab_tree_path.startswith("http://") or self.vocab_tree_path.startswith("https://"):
                kwargs['vocab_tree_path'] = f"{self.vocab_tree_path};{self.vocab_tree_name};{self.vocab_tree_hash}"
            else:
                kwargs['vocab_tree_path'] = self.vocab_tree_path
        return pycolmap.VocabTreeMatchingOptions(**kwargs)

class SequentialMatchingOptionsPropertyGroup(bpy.types.PropertyGroup):
    overlap: bpy.props.IntProperty(name="Overlap", default=10, description="Number of overlapping image pairs")
    quadratic_overlap: bpy.props.BoolProperty(name="Quadratic Overlap", default=True, description="Whether to match images against their quadratic neighbors")
    expand_rig_images: bpy.props.BoolProperty(name="Expand Rig Images", default=True, description="Whether to match an image against all images in neighboring rig frames. If no rigs/frames are configured in the database, this option is ignored")
    
    loop_detection: bpy.props.BoolProperty(name="Loop Detection", default=False, description="Loop detection is invoked every loop_detection_period images")
    loop_detection_period: bpy.props.IntProperty(name="Loop Detection Period", default=10, description="The number of images to retrieve in loop detection. This number should be significantly bigger than the sequential matching overlap")
    loop_detection_num_images: bpy.props.IntProperty(name="Loop Detection Images", default=50, description="The number of images to retrieve in loop detection. This number should be significantly bigger than the sequential matching overlap")
    loop_detection_num_nearest_neighbors: bpy.props.IntProperty(name="Loop Detection Nearest Neighbors", default=1, description="Number of nearest neighbors to retrieve per query feature")
    loop_detection_num_checks: bpy.props.IntProperty(name="Loop Detection Checks", default=64, description="Number of nearest-neighbor checks to use in retrieval")
    loop_detection_num_images_after_verification: bpy.props.IntProperty(name="Loop Detection Images After Verification", default=0, description="How many images to return after spatial verification. Set to 0 to turn off spatial verification")
    loop_detection_max_num_features: bpy.props.IntProperty(name="Loop Detection Max Features", default=-1, description="The maximum number of features to use for indexing an image. If an image has more features, only the largest-scale features will be indexed")
    
    vocab_tree_path: bpy.props.StringProperty(name="Vocab Tree Path", default="https://github.com/colmap/colmap/releases/download/3.11.1/vocab_tree_faiss_flickr100K_words256K.bin", description='Path to the vocabulary tree')
    vocab_tree_name: bpy.props.StringProperty(name="Vocab Tree Name", default="vocab_tree_faiss_flickr100K_words256K.bin", description='Name of the vocabulary tree')
    vocab_tree_hash: bpy.props.StringProperty(name="Vocab Tree Hash", default="96ca8ec8ea60b1f73465aaf2c401fd3b3ca75cdba2d3c50d6a2f6f760f275ddc", description='SHA256 hash of the vocabulary tree')

    def build(self):
        kwargs = {
            'overlap': self.overlap,
            'quadratic_overlap': self.quadratic_overlap,
            'expand_rig_images': self.expand_rig_images,
            'loop_detection': self.loop_detection,
            'loop_detection_period': self.loop_detection_period,
            'loop_detection_num_images': self.loop_detection_num_images,
            'loop_detection_num_nearest_neighbors': self.loop_detection_num_nearest_neighbors,
            'loop_detection_num_checks': self.loop_detection_num_checks,
            'loop_detection_num_images_after_verification': self.loop_detection_num_images_after_verification,
            'loop_detection_max_num_features': self.loop_detection_max_num_features
        }
        if self.vocab_tree_path.strip() != "":
            if self.vocab_tree_path.startswith("http://") or self.vocab_tree_path.startswith("https://"):
                kwargs['vocab_tree_path'] = f"{self.vocab_tree_path};{self.vocab_tree_name};{self.vocab_tree_hash}"
            else:
                kwargs['vocab_tree_path'] = self.vocab_tree_path
        return pycolmap.SequentialMatchingOptions(**kwargs)

class MatchFeaturesPropertyGroup(bpy.types.PropertyGroup):
    matcher: bpy.props.EnumProperty(
        name="Matcher",
        items=[
            ('EXHAUSTIVE', 'Exhaustive', 'Exhaustive feature matching'),
            ('SPATIAL', 'Spatial', 'Spatial feature matching'),
            ('VOCABTREE', 'Vocab Tree', 'Vocab tree feature matching'),
            ('SEQUENTIAL', 'Sequential', 'Sequential feature matching'),
        ]
    )

    # ExhaustiveMatchingOptions
    exhaustive: bpy.props.PointerProperty(type=ExhaustiveMatchingOptionsPropertyGroup)

    # SpatialMatchingOptions
    spatial: bpy.props.PointerProperty(type=SpatialMatchingOptionsPropertyGroup)

    # VocabTreeMatchingOptions
    vocab_tree: bpy.props.PointerProperty(type=VocabTreeMatchingOptionsPropertyGroup)

    # SequentialMatchingOptions
    sequential: bpy.props.PointerProperty(type=SequentialMatchingOptionsPropertyGroup)

    # SiftMatchingOptions
    sift_options: bpy.props.PointerProperty(type=SiftMatchingOptionsPropertyGroup)

    # TwoViewGeometryOptions
    verification_options: bpy.props.PointerProperty(type=TwoViewGeometryOptionsPropertyGroup)

    def matching_options(self):
        match self.matcher:
            case 'EXHAUSTIVE':
                return self.exhaustive.build()
            case 'SPATIAL':
                return self.spatial.build()
            case 'VOCABTREE':
                return self.vocab_tree.build()
            case 'SEQUENTIAL':
                return self.sequential.build()

    def build(self, database_path):
        return self.matcher, {
            'database_path': database_path,
            'sift_options': self.sift_options.build(),
            'matching_options': self.matching_options(),
            'verification_options': self.verification_options.build()
        }

class IncrementalBundleAdjustmentPropertyGroup(bpy.types.PropertyGroup):
    refine_focal_length: bpy.props.BoolProperty(name="Refine Focal Length", description="Whether to refine the focal length during the reconstruction.", default=True)
    refine_principal_point: bpy.props.BoolProperty(name="Refine Principal Point", description="Whether to refine the principal point during the reconstruction.", default=False)
    refine_extra_params: bpy.props.BoolProperty(name="Refine Extra Params", description="Whether to refine extra parameters during the reconstruction.", default=True)
    refine_sensor_from_rig: bpy.props.BoolProperty(name="Refine Sensor From Rig", description="Whether to refine rig poses during the reconstruction.", default=True)
    min_num_residuals_for_cpu_multi_threading: bpy.props.IntProperty(name="Min Residuals For CPU Multi Threading", description="The minimum number of residuals per bundle adjustment problem to enable multi-threading solving of the problems.", default=50000)
    local_num_images: bpy.props.IntProperty(name="Local Images", description="The number of images to optimize in local bundle adjustment.", default=6)
    local_function_tolerance: bpy.props.FloatProperty(name="Local Function Tolerance", description="Ceres solver function tolerance for local bundle adjustment.", default=0.0)
    local_max_num_iterations: bpy.props.IntProperty(name="Local Max Iterations", description="The maximum number of local bundle adjustment iterations.", default=25)
    global_frames_ratio: bpy.props.FloatProperty(name="Global Frames Ratio", description="The growth rates after which to perform global bundle adjustment.", default=1.1)
    global_points_ratio: bpy.props.FloatProperty(name="Global Points Ratio", description="The growth rates after which to perform global bundle adjustment.", default=1.1)
    global_frames_freq: bpy.props.IntProperty(name="Global Frames Freq", description="The growth rates after which to perform global bundle adjustment.", default=500)
    global_points_freq: bpy.props.IntProperty(name="Global Points Freq", description="The growth rates after which to perform global bundle adjustment.", default=250000)
    global_function_tolerance: bpy.props.FloatProperty(name="Global Function Tolerance", description="Ceres solver function tolerance for global bundle adjustment.", default=0.0)
    global_max_num_iterations: bpy.props.IntProperty(name="Global Max Iterations", description="The maximum number of global bundle adjustment iterations.", default=50)
    local_max_refinements: bpy.props.IntProperty(name="Local Max Refinements", description="The thresholds for iterative bundle adjustment refinements.", default=2)
    local_max_refinement_change: bpy.props.FloatProperty(name="Local Max Refinement Change", description="The thresholds for iterative bundle adjustment refinements.", default=0.001)
    global_max_refinements: bpy.props.IntProperty(name="Global Max Refinements", description="The thresholds for iterative bundle adjustment refinements.", default=5)
    global_max_refinement_change: bpy.props.FloatProperty(name="Global Max Refinement Change", description="The thresholds for iterative bundle adjustment refinements.", default=0.0005)
    use_gpu: bpy.props.BoolProperty(name="Use Gpu", description="Whether to use Ceres’ CUDA sparse linear algebra library, if available.", default=False)

class IncrementalMapperOptionsPropertyGroup(bpy.types.PropertyGroup):
    init_min_num_inliers: bpy.props.IntProperty(name="Init Min Inliers", description="Minimum number of inliers for initial image pair.", default=100)
    init_max_error: bpy.props.FloatProperty(name="Init Max Error", description="Maximum error in pixels for two-view geometry estimation for initial image pair.", default=4.0)
    init_max_forward_motion: bpy.props.FloatProperty(name="Init Max Forward Motion", description="Maximum forward motion for initial image pair.", default=0.95)
    init_min_tri_angle: bpy.props.FloatProperty(name="Init Min Tri Angle", description="Minimum triangulation angle for initial image pair.", default=16.0)
    init_max_reg_trials: bpy.props.IntProperty(name="Init Max Reg Trials", description="Maximum number of trials to use an image for initialization.", default=2)
    abs_pose_max_error: bpy.props.FloatProperty(name="Abs Pose Max Error", description="Maximum reprojection error in absolute pose estimation.", default=12.0)
    abs_pose_min_num_inliers: bpy.props.IntProperty(name="Abs Pose Min Inliers", description="Minimum number of inliers in absolute pose estimation.", default=30)
    abs_pose_min_inlier_ratio: bpy.props.FloatProperty(name="Abs Pose Min Inlier Ratio", description="Minimum inlier ratio in absolute pose estimation.", default=0.25)
    abs_pose_refine_focal_length: bpy.props.BoolProperty(name="Abs Pose Refine Focal Length", description="Whether to estimate the focal length in absolute pose estimation.", default=True)
    abs_pose_refine_extra_params: bpy.props.BoolProperty(name="Abs Pose Refine Extra Params", description="Whether to estimate the extra parameters in absolute pose estimation.", default=True)
    local_ba_num_images: bpy.props.IntProperty(name="Local Bundle Adjustment Images", description="Number of images to optimize in local bundle adjustment.", default=6)
    local_ba_min_tri_angle: bpy.props.FloatProperty(name="Local Bundle Adjustment Min Tri Angle", description="Minimum triangulation for images to be chosen in local bundle adjustment.", default=6.0)
    min_focal_length_ratio: bpy.props.FloatProperty(name="Min Focal Length Ratio", description="The threshold used to filter and ignore images with degenerate intrinsics.", default=0.1)
    max_focal_length_ratio: bpy.props.FloatProperty(name="Max Focal Length Ratio", description="The threshold used to filter and ignore images with degenerate intrinsics.", default=10.0)
    max_extra_param: bpy.props.FloatProperty(name="Max Extra Param", description="The threshold used to filter and ignore images with degenerate intrinsics.", default=1.0)
    filter_max_reproj_error: bpy.props.FloatProperty(name="Filter Max Reprojection Error", description="Maximum reprojection error in pixels for observations.", default=4.0)
    filter_min_tri_angle: bpy.props.FloatProperty(name="Filter Min Tri Angle", description="Minimum triangulation angle in degrees for stable 3D points.", default=1.5)
    max_reg_trials: bpy.props.IntProperty(name="Max Reg Trials", description="Maximum number of trials to register an image.", default=3)
    fix_existing_frames: bpy.props.BoolProperty(name="Fix Existing Frames", description="If reconstruction is provided as input, fix the existing frame poses.", default=False)
    image_selection_method: bpy.props.EnumProperty(
        name="Image Selection Method",
        description="Method to find and select next best image to register.",
        default='MIN_UNCERTAINTY',
        items=[
            ('MAX_VISIBLE_POINTS_NUM', 'Max Visible Points Num', ''),
            ('MAX_VISIBLE_POINTS_RATIO', 'Max Visible Points Ratio', ''),
            ('MIN_UNCERTAINTY', 'Min Uncertainty', ''),
        ]
    )

    def build(self):
        return pycolmap.IncrementalMapperOptions(
            init_min_num_inliers=self.init_min_num_inliers,
            init_max_error=self.init_max_error,
            init_max_forward_motion=self.init_max_forward_motion,
            init_min_tri_angle=self.init_min_tri_angle,
            init_max_reg_trials=self.init_max_reg_trials,
            abs_pose_max_error=self.abs_pose_max_error,
            abs_pose_min_num_inliers=self.abs_pose_min_num_inliers,
            abs_pose_min_inlier_ratio=self.abs_pose_min_inlier_ratio,
            abs_pose_refine_focal_length=self.abs_pose_refine_focal_length,
            abs_pose_refine_extra_params=self.abs_pose_refine_extra_params,
            local_ba_num_images=self.local_ba_num_images,
            local_ba_min_tri_angle=self.local_ba_min_tri_angle,
            min_focal_length_ratio=self.min_focal_length_ratio,
            max_focal_length_ratio=self.max_focal_length_ratio,
            max_extra_param=self.max_extra_param,
            filter_max_reproj_error=self.filter_max_reproj_error,
            filter_min_tri_angle=self.filter_min_tri_angle,
            max_reg_trials=self.max_reg_trials,
            fix_existing_frames=self.fix_existing_frames,
            image_selection_method=self.image_selection_method,
        )

class IncrementalTriangulatorOptionsPropertyGroup(bpy.types.PropertyGroup):
    max_transitivity: bpy.props.IntProperty(
        name="Max Transitivity",
        description="Maximum transitivity to search for correspondences.",
        default=1
    )
    create_max_angle_error: bpy.props.FloatProperty(
        name="Create Max Angle Error",
        description="Maximum angular error to create new triangulations.",
        default=2.0
    )
    continue_max_angle_error: bpy.props.FloatProperty(
        name="Continue Max Angle Error",
        description="Maximum angular error to continue existing triangulations.",
        default=2.0
    )
    merge_max_reproj_error: bpy.props.FloatProperty(
        name="Merge Max Reproj Error",
        description="Maximum reprojection error in pixels to merge triangulations.",
        default=4.0
    )
    complete_max_reproj_error: bpy.props.FloatProperty(
        name="Complete Max Reproj Error",
        description="Maximum reprojection error to complete an existing triangulation.",
        default=4.0
    )
    complete_max_transitivity: bpy.props.IntProperty(
        name="Complete Max Transitivity",
        description="Maximum transitivity for track completion.",
        default=5
    )
    re_max_angle_error: bpy.props.FloatProperty(
        name="Re Max Angle Error",
        description="Maximum angular error to re-triangulate under-reconstructed image pairs.",
        default=5.0
    )
    re_min_ratio: bpy.props.FloatProperty(
        name="Re Min Ratio",
        description="Minimum ratio of common triangulations between an image pair over the number of correspondences between that image pair to be considered as under-reconstructed.",
        default=0.2
    )
    re_max_trials: bpy.props.IntProperty(
        name="Re Max Trials",
        description="Maximum number of trials to re-triangulate an image pair.",
        default=1
    )
    min_angle: bpy.props.FloatProperty(
        name="Min Angle",
        description="Minimum pairwise triangulation angle for a stable triangulation.",
        default=1.5
    )
    ignore_two_view_tracks: bpy.props.BoolProperty(
        name="Ignore Two View Tracks",
        description="Whether to ignore two-view tracks.",
        default=True
    )
    min_focal_length_ratio: bpy.props.FloatProperty(
        name="Min Focal Length Ratio",
        description="The threshold used to filter and ignore images with degenerate intrinsics.",
        default=0.1
    )
    max_focal_length_ratio: bpy.props.FloatProperty(
        name="Max Focal Length Ratio",
        description="The threshold used to filter and ignore images with degenerate intrinsics.",
        default=10.0
    )
    max_extra_param: bpy.props.FloatProperty(
        name="Max Extra Param",
        description="The threshold used to filter and ignore images with degenerate intrinsics.",
        default=1.0
    )

    def build(self):
        return pycolmap.IncrementalTriangulatorOptions(
            max_transitivity=self.max_transitivity,
            create_max_angle_error=self.create_max_angle_error,
            continue_max_angle_error=self.continue_max_angle_error,
            merge_max_reproj_error=self.merge_max_reproj_error,
            complete_max_reproj_error=self.complete_max_reproj_error,
            complete_max_transitivity=self.complete_max_transitivity,
            re_max_angle_error=self.re_max_angle_error,
            re_min_ratio=self.re_min_ratio,
            re_max_trials=self.re_max_trials,
            min_angle=self.min_angle,
            ignore_two_view_tracks=self.ignore_two_view_tracks,
            min_focal_length_ratio=self.min_focal_length_ratio,
            max_focal_length_ratio=self.max_focal_length_ratio,
            max_extra_param=self.max_extra_param,
        )

class IncrementalPipelineOptionsPropertyGroup(bpy.types.PropertyGroup):
    min_num_matches: bpy.props.IntProperty(name="Min Matches", description="The minimum number of matches for inlier matches to be considered.", default=15)
    ignore_watermarks: bpy.props.BoolProperty(name="Ignore Watermarks", description="Whether to ignore the inlier matches of watermark image pairs.", default=False)
    multiple_models: bpy.props.BoolProperty(name="Multiple Models", description="Whether to reconstruct multiple sub-models.", default=True)
    max_num_models: bpy.props.IntProperty(name="Max Models", description="The number of sub-models to reconstruct.", default=50)
    max_model_overlap: bpy.props.IntProperty(name="Max Model Overlap", description="The maximum number of overlapping images between sub-models. If the current sub-models shares more than this number of images with another model, then the reconstruction is stopped.", default=20)
    min_model_size: bpy.props.IntProperty(name="Min Model Size", description="The minimum number of registered images of a sub-model, otherwise the sub-model is discarded. Note that the first sub-model is always kept independent of size.", default=10)
    init_image_id1: bpy.props.IntProperty(name="Init Image Id 1", description="The image identifier of the first image used to initialize the reconstruction.", default=-1)
    init_image_id2: bpy.props.IntProperty(name="Init Image Id 2", description="The image identifier of the second image used to initialize the reconstruction. Determined automatically if left unspecified.", default=-1)
    init_num_trials: bpy.props.IntProperty(name="Init Num Trials", description="The number of trials to initialize the reconstruction.", default=200)
    extract_colors: bpy.props.BoolProperty(name="Extract Colors", description="Whether to extract colors for reconstructed points.", default=True)
    min_focal_length_ratio: bpy.props.FloatProperty(name="Min Focal Length Ratio", description="The threshold used to filter and ignore images with degenerate intrinsics.", default=0.1)
    max_focal_length_ratio: bpy.props.FloatProperty(name="Max Focal Length Ratio", description="The threshold used to filter and ignore images with degenerate intrinsics.", default=10.0)
    max_extra_param: bpy.props.FloatProperty(name="Max Extra Param", description="The threshold used to filter and ignore images with degenerate intrinsics.", default=1.0)
    
    bundle_adjustment: bpy.props.PointerProperty(type=IncrementalBundleAdjustmentPropertyGroup)

    use_prior_position: bpy.props.BoolProperty(name="Use Prior Position", description="Whether to use priors on the camera positions.", default=False)
    use_robust_loss_on_prior_position: bpy.props.BoolProperty(name="Use Robust Loss On Prior Position", description="Whether to use a robust loss on prior camera positions.", default=False)
    prior_position_loss_scale: bpy.props.FloatProperty(name="Prior Position Loss Scale", description="Threshold on the residual for the robust position prior loss (chi2 for 3DOF at 95% = 7.815).", default=7.815)
    snapshot_path: bpy.props.StringProperty(name="Snapshot Path", description="Path to a folder in which reconstruction snapshots will be saved during incremental reconstruction", default="", subtype="DIR_PATH")
    snapshot_frames_freq: bpy.props.IntProperty(name="Snapshot Frames Freq", description="Frequency of registered images according to which reconstruction snapshots will be saved.", default=0)
    fix_existing_frames: bpy.props.BoolProperty(name="Fix Existing Frames", description="If reconstruction is provided as input, fix the existing frame poses.", default=False)
    
    mapper: bpy.props.PointerProperty(type=IncrementalMapperOptionsPropertyGroup)
    triangulation: bpy.props.PointerProperty(type=IncrementalTriangulatorOptionsPropertyGroup)

    def build(self):
        return pycolmap.IncrementalPipelineOptions(
            min_num_matches=self.min_num_matches,
            ignore_watermarks=self.ignore_watermarks,
            multiple_models=self.multiple_models,
            max_num_models=self.max_num_models,
            max_model_overlap=self.max_model_overlap,
            min_model_size=self.min_model_size,
            init_image_id1=self.init_image_id1,
            init_image_id2=self.init_image_id2,
            init_num_trials=self.init_num_trials,
            extract_colors=self.extract_colors,
            min_focal_length_ratio=self.min_focal_length_ratio,
            max_focal_length_ratio=self.max_focal_length_ratio,
            max_extra_param=self.max_extra_param,

            ba_refine_focal_length=self.bundle_adjustment.refine_focal_length,
            ba_refine_principal_point=self.bundle_adjustment.refine_principal_point,
            ba_refine_extra_params=self.bundle_adjustment.refine_extra_params,
            ba_refine_sensor_from_rig=self.bundle_adjustment.refine_sensor_from_rig,
            ba_min_num_residuals_for_cpu_multi_threading=self.bundle_adjustment.min_num_residuals_for_cpu_multi_threading,
            ba_local_num_images=self.bundle_adjustment.local_num_images,
            ba_local_function_tolerance=self.bundle_adjustment.local_function_tolerance,
            ba_local_max_num_iterations=self.bundle_adjustment.local_max_num_iterations,
            ba_global_frames_ratio=self.bundle_adjustment.global_frames_ratio,
            ba_global_points_ratio=self.bundle_adjustment.global_points_ratio,
            ba_global_frames_freq=self.bundle_adjustment.global_frames_freq,
            ba_global_points_freq=self.bundle_adjustment.global_points_freq,
            ba_global_function_tolerance=self.bundle_adjustment.global_function_tolerance,
            ba_global_max_num_iterations=self.bundle_adjustment.global_max_num_iterations,
            ba_local_max_refinements=self.bundle_adjustment.local_max_refinements,
            ba_local_max_refinement_change=self.bundle_adjustment.local_max_refinement_change,
            ba_global_max_refinements=self.bundle_adjustment.global_max_refinements,
            ba_global_max_refinement_change=self.bundle_adjustment.global_max_refinement_change,
            ba_use_gpu=self.bundle_adjustment.use_gpu,

            use_prior_position=self.use_prior_position,
            use_robust_loss_on_prior_position=self.use_robust_loss_on_prior_position,
            prior_position_loss_scale=self.prior_position_loss_scale,
            snapshot_path=self.snapshot_path,
            snapshot_frames_freq=self.snapshot_frames_freq,
            fix_existing_frames=self.fix_existing_frames,

            mapper=self.mapper.build(),
            triangulation=self.triangulation.build(),
        )

class ColmapCachedResultsPropertyGroup(bpy.types.PropertyGroup):
    num_descriptors: bpy.props.IntProperty()
    
    num_matches: bpy.props.IntProperty()
    num_inlier_matches: bpy.props.IntProperty()
    num_matched_image_pairs: bpy.props.IntProperty()
    num_verified_image_pairs: bpy.props.IntProperty()

class ColmapPropertyGroup(bpy.types.PropertyGroup):
    use_custom_directory: bpy.props.BoolProperty(name="Custom Directory")
    directory: bpy.props.StringProperty(name="Directory", subtype = 'DIR_PATH')
    
    extract_features: bpy.props.PointerProperty(type=ExtractFeaturesPropertyGroup)
    
    match_features: bpy.props.PointerProperty(type=MatchFeaturesPropertyGroup)

    incremental_pipeline: bpy.props.PointerProperty(type=IncrementalPipelineOptionsPropertyGroup)

    cached_results: bpy.props.PointerProperty(type=ColmapCachedResultsPropertyGroup)

def register():
    bpy.utils.register_class(RansacOptionsPropertyGroup)
    bpy.utils.register_class(SiftMatchingOptionsPropertyGroup)
    bpy.utils.register_class(TwoViewGeometryOptionsPropertyGroup)
    bpy.utils.register_class(ExhaustiveMatchingOptionsPropertyGroup)
    bpy.utils.register_class(SpatialMatchingOptionsPropertyGroup)
    bpy.utils.register_class(VocabTreeMatchingOptionsPropertyGroup)
    bpy.utils.register_class(SequentialMatchingOptionsPropertyGroup)
    bpy.utils.register_class(MatchFeaturesPropertyGroup)

    bpy.utils.register_class(IncrementalBundleAdjustmentPropertyGroup)
    bpy.utils.register_class(IncrementalMapperOptionsPropertyGroup)
    bpy.utils.register_class(IncrementalTriangulatorOptionsPropertyGroup)
    bpy.utils.register_class(IncrementalPipelineOptionsPropertyGroup)

    bpy.utils.register_class(SiftExtractionOptionsPropertyGroup)
    bpy.utils.register_class(ExtractFeaturesPropertyGroup)
    bpy.utils.register_class(ColmapCachedResultsPropertyGroup)
    bpy.utils.register_class(ColmapPropertyGroup)

    bpy.types.MovieClip.colmap = bpy.props.PointerProperty(type=ColmapPropertyGroup)

def unregister():
    bpy.utils.unregister_class(RansacOptionsPropertyGroup)
    bpy.utils.unregister_class(SiftMatchingOptionsPropertyGroup)
    bpy.utils.unregister_class(TwoViewGeometryOptionsPropertyGroup)
    bpy.utils.unregister_class(ExhaustiveMatchingOptionsPropertyGroup)
    bpy.utils.unregister_class(SpatialMatchingOptionsPropertyGroup)
    bpy.utils.unregister_class(VocabTreeMatchingOptionsPropertyGroup)
    bpy.utils.unregister_class(SequentialMatchingOptionsPropertyGroup)
    bpy.utils.unregister_class(MatchFeaturesPropertyGroup)

    bpy.utils.unregister_class(IncrementalBundleAdjustmentPropertyGroup)
    bpy.utils.unregister_class(IncrementalMapperOptionsPropertyGroup)
    bpy.utils.unregister_class(IncrementalTriangulatorOptionsPropertyGroup)
    bpy.utils.unregister_class(IncrementalPipelineOptionsPropertyGroup)

    bpy.utils.unregister_class(SiftExtractionOptionsPropertyGroup)
    bpy.utils.unregister_class(ExtractFeaturesPropertyGroup)
    bpy.utils.unregister_class(ColmapCachedResultsPropertyGroup)
    bpy.utils.unregister_class(ColmapPropertyGroup)