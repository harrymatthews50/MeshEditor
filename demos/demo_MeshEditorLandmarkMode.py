##
# Mesh Editor Demo, designed to be used using 'cell mode' plug in in PyCharm'
import pyvista as pv
import sys

# add path to MeshEditor.py
sys.path.append('/usr/local/micapollo01/MIC/DATA/STAFF/hmatth5/tmp/MeshEditor/')
from MeshEditor import MeshEditor, BatchMeshEditor

# load a mesh
obj = pv.read('/usr/local/micapollo01/MIC/DATA/STAFF/hmatth5/tmp/MeshEditor/demos/DemoData/DemoMeshSource/demoFace1.obj')

# create and set up Mesh Editor object
saveFileName ='/usr/local/micapollo01/MIC/DATA/STAFF/hmatth5/tmp/MeshEditor/demos/DemoData/DemoLandmarkDestination/demoFace1.txt' # what and where to save the output file
ME = MeshEditor(obj,'landmark',saveFileName=saveFileName)


