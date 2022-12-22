##
import pyvista as pv
from MeshEditor.MeshEditor import BatchMeshEditor
import os
# get path to the current file
WD,_ = os.path.split(__file__)
print(WD)
##
# where are the meshes you want to proces
srcPath = os.path.join(WD,'DemoData','DemoMeshSource')
# landmarking demo
dstPath = os.path.join(WD,'DemoData','DemoLandmarkDestination')
BME = BatchMeshEditor()
BME.SourcePath = srcPath
BME.DestinationPath = dstPath
BME.InputFileTypes = '.obj'
BME.Mode = 'landmark'
BME.Overwrite = True  # if false will only process meshes without an output already in the destination
BME.PreLoadObjs = False  # optionally all files will be loaded prior to landmarking or cleaning during the call to prepare files
BME.PreserveSubFolders = False
BME.prepareFiles() # find files to process
BME.processFiles()

# batch clean files
dstPath = dstPath = os.path.join(WD,'DemoData','DemoMeshDestination')
BME = BatchMeshEditor()
BME.SourcePath = srcPath
BME.DestinationPath = dstPath
BME.InputFileTypes = '.obj'
BME.Mode = 'edit'
BME.Overwrite = True  # if false will only process meshes without an output already in the destination
BME.PreLoadObjs = False  # optionally all files will be loaded prior to landmarking or cleaning during the call to prepare files
BME.prepareFiles() # find files to process
BME.processFiles()