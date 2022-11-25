import os
import glob
from itertools import compress
import pyvista as pv
from copy import deepcopy
import numpy as np
import csv


######## Define Miscellaneous helper functions

# calculates the median distance of all points from the centroid of a configuration of points
def meshRadius(verts):
    v0 = verts - np.mean(verts, axis=0)
    N = np.sqrt(np.sum(v0 ** 2, axis=1))
    return np.median(N)  #


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

    # parse tail into filename and extension
    parts = [os.path.splitext(x) for x in tail]
    fn, ext = list(zip(*parts))

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
        F = lambda x: x.update({'subFolder': ''})
        [F(x) for x in outFiles]  # modify in situ
    if mode == 'landmark':  # foutput file will be text
        F = lambda x: x.update({'ext': '.txt'})
        [F(x) for x in outFiles]  # modify in situ
    elif mode == 'edit':  # output file will be obj
        F = lambda x: x.update({'ext': '.obj'})
    [F(x) for x in outFiles]  # modify in situ
    return outFiles


def writePolyDataToObj(polyData, fn):
    # basic obj exporter for pyvista polydata since obj is not supported yet in pyvista.save
    if os.path.splitext(fn)[1] != '.obj':
        raise ValueError('Filename does not have \'.obj\' extension')
    verts = polyData.points.T
    faces = np.reshape(polyData.faces, (int(len(polyData.faces) / 4), 4));
    faces = faces[:, 1:] + 1  # remove first column and add 1 to the index
    with open(fn, 'w') as csvfile:
        writerobj = csv.writer(csvfile, delimiter=' ')
        for i in range(verts.shape[1]):
            row = ['v'] + [str(item) for item in verts[:, i]]
            writerobj.writerow(row)
        for i in range(faces.shape[0]):
            row = ['f'] + [str(item) for item in faces[i, :]]
            writerobj.writerow(row)


def writeLandmarksToText(landmarks, fn):
    with open(fn, 'w') as csvfile:
        writerobj = csv.writer(csvfile, delimiter=',')
        for i in range(len(landmarks)):
            row = [str(item) for item in landmarks[i]]
            writerobj.writerow(row)


def load3DImage(fileDict):
    fn = dictToPath(fileDict)
    try:
        shp = pv.read(fn)
        shp.triangulate(inplace=True)
    except:
        print('Unable to load ' + fn)
        shp = None
    # add to dictionary
    fileDict.update({'polydata': shp})
    return shp, fileDict


class MeshEditor:
    def __init__(self, S, mode, landmark_size=4, showSelectionPreview=True, saveFileName=None):

        ##### Define callbacks - all callbacks will have access to variables definied within this init function
        # such as 'P' the plotting window, 'S' the mesh being edited and 'previewMesh' a copy of S on which the selection preview is rendered


        ### Brushing related callbacks for 'edit' mode
        def toggleBrushing():
            # enable/disable brushing
            if self.Brushing:
                self.Brushing = False
                P.background_color = [.7, .7, .7]
            else:
                self.Brushing = True
                P.background_color = [.8, .8, .8];

        # these next 3 callbacks are attached to left, right or left double mouse clicks so will take the position of the click as an argument
        def enableSelecting(pos):
            self.BrushSelectionType = 'Select'
            toggleBrushing()

        def enableDeselecting(pos):
            self.BrushSelectionType = 'Deselect'
            toggleBrushing()

        def increaseBrushRadius():
            currR = self.brushRadius
            newR = currR + self.brushRadiusIncrement
            self.brushRadius = newR
           # print(newR)
            # updateCurrentSelection()

        def decreaseBrushRadius():
            currR = self.brushRadius
            newR = currR - self.brushRadiusIncrement
            if newR < 0:
                newR = 0
            self.brushRadius = newR
          #  print(newR)
            # updateCurrentSelection()

        def paintBucket(pos): # paint bucket selection, does not really work
            if self.Brushing:
                toggleBrushing() # turn off brushing
            DS = S.connectivity() # get labels of connected components (does not seem to really work)
            L = DS.point_data['RegionId']
            # find point to which it belongs
            D = np.sqrt(np.sum((S.points - np.array(pos)) ** 2, axis=1))
            posL = L[np.argmin(D)]
            S.point_data['Vertex Selection'] = (L == posL).astype(float)
            P.update()

        def addToSelection(pos):
            # add points within a given radius of mouse position (input to calllback) to the selection
            psel = S.point_data['Vertex Selection']
            v0 = np.array(S.points - pos)
            D = np.sqrt(np.sum(v0 ** 2, axis=1))
            newP = D < self.brushRadius
            S.point_data['Vertex Selection'] = ((psel == 1) | (newP == 1)).astype(float)
            P.update()


        def removeFromSelection(pos):
            # # remoive points within a given radius of mouse position (input to calllback) to the selection
            psel = S.point_data['Vertex Selection']
            v0 = np.array(S.points - pos)
            D = np.sqrt(np.sum(v0 ** 2, axis=1))
            newP = D < self.brushRadius
            S.point_data['Vertex Selection'] = ((psel == 1) & (newP == 0)).astype(float)
            P.update()

        def mouseMoved(src, evt):
            # this callback to mouse movement configures the whole brushing operation dependent on whether brushing is active and the current selection type
            pos = P.pick_mouse_position()
            if showSelectionPreview:
                v0 = np.array(previewMesh.points) - pos
                D = np.sqrt(np.sum(v0 ** 2, axis=1))
                newP = D < self.brushRadius
                previewMesh['Vertex Selection'] = newP
                if self.Brushing == False:
                    P.update()  # otherwise wait to update both meshes
            if self.Brushing:
                if self.BrushSelectionType == 'Select':
                    addToSelection(pos)
                elif self.BrushSelectionType == 'Deselect':
                    removeFromSelection(pos)
        ########### End brushing callbacks
        ########### Vertex selection manipulation and deletion in 'edit' mode
        def invertVertexSelection():
            S.point_data['Vertex Selection'] = S.point_data['Vertex Selection'] == 0
            P.update()

        def deleteVertexSelection():
            if showSelectionPreview:
                previewMesh.point_data['Clipping Selection'] = S.point_data['Vertex Selection']
                previewMesh.clip_scalar(inplace=True, value=.5)
            S.clip_scalar(inplace=True, value=.5)
            P.update()

        def deleteInverseVertexSelection():
            invertVertexSelection()
            if showSelectionPreview:
                previewMesh.point_data['Clipping Selection'] = S.point_data['Vertex Selection']
                previewMesh.clip_scalar('Clipping Selection', inplace=True, value=.5)
            S.clip_scalar(inplace=True, value=.5)
            P.update()
        ######### End vertex manipulation and deletion in edot mode
        ######### Callbacks for adding  and deleting landmarks
        def addLandmark(pos):
            if self.landmarkSelectionModeActive:
                lm = pv.Sphere(center=pos, radius=self.landmarkSize)
                actor = P.add_mesh(lm, color='r')
                self.landmarks.append(pos)
                self.landmark_objects.append((lm, actor))

        def deleteLastLandmark():
            # remove from viewer
            if len(self.landmarks) > 0:
                lm, actor = self.landmark_objects.pop(-1)
                P.remove_actor(actor)
                self.landmarks.pop(-1)
            # pass
        ##### End callbacks fro landmrking and deleting landmarks
        ##### Callbacks to toggle between plotter mode
        def toggleLandmarkSelectionMode():
            # toggles between landmark selection s and interacting with the camera
            if self.landmarkSelectionModeActive:  # then disable
                self.landmarkSelectionModeActive = False
                P.renderer.enable()  # enable camera interaction
                P.set_background([.9, .9, .9])
                P.untrack_click_position(side='left')
            else:
                self.landmarkSelectionModeActive = True
                P.renderer.disable()
                P.set_background([0.5, 0.5, 0.5])
                P.track_click_position(callback=addLandmark, side='left')

        def toggleVertexSelectionMode():
            if self.vertexSelectionModeActive:  # then disable
                self.vertexSelectionModeActive = False
                P.renderer.enable()  # enable camera interaction
                P.untrack_click_position(side='right')
                P.untrack_click_position(side='left')
                P.set_background([.9, .9, .9])
                P.untrack_mouse_position()
                P.clear_events_for_key('i')
                P.clear_events_for_key('1')
                P.clear_events_for_key('2')
            else:  # then enable
                self.vertexSelectionModeActive = True
                P.renderer.disable()  # disable camera interaction
                P.track_mouse_position()
                P.iren.add_observer("MouseMoveEvent", mouseMoved)
                P.add_key_event('i', invertVertexSelection)
                P.add_key_event('2', increaseBrushRadius)
                P.add_key_event('1', decreaseBrushRadius)
                P.track_click_position(enableSelecting, side='left')
                P.track_click_position(enableDeselecting, side='right')
                P.track_click_position(paintBucket, side='left', double=True)
                P.set_background([0.5, 0.5, 0.5])

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
                writePolyDataToObj(S, fn)
                P.background_color = [0, 0, 0]
                P.update()
            elif self.mode == 'landmark':
                writeLandmarksToText(self.landmarks, fn)
                P.background_color = [0, 0, 0]
                P.update()
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
        self.Brushing = False
        self.mode = mode.lower()
        # create pyvista plotter
        P = pv.Plotter()
        self.plotter = P
        if mode.lower() == 'edit':
            S.point_data['Vertex Selection'] = np.zeros(S.n_points)
            self.brushRadius = np.array([meshRadius(S.points) / 2])  # default brush size
            self.brushRadiusIncrement = np.array([meshRadius(S.points) / 20])

            P.add_key_event('s', toggleVertexSelectionMode)
            P.add_key_event('i', invertVertexSelection)
            P.add_key_event('Delete', deleteVertexSelection)
            P.add_key_event('f', deleteInverseVertexSelection)
            # create extra mesh which will plot the vertex selection
            if showSelectionPreview:
                previewMesh = S.copy(deep=True)
                previewMesh['Vertex Selection'] = np.zeros(S.n_points)
                actor = P.add_mesh(previewMesh, style='points', pickable=True, point_size=.5)
                self.previewMesh = (previewMesh, actor)

        elif mode.lower() == 'landmark':
            P.add_key_event('s', toggleLandmarkSelectionMode)
            self.landmarks = list()
            self.landmark_objects = list()
            toggleLandmarkSelectionMode()
            P.add_key_event('Delete', deleteLastLandmark)
        else:
            raise ValueError('Invalid Mode')

        P.add_key_event('Return', saveResult)

        self.plotter.add_mesh(S, pickable=True, cmap='Wistia')
        if mode == 'edit':
            toggleVertexSelectionMode()
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
        self.InputFileType = '.obj'
        self.PreserveSubFolders = True
        self.LandmarkSize = 4
        self.PreLoadObjs = True
        self.ShowSelectionPreview = True;
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
        [inFiles, outFiles] = findFiles(self.SourcePath, self.InputFileType, self.DestinationPath,
                                        self.PreserveSubFolders, self.Mode)

        # check if the output file exists
        if self.Overwrite == False:
            notExisting = [fileExists(x) == False for x in outFiles]
            inFiles = compress(inFiles, notExisting)
            inFiles = [x for x in inFiles]
            outFiles = compress(outFiles, notExisting)
            outFiles = [x for x in outFiles]
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
                os.mkdir(path)
            print('Processing image ' + str(i) + 'of ' + str(len(self._InFiles)))
            MeshEditor(mesh, self.Mode, landmark_size=self.LandmarkSize,
                            showSelectionPreview=self.ShowSelectionPreview, saveFileName=fn)



