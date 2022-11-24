# Mesh Editor
A tool for editing and landmarking meshes written using pyvista.
## Note
Due to a longstanding bug in vtk (https://github.com/pyvista/pyvista/issues/1033) that stops closing of pyvista plotters this will not work on mac. It has been tested on Linux 
## Dependencies
- Python 3.10
- pyvista 0.37 and its dependencies
- joblib 1.2 and its dependenciew
## Overview
The MeshEditor module implements two classes:
- MeshEditor enables vertex selection, deletion and basic landmarking as well as saving the resulting mesh and landmark coordinates. This was done simply by ading a bunch of callbacks to keyboard and mouse events to a pyvista Plotter
- BatchMeshEditor enables batch processing of multiple files loading files from a source directory and outputting them into a destination directory.
## Using the Mesh Editor
There is a demonstration of this in demo.py
### MeshEditor controls - 'edit' mode
- Toggle between 'selection' and 'interaction' modes' by pressing 's'
    - in interaction mode mouse click modify the camera prespective
    - in selection mode brushimng and vertex selection is controlled by mouse clicks.
- Select or deselect vertices using the brush
    - Right or left clicking toggles between modifying the selection and not modifying the selection (this is indicated visulaly by a chnage in the background color)
    - Right clicking makes the brush deselect vertices
    - Left clicking makes the brush select vertices
    - 1 and 2 decrease/increase the radius of the brush
- Pressing 'i' inverts the selection
- 'Delete' deletes the selection
- 'f' deletes the inverse of the selection
- 'Enter/Return exports the mesh to .obj (if saveFileName was specified in the call to the constructor)
#### Experimental (read buggy) features



