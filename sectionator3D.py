#!/usr/bin/env python
 
####based on pick_closest-point_04.py

###run with:
## PYTHONPATH=/opt/vtk-5.10.1/lib/python2.7/site-packages/ LD_LIBRARY_PATH=/opt/vtk-5.10.1/lib/vtk-5.10/ /opt/VirtualGL/bin/vglrun python ~/vtk/py/pick_closest-point_03.py -i SLOT_01_seg-131125_s255_mean3_fh0_mc127_cap_clip_lmp_cl-skel_be.vtp

##01: load skel and place boxWidget at picked point (Shift+MMB)
##02: orient glyph and boxWidget
##03: clip with boxWidget and save result, v1.0
##04: remove all but largest mesh part, v1.1
##05: color mesh according to voxel data (vtkProbeFilter), remember cBox scale, optimize performance, v1.2
##06: progress report of filters, toggle transparency, v1.3
##07: debugging repetitive clip-box transform, v1.3.1

###todo:
## f: centre on marker

VERSION="1.3.1"


import sys,os,getopt
import optparse  # to parse options for us and print a nice help message
import math

OK_vtk=0
OK_vtkblender=0

try:
    import vtk
    OK_vtk=1
except ImportError, error:
    sys.stderr.write("Error: %s.\n"%error)
    sys.stderr.write("Please check if the vtk library for Python is correctly installed.\n")
    #sys.exit(1)
    #return #return outside function not possible
    OK_vtk=0


#### http://vtk.1045678.n5.nabble.com/Re-vtk-transparency-problem-td1240066.html
# class MyPainter(vtk.vtkPainter):

#     def RenderInternal(renderer, actor, typeflags):
#         glEnable(GL_CULL_FACE);
#         glCullFace(GL_FRONT);
#         vtk.vtkPainter.RenderInternal(renderer, actor, typeflags);
#         glEnable(GL_CULL_FACE);
#         glCullFace(GL_BACK);
#         vtk.vtkPainter.RenderInternal(renderer, actor, typeflags);
#         glDisable(GL_CULL_FACE);



class MyInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
#class MyInteractorStyle(vtk.vtkInteractorStyleTrackballActor):
    def __init__(self,parent=None):
        self.AddObserver("MiddleButtonPressEvent",self.middleButtonPressEvent)
        #self.AddObserver("OnMiddleButtonDown",self.middleButtonPressEvent)
        self.AddObserver("MiddleButtonReleaseEvent",self.middleButtonReleaseEvent)
        self.AddObserver("MouseMoveEvent", self.MoveEvent)
        #self.AddObserver("LeftButtonPressEvent", self.OnLeftButtonDown)
        self.AddObserver ("KeyPressEvent", self.keypressCallback )

        self.MMBpressed= False
        #picker = vtk.vtkCellPicker()
        self.picker = vtk.vtkPointPicker()
        self.picker.SetTolerance(1E-2)
        self.refNormal=[-1,0,0]
        self.opaque= False


    def keypressCallback(self,obj,event):
        key = interactor.GetKeySym()
        #print key
        if(key == "c"):
            print "Toggle visibility of clip region"
            ClipWidget.GetPlanes(planes)
            #add_progress_observer(selectMapper)
            clipper.Update()
            selectMapper.SetInputConnection(clipper.GetOutputPort())
            selectMapper.ScalarVisibilityOff()
            #selectActor.VisibilityOn()
            #ClipWidget.Off()
            selectActor.SetVisibility(not selectActor.GetVisibility())
            ClipWidget.SetEnabled(not selectActor.GetVisibility())
            #SeedActor.SetVisibility(not selectActor.GetVisibility())
            #rem_progress_observer(selectMapper)
        if(key == "C"):
            print "Applying clip"
            #clipper.Update()
            surf.DeepCopy(clipper.GetOutput())
            selectActor.VisibilityOff()
            #sactor.VisibilityOff()
            ClipWidget.Off()
        if(key == "o"):
            print "Saving clip"
            surf.Update()
            surfw.SetFileName(options.surfof)
            surfw.SetInput(surf)
            surfw.Update()
        if(key == "l"):
            print "Toggle visibility of largest mesh regions"
            connectivity.ScalarConnectivityOff()
            #connectivity.SetExtractionModeToAllRegions()
            #connectivity.ColorRegionsOn()
            connectivity.SetExtractionModeToLargestRegion()
            connectivity.ColorRegionsOff()
            #connectivity.Update()
            # pd= connectivity.GetOutput().GetPointData();
            # if (pd):
            #     print " contains point data with ", pd.GetNumberOfArrays() 
            #     for  i in range(pd.GetNumberOfArrays()):
            #         print "\tArray ", i, " is named ", pd.GetArrayName(i)


            selectMapper.SetInputConnection(connectivity.GetOutputPort())
            # #selectMapper.ScalarVisibilityOn()
            # #selectMapper.SetScalarModeToUseCellData ()
            # selectMapper.SetScalarModeToUsePointData ()
            # #selectMapper.SetScalarModeToUsePointFieldData()
            # selectMapper.SelectColorArray("RegionId")
            # #selectMapper.ColorByArrayComponent("RegionId", 0);
            # selectMapper.SetColorModeToMapScalars ()
            # selectMapper.InterpolateScalarsBeforeMappingOn ()
            # #selectMapper.SetScalarRange(connectivity.GetOutput().GetScalarRange())
            # #selectMapper.UseLookupTableScalarRangeOn ()
            # print selectMapper.GetArrayName()
            selectActor.SetVisibility(not selectActor.GetVisibility())
        if(key == "L"):
            print "Removing all but the largest mesh part"
            # connectivity = vtk.vtkPolyDataConnectivityFilter()
            # connectivity.SetInput(surf)
            # connectivity.ScalarConnectivityOff()
            # connectivity.SetExtractionModeToLargestRegion()
            # connectivity.ColorRegionsOff()
            # connectivity.Update()
            surf.DeepCopy(connectivity.GetOutput())
            selectActor.VisibilityOff()
        if(key == "t"):
            print "Toggling transparency"
            if self.opaque:
                sactor.GetProperty().SetOpacity(.5)
                self.opaque= False
            else:
                sactor.GetProperty().SetOpacity(1.0)
                self.opaque= True
        if(key == "p"):
            print "Toggling coloring according to voxel data"
            #smapper.SetScalarModeToUsePointData ()
            smapper.SetScalarVisibility(not smapper.GetScalarVisibility())
        if(key == "d"):
            print "Toggling direction of marker"
            self.refNormal= [-self.refNormal[0],-self.refNormal[1],-self.refNormal[2]]
        if(key == "m"):
            print "Toggling visibility of marker"
            SeedActor.SetVisibility(not SeedActor.GetVisibility())
        if(key == "r"):
            print "Resetting clip region"
            selectActor.VisibilityOff()
            ClipWidget.Off()

        renwin.Render()##rerender to show changes
        self.OnKeyPress()


    def middleButtonPressEvent(self,obj,event):
        #print "Middle Button pressed"
        if(interactor.GetShiftKey()):
            #print "Shift held. "
            self.MMBpressed= True
            SeedActor.SetVisibility(True)

            eventPosition = interactor.GetEventPosition()
            #print "Picking pixel: ", eventPosition 
           
            result = self.picker.Pick(float(eventPosition[0]),float(eventPosition[1]),0.0,interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()) 
            if result == 0:
                return

            self.ppPId= self.picker.GetPointId()
            self.ppP= source.GetPoint(self.ppPId);
            #self.ppP = self.picker.GetPickPosition() 
            #print "World pick pos: ", self.ppP 
            PickedSeeds.GetPoints().InsertPoint(0,self.ppP)
            PickedSeeds.Modified()##needed for renderer to notice changes

            renwin.Render()##rerender to show changes
        else:
            self.OnMiddleButtonDown() 
        return
 
    def MoveEvent(self,obj,event):
        #if (self.MMBpressed and interactor.GetShiftKey()):
        if(self.MMBpressed):
            #print "Shift held, Middle Button pressed and moving"
            eventPosition = interactor.GetEventPosition()
            #print "Picking pixel: ", eventPosition 
           
            result = self.picker.Pick(float(eventPosition[0]),float(eventPosition[1]),0.0,interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()) 
            if result == 0:
                return

            self.ppPId= self.picker.GetPointId()
            self.ppP= source.GetPoint(self.ppPId);
           #self.ppP = self.picker.GetPickPosition() 
            #print "World pick pos: ", self.ppP 
            PickedSeeds.GetPoints().InsertPoint(0,self.ppP)
            PickedSeeds.Modified()##needed for renderer to notice changes
            renwin.Render()##rerender to show changes


            self.p= source.GetPoint(self.ppPId-1);
            #print "p: ", self.p

            self.n= [0,0,0]
            vtk.vtkMath.Subtract(self.p, self.ppP, self.n);
            vtk.vtkMath.Normalize(self.n)
            #print "n: ", self.n

            self.raxis= [0,0,0]
            vtk.vtkMath.Cross(self.refNormal, self.n, self.raxis)
            self.w= math.acos(vtk.vtkMath.Dot(self.refNormal, self.n)) * 180 / math.pi
            
            gtransf = vtk.vtkTransform()
            gtransf.RotateWXYZ(self.w, self.raxis)
            glyphtransf.SetTransform(gtransf)


        else:
            self.OnMouseMove()
        return

    def middleButtonReleaseEvent(self,obj,event):
        global ClipWidget

        #print "Middle Button released"
        #if(interactor.GetShiftKey()):
        if(self.MMBpressed):
            #print "Shift held. "
            eventPosition = interactor.GetEventPosition()
            print "Picking pixel: ", eventPosition 
           
            result = self.picker.Pick(float(eventPosition[0]),float(eventPosition[1]),0.0,interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()) 
            if result:
                self.ppPId= self.picker.GetPointId()
                self.ppP= source.GetPoint(self.ppPId);
                #self.ppP = self.picker.GetPickPosition() 
            print "World pick pos: ", self.ppP 
            #PickedSeeds.GetPoints().InsertNextPoint(self.ppP)
            PickedSeeds.GetPoints().InsertPoint(0,self.ppP)
            PickedSeeds.Modified()##needed for renderer to notice changes


            self.p= source.GetPoint(self.ppPId-1);
            #print "p: ", self.p

            self.n= [0,0,0]
            vtk.vtkMath.Subtract(self.p, self.ppP, self.n);
            vtk.vtkMath.Normalize(self.n)
            #print "n: ", self.n

            self.raxis= [0,0,0]
            vtk.vtkMath.Cross(self.refNormal, self.n, self.raxis)
            self.w= math.acos(vtk.vtkMath.Dot(self.refNormal, self.n)) * 180 / math.pi
            
            self.scale= [1,1,1]
            ctransf = vtk.vtkTransform()
            ClipWidget.GetTransform(ctransf)
            ctransf.GetScale(self.scale)

            transf = vtk.vtkTransform()
            #transf.Scale(ctransf.GetScale)
            transf.Translate(self.p)
            transf.RotateWXYZ(self.w, self.raxis)
            transf.Scale(self.scale)###Order matters!!! first translate, then rotate then scale!!!!! swapping rot and scale causes e.g. translation and shering effects
            ClipWidget.SetTransform(transf)
            #ClipWidget.GetProp3D().SetUserTransform(transf)
            ClipWidget.On()

            gtransf = vtk.vtkTransform()
            gtransf.RotateWXYZ(self.w, self.raxis)
            glyphtransf.SetTransform(gtransf)

            SeedActor.SetVisibility(False)

            self.MMBpressed= False
            renwin.Render()##rerender to show changes


        else:
            self.OnMiddleButtonUp() ##execute OnMiddleButtonUp() from vtk.vtkInteractorStyleTrackballCamera
        return


##### globals and defaults #####################################################

invocation_name = os.path.basename(sys.argv[0])

(QUIET, VERB) = (0, 1)
verbosity = VERB

##### function definitions #####################################################


def print_info(level, message_str):
    global verbosity
    if level <= verbosity: 
        sys.stdout.write(message_str)
        sys.stdout.flush()

def print_vtk_progress(vtkObject, event):
    name = vtkObject.GetClassName()
    progress = vtkObject.GetProgress()
    print_info(VERB, "\r  Progress of %s: %5.1f%%"%(name, 100.0*progress))

def print_vtk_end(obj, event):
    print_info(VERB, " done.\n")

def add_progress_observer(filter):
    filter.AddObserver("ProgressEvent", print_vtk_progress)
    filter.AddObserver("EndEvent", print_vtk_end)

def rem_progress_observer(filter):
    #filter.AddObserver("ProgressEvent", None)
    # filter.RemoveObserver("ProgressEvent")
    filter.RemoveObserver(vtk.vtkCommand.ProgressEvent)
    filter.RemoveObserver(vtk.vtkCommand.EndEvent)




argv= sys.argv

usage_text = '\n' + invocation_name + ' Version: ' + VERSION + '\nClip polydata interactively with a clipping box guided by a skeleton.\n\nPosition clipBox marker with Shift+MMB\n c: Set clip regeion\n C: Apply clip\n l: Labelling connected mesh regions\n L: Removing all but the largest mesh part\n d: toggle direction of marker\n m: toggle marker visibility\n p: toggle coloring according to voxel data\n o: Write to output file\n r: Reset clip region\n q: Quit'

parser = optparse.OptionParser(usage = usage_text)

parser.add_option('-i', '--skel', dest='skelf', help='Skeleton file (*.vtp)', type='string')
parser.add_option('-s', '--surf', dest='surff', help='Surface file (*.vtp)', type='string')
parser.add_option('-v', '--voxeld', dest='voxelf', help='Voxel data file (*.mhd) optional', type='string')
parser.add_option('-o', '--out', dest='surfof', help='Output file (*.vtp)', type='string')

options, args = parser.parse_args(argv)

if not argv:
    print
    parser.print_help()
    sys.exit(1)

if not options.skelf:
   print 'Need a skeleton input file\n'
   parser.print_help()
   sys.exit(1)

if not options.surff:
   print 'Need a surface input file\n'
   parser.print_help()
   sys.exit(1)

# if not options.voxelf:
#    print 'Need a surface input file\n'
#    parser.print_help()
#    sys.exit(1)

if not options.surfof:
   print 'Need a surface output file\n'
   parser.print_help()
   sys.exit(1)


PickedSeeds = vtk.vtkPolyData()

# source = vtk.vtkSphereSource()
# source.SetCenter(0, 0, 0)
# source.SetRadius(1)
# source.Update()

skelr = vtk.vtkXMLPolyDataReader()
skelr.SetFileName(options.skelf)
skelr.Update()
#skelr.UpdateWholeExtent()

source= skelr.GetOutput()
#source.ComputeBounds()
#source.Update()

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(skelr.GetOutputPort())


actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(0,0,1)
actor.GetProperty().SetOpacity(.5)
#actor.GetProperty().SetRepresentationToWireframe ()
actor.GetProperty().SetRepresentationToSurface ()
actor.GetProperty().EdgeVisibilityOn()

seedPoints = vtk.vtkPoints()
PickedSeeds.SetPoints(seedPoints)


#glyphSource = vtk.vtkSphereSource()
glyphSource = vtk.vtkConeSource()
glyphSource.SetRadius(0.01 * source.GetLength())
glyphSource.SetHeight(0.02 * source.GetLength())

glyphtransf= vtk.vtkTransformPolyDataFilter()
glyphtransf.SetInputConnection(glyphSource.GetOutputPort())
glyphtransf.SetTransform(vtk.vtkTransform())

glyphs = vtk.vtkGlyph3D()
glyphs.SetInput(PickedSeeds)
#glyphs.SetSource(glyphSource.GetOutput())
glyphs.SetSource(glyphtransf.GetOutput())
glyphs.SetScaleModeToDataScalingOff()
        #glyphs.SetScaleFactor(self._Surface.GetLength()*0.01)
glyphMapper = vtk.vtkPolyDataMapper()
glyphMapper.SetInput(glyphs.GetOutput())
#glyphMapper.SetInput(glyphSource.GetOutput())

SeedActor = vtk.vtkActor()
SeedActor.SetMapper(glyphMapper)
SeedActor.GetProperty().SetColor(.0,.0,1.0)
#SeedActor.GetProperty().SetOpacity(.5)
SeedActor.PickableOff()


surfr = vtk.vtkXMLPolyDataReader()
surfr.SetFileName(options.surff)
surfr.Update()

#surf= surfr.GetOutput()
surf = vtk.vtkPolyData()
surf.DeepCopy(surfr.GetOutput())

smapper = vtk.vtkPolyDataMapper()
#add_progress_observer(smapper)
#smapper.SetInputConnection(surfr.GetOutputPort())
smapper.SetInput(surf)
#smapper.ImmediateModeRenderingOn()
smapper.ImmediateModeRenderingOff()
#smapper.GlobalImmediateModeRenderingOn()
# transparentPainter = MyPainter();
# transparentPainter.SetDelegatePainter(smapper.GetPainter());
# smapper.SetPainter(transparentPainter);
smapper.ScalarVisibilityOff()

sactor = vtk.vtkActor()
sactor.SetMapper(smapper)
sactor.GetProperty().SetColor(.5,.5,.5)
sactor.GetProperty().SetOpacity(.5)
sactor.GetProperty().SetRepresentationToSurface ()
#sactor.GetProperty().EdgeVisibilityOn()
sactor.PickableOff()

renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.AddActor(SeedActor)
renderer.AddActor(sactor)
renderer.SetBackground(0.9, 0.9, 0.9)

renwin = vtk.vtkRenderWindow()
renwin.AddRenderer(renderer)


interactor = vtk.vtkRenderWindowInteractor()
interactor.SetInteractorStyle(MyInteractorStyle())
#interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
interactor.SetRenderWindow(renwin)
 

# def Clip(object, event):
#     # object will be the boxWidget
#     global selectActor, planes
#     object.GetPlanes(planes)
#     selectActor.VisibilityOn()



ClipWidget = vtk.vtkBoxWidget()
#ClipWidget = vtk.vtkBoxWidget()
ClipWidget.GetFaceProperty().SetColor(0.6,0.6,0.2)
ClipWidget.GetFaceProperty().SetOpacity(0.25)
ClipWidget.SetInput(source)
ClipWidget.SetInteractor(interactor)
ClipWidget.SetPlaceFactor(1)
#ClipWidget.SetPlaceFactor(.2)
#ClipWidget.SetProp3D(SeedActor)
#ClipWidget.SetTransform(transf)
#ClipWidget.GetTransform(transf)
#ClipWidget.GetProp3D().SetUserTransform(transf)

#surf.ComputeBounds()
#print surf.GetWholeExtent()
#print surf.GetUpdateExtent()
b= surf.GetBounds()
bs=10
#ClipWidget.PlaceWidget(1*ws, -1*ws, 1*ws, -1*ws, 1*ws, -1*ws)##places widget without origin translation, centred on 3d centre
ClipWidget.PlaceWidget(2*(b[0]-b[1])/bs, 0*(b[0]-b[1])/bs, 1*(b[2]-b[3])/bs, -1*(b[2]-b[3])/bs, 1*(b[4]-b[5])/bs, -1*(b[4]-b[5])/bs)##places widget without origin translation, centred on x0-face centre
#ClipWidget.PlaceWidget()##places widget with origin translation according to the extent of the source
#ClipWidget.AddObserver("EndInteractionEvent", Clip)
#ClipWidget.On()
ClipWidget.Off()


planes = vtk.vtkPlanes()
clipper = vtk.vtkClipPolyData()
add_progress_observer(clipper)
#clipper.SetInputConnection(surfr.GetOutputPort())
clipper.SetInput(surf)
clipper.SetClipFunction(planes)
#clipper.InsideOutOn()
clipper.InsideOutOff()
#clipper.Update()
selectMapper = vtk.vtkPolyDataMapper()
#add_progress_observer(selectMapper)
#selectMapper.SetInputConnection(clipper.GetOutputPort())
#selectMapper.ScalarVisibilityOff()
#selectActor = vtk.vtkLODActor()
selectActor = vtk.vtkActor()
selectActor.SetMapper(selectMapper)
selectActor.GetProperty().SetColor(0, 1, 0)
selectActor.VisibilityOff()
#selectActor.SetScale(1.01, 1.01, 1.01)
selectActor.PickableOff()

lut = vtk.vtkLookupTable()
#lut.SetHueRange(0.0, 1.0)# This creates a red to blue lut.
#lut.SetHueRange(0.0, 0.667)# This creates a red to blue lut.
lut.SetHueRange(0.667, 0.0)# This creates a blue to red lut.
lut.Build()
#selectMapper.SetLookupTable(lut)

if options.voxelf:
    readerVolume = vtk.vtkMetaImageReader()
    readerVolume.SetFileName(options.voxelf)
    readerVolume.Update()

    voxeld= readerVolume.GetOutput()
    
    probe = vtk.vtkProbeFilter()
    add_progress_observer(probe)
    probe.SetInput(surf)
    probe.SetSource(voxeld)
    probe.Update()
    #surf= probe.GetOutput()
    surf.DeepCopy(probe.GetOutput())

    smapper.ScalarVisibilityOn()
    smapper.SetLookupTable(lut)
    #smapper.SetScalarModeToUsePointData ()
    smapper.SetColorModeToMapScalars()
    #smapper.SetColorModeToDefault()#unsigned char scalars are treated as colors, and NOT LUT mapped
    #smapper.InterpolateScalarsBeforeMappingOn ()
    #smapper.SetScalarModeToUsePointFieldData()
    #smapper.SelectColorArray("MetaImage")
    smapper.SetScalarRange(surf.GetScalarRange())
    

connectivity = vtk.vtkPolyDataConnectivityFilter()
add_progress_observer(connectivity)
connectivity.SetInput(surf)

surfw = vtk.vtkXMLPolyDataWriter()
add_progress_observer(surfw)

renderer.AddActor(selectActor)


interactor.Initialize()
interactor.Start()



