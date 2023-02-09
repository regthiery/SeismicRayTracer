import os
import numpy as np
import matplotlib.pyplot as plt
from moviepy.editor import ImageSequenceClip

from Interface import Interface
from Layer import Layer
from SeismicProfile import SeismicProfile


#===========================================================
class Scene:
#===========================================================
#
#   Classe principale regroupant tous les autres objets
#       nécessaire à une coupe sismqie
#
#===========================================================

    def __init__(self):
        self.xmin=0
        self.xmax= 4000
        self.ymax=200
        self.ymin= -2500
        self.interfaces = []
        self.layers = []
        self.dseg = 400
        self.profile = None
        self.logging = True
        self.filename = None

        self.ax = None
        self.fig = None

        self.incidentColor  = 'black'
        self.reflectedColor = 'black'
        self.refractedColor = 'black'
        self.conicColor     = 'black'

        self.incidentLineWidth  = 0.5
        self.reflectedLineWidth = 0.5
        self.refractedLineWidth = 0.5
        self.conicLineWidth     = 0.5

        self.showSegments = False
        self.showNormals  = False
        self.normalsLength = 50

        self.indexFocus = 0
        self.xFocus = 0
        self.yFocus = 0

        self.backRaysOnly = False
        self.showHodochrone = False
        self.annotate = False
        self.showConic = False

        self.isAnimating = False
        self.imagesFolderPath = "images"
        self.animationFileName = "animation.mp4"
        self.resImagesFolderPath = "resImages"
        self.hodochronesFolderPath = "hodochrones"
        self.showIncrement = False
        
        self.labelReflex = 0
        self.labelRefrac = 0
        self.labelConic  = 0
        
        self.rayIndex = None
        
        if not os.path.exists (self.imagesFolderPath):
            os.makedirs(self.imagesFolderPath)
        if not os.path.exists (self.resImagesFolderPath):
            os.makedirs(self.resImagesFolderPath)
        if not os.path.exists (self.hodochronesFolderPath):
            os.makedirs(self.hodochronesFolderPath)


    def setBounds(self,xmin,xmax,ymin,ymax):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

    def appendInterface (self):
        interface = Interface ()
        interface.scene = self
        self.interfaces.append (interface)
        return interface

    def appendLayer (self):
        layer = Layer ()
        layer . scene = self
        self.layers.append (layer)
        n = len (self.layers)

        colors = [ '#f1798b', '#f29083', '#f4af90', '#f7cfac', '#f8e4bf', '#d983bf', '#dc9d94', '#dccd8e', '#e8e8c2', '#d6eaea' ]
        layer.color = colors[n%10]

        return layer

    def prepareCalculations(self):

        for interface in self.interfaces:
            interface.calculateSegments (self.dseg)
            interface.calculateNormals()




    def parseFile(self, fileName):
        with open ("scripts/"+fileName+".txt", "r") as file:
            fileContent = file.read()

        lines = fileContent.strip().split("\n")
        data = {}
        current_section = None
        for line in lines:
            line = line.strip()
            index = line.find('#')
            if index != -1:
                line = line [:index]
                line.strip()
            # if line.startswith("#"):
            #   # c'est un commentaire dans le script -> ne rien faire
            #     continue
            if line == '':
                continue
            elif line.startswith("xmin"):
                data["xmin"] = int(line.split()[1])
            elif line.startswith("xmax"):
                data["xmax"] = int(line.split()[1])
            elif line.startswith("ymin"):
                data["ymin"] = int(line.split()[1])
            elif line.startswith("ymax"):
                data["ymax"] = int(line.split()[1])
            elif line.startswith("target"):
                data["target"] = line.split()[1]
            elif line.startswith("dseg"):
                data["dseg"] = float(line.split()[1])
            elif line.startswith("interface") or line.startswith("surface"):
                if "interfaces" not in data:
                    data["interfaces"] = []
                current_section = "interface"
                interface = {}
                interface["x"]=[]
                interface["y"]=[]
                data["interfaces"].append(interface)
            elif line.startswith("layer"):
                if "layers" not in data:
                    data["layers"] = []
                layer = {}
                layer ["v"] = float(line.split()[1])
                data["layers"].append(layer)
            elif line.startswith("incident"):
                tokens = line.split()
                data["incidentColor"] = tokens[1]
                if len(tokens) == 3:
                    data["incidentLineWidth"] = float(tokens[2])
            elif line.startswith("reflected"):
                tokens = line.split()
                data["reflectedColor"] = line.split()[1]
                if len(tokens) == 3:
                    data["reflectedLineWidth"] = float(tokens[2])
            elif line.startswith("refracted"):
                tokens = line.split()
                data["refractedColor"] = line.split()[1]
                if len(tokens) == 3:
                    data["refractedLineWidth"] = float(tokens[2])
            elif line.startswith("conic"):
                    data["conic"] = True
                    tokens = line.split()
                    if len(tokens) >= 2:
                        data["conicColor"] = line.split()[1]
                    if len(tokens) == 3:
                        data["conicLineWidth"] = float(tokens[2])

            elif line.startswith("showSegments"):
                    data["showSegments"] = True
            elif line.startswith("showNormals"):
                    data["showNormals"] = True
                    tokens = line.split()
                    if len(tokens) == 2:
                        data["normalsLength"] = float(tokens[1])

            elif line.startswith("indexFocus"):
                    data["indexFocus"] = int(line.split()[1])
            elif line.startswith("xFocus"):
                    data["xFocus"] = float(line.split()[1])
            elif line.startswith("yFocus"):
                    data["yFocus"] = float(line.split()[1])

            elif line.startswith("backRaysOnly"):
                    data["backRaysOnly"] = True
            elif line.startswith("annotate"):
                    data["annotate"] = True

            elif line.startswith("conic"):
                    data["conic"] = True


            elif line.startswith("animating"):
                    data["animating"] = True
            elif line.startswith("increment"):
                    data["increment"] = True

            elif line.startswith("hodochrone"):
                    data["hodochrone"] = True

            elif current_section == "surface" or current_section == "interface":
                if line != "":
                    if line[0].isdigit():
                        x, y = map(float, line.split())
                        interface["x"].append (x)
                        interface["y"].append (y)
                    elif line.startswith("extend"):
                        tokens = line.split()
                        interface["extend"] = [ float(tokens[1]), float(tokens[2]) ]
                else:
                    current_section = ""
        return data


    def buildFromScript(self,filename):
        self.filename=filename
        data = self.parseFile(filename)
        self.buildScene(data)


    def buildScene(self,data):
        if "xmin" in data:
            self.xmin = data["xmin"]
        if "xmax" in data:
            self.xmax = data["xmax"]
        if "ymin" in data:
            self.ymin = data["ymin"]
        if "ymax" in data:
            self.ymax = data["ymax"]
        if "target" in data:
            self.target = data["target"]
            if data["target"] != "all":
                self.target = int(data["target"])
            if self.rayIndex != None:
                self.target = self.rayIndex    
        if "dseg" in data:
            self.dseg = data["dseg"]
        if "interfaces" in data:
            nInterfaces = len (data["interfaces"])
            for k in range(0,nInterfaces):
                interface = self.appendInterface()
                n = len (data["interfaces"][k]["x"])
                for i in range(0,n):
                    x = data["interfaces"][k]["x"][i]
                    y = data["interfaces"][k]["y"][i]
                    interface.appendPoint(x,y)
                if "extend" in data["interfaces"][k]:
                    interface.extendLeft  = data["interfaces"][k]["extend"][0]
                    interface.extendRight = data["interfaces"][k]["extend"][1]
        if "layers" in data:
            nLayers = len (data["layers"])
            for k in range(0,nLayers):
                layer = self.appendLayer()
                layer.v = data["layers"][k]["v"]

        if "indexFocus" in data:
            self.indexFocus = data["indexFocus"]
        if "xFocus" in data:
            self.xFocus = data["xFocus"]
            self.indexFocus = -1
        if "yFocus" in data:
            self.yFocus = float(data["yFocus"])
            self.indexFocus = -1

        if "incidentColor" in data:
            self.incidentColor = data["incidentColor"]
        if "reflectedColor" in data:
            self.reflectedColor = data["reflectedColor"]
        if "refractedColor" in data:
            self.refractedColor = data["refractedColor"]
        if "conicColor" in data:
            self.conicColor = data["conicColor"]

        if "incidentLineWidth" in data:
            self.incidentLineWidth = data["incidentLineWidth"]
        if "reflectedLineWidth" in data:
            self.reflectedLineWidth = data["reflectedLineWidth"]
        if "refractedLineWidth" in data:
            self.refractedLineWidth = data["refractedLineWidth"]
        if "conicLineWidth" in data:
            self.conicLineWidth = data["conicLineWidth"]

        if "showSegments" in data:
            self.showSegments = True
        if "showNormals" in data:
            self.showNormals = True
        if "normalsLength" in data:
            self.normalsLength = data["normalsLength"]

        if "backRaysOnly" in data:
            self.backRaysOnly = True
        if "annotate" in data:
            self.annotate = True
        if "animating" in data:
            self.isAnimating = True
        if "increment" in data:
            self.showIncrement = True

        if "hodochrone" in data:
            self.showHodochrone = True

        if "conic" in data:
            self.showConic = True

        for k in range(0,nInterfaces):
            if k==0:
                layer1 = None
                layer2 = self.layers[0]
            else:
                layer1 = self.layers[k-1]
                if k == nLayers:
                    layer2 = None
                else:
                    layer2 = self.layers[k]
            self.interfaces[k].setLayers (layer1, layer2)

        self.prepareCalculations()

        profile = SeismicProfile()
        profile.setScene (self)

        return self

    def calculate(self):
        self.profile.calculateRays(self.target)


        # Code pour créer le graphique

    def closeWindow(self,event):
        if event.key == 'cmd+w':
            plt.close(self.fig)

    def prepareDraw(self):
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.fig.canvas.mpl_connect('key_press_event',self.closeWindow)
        self.ax.set_xlim (self.xmin, self.xmax)
        self.ax.set_ylim (self.ymin, self.ymax)
        self.ax.set_aspect ('equal')
        self.ax.spines['top'].set_visible(False)
        plt.xlabel("Distance (mètres)")
        plt.ylabel("Profondeur (mètres)")
        plt.title("Coupe")


    def finishDraw(self):
        plt.legend()
        filename = "{}/{}.png".format(self.resImagesFolderPath,self.filename)
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.show()
        plt.close(self.fig)

    def drawProfile(self):
        for layer in self.layers:
            layer.drawFilling()

        for interface in self.interfaces:
            interface.draw()

        self.labelReflex = 0
        self.labelRefrac = 0
        self.labelConic  = 0
        self.profile.draw()

    def drawHodochrone(self):
        if self.showHodochrone == False:
            return

        plt.clf()
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.fig.canvas.mpl_connect('key_press_event',self.closeWindow)
        plt.xlabel("Distance épicentrale (mètres)")
        plt.ylabel("Temps (seconde)")
        plt.title("Hodochrone")
        plt.grid()
        self.profile.drawHodochrone()
        filename = "{}/h{}.png".format (self.hodochronesFolderPath, self.filename)
        plt.savefig(filename, dpi=300, bbox_inches='tight')

    def draw(self):
        self.prepareDraw()
        self.drawProfile()
        self.finishDraw()

    def eraseImagesFolder(self):
        if not os.path.exists (self.imagesFolderPath):
            os.makedirs(self.imagesFolderPath)
        files = os.listdir(self.imagesFolderPath)
        for file in files:
            filePath = os.path.join(self.imagesFolderPath, file)
            if os.path.exists(filePath):
                os.remove(filePath)

    def buildAnimation(self):
        self.eraseImagesFolder()
        n = len(self.interfaces[0].xgrid)
        for k in range(0,n):
            print ("Process {}/{} image".format(k,n-1))
            self.indexFocus = k
            self.calculate()
            plt.clf()
            self.prepareDraw()
            self.drawProfile()
            filename = "{}}/{}-{:04d}.png".format(self.imagesFolderPath,self.filename,k)
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close(self.fig)
            self.profile.clear()
            self.profile.setScene(self)

        clip = ImageSequenceClip(self.imagesFolderPath, fps=30)
        clip.write_videofile(self.animationFileName)
