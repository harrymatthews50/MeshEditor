##

import pyvista as pv
import sys

# add path to MeshEditor.py
sys.path.append('/usr/local/micapollo01/MIC/DATA/STAFF/hmatth5/tmp/MeshEditor/MeshEditor')
from MeshEditor import MeshEditor


# load a mesh
obj = pv.read('/usr/local/micapollo01/MIC/DATA/STAFF/hmatth5/tmp/MeshEditor/MeshEditor/demos/DemoData/DemoMeshSource/demoFace1.obj')
obj.clean(inplace=True)
# create and set up Mesh Editor object
saveFileName ='/usr/local/micapollo01/MIC/DATA/STAFF/hmatth5/tmp/MeshEditor/MeshEditor/demos/DemoData/DemoMeshDestination/demoFace1.obj' # what and where to save the output file
ME = MeshEditor(obj,'edit',showSelectionPreview=True,saveFileName=saveFileName)


