# Mesh Editor
A tool for editing and landmarking meshes written using pyvista.
## Note
Due to a longstanding bug in vtk (https://github.com/pyvista/pyvista/issues/1033) that stops closing of pyvista plotters this will not work on mac. It has been tested on Linux 
## Dependencies
- Python 3.10
- pyvista 0.37 and its dependencies
## Installation
After installing the dependencies the MeshEditor module can be imported within a script after calls to
```
import sys
sys.path.append('/path/to/mesh/editor') # path to the location of the Mesheditor repo on your computer
```
## Overview
### MeshEditor module
The MeshEditor module implements two classes:
- MeshEditor enables vertex selection, deletion and basic landmarking as well as saving the resulting mesh or landmark coordinates. Essentially it adds a bunch of callbacks in response to key and mouse events to a pyvista plotter. 
- BatchMeshEditor enables batch processing of multiple files loading files from a source directory and outputting them into a destination directory.
### Demos
Check the demos folder for:
- demo_MeshEditorEditMode.py which runs the MeshEditor in 'edit' mode (see below for explanation of the controls)
- demo_MeshEditorLandmarkMode.py which runs the MeshEditor in 'landmark mode' (see below for explanation of the controls)
- demo_BatchMesheditor.py which runs the BatchMeshEditor to process multiple scans in sequence
To run them make sure you modify the call to sys.path.append at the beginning of the script (see installation above)
## Using the Mesh Editor
The different modes are 'edit' and 'landmark' and are specified by the second positional argument to the MeshEditor constructor
### MeshEditor controls - 'edit' mode
- Toggle between 'selection' and 'interaction' modes' by pressing 's'
    - In interaction mode mouse clicking and tracking modify the camera prespective
    - In selection mode brushing and vertex selection is controlled by mouse clicks
- Select or deselect vertices using the brush
    - Right or left clicking toggles between modifying the selection and not modifying the selection (this is indicated visually by a chnage in the background color)
    - Right clicking makes the brush deselect vertices
    - Left clicking makes the brush select vertices
    - Pressing keys '1' and '2' decrease and increase the radius of the brush respectively
- Pressing 'i' inverts the selection
- 'Delete' deletes the selection
- 'f' deletes the inverse of the selection
- 'Enter/Return exports the mesh to .obj (if saveFileName='filename' was specified in the call to the constructor). the background turns black when saving is complete. The plotter can then be safely closed
#### Experimental (buggy) features
- The capacity to view the brush as a highlighted region on the surface that tracks with changes to the cursor position is enabled. This is buggy when toggling between selection and interaction mode. You may not be able to see the brush after re-enabling camera interaction. I am hoping for a solution (https://github.com/pyvista/pyvista/issues/3647). This can also slow things down for dense meshes and can be disabled by setting showSelectionPreview=False in the call to the MeshEditor constructor.
- Double left click tries a 'paint bucket' selection of all vertices connected to the one that is clicked. This doesn't really work as expected. The issue seems to be that the connectivity method of pyvista.PolyData (on which this depends) does not label the connected components correctly. This might be fixed in future.
- If you try to brush too fast the viewer can crash because it cannot keep up with tracking the mouse (I assume). Just brush at a sensible speed and everything should be fine. You may also get a recursion error triggered while brushing fast. It doesn't interfere with the actual brushing.
### MeshEditor controls - 'landmark' mode
- Toggle between 'selection' and 'interaction' modes' by pressing 's'
    - in interaction mode mouse clicking and tracking modify the camera prespective
    - in selection mode left clicking puts a landmark in the position of the click
- Left clicking puts a landmark in the location
- 'Delete' removes the landmark that was placed last
- 'Return/Enter' exports the landmarks in the order they were specified to a comma delimeted text file if  (if saveFileName='filename' was specified in the call to the constructor)
## Using the BatchMeshEditor
Various attributes of the BatchMeshEditor object need to be set inside of the script:
- 'SourcePath' the path where the meshes are. All subfolders of this path will be searched
- 'DestinationPath' the path where the output is to be placed
- 'InputFileType' file extension with leading '.' (e.g. '.obj') of the file type in the SourcePath. This can be any type supported by pyvista.read https://docs.pyvista.org/api/utilities/_autosummary/pyvista.read.html
- 'PreserveSubFolders' if True then the subfolder structure of SourcePath and DestinationPath will be preserved. Otherwise all files found in the SourcePath will be written to the first level of the DestinationPath
- 'Overwrite' if False only the files in the SourcePath without a match in the DestinationPath will be processed
- 'PreLoadObjs' if True all files will be loaded prior to processing, otheriwse they will be loaded on the fly
- 'Mode'corresponds to 'mode' of the MeshEditor and controls whetehr to landmark or edit the scans
- 'ShowSelectionPreview' corresponds to the 'showSelectionPreview' setting of the MeshEditor

Two methods of the Batch Mesheditor need to be run in sequence 'prepareFiles' (finds the files and preloads them if necessary) 'processFiles' strats the process of iterating through the files. For each file:
1. The MeshEditor will open
2. You edit or landmark the scan as needed
3. You press return to save the results. The background of the editor will go black if the file has been saved.
4. Close the editor and the next file will open.
# MIRC-specific instructions
This was deveoped as an in house tool for the Laboratory of Imaging Genetics at KU Leuven. The following instructions are mostly relevant to those working on the MIRC infrastructure. 

## Working in PyCharm with conda
The relevant conda environment (MeshEditing) is installed on micbb01 at the time of writing. The simplest way is to run the (e.g demo) scripts is to 
1. Modify the scripts to process the meshes that you want to process (pay attention to the call to sys.path.append - see 'installation' above)
2. In the terminal run:
```
conda activate MeshEditing
python 'scriptName.py' # change to the full or relative path to the script you are trying to run
```
Those who are more used to MATLAB might prefer work in an interactive IDE. With PyCharm it is very easy to set python interpreters per project and will give you excellent debugging features so I recommend that. You will first need to make a new pycharm project configured with the correct python interpreter. This interpreter only needs to correspond to a conda environment in which the relevant dependencies are installed and could be 'MeshEditing' or one you create yourself. To create a new project correctly configured. It is easiest if you first activate the conda environment and then start pycharm:
1. Start pycharm by typing in ther terminal
 ``` 
 conda activate MeshEditing
 pycharm
 ```

2. File>NewProject
    - Set the 'location' to where you want to keep your scripts
    - Check the 'PythonInterpreter' is 'Python 3.10 (MeshEditing)' # or whatever you are expecting it to be :p
    - Uncheck 'Create a main.py welcome script'
    - Click Create
 
 Within this open project you can open (File>Open), edit and run scripts using the configured python interpreter.
 For anybody missing MATLAB's 'cell mode' ... there is a plugin for that: 
 1. File>Settings>Plugins 
 2. Search for 'pycharm cell mode' and install
You can then make 'cells' in python scripts between double '##'
Having created this project you can open it again at any point (File>Open) and run and edit scripts according to the required Python interpreter. 
## Integration with MATLAB BatchMapper
-   If you are also working with the inhouse BatchMapper tool in MATLAB. Do not run the cleaning and pose landmarking methods of the BatchMapper (as these are replaced by this tool)
- When using the BatchMeshEditor you can set the 'HomeDirectory' to the corresponding HomeDirectory of the BatchMapper. This will set the source and destination paths of the BatchMeshEditor correctly to write into the paths expected by the BatchMapper for running the registration
- Prior to running 'step4MapShape' with the BatchMapper set its 'PoseAndCleanSoftware' attribute to 'PythonMeshEditor'. This will make sure it looks for '.obj' and '.txt' landmark files and these in the correct directories.




