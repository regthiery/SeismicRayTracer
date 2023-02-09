import numpy as np
import matplotlib.pyplot as plt
from moviepy.editor import ImageSequenceClip

from src.Ray import Ray

#===========================================================
class SeismicProfile:
#===========================================================
#
#   Classe utilisée pour calculer les trajets des  ondes
#
#===========================================================

    def __init__(self):
        self.ray = Ray()
        self.scene = None
        self.ray.setRoot()

    def clear(self):
        self.ray = Ray()
        self.ray.setRoot()

    def setScene(self,scene):
        self.scene = scene
        self.ray.setScene(scene)
        scene.profile = self

    def calculateRays(self,target):
        nInterfaces = len (self.scene.interfaces)

        if self.scene.showConic == True:
            self.calculateConicRaysFor(target)

        if nInterfaces >= 3 :
            self.calculateRefractionRaysFor(target)
        else:
            self.calculateReflectionRaysFor(target)

    def calculateReflectionRaysFor(self,target):
        self.ray.setInterfaces(0,1,0)
        self.ray.calculateReflectionPathsForTargets(target)

    def calculateRefractionRaysFor(self,target):
        self.ray.setInterfaces(0,1,2)
        self.ray.calculateRefractionPathsForTargets(target)

    def calculateConicRaysFor(self,target):
        self.ray.setInterfaces(0,1,0)
        self.ray.calculateConicPathsForTargets(target)

    def draw (self):
        if self.scene.showIncrement:
            i = 0
            self.scene.eraseImagesFolder()
            for ray in self.ray.children:
                ray.draw()
                filename = "images/{}-{:04d}.png".format(self.scene.filename,i)
                plt.savefig(filename, dpi=300, bbox_inches='tight')
                i = i + 1
            clip = ImageSequenceClip(self.scene.imagesFolderPath, fps=30)
            clip.write_videofile(self.scene.animationFileName)
        else:    
            for ray in self.ray.children:
                    ray.draw()

    def drawHodochrone(self):
        dmin = self.scene.xmin
        dmax = self.scene.xmax
        tmin = 0
        tmax = 0

        dreflex = []
        treflex = []
        dconic  = []
        tconic  = []
        drefrac = []
        trefrac = []

        for ray in self.ray.children:
            if ray.type == 'reflex':
                if ray.d>= dmin and ray.d <=dmax:
                    dreflex.append (ray.d)
                    treflex.append (ray.t)
                    if self.scene.annotate:
                        plt.annotate( "{}".format(ray.k2), (ray.d, ray.t), textcoords='offset points', xytext=(-1,-12), fontsize=8 )
                    if ray.d <= dmax:
                        if tmax < ray.t:
                            tmax = ray.t
            elif ray.type == 'conic':
                dconic.append (ray.d)
                tconic.append (ray.t)
                if ray.d <= dmax:
                    if tmax < ray.t:
                        tmax = ray.d
            elif ray.type == 'refrac':
                res = ray.calculatePropagationTimeToSurface()
                if res != None:
                    [tt,dd] = res
                    if self.scene.annotate:
                        plt.annotate( "{}".format(ray.k2), (dd, tt), textcoords='offset points', xytext=(-1,12), fontsize=8 )
                    if dd <= dmax:    
                        if tmax < tt:
                            tmax = tt
                    drefrac.append (dd)
                    trefrac.append (tt)
                    


        self.scene.ax.set_ylim (tmin, tmax + 0.1*(tmax-tmin))
        self.scene.ax.set_xlim (dmin, dmax )
        
        if len(dreflex)>0:
            plt.plot ( dreflex, treflex, '-o', color=self.scene.reflectedColor, label='Onde réfléchie')
        if len(dconic)>0:            
            plt.plot ( dconic , tconic , '-o', color=self.scene.conicColor , label='Onde conique')
        if len(drefrac)>0:            
            plt.plot ( drefrac , trefrac , '-o', color=self.scene.refractedColor , label='Onde réfractée')

        v = self.scene.interfaces[0].layer2.v
        xdirect = []
        step = (dmax-dmin)/100
        for i in range (0,101):
            xdirect.append(dmin+i*step)

        ddirect = []
        tdirect = []
        if self.scene.indexFocus == -1:
            xFocus = self.scene.xFocus
            yFocus = self.scene.yFocus
        else:
            xFocus = self.scene.interfaces[0].xgrid[self.scene.indexFocus]
            yFocus = self.scene.interfaces[0].ygrid[self.scene.indexFocus]

        for xx in xdirect:
            dd = np.sqrt( yFocus*yFocus + xx*xx )
            tt = dd / v
            ddirect.append (xx)
            tdirect.append (tt)

        plt.plot ( ddirect, tdirect, '-', color='red', label='Onde directe')
        plt.legend()

