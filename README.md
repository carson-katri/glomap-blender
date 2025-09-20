# COLMAP + GLOMAP Motion Tracking

Blender extension for [COLMAP](https://github.com/colmap/colmap) and [GLOMAP](https://github.com/colmap/glomap).

## Installation

Just drag and drop the add-on ZIP file into Blender.

## Usage

Find COLMAP and GLOMAP in the *Movie Clip Editor* in *Tracking* mode next to Blender's built-in tracker.

There are 3 steps to track a scene.

1. Open a video clip. You can *Set Scene Frames* and *Prefetch Frames* as normal in the *Movie Clip Editor*.
2. In the *Track* tab, under the *COLMAP Feature Extraction* panel, click *Extract Features*.
3. In the *COLMAP Feature Matching* panel, click *Match Features*.
4. In the *Solve* tab, under the *GLOMAP Solver* panel, click *Solve Camera Motion*.
5. In the *GLOMAP Solver* panel, click *Setup Tracking Scene*.

Each step may take a few minutes to complete, depending on the chosen settings.
You should have a point cloud mesh and animated camera added to your scene.