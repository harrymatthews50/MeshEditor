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
There are demos opf this in the dmeo folder. The different modes are 'edit' and 'landmark' and are specified by the second positional argument to the MeshEditor constructor
### MeshEditor controls - 'edit' mode
- Toggle between 'selection' and 'interaction' modes' by pressing 's'
    - in interaction mode mouse click modify the camera prespective
    - in selection mode brushimng and vertex selection is controlled by mouse clicks
- Select or deselect vertices using the brush
    - Right or left clicking toggles between modifying the selection and not modifying the selection (this is indicated visulaly by a chnage in the background color)
    - Right clicking makes the brush deselect vertices
    - Left clicking makes the brush select vertices
    - 1 and 2 decrease/increase the radius of the brush
- Pressing 'i' inverts the selection
- 'Delete' deletes the selection
- 'f' deletes the inverse of the selection
- 'Enter/Return exports the mesh to .obj (if saveFileName='filename' was specified in the call to the constructor)
#### Experimental (buggy) features
- the capacity to view the brush as a highlighted region on the surface that tracks with changes to the cursor position is enabled. This is buggy when toggling between selection and interaction mode. I am hoping for a solution (https://stackoverflow.com/questions/74558545/enabling-disabling-renderer-multiple-times-changes-appearance-of-second-actor-in). This can also slow things down for dense meshes and can be disabled by setting showSelectionPreview=False in the call to the MeshEditor constructor.
- double left click tries a 'paint bucket' selection of all vertices connected to the one that is clicked. This doesn;t really work as expected. The issue seems to be that the connectivity method of pyvista.PolyData does not label the connected components correctly. This might be fixed in future.
### MeshEditor controls - 'landmark' mode
- Toggle between 'selection' and 'interaction' modes' by pressing 's'
    - in interaction mode mouse click modify the camera prespective
    - in selection mode left clicking puts a landmark in the position of the click
- Left clicking puts a landmark in the location
- 'Delete' removes the landmark that was placed last
- 'Return/Enter' exports the landmarks in the order they were specified to a comma delimeted text file if  (if saveFileName='filename' was specified in the call to the constructor)





