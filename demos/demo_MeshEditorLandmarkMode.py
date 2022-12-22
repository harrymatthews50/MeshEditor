##
import pyvista as pv
from MeshEditor.MeshEditor import MeshEditor
import os
# get path to the current file
WD,_ = os.path.split(__file__)
print(WD)

# load a mesh
obj = pv.read(os.path.join(WD,'DemoData','DemoMeshSource','demoFace1.obj'))
obj.clean(inplace=True)
# create and set up Mesh Editor object
saveFileName =os.path.join(WD,'DemoData','DemoMeshDestination','demoFace1.obj') # what and where to save the output file
ME = MeshEditor(obj,'landmark',saveFileName=saveFileName)


