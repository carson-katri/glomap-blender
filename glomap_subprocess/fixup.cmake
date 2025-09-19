include(BundleUtilities)

set(bundle_path "${BUNDLE_PATH}")
fixup_bundle(
    "${bundle_path}"
    ""
    "${EXTRA_SEARCH_DIRS}"
)