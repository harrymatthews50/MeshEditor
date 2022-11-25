##
import pyvista as pv
import sys
# add path to MeshEditor.py
sys.path.append('/usr/local/micapollo01/MIC/DATA/STAFF/hmatth5/tmp/MeshEditor/')
from MeshEditor import BatchMeshEditor
##
# where are the meshes you want to proces
srcPath = '/usr/local/micapollo01/MIC/DATA/STAFF/hmatth5/tmp/MeshEditor/demos/DemoData/DemoMeshSource'
# landmarking demo
dstPath = '/usr/local/micapollo01/MIC/DATA/STAFF/hmatth5/tmp/MeshEditor/demos/DemoData/DemoLandmarkDestination'
BME = BatchMeshEditor()
BME.SourcePath = srcPath
BME.DestinationPath = dstPath
BME.InputFileTypes = '.obj'
BME.Mode = 'landmark'
BME.Overwrite = True  # if false will only process meshes without an output already in the destination
BME.PreLoadObjs = False  # optionally all files will be loaded prior to landmarking or cleaning during the call to prepare files
BME.ShowSelectionPreview = True; # controls the showSelectionPreview argument that will be passed to the MeshEditor constructor
BME.PreserveSubFolders = False
BME.prepareFiles() # find files to process
BME.processFiles()

# batch clean files
dstPath = '/usr/local/micapollo01/MIC/DATA/STAFF/hmatth5/tmp/MeshEditor/demos/DemoData/DemoMeshDestination'
BME = BatchMeshEditor()
BME.SourcePath = srcPath
BME.DestinationPath = dstPath
BME.InputFileTypes = '.obj'
BME.Mode = 'edit'
BME.Overwrite = True  # if false will only process meshes without an output already in the destination
BME.PreLoadObjs = False  # optionally all files will be loaded prior to landmarking or cleaning during the call to prepare files
BME.ShowSelectionPreview = True; # controls the showSelectionPreview argument that will be passed to the MeshEditor constructor
BME.prepareFiles() # find files to process
BME.processFiles()