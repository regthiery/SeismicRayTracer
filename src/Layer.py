from matplotlib.patches import Polygon

#===========================================================
class Layer:
#===========================================================
#
#   Classe représentant une couche.
#   Une couche est délimitée par deux interfaces
#       et est caractérisée par sa vitesse
#
#===========================================================
    def __init__(self):
        self.v = 0
        self.interface1 = None
        self.interface2 = None
        self.color = 'yellow'
        self.scene=None

    def setInterfaces(self,interface1,interface2):
        self.interface1 = interface1
        self.interface2 = interface2
        if interface1 != None:
            interface1.layer2 = self
        if interface2 != None:
            interface2.layer1 = self

    def drawFilling (self):
        points = []
        if self.interface1 != None:
            len1 = len (self.interface1.x)
            for i in range(0,len1):
                x = self.interface1.x[i]
                y = self.interface1.y[i]
                points.append( [x,y])
        if self.interface2 != None:
            len2 = len (self.interface2.x)
            for i in range(len2-1,-1,-1):
                x = self.interface2.x[i]
                y = self.interface2.y[i]
                points.append( [x,y])
        else:
            points.append ( [self.scene.xmax,self.scene.ymin] )
            points.append ( [self.scene.xmin,self.scene.ymin] )

        polygon = Polygon(points, facecolor=self.color)
        self.scene.ax.add_patch (polygon)
