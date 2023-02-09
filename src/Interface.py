import numpy as np
import Util
import matplotlib.pyplot as plt


#===========================================================
class Interface:
#===========================================================
#
#   Classe représentant un dioptre entre deux couches
#
#===========================================================
    def __init__(self):
            # les points nodaux
        self.x=[]
        self.y=[]
            # les points de segmentation
        self.xgrid=[]
        self.ygrid=[]
        self.igrid=[]

        self.refractionAngle = None

            # Extension des interfaces à gauche et à droite
        self.extendLeft = 0
        self.extendRight = 0

    def setLayers(self,layer1,layer2):
        self.layer1 = layer1
        self.layer2 = layer2
        if layer1 != None:
            layer1.interface2 = self
        if layer2 != None:
            layer2.interface1 = self

    def calculateAngleLimitRefraction(self):
        v1 = self.layer1.v
        v2 = self.layer2.v
        self.refractionAngle = np.arcsin ( v1/v2 )

        # pour ajouter un point nodal
    def appendPoint(self,x,y):
        self.x.append(x)
        self.y.append(y)

    def calculateNormal(self,x1,y1,x2,y2):
        vector = np.array ( [x2-x1, y2-y1])
        normal = np.array ( [-vector[1], vector[0]], float )
        norm = np.sqrt ( normal[0] * normal[0] + normal[1] * normal [1] )
        normal[0] = normal[0] / norm
        normal[1] = normal[1] / norm
        return normal

        # calcul des normales des segments aux points nodaux
    def calculateNormals(self):
        n = len(self.x)
        if n >=2:
            self.nx0 = [0]*n    # normale à droite du 1er point nodal
            self.ny0 = [0]*n

                # pour chaque segment (i,i+1)
            for i in range(0,n-1):
                x1 = self.x[i]
                y1 = self.y[i]
                x2 = self.x[i+1]
                y2 = self.y[i+1]
                normal = self.calculateNormal (x1,y1,x2,y2)

                theta = np.arctan(normal[1]/normal[0]) if normal[0] > 0 else np.pi / 2

                self.nx0    [i] = normal[0]
                self.ny0    [i] = normal[1]



        # Fonction pour segmenter la ligne d'interface
        #   dseg est la distance entre deux points de segmentation
    def  calculateSegments(self,dseg):
        n = len(self.x)
        if n >=2:
            d0 = 0
            self.xgrid=[]
            self.ygrid=[]
            self.igrid=[]

                # le point nodal est le 1er point de segmentation
            self.xgrid.append (self.x[0])
            self.ygrid.append (self.y[0])
            self.igrid.append (0)

            for i in range(0,n-1):
                x1 = self.x[i]
                y1 = self.y[i]
                x2 = self.x[i+1]
                y2 = self.y[i+1]

                    # dnode : distance entre deux points nodaux
                dnode = np.sqrt ((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))

                    # d0 est la distance résiduelle qui n'a pas
                    # pu être incorporé dans le segment précédent

                while dnode + d0  >= dseg:
                        # on segmente
                    alpha = (dseg-d0)/dnode
                    xx = x1 + alpha * (x2-x1)
                    yy = y1 + alpha * (y2-y1)
                    self.xgrid.append ( xx )
                    self.ygrid.append ( yy )
                    self.igrid.append ( i  )
                    dnode -= (dseg-d0)
                    d0 = 0
                    x1 = xx
                    y1 = yy
                else:
                    d0 += dnode

    def locateSegment(self,x,y):
        n = len(self.x)
        if n >= 2:
            for i in range(0,n-1):
                x1 = self.x[i]
                y1 = self.y[i]
                x2 = self.x[i+1]
                y2 = self.y[i+1]
                if Util.isBetween (x,x1,x2) and Util.isBetween (y,y1,y2):
                    if Util.isClose(x1,x2):
                        if Util.isClose(x,x1):
                            return i
                    if Util.isClose(y1,y2):
                        if Util.isClose(y,y1):
                            return i
                    alpha = (y2-y1)/(x2-x1)
                    y0 = y1 + alpha * (x-x1)
                    if Util.isClose(y0,y):
                        return i
                    
            if x < self.x[0]:
                return 0
            if x > self.x[n-1]:
                return n-1
        return None


    def draw(self):
        n = len(self.x)
        if n >=2:
            for i in range(0,n-1):
                x1 = self.x[i]
                y1 = self.y[i]
                x2 = self.x[i+1]
                y2 = self.y[i+1]
                plt.plot ([x1,x2], [y1,y2], color='black', linewidth=1)

        self.drawNormals(self.scene.normalsLength)
        self.drawSegments()

    def drawSegments(self):
        if self.scene.showSegments:
            plt.plot( self.xgrid, self.ygrid, 'o', color='blue', markersize=2 )

        # alpha : facteur de grossissement des normales
    def drawNormals(self, alpha):
        if self.scene.showNormals:
            n = len(self.xgrid)
            for i in range(0,n):
                x1=self.xgrid[i]
                y1=self.ygrid[i]
                igrid=self.igrid[i]
                nx0=self.nx0[igrid]
                ny0=self.ny0[igrid]
                x2=x1+nx0*alpha
                y2=y1+ny0*alpha
                plt.plot ([x1,x2], [y1,y2], linewidth=0.5, color='blue')

