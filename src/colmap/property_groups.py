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

    def build(self, database_path, image_path):
        return {
            'database_path': database_path,
            'image_path': image_path,
            'camera_mode': pycolmap.CameraMode(self.camera_mode),
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
    vocab_tree_path: bpy.props.StringProperty(name="Vocab Tree Path", default="https://github.com/colmap/colmap/releases/download/3.11.1/vocab_tree_faiss_flickr100K_words256K.bin;vocab_tree_faiss_flickr100K_words256K.bin;96ca8ec8ea60b1f73465aaf2c401fd3b3ca75cdba2d3c50d6a2f6f760f275ddc", description='Path to the vocabulary tree')
    match_list_path: bpy.props.StringProperty(name="Match List Path", default="", description='Optional path to file with specific image names to match')

    def build(self):
        return pycolmap.VocabTreeMatchingOptions(
            num_images=self.num_images,
            num_nearest_neighbors=self.num_nearest_neighbors,
            num_checks=self.num_checks,
            num_images_after_verification=self.num_images_after_verification,
            max_num_features=self.max_num_features,
            vocab_tree_path=self.vocab_tree_path,
            match_list_path=self.match_list_path
        )

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
    
    vocab_tree_path: bpy.props.StringProperty(name="Vocab Tree Path", default="https://github.com/colmap/colmap/releases/download/3.11.1/vocab_tree_faiss_flickr100K_words256K.bin;vocab_tree_faiss_flickr100K_words256K.bin;96ca8ec8ea60b1f73465aaf2c401fd3b3ca75cdba2d3c50d6a2f6f760f275ddc", description="Path to the vocabulary tree")

    def build(self):
        return pycolmap.SequentialMatchingOptions(
            overlap=self.overlap,
            quadratic_overlap=self.quadratic_overlap,
            expand_rig_images=self.expand_rig_images,
            loop_detection=self.loop_detection,
            loop_detection_period=self.loop_detection_period,
            loop_detection_num_images=self.loop_detection_num_images,
            loop_detection_num_nearest_neighbors=self.loop_detection_num_nearest_neighbors,
            loop_detection_num_checks=self.loop_detection_num_checks,
            loop_detection_num_images_after_verification=self.loop_detection_num_images_after_verification,
            loop_detection_max_num_features=self.loop_detection_max_num_features,
            vocab_tree_path=self.vocab_tree_path
        )

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

    bpy.utils.unregister_class(SiftExtractionOptionsPropertyGroup)
    bpy.utils.unregister_class(ExtractFeaturesPropertyGroup)
    bpy.utils.unregister_class(ColmapCachedResultsPropertyGroup)
    bpy.utils.unregister_class(ColmapPropertyGroup)