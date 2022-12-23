import os
import glob
from itertools import compress
#from collections import counter
import pyvista as pv
from copy import deepcopy
import numpy as np
import csv
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components,dijkstra


######## Define Miscellaneous helper functions

# calculates the median distance of all points from the centroid of a configuration of points
def meshRadius(verts):
    v0 = verts - np.mean(verts, axis=0)
    N = np.sqrt(np.sum(v0 ** 2, axis=1))
    return np.median(N)  #


def makeAdjacencyMatrix(polyData):
    faces = np.reshape(polyData.faces, (int(len(polyData.faces) / 4), 4))
    faces = faces[:, 1:]
    edge1 = faces[:,(0,1)]
    edge2 = faces[:,(1,2)]
    edge3 = faces[:,(0,2)]
    edges = np.concatenate((edge1,edge2,edge3),axis=0)
    edges2 = np.concatenate((edges,edges),axis=0)
    A = csr_matrix((np.ones(edges2.shape[0]).astype(int),(edges2[:,0],edges2[:,1])),shape=(polyData.n_points,polyData.n_points))
    return A

def labelConnectedComponents(polyData):
    A = makeAdjacencyMatrix(polyData)
    _,L = connected_components(A,directed=False)
    return L

def minMedEdgeLength(polyData):
    verts = polyData.points
    faces = np.reshape(polyData.faces, (int(len(polyData.faces) / 4), 4))
    faces = faces[:,1:]
    v0 = faces[:,0]
    v1 = faces[:,1]
    v2 = faces[:,2]
    e0 = verts[v0,:]-verts[v1,:]
    e1 = verts[v1,:]-verts[v2,:]
    e2 = verts[v2,:]-verts[v0,:]
    E = np.concatenate((e0,e1,e2),axis = 0)
    N = np.linalg.norm(E,axis=1)
    return np.min(N), np.median(N)
def uniqueIndexes(l):
    seen = set()
    res = []
    for i, n in enumerate(l):
        if n not in seen:
            res.append(i)
            seen.add(n)
    return res



def makeFileDict(head, subpath, fn, ext):
    # makes a dictionary representing an image and its file path - used in BatchMeshEditor
    out = dict()
    out['superPath'] = head
    out['subPath'] = subpath
    out['fileName'] = fn
    out['ext'] = ext
    out['polydata'] = None
    return out


def dictToPath(fileDict):
    # extracts path information (represented in a dictionary) and composes a full file path
    return os.path.join(fileDict['superPath'], fileDict['subPath'], fileDict['fileName'] + fileDict['ext'])


def fileExists(fileDict):
    # checks if a file, represenrted as a dictionary, exists
    return os.path.isfile(dictToPath(fileDict))

def removeLeadingPathSeparator(x):
    # removes leading path separator character from a string
    if len(x) == 0:
        return x
    sepChar = os.path.sep
    lenSep = len(sepChar)
    if x[0:lenSep] == sepChar:
        return x[lenSep:]
    else:
        return x


def findFiles(sourcePath, filetype, destination, preserveSubFolders, mode):
    # prepare initial list of input and output files
    # returns a dictionary for each file in a list

    # find files matching file type
    inList = glob.glob(os.path.join(sourcePath, '**', '*' + filetype), recursive=True)  # recursive serach for files
    if len(inList) == 0:
        return [], []
    # parse and unpack
    parts = [os.path.split(x) for x in inList]
    head, tail = list(zip(*parts))
    # remove any hidden files
    notHidden = [x[0] != '.' for x in tail]
    head = compress(head, notHidden)
    tail = compress(tail, notHidden)
    head = [item for item in head]
    tail = [item for item in tail]
    # parse tail into filename and extension
    parts = [os.path.splitext(x) for x in tail]
    fn, ext = list(zip(*parts))

    # remove any non-unique filenames
    unqInds = uniqueIndexes(fn)
    if len(unqInds) != len(fn):
        print('Duplicate file names found in source folder...will only process one')
        fn = [fn[i] for i in range(len(fn)) if i in unqInds]
        ext = [ext[i] for i in range(len(ext)) if i in unqInds]
        head = [head[i] for i in range(len(head)) if i in unqInds]
    # getsub path if any
    subPath = [removeLeadingPathSeparator(x.replace(sourcePath, '')) for x in head]
    inFiles = [makeFileDict(sourcePath, subPath[x], fn[x], ext[x]) for x in range(len(fn))]
    outFiles = createOutputFiles(inFiles, destination, preserveSubFolders, mode)
    return inFiles, outFiles


def createOutputFiles(inFiles, newPath, preserveSubFolders, mode):
    # asse,bles info about the files to output
    outFiles = [deepcopy(x) for x in inFiles]
    F = lambda x: x.update({'superPath': newPath})
    [F(x) for x in outFiles];
    if preserveSubFolders == False:  # remove path to subfolder from output files
        F = lambda x: x.update({'subPath': ''})
        [F(x) for x in outFiles]  # modify in situ
    if mode == 'landmark':  # foutput file will be text
        F = lambda x: x.update({'ext': '.txt'})
        [F(x) for x in outFiles]  # modify in situ
    elif mode == 'edit':  # output file will be obj
        F = lambda x: x.update({'ext': '.obj'})
        [F(x) for x in outFiles]  # modify in situ
    elif mode == 'converttovtk':
        F = lambda x: x.update({'ext': '.vtk'})
        [F(x) for x in outFiles]  # modify in situ
    else:
        raise ValueError('Invalid mode')

    return outFiles


def writePolyDataToObj(polyData, fn):
    # basic obj exporter for pyvista polydata since obj is not supported yet in pyvista.save
    if os.path.splitext(fn)[1] != '.obj':
        raise ValueError('Filename does not have \'.obj\' extension')
    verts = polyData.points.astype(str)
    verts = np.concatenate((np.tile('v',[verts.shape[0],1]), verts),axis=1)
    faces = np.reshape(polyData.faces, (int(len(polyData.faces) / 4), 4));
    faces = faces[:, 1:] + 1  # remove first column and add 1 to the index
    faces = np.concatenate((np.tile('f', [faces.shape[0], 1]), faces.astype(str)), axis=1)

    with open(fn, 'w') as csvfile:
            writerobj = csv.writer(csvfile, delimiter=' ')
            writerobj.writerows(np.concatenate((verts,faces),axis=0))


def writeLandmarksToText(landmarks, fn):
    with open(fn, 'w') as csvfile:
        writerobj = csv.writer(csvfile, delimiter=',')
        for i in range(len(landmarks)):
            row = [str(item) for item in landmarks[i]]
            writerobj.writerow(row)
def removeExistingFiles(inFiles,outFiles):
    notExisting = [fileExists(x) == False for x in outFiles]
    inFiles = compress(inFiles, notExisting)
    inFiles = [x for x in inFiles]
    outFiles = compress(outFiles, notExisting)
    outFiles = [x for x in outFiles]
    return inFiles, outFiles


def load3DImage(fileDict):
    fn = dictToPath(fileDict)
    try:
        print('Loading '+fn)
        shp = pv.read(fn)
        if shp.n_points==0:
            print('Mesh '+fn + 'is empty')
            raise ValueError()
        shp.clean(inplace=True)
        print('Finished Loading')
        if shp.is_all_triangles == False:
            print('Triangulating ' + fn)
            shp.triangulate(inplace=True)
            print('Finished Triangulating')
    except:
        print('Unable to load ' + fn)
        shp = None
    # add to dictionary
    fileDict.update({'polydata': shp})
    return shp, fileDict


class MeshEditor:
    @property
    def VertexRGB(self): # color of each node of the mesh in 'edit' mode
        if (self.SelectedVertices is None) | (self.VerticesInRadius is None):
            if self.mesh is None:
                return None
            else:
                NP = self.mesh.n_points
                out = np.ones([NP,3])*0.7*255
                return out.astype('uint8')
        else:
            NP = self.mesh.n_points
            out = np.ones([NP, 3]) * 0.7
            out[self.SelectedVertices.astype('bool'),:] = [1,0,0]
            if (self.VertexSelectionMode=='Brushing') | (self.VertexSelectionMode is None):
                col = [0,1,1]
            elif self.VertexSelectionMode=='Geodesic':
                col = [.1, .5, .1]
            out[self.VerticesInRadius.astype('bool'),:] = col
            out = (out*255).astype('uint8')
            return out

    @property
    def BackgroundColor(self):
        if self.mode=='edit':
            if self.vertexSelectionModeActive ==  False:
                return [0,0,1.]
            else:
                if self.VertexSelectionMode == 'Geodesic':
                    return [0,.7,.7]
                elif self.VertexSelectionMode == 'Brushing':
                    return [0,.7,.7]
                elif self.VertexSelectionMode is None:
                    return [.7,.7,.7]

        else:
            return [.7,.7,.7]



    def __init__(self, S, mode, landmark_size=4, saveFileName=None):
        # declare some proerties
        self.SelectedVertices = np.zeros([S.n_points]).astype('bool')
        self.VerticesInRadius = np.zeros([S.n_points]).astype('bool')
        self._RecordDeletions=[]
        self._MeshCopy = None








        ##### Define callbacks - all callbacks will have access to variables definied within this init function
        # such as 'P' the plotting window, 'S' the mesh being edited and 'previewMesh' a copy of S on which the selection preview is rendered


        ### Brushing related callbacks for 'edit' mode
        def toggleBrushing():
            if self.vertexSelectionModeActive:
                # enable/disable brushing
                if self.VertexSelectionMode == 'Brushing':
                    self.VertexSelectionMode = None
                else:
                    self.VertexSelectionMode = 'Brushing'

                    triggerSelectionUpdate()
                self.plotter.set_background(self.BackgroundColor)
                self.plotter.update()
        def updatePointsInRadius(*args):
            # given the current cursor position work out which points of the mesh are within the brush sphere
            if self.VertexSelectionMode == 'Geodesic':
                    D = self.geodesicDistances
            else:
                if len(args)>0:
                    pos = args[0]
                else:
                    pos = self.plotter.pick_mouse_position()
                v0 = np.array(self.mesh.points - pos)
                D = np.sqrt(np.sum(v0 ** 2, axis=1))

            self.VerticesInRadius = D < self.brushRadius


        # these next 3 callbacks are attached to left, right or left double mouse clicks so will take the position of the click as an argument
        def enableSelecting(*args):
            if self.vertexSelectionModeActive:
                self.BrushSelectionType = 'Select'
                toggleBrushing()

        def enableDeselecting(*args):
            if self.vertexSelectionModeActive:
                self.BrushSelectionType = 'Deselect'
                toggleBrushing()

        def increaseBrushRadius():
            if self.vertexSelectionModeActive:
                currR = self.brushRadius
                newR = currR + self.brushRadiusIncrement
                self.brushRadius = newR
                updateMeshVertexColors()
                updatePointsInRadius()
                updateMeshVertexColors()

        def decreaseBrushRadius():
            if self.vertexSelectionModeActive:
                currR = self.brushRadius
                newR = currR - self.brushRadiusIncrement
                if newR < self.minBrushSize:
                    newR = self.minBrushSize
                self.brushRadius = newR
                updatePointsInRadius()
                updateMeshVertexColors()
  


        def addToSelection(*args):
            # add points within a given radius of mouse position (input to calllback) to the selection
            self.SelectedVertices = self.SelectedVertices | self.VerticesInRadius
        def removeFromSelection(*args):
            self.SelectedVertices = self.SelectedVertices & (self.VerticesInRadius == False)
        def updateMeshVertexColors():
            self.plotter.update_scalars(self.VertexRGB, mesh=self.mesh)

        def triggerSelectionUpdate(*args):
            if self.vertexSelectionModeActive:
                # update the selection of the vertices and the visualisation
                pos = self.plotter.pick_mouse_position()
                updatePointsInRadius(pos) # which points are now in the radius
                if self.VertexSelectionMode == 'Brushing':
                    if self.BrushSelectionType == 'Select':
                        addToSelection()
                    elif self.BrushSelectionType == 'Deselect':
                        removeFromSelection()
                updateMeshVertexColors()
        
        def leftClick(*args):
            if self.VertexSelectionMode is None:
                enableSelecting() # enable selection and brushing
            elif self.VertexSelectionMode == 'Brushing':
                toggleBrushing() # turn off brishing if it is on
            elif self.VertexSelectionMode == 'Geodesic':
                addToSelection()
                # reset the brush radius to a comparaple size
                self.brushRadius = meshRadius(self.mesh.points[self.VerticesInRadius,:])
                updatePointsInRadius()
                updateMeshVertexColors()
                self.VertexSelectionMode = None
                self.plotter.set_background(self.BackgroundColor)
                self.plotter.update()

            #

        def rightClick(*args):
            if self.VertexSelectionMode is None:
                enableDeselecting()
            elif self.VertexSelectionMode == 'Brushing':
                toggleBrushing()
            elif self.VertexSelectionMode == 'Geodesic':
                self.VertexSelectionMode = None
                self.plotter.set_background(self.BackgroundColor)
                self.plotter.update()
                updatePointsInRadius()
                updateMeshVertexColors()

        ########### End brushing callbacks
        ########### Vertex selection manipulation and deletion in 'edit' mode
        def invertVertexSelection():
            self.SelectedVertices = self.SelectedVertices == False
            updateMeshVertexColors()

        def deleteVertexSelection():
           # S["ClippingPoints"] = self.SelectedVertices;
            self.mesh.remove_points(self.SelectedVertices.astype('bool'),inplace=True, keep_scalars=True)
            self._RecordDeletions.append(self.SelectedVertices)
            self.SelectedVertices = np.zeros(self.mesh.n_points).astype('bool')
            self.VerticesInRadius = self.SelectedVertices
            updateMeshVertexColors()
            self.mesh.set_active_scalars("Colors")
        
        def undoDeletion():
            # remove current mesh actor
            if len(self._RecordDeletions) > 0:
                self.plotter.remove_actor(self.mesh_actor)
                # make a new mesh from the copy
                self.mesh = deepcopy(self._MeshCopy)
                # remove last deletion from list
                selection = self._RecordDeletions.pop(-1)
                # apply deletions again in sequence except the last one
                for i in range(len(self._RecordDeletions)):
                    self.mesh.remove_points(self._RecordDeletions[i],inplace=True)
                self.SelectedVertices = selection
                self.VerticesInRadius = np.zeros_like(selection).astype('bool')
                updateMeshVertexColors()
                self.mesh_actor = self.plotter.add_mesh(self.mesh,pickable=True,scalars = "Colors",rgb=True)





        def deleteInverseVertexSelection():
            invertVertexSelection()
            deleteVertexSelection()
        ######### End vertex manipulation and deletion in edot mode
        ######### Callbacks for adding  and deleting landmarks
        def addLandmark(pos):
            if self.landmarkSelectionModeActive:
                lm = pv.Sphere(center=pos, radius=self.landmarkSize)
                actor = self.plotter.add_mesh(lm, color='r')
                self.landmarks.append(pos)
                self.landmark_objects.append((lm, actor))

        def deleteLastLandmark():
            # remove from viewer
            if len(self.landmarks) > 0:
                lm, actor = self.landmark_objects.pop(-1)
                self.plotter.remove_actor(actor)
                self.landmarks.pop(-1)
            # pass
        ##### End callbacks fro landmrking and deleting landmarks
        ##### Callbacks to toggle between plotter mode
        def toggleLandmarkSelectionMode():
            # toggles between landmark selection s and interacting with the camera
            if self.landmarkSelectionModeActive:  # then disable
                self.landmarkSelectionModeActive = False
                self.plotter.renderer.enable()  # enable camera interaction
                self.plotter.set_background(self.BackgroundColor)
                self.plotter.untrack_click_position(side='left')
            else:
                self.landmarkSelectionModeActive = True
                self.plotter.renderer.disable()
                self.plotter.set_background(self.BackgroundColor)
                self.plotter.track_click_position(callback=addLandmark, side='left')

        def toggleVertexSelectionMode():
            if self.vertexSelectionModeActive:  # then disable
                self.vertexSelectionModeActive = False
                self.VertexSelectionMode= None
                # self.plotter.untrack_click_position(side='right')
                # self.plotter.untrack_click_position(side='left')
              #  self.plotter.untrack_mouse_position()
                # self.plotter.clear_events_for_key('i')
                # self.plotter.clear_events_for_key('1')
                # self.plotter.clear_events_for_key('2')
           #     self.plotter.iren.remove_observer("MouseMoveEvent")
                self.plotter.update()
                self.plotter.renderer.enable()  # enable camera interaction
                self.plotter.set_background(self.BackgroundColor)
            else:  # then enable
                if self.VertexSelectionMode is not None:
                    self.VertexSelectionMode is None
                self.vertexSelectionModeActive = True
                self.plotter.renderer.disable()  # disable camera interaction
                self.plotter.set_background(self.BackgroundColor)
                self.plotter.update()

              #  self.plotter.track_mouse_position()

        def enterGeodesicSelection(*args):
            pos = self.plotter.pick_mouse_position();
            self.VertexSelectionMode = 'Geodesic'
            A= makeAdjacencyMatrix(self.mesh)
            #self.mesh["ConnectedComponents"] = labelConnectedComponents(self.mesh)
            v0 = self.mesh.points-pos
            D = np.linalg.norm(v0,axis=1)
            I = np.argmin(D)
            GD = dijkstra(A,directed=False,indices=I)
            self.geodesicDistances = GD
            self.mesh.set_active_scalars("Colors")
            self.brushRadius = np.max(GD[GD != np.Inf]) # select the whole connected component
            updatePointsInRadius(pos)
            updateMeshVertexColors()

        def mouseMoved(*args):
            if self.VertexSelectionMode != 'Geodesic': # geodesic is too expensive to update on the fly
                pos = self.plotter.pick_mouse_position()
                triggerSelectionUpdate(pos)
        def saveResult():
            # save the output depending on the mode
            fn = self.SaveFileName
            if fn is not None:
                 head, _ = os.path.split(fn)
                 if os.path.isdir(head) == False:
                     print('Creating destination folder')
                     os.makedirs(head)
            else:
                print('Filename not specified...so file is not saved')
            if self.mode == 'edit':
                writePolyDataToObj(self.mesh, fn)
                self.plotter.background_color = [0, 0, 0]
                #self.plotter.update()
            elif self.mode == 'landmark':
                writeLandmarksToText(self.landmarks, fn)
                self.plotter.background_color = [0, 0, 0]
               # self.plotter.update()
            else:
                raise ValueError('Invalid mode')
            print(fn+' saved')
        ### end callback function definition

        # assign some attributes and opening settings
        self.SaveFileName = saveFileName
        self.landmarkSize = landmark_size
        self.BrushSelectionType = 'Deselect'
        self.mesh = S
        self.vertexSelectionModeActive = False
        self.landmarkSelectionModeActive = False
        self.VertexSelectionMode = None
        self.mode = mode.lower()
        # create pyvista plotter
        P = pv.Plotter()
        self.plotter = P
        if mode.lower() == 'edit':
            self.brushRadius = np.array([meshRadius(self.mesh.points) / 1.2])  # default brush size
            minE,medE = minMedEdgeLength(S)
            self.brushRadiusIncrement = np.array([meshRadius(self.mesh.points) / 20])
            self.minBrushSize = minE/2
            self.mesh["Colors"] = self.VertexRGB
            self.plotter.add_key_event('t', toggleVertexSelectionMode)
            self.plotter.add_key_event('i', invertVertexSelection)
            self.plotter.add_key_event('Delete', deleteVertexSelection)
            self.plotter.add_key_event('f', deleteInverseVertexSelection)
            self.plotter.add_key_event('i', invertVertexSelection)
            self.plotter.add_key_event('2', increaseBrushRadius)
            self.plotter.add_key_event('1', decreaseBrushRadius)
            self.plotter.add_key_event('z',undoDeletion)
            self.plotter.add_key_event('g', enterGeodesicSelection)
            self.plotter.track_click_position(leftClick, side='left')
            self.plotter.track_click_position(rightClick, side='right')
      #      self.plotter.track_click_position(enterGeodesicSelection, side='left', double=True)

           # self.plotter.track_click_position(paintBucketRemove, side='right', double=True)
            self.plotter.set_background([0.5, 0.5, 0.5])
            self.plotter.track_mouse_position()
            self.plotter.iren.add_observer("MouseMoveEvent", mouseMoved)
            actor = self.plotter.add_mesh(self.mesh, pickable=True, scalars="Colors",rgb=True)
            self.mesh_actor = actor
            self._MeshCopy = deepcopy(S);
            self.vertexSelectionModeActive = True
            self.plotter.renderer.disable()  # disable camera interaction


        # create extra mesh which will plot the vertex selection
            # if showSelectionPreview:
            #     previewMesh = self.meshcopy(deep=True)
            #     previewMesh['Vertex Selection'] = np.zeros(self.mesh.n_points)
            #     actor = self.plotter.add_mesh(previewMesh, style='points', pickable=True, point_size=.5)
            #     self.previewMesh = (previewMesh, actor)

        elif mode.lower() == 'landmark':
            self.plotter.add_key_event('t', toggleLandmarkSelectionMode)
            self.landmarks = list()
            self.landmark_objects = list()
            toggleLandmarkSelectionMode()
            self.plotter.add_key_event('Delete', deleteLastLandmark)
            self.plotter.add_mesh(S, pickable=True)
        else:
            raise ValueError('Invalid Mode')

        self.plotter.add_key_event('a', saveResult)
        self.plotter.add_key_event('y',lambda: self.plotter.view_xz())
        self.plotter.view_xy()
        self.plotter.show()


class BatchMeshEditor:
    def __init__(self):
        self._HomeDirectory = None
        self._SourcePath = None
        self._DestinationPath = None
        self.Overwrite = False
        self._Mode = 'landmark'
        self.FileProcessingInfo = None
        self.PreLoadObjs = True
        self.ConvertToVtk = False
        self.InputFileType = '.obj'
        self.PreserveSubFolders = True
        self.LandmarkSize = 4
        self.PreLoadObjs = True
        self._InFiles = None
        self._OutFiles = None
        self._Testing = False  # for deevelopment only

    # dependent properties
    @property
    def SourcePath(self):
        if self.HomeDirectory is None:
            return self._SourcePath
        else:
            return os.path.join(self.HomeDirectory, 'IMAGES', '01 ORIGINAL IMAGES')

    @SourcePath.setter
    def SourcePath(self, value):
        if os.path.isdir(value) | (value is None):
            self._SourcePath = value
        else:
            raise ValueError('path does not exist or is not a directory')

    @property
    def DestinationPath(self):
        if self.HomeDirectory is None:
            return self._DestinationPath
        else:
            if self.Mode == 'landmark':
                return os.path.join(self.HomeDirectory, 'IMAGES', '22 TEXT POSE POINTS')
            elif self.Mode == 'edit':
                return os.path.join(self.HomeDirectory, 'IMAGES', '31 OBJ CLEANED')
            else:
                raise ValueError('Invalid mode')

    @DestinationPath.setter
    def DestinationPath(self, value):
        if  isinstance(value,(str,None)):
            self._DestinationPath = value
        else:
            raise ValueError('Destination path must be string or NoneType')
        if isinstance(value,str) & os.path.isdir(value)==False:
            os.makedirs(value)
            print('Destination path does not exist so it is being made')

    # properties with setters
    @property
    def Mode(self):
        return self._Mode

    @Mode.setter
    def Mode(self, mode):
        if mode.lower() not in ['landmark', 'edit']:
            raise ValueError('Mode must be landmark or edit')
        else:
            self._Mode = mode.lower()

    @property
    def HomeDirectory(self):
        return self._HomeDirectory

    @HomeDirectory.setter
    def HomeDirectory(self, path):
        if os.path.isdir(path):
            self._HomeDirectory = path
        else:
            raise ValueError('path does not exist or is not a directory')

    # methods
    def prepareFiles(self):
        # check source path exists
        if os.path.isdir(self.SourcePath) == False:
            raise ValueError('Source path does not exist or is not a directory')
        # if destination path doesn't exist then make it
        if os.path.isdir(self.DestinationPath) == False:
            print('Destionation path not found so will make it')
            os.mkdir(self.DestinationPath)
        if self.SourcePath == self.DestinationPath:
            raise ValueError('Source and destination paths cannot be the same')
        # find files

        if self.ConvertToVtk:
            # find files that don't have a vtk counterpart in the original directory
            [inObj,outVtk] = findFiles(self.SourcePath,self.InputFileType,self.SourcePath,True,'converttovtk')
            inObj,outVtk = removeExistingFiles(inObj,outVtk)
            for i in range(len(inObj)):
                print('Converting shape ' + str(i) +' of ' + str(len(inObj)))
                shp,_ = load3DImage(inObj[i])
                if shp is not None:
                    shp.save(dictToPath(outVtk[i]),binary=True,texture = True)
            inType = '.vtk' # moving forward the vtk files will be the input files
        else:
            inType=self.InputFileType

        [inFiles, outFiles] = findFiles(self.SourcePath,inType, self.DestinationPath,
                                        self.PreserveSubFolders, self.Mode)



        # check if the output file exists
        if self.Overwrite == False:
            inFiles,outFiles = removeExistingFiles(inFiles,outFiles)
        if self._Testing:
            inFiles = inFiles[0:5]
            outFiles = outFiles[0:5]
        if self.PreLoadObjs:
            for i in range(len(inFiles)):
                print('Loading image ' + str(i) + ' of' + str(len(inFiles)))
                load3DImage(inFiles[i])
        self._InFiles = inFiles
        self._OutFiles = outFiles
        print('Ready to process ' + str(len(self._InFiles)) + ' files')

    def processFiles(self):
        for i in range(len(self._InFiles)):
            # bullet proof against ever saving an infile with the wrong corresponding outfile name
            if self._InFiles[i]['fileName'] != self._OutFiles[i]['fileName']:
                raise ValueError('Input and output filenames don\'t match. This requires investigation')
            currF = self._InFiles[i]

            if self.PreLoadObjs == False: # load the polydata into the file dictionary
                load3DImage(currF)
            mesh = currF['polydata']
            if mesh is None:
                print(dictToPath(currF) + ' is missing or cant be loaded')
                continue
            fn = dictToPath(self._OutFiles[i])
            path, _ = os.path.split(fn)
            if os.path.isdir(path) == False:
                os.makedirs(path)
            print('Processing image ' + str(i) + 'of ' + str(len(self._InFiles)))
            MeshEditor(mesh, self.Mode, landmark_size=self.LandmarkSize,
                             saveFileName=fn)



