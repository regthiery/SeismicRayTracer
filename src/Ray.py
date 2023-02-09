import numpy as np
import Util
import matplotlib.pyplot as plt

#===========================================================
class Ray:
#===========================================================
#
#   Classe gérant un rai sismique et tous ses descendants
#       sous forme d'un arbre
#
#===========================================================

    def __init__(self):
        self.interface1 = None
        self.interface2 = None
        self.interface3 = None
        self.i1 = -1
        self.i2 = -1
        self.i3 = -1
        self.k1 = None
        self.k2 = None
        self.type = None
        self.x1 = None
        self.y1 = None
        self.x2 = None
        self.y2 = None
        self.x3 = None
        self.y3 = None
        self.scene = None
        self.father = None
        self.children = []
        self.isRoot = False
        self.v = None
        self.v1 = None
        self.v2 = None
        self.igrid = None
        self.level = 0
        self.direction = None
        self.refractionAngle = None

    def setScene(self, scene):
        self.scene = scene

    def setRoot(self):
        self.isRoot = True

    def setDirection(self,direction):
        self.direction = direction

    def appendChild (self,ray):
        self.children.append (ray)
        ray.father = self
        ray.level = self.level+1
        ray.log()

    def setInterfaces(self, i1, i2, i3):
        if i1 != -1:
            self.interface1 = self.scene.interfaces[i1]
            self.i1 = i1
        if i2 != -1:
            self.interface2 = self.scene.interfaces[i2]
            self.i2 = i2
        if i3 != -1:
            self.interface3 = self.scene.interfaces[i3]
            self.i3 = i3

    def setSourcePoint(self,k1,x1,y1):
        self.k1 = k1
        if k1 != -1:
            n = len (self.interface1.xgrid)
            if k1 <0 or k1 >= n:
                print ("Script error: you have defined a target index {} for only {} segmentation points.".format(k1,n))
                exit()
            self.x1 = self.interface1.xgrid[k1]
            self.y1 = self.interface1.ygrid[k1]
        else:
            self.x1 = x1
            self.y1 = y1

    def setTargetPoint(self,x2,y2):
        self.x2 = x2
        self.y2 = y2
        self.igrid = self.interface2.locateSegment(x2,y2)
        self.k2 = -1


    def setSpeeds(self):
        self.v  = self.interface2.layer1.v
        if self.direction == 'down' or self.direction == 'downUp':
            self.v1 = self.interface2.layer1.v
            self.v2 = self.interface2.layer2.v
        else:
            self.v1 = self.interface2.layer2.v
            self.v2 = self.interface2.layer1.v

    def log(self):
        if self.scene.logging:
            if self.type == 'reflex':
                print ("{}Ray {:1d} {:04} {} {} ({:.2f}:{:.2f}) ({:.2f}:{:.2f}) ({:.2f}:{:.2f}) :\t {:.4f} {:.2f}".format( '\t'*self.level, self.level, self.k2, self.type, self.direction,  self.x1, self.y1, self.x2, self.y2, self.x3, self.y3, self.t, self.d))
            elif self.type == 'reflex2':
                print ("{}Ray {:1d} {:04} {} {} ({:.2f}:{:.2f}) ({:.2f}:{:.2f}) ({:.2f}:{:.2f})".format( '\t'*self.level, self.level, self.k2, self.type, self.direction,  self.x1, self.y1, self.x2, self.y2, self.x3, self.y3))
            elif self.type == 'refrac':
                print ("{}Ray {:1d} {:04} {} {} ({:.2f}:{:.2f}) ({:.2f}:{:.2f}) ({:.2f}:{:.2f})".format( '\t'*self.level, self.level, self.k2, self.type, self.direction,  self.x1, self.y1, self.x2, self.y2, self.x3, self.y3))
            if self.type == 'conic':
                print ("{}Ray {:1d} {:04} {} {} ({:.2f}:{:.2f}) ({:.2f}:{:.2f}) ({:.2f}:{:.2f}) ({:.2f}:{:.2f}) :\t {:.4f} {:.2f}".format( '\t'*self.level, self.level, self.k2, self.type, self.direction,  self.x1, self.y1, self.x4, self.y4, self.x2, self.y2, self.x3, self.y3, self.t, self.d))


    def calculateRayReflectionPoint(self):
        incident = np.array ( [self.x2-self.x1,self.y2-self.y1], float)
        igrid = self.igrid
        nx = self.interface2.nx0[igrid]
        ny = self.interface2.ny0[igrid]
        normal = np.array ( [nx,ny] )
        reflex = incident - 2 * (np.dot(incident,normal)) * normal
        self.x3 = self.x2 + reflex[0] * 1e4
        self.y3 = self.y2 + reflex[1] * 1e4
        res0 = Util.findIntersectionWithInterface(self.x2, self.y2, self.x3, self.y3, self.interface3)
        
            # is there secondary reflection point ?
        res1 = Util.findIntersectionWithInterface (self.x2, self.y2, self.x3, self.y3, self.interface2)
        if res1 !=  None :
            self.type = "reflex2" 
            self.x3 = res1[0]
            self.y3 = res1[1]
            return True
        
        
        if res0 == None:
            return False
        else:
            self.x3 = res0[0]
            self.y3 = res0[1]
            self.type = "reflex"
            self.v = self.interface2.layer1.v
            self.dist1 = np.sqrt ((self.x1-self.x2)*(self.x1-self.x2)+(self.y1-self.y2)*(self.y1-self.y2))
            self.dist2 = np.sqrt ((self.x2-self.x3)*(self.x2-self.x3)+(self.y2-self.y3)*(self.y2-self.y3))
            self.dist3 = np.sqrt ((self.x1-self.x3)*(self.x1-self.x3)+(self.y1-self.y3)*(self.y1-self.y3))
            self.t1 = self.dist1 / self.v
            self.t2 = self.dist2 / self.v
            self.t = self.t1 + self.t2
            self.d = self.dist3
            return True


    def calculateRayRefractionPoint(self):
        incident = np.array ( [self.x2-self.x1,self.y2-self.y1], float)
        igrid = self.igrid
        nx = self.interface2.nx0[igrid]
        ny = self.interface2.ny0[igrid]
        normal = np.array ( [nx,ny] )
        if self.direction == 'up':
            normal = -normal

        sini = (self.x2-self.x1)*normal[1] - (self.y2-self.y1)*normal[0]
        sini /= np.sqrt ( (self.x2-self.x1)*(self.x2-self.x1) + (self.y2-self.y1)*(self.y2-self.y1) )
        val0 = sini * self.v2 / self.v1

        if val0 >= -1 and val0 <= 1.0 :
            r = np.arcsin( self.v2*sini/self.v1)
            vector1 = [0.0]*2
            vector1[0] = np.cos(r) * (-normal[0]) - np.sin(r) * (-normal[1])
            vector1[1] = np.sin(r) * (-normal[0]) + np.cos(r) * (-normal[1])

                    # r = vector - 2 * (np.dot(vector,normal)) * normal
            self.x3 = self.x2 + vector1[0] * 1e4
            self.y3 = self.y2 + vector1[1] * 1e4

            res = Util.findIntersectionWithInterface(self.x2, self.y2, self.x3, self.y3, self.interface3)

            if res == None:
                return False

            self.x3 = res[0]
            self.y3 = res[1]
            self.type = "refrac"

            return True

        return False
    
    
    def recursiveSecondaryReflexionPoint(self):
        ray = Ray()
        ray.setScene(self.scene)
        ray.setInterfaces(self.i2,self.i2,self.i3)
        ray.setSourcePoint(-1, self.x2,self.y2)
        ray.setDirection('downUp')
        ray.setTargetPoint(self.x3, self.y3)
        res = ray.calculateRayReflectionPoint()
        if res == True:
            self.appendChild(ray) 
            if ray.type == 'reflex2':
                ray.recursiveSecondaryReflexionPoint()
            return True           
        return False


    def recursiveRefractionPoint(self):
        ray = Ray ()
        ray.setScene(self.scene)
        ninterfaces = len (self.scene.interfaces)
        if self.i3 >= (ninterfaces-1):
            return False
        if self.direction == 'down':
            ray.setInterfaces(self.i2,self.i3,self.i3+1)
            ray.setDirection ('down')
            ray.setSourcePoint(-1,self.x2,self.y2)
            ray.setTargetPoint(self.x3,self.y3)
        elif self.direction == 'downUp' or self.direction == 'up' :
            if self.i3 == 0:
                return  False
            ray.setInterfaces(self.i2,self.i3,self.i3-1)
            ray.setSourcePoint(-1,self.x2,self.y2)
            ray.setTargetPoint(self.x3,self.y3)
            ray.setDirection('up')

        ray.setSpeeds()
        res = ray.calculateRayRefractionPoint()
        if res:
            if self.direction == 'down':
                ray.setDirection ( 'down' )
            elif self.direction == 'downUp':
                ray.setDirection ( 'up' )
            self.appendChild(ray)
            ray.recursiveRefractionPoint()
            return True
        else:
            if ray.direction == 'down' :
                ray.setInterfaces(self.i2,self.i3,self.i2)
                ray.setDirection('downUp')
                ray.setSpeeds()
                res = ray.calculateRayReflectionPoint()
                if res:
                    self.appendChild(ray)
                    ray.recursiveRefractionPoint()
                    return True

        return False

    def calculateSecondaryReflectionPoint(self):
        ray = Ray()
        ray.setScene(self.scene)
        ray.setInterfaces(self.i2,self.i2,self.i3)
        ray.setSourcePoint(-1, self.x2,self.y2)
        ray.setDirection('downUp')
        ray.setTargetPoint(self.x3, self.y3)
        res = ray.calculateRayReflectionPoint()
        if res == True:
            ray.type = 'reflex2'
            self.appendChild(ray) 
            return True           
        return False


        # Cette fonction calcule le rayon réfléchi sur un point de segmentation
        # de l'interface
    def calculateReflectionPoint(self, k2):

            # les coordonnées du point cible sur son interface
        self.k2 = k2
        self.x2 = self.interface2.xgrid[k2]
        self.y2 = self.interface2.ygrid[k2]

        res = Util.detectIntersectionWithInterface (self.x1, self.y1, self.x2, self.y2, self.interface2)

        if res:
                # le point cible se trouve dans une zone d'ombre
                # car le rayon intersecte l'interface en un autre point.
                # Le calcul est donc abandonné.
            return False
        else:
            incident = np.array ( [self.x2-self.x1,self.y2-self.y1], float)
            igrid = self.interface2.igrid[self.k2]
            nx = self.interface2.nx0[igrid]
            ny = self.interface2.ny0[igrid]
            normal = np.array ( [nx,ny] )
            reflex = incident - 2 * (np.dot(incident,normal)) * normal
            self.x3 = self.x2 + reflex[0] * 1e4
            self.y3 = self.y2 + reflex[1] * 1e4

            res0 = Util.findIntersectionWithInterface(self.x2, self.y2, self.x3, self.y3, self.interface3)
            
                # is there secondary reflection point ?
            res1 = Util.findIntersectionWithInterface (self.x2, self.y2, self.x3, self.y3, self.interface2)
            if res1 !=  None :
                self.type = "reflex2" 
                self.x3 = res1[0]
                self.y3 = res1[1]
                # self.calculateSecondaryReflectionPoint()
                return True
                

            if res0 == None and self.scene.backRaysOnly:
                return False

            if res0 != None:
                self.x3 = res0[0]
                self.y3 = res0[1]

            self.type = "reflex"
            self.level = 1
            self.direction = 'downUp'

            self.v = self.interface2.layer1.v
            self.dist1 = np.sqrt ((self.x1-self.x2)*(self.x1-self.x2)+(self.y1-self.y2)*(self.y1-self.y2))
            self.dist2 = np.sqrt ((self.x2-self.x3)*(self.x2-self.x3)+(self.y2-self.y3)*(self.y2-self.y3))
            self.dist3 = np.sqrt ((self.x1-self.x3)*(self.x1-self.x3))
            self.t1 = self.dist1 / self.v
            self.t2 = self.dist2 / self.v
            self.t = self.t1 + self.t2
            self.d = self.dist3

            return True


        # Cette fonction calcule le rayon réfracté sur un point de segmentation
        # de l'interface
    def calculateRefractionPoint(self, k2):

            # les coordonnées du point cible sur son interface
        self.k2 = k2
        self.x2 = self.interface2.xgrid[k2]
        self.y2 = self.interface2.ygrid[k2]
        self.igrid = self.interface2.igrid[self.k2]

        res = Util.detectIntersectionWithInterface (self.x1, self.y1, self.x2, self.y2, self.interface2)

        if res:
                # le point cible se trouve dans une zone d'ombre
                # car le rayon intersecte l'interface en un autre point.
                # Le calcul est donc abandonné.
            return False
        else:

            res = self.calculateRayRefractionPoint()

            if res == False:
                    # le calcul du rayon réfracté a échoué
                    # on calcule le rayon réfléchi
                self.setInterfaces(self.i1,self.i2,self.i1)
                self.setSpeeds()
                res = self.calculateReflectionPoint(k2)

            return res

    def calculateConicRefractionPoint (self,k2):

            # les coordonnées du point cible sur son interface
        self.k2 = k2
        self.x2 = self.interface2.xgrid[k2]
        self.y2 = self.interface2.ygrid[k2]
        self.igrid = self.interface2.igrid[self.k2]

        self.refractionAngle = np.arcsin ( self.v1/self.v2 )

        incident = np.array ( [self.x1-self.x2,self.y1-self.y2], float)
        igrid = self.interface2.igrid[self.k2]
        nx = self.interface2.nx0[igrid]
        ny = self.interface2.ny0[igrid]
        normal = np.array ( [nx,ny] )

        cosa = incident[0]*nx + incident[1]*ny
        cosa = cosa / np.sqrt ( incident[0]*incident[0] + incident[1]*incident[1])
        angle = np.arccos(cosa)

        if abs(angle) < self.refractionAngle:
            return False

        angle = self.refractionAngle
        if self.x2 > self.x1:
            angle = -angle

        res = Util.searchDestInterfacePointWithAngle (self.x1, self.y1, self.interface2, angle)

        if res == False:
            return False

        self.x4 = res[0]
        self.y4 = res[1]

        if self.x2 < self.x1:
            if self.x4 < self.x2:
                return False
        else:
            if self.x4 > self.x2:
                return False


        angle = self.refractionAngle
        if self.x2 < self.x1:
            angle = -angle
        res = Util.searchSrcInterfacePointWithAngle (self.x2, self.y2, nx, ny, self.interface3, angle)

        if res == False:
            return False

        self.x3 = res[0]
        self.y3 = res[1]
        self.type = "conic"

        self.dist1 = np.sqrt ((self.x1-self.x4)*(self.x1-self.x4)+(self.y1-self.y4)*(self.y1-self.y4))
        self.dist2 = np.sqrt ((self.x4-self.x2)*(self.x4-self.x2)+(self.y4-self.y2)*(self.y4-self.y2))
        self.dist3 = np.sqrt ((self.x2-self.x3)*(self.x2-self.x3)+(self.y3-self.y2)*(self.y3-self.y2))
        self.t1 = self.dist1 / self.v1
        self.t2 = self.dist2 / self.v2
        self.t3 = self.dist3 / self.v1

        self.t = self.t1 + self.t2 + self.t3
        self.d = abs(self.x3-self.x1)

        self.level = 1
        self.direction = 'downUp'

        return True




        # Cette fonction calcule les rayons réfléchis à partir de la surface
        #       et qui reviennent sur la surface
    def calculateReflectionPathsForTargets(self, target):
        if self.isRoot:
            n = len (self.interface2.xgrid)
            if target == "all" :
                theRange = range(0,n)
            else:
                if target >= 0 and target < n:
                    theRange = range (target,target+1)
                else:
                    return

            for k in theRange:
                ray = Ray()
                ray.setScene (self.scene)
                ray.setInterfaces (0,1,0)
                ray.setSourcePoint (self.scene.indexFocus, self.scene.xFocus, self.scene.yFocus )
                res = ray.calculateReflectionPoint (k)
                if res == True:
                    if ray.type == 'reflex2':
                        self.appendChild (ray)
                        ray.recursiveSecondaryReflexionPoint()
                    elif ray.type == 'reflex':                       
                        self.appendChild (ray)

        # Cette fonction calcule les rayons réfractés
    def calculateRefractionPathsForTargets(self,target):
        if self.isRoot:
            n = len (self.interface2.xgrid)
            if target == "all" :
                theRange = range(0,n)
            else:
                if target >= 0 and target < n:
                    theRange = range (target,target+1)
                else:
                    return

            for k in theRange:
                ray = Ray()
                ray.setScene (self.scene)
                ray.setInterfaces ( self.i1,self.i2,self.i3)
                ray.setSourcePoint (self.scene.indexFocus, self.scene.xFocus, self.scene.yFocus )
                ray.setDirection('down')
                ray.setSpeeds()
                res = ray.calculateRefractionPoint (k)
                if res == True:
                    if ray.type == 'refrac':
                        ray.direction = 'down'
                        self.appendChild (ray)
                        ray.recursiveRefractionPoint()
                    elif ray.type == 'reflex':
                        ray.direction = 'downUp'
                        self.appendChild (ray)
                        ray.recursiveRefractionPoint()


    def calculateConicPathsForTargets(self,target):
        if self.isRoot:
            n = len (self.interface2.xgrid)
            if target == "all" :
                theRange = range(0,n)
            else:
                if target >= 0 and target < n:
                    theRange = range (target,target+1)
                else:
                    return

            for k in theRange:
                ray = Ray()
                ray.setScene (self.scene)
                ray.setInterfaces ( self.i1,self.i2,self.i3)
                ray.setSourcePoint (self.scene.indexFocus, self.scene.xFocus, self.scene.yFocus )
                ray.setDirection('downUp')
                ray.setSpeeds()
                ray.refractionAngle = np.arcsin ( ray.v1/ray.v2 )
                res = ray.calculateConicRefractionPoint (k)
                if res != False:
                    self.appendChild (ray)


        # Cette focntion calcule le temps de retour d'une onde refractée et de ses descendantes 
        # jusqu'à la surface (le cas échéant)
    def calculatePropagationTimeToSurface(self):
        if self.type != 'refrac':
            return None
        
        d1 = np.sqrt( (self.x1-self.x2)*(self.x1-self.x2) + (self.y1-self.y2)*(self.y1-self.y2))
        t1 = d1/self.v1
        d2 = np.sqrt( (self.x2-self.x3)*(self.x2-self.x3) + (self.y2-self.y3)*(self.y2-self.y3))
        t1 = d1/self.v1
        t2 = d2/self.v2
        tt = t1+t2
        
        xfirst = self.x1
        lastInterface = self.interface3
        
        n = len(self.children)
        if n == 0:
            ray = None
        else:    
            ray = self.children[0]

        while ray != None:
            if ray.type == 'refrac':
                d2 = np.sqrt( (ray.x2-ray.x3)*(ray.x2-ray.x3) + (ray.y2-ray.y3)*(ray.y2-ray.y3))
                t2 = d2/ray.v2
                tt = tt + t2
            elif ray.type == 'reflex' or ray.type == 'reflex2' :
                d2 = np.sqrt( (ray.x2-ray.x3)*(ray.x2-ray.x3) + (ray.y2-ray.y3)*(ray.y2-ray.y3))
                t2 = d2/ray.v
                tt = tt + t2

            xlast = ray.x3
            lastInterface = ray.interface3

            n = len(ray.children)
            if n == 0:
                ray = None
            else:    
                ray = ray.children[0]

        if lastInterface != self.scene.interfaces[0]:
            return None
            
        return [tt,xlast-xfirst]

    def draw (self):

        if self.type == 'reflex' or self.type == 'refrac' or self.type == 'reflex2' :
            xx = [ self.x1, self.x2 ]
            yy = [ self.y1, self.y2 ]
            if self.scene.incidentColor != "hidden":
                plt.plot ( xx, yy, '-' , color=self.scene.incidentColor, linewidth=0.5)
            xx = [ self.x2, self.x3 ]
            yy = [ self.y2, self.y3 ]
            if self.type == "reflex" or self.type == "reflex2" :
                if self.scene.reflectedColor != "hidden":
                    if self.scene.labelReflex == 0:
                        plt.plot ( xx, yy, '-' , color=self.scene.reflectedColor, linewidth=self.scene.reflectedLineWidth, label="Onde réfléchie")
                        self.scene.labelReflex = 1
                    else:    
                        plt.plot ( xx, yy, '-' , color=self.scene.reflectedColor, linewidth=self.scene.reflectedLineWidth )
            elif self.type == "refrac":
                if self.scene.refractedColor != "hidden":
                    if self.scene.labelRefrac == 0:
                        plt.plot ( xx, yy, '-' , color=self.scene.refractedColor, linewidth=self.scene.refractedLineWidth, label="Onde réfractée")
                        self.scene.labelRefrac = 1
                    else:    
                        plt.plot ( xx, yy, '-' , color=self.scene.refractedColor, linewidth=self.scene.refractedLineWidth )

        elif self.type == "conic":
            xx = [ self.x1, self.x4, self.x2, self.x3 ]
            yy = [ self.y1, self.y4, self.y2, self.y3 ]
            if self.scene.conicColor != "hidden":
                if self.scene.labelConic == 0:
                    plt.plot ( xx, yy, '-' , color=self.scene.conicColor, linewidth=self.scene.conicLineWidth, label="Onde conique")
                    self.scene.labelConic = 1
                else:    
                    plt.plot ( xx, yy, '-' , color=self.scene.conicColor, linewidth=self.scene.conicLineWidth )


        for ray in self.children:
            ray.draw()

