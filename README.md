# MeshEditor
A tool for editing and landmarking 3D meshes, written using pyvista.
## Note
Due to a longstanding bug in vtk (https://github.com/pyvista/pyvista/issues/1033) that stops closing of pyvista plotters, this will not work on Mac. It has been tested on Linux 
## Dependencies
- Python 3.10
- pyvista 0.37 and its dependencies
- scipy 1.9.3
## Installation
### Creating the conda environment from scratch
1. Install anaconda or miniconda (https://docs.anaconda.com/anaconda/install/index.html)
2. Create a new conda environment with python 3.10. In your anaconda prompt (Windows) or computer terminal (Mac/Linux)
```
conda create --name MeshEditing python=3.10
```
3. Install MeshEditor by typing in the terminal/Anaconda prompt
```
conda activate MeshEditing
pip install MeshEditor
pip install pyvista
pip install scipy
```
Try to run a demo script

```
conda activate MeshEditing
python path/to/demo/script.py
```
## Overview
### MeshEditor module
The MeshEditor module implements two classes:
- MeshEditor enables vertex selection, deletion and basic landmarking of a 3D mesh. It allows saving the resulting mesh or landmark coordinates. Essentially it adds a bunch of callbacks in response to key and mouse events to a pyvista plotter. 
- BatchMeshEditor enables batch processing of multiple files. Handkes loading files from a source directory and outputting them into a destination directory after editing or landmarking.
### Demos
Check the demos folder for:
- demo_MeshEditorEditMode.py which runs the MeshEditor in 'edit' mode (see below for explanation of the controls)
- demo_MeshEditorLandmarkMode.py which runs the MeshEditor in 'landmark' mode (see below for explanation of the controls)
- demo_BatchMeshEditor.py which runs the BatchMeshEditor to process multiple scans in sequence.

To run the demos make sure you modify the call to sys.path.append at the beginning of the script (see installation above)
## Using the Mesh Editor
The different modes are 'edit' and 'landmark' and are specified by the second positional argument to the MeshEditor constructor
### MeshEditor controls - 'edit' mode
- Toggle between 'selection' and 'interaction' modes' by pressing 't'
    - In interaction mode mouse clicking and tracking modify the camera prespective
    - In selection mode brushing and vertex selection is controlled by mouse clicks
#### Brush Selection
- Select or deselect vertices using the brush
    - Right or left clicking toggles between modifying the selection and not modifying the selection (this is indicated visually by a change in the background color)
    - Right clicking makes the brush deselect vertices
    - Left clicking makes the brush select vertices
    - Pressing keys '1' and '2' decrease and increase the radius of the brush respectively
    - Vertices within the brush radius are colored cyan
    - Selected vertices are colored red
    - Unselected vertices are colored grey
#### Geodesic Selection
Geodesic selection selects vertices within a given geodesic distance of the picked point
- to enter geodesic selection mode type 'g'
- this will highlight in forest green all vertices connected to the location of the mouse cursor
- the radius of the geodesic selection can be adjusted using 1 and 2 as for the brush selection
- left clicking adds the highlighted vertices to the selection and returns to brushing mode
- right clicking returns to brushing mode without modifying the selection
#### Other controls
- Pressing 'i' inverts the selection
- 'Delete' deletes the selection
- 'f' deletes the inverse of the selection
- 'z' is an 'Undo' function. It will reverse the last deletion that was done. It can be pressed multiple times to undo a series of deletions.
- 'a' exports the mesh to .obj (if saveFileName='filename' was specified in the call to the MeshEditor constructor). the background turns black when saving is complete. The plotter can then be safely closed
- 'q' closes the plotter
#### Experimental (buggy) features
- In both 'landmark' and 'edit' mode the program can simply crash with a C++ error. This does not seem to occur in a patterned way. 
### MeshEditor controls - 'landmark' mode
- Toggle between 'selection' and 'interaction' modes' by pressing 't'
    - in interaction mode mouse clicking and tracking modify the camera prespective
    - in selection mode left clicking puts a landmark in the position of the click
- Left clicking puts a landmark in the location
- 'Delete' removes the landmark that was placed last
- 'a' exports the landmarks in the order they were specified to a comma delimited text file if  (if saveFileName='filename' was specified in the call to the constructor)
## Using the BatchMeshEditor
Various attributes of the BatchMeshEditor object need to be set inside of the script:
- 'SourcePath' the path where the meshes are. All subfolders of this path will be searched
- 'DestinationPath' the path where the output is to be placed
- 'InputFileType' file extension with leading '.' (e.g. '.obj') of the file type in the SourcePath. This can be any type supported by pyvista.read https://docs.pyvista.org/api/utilities/_autosummary/pyvista.read.html
- 'PreserveSubFolders' if True then the subfolder structure of SourcePath and DestinationPath will be preserved. Otherwise all files found in the SourcePath will be written to the first level of the DestinationPath
- 'Overwrite' if False only the files in the SourcePath without a match in the DestinationPath will be processed - this is recommended since, if the program crashes you can simply restart where you left off
- 'PreLoadObjs' if True all files will be loaded prior to processing, otherwise they will be loaded on the fly - this is not recommended since preloading takes a long time and the program will sometimes crash mid way through you do not want to have to run the preloading again every time
- 'Mode'corresponds to 'mode' of the MeshEditor and controls whetehr to landmark or edit the scans
- 'Convert to vtk' if true this will make a copy of each input file in the cource directory saved in 'vtk' format for faster loading. This overides 'InputFileType' ... during processing the '.vtk' files will be loaded. 

Two methods of the Batch Mesheditor need to be run in sequence 'prepareFiles' (finds the files and preloads them if necessary) 'processFiles' strats the process of iterating through the files. For each file:
1. The MeshEditor will open
2. You edit or landmark the scan as needed
3. You press 'a' to save the results. The background of the editor will go black if the file has been saved.
4. Close the editor by pressing 'q' and the next file will open.

### Note
If there are multiple files with tthe same filename in the source path (e.g. in different sub folders) only one will be processed. This is regardless of whether 'PreserveSubFolders' is true or not. A warning will be printed in the terminal. I don't recommend having files with the same filename in the source directory. 

# MIRC-specific instructions
This was deveoped as an in house tool for the Laboratory of Imaging Genetics at KU Leuven. The following instructions are mostly relevant to those working on the MIRC infrastructure. 

## Working in PyCharm with conda
The relevant conda environment (MeshEditingMicsd01) is installed on micsd01 at the time of writing. Or you can create your own with the required dependencies. Contact Dominique or the MIRC Wiki for up-to-date instructions for how to create your own conda environmnet.

The simplest way to run the (e.g demo) scripts is to 
1. Modify the scripts to process the meshes that you want to process (pay attention to the call to sys.path.append - see 'installation' above)
2. In the terminal run:
```
conda activate MeshEditingMicsd01
python scriptName.py # change to the full or relative path to the script you are trying to run
```
Those who are more used to MATLAB might prefer work in an interactive IDE. With PyCharm it is very easy to set python interpreters per project and will give you excellent debugging features so I recommend that. You will first need to make a new pycharm project configured with the correct python interpreter. This interpreter only needs to correspond to a conda environment in which the relevant dependencies are installed and could be 'MeshEditing' or one you create yourself. To create a new project correctly configured. It is easiest if you first activate the conda environment and then start pycharm:
1. Start pycharm by typing in ther terminal
 ``` 
 conda activate MeshEditingMicsd01
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




