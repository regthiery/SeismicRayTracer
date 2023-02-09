import math
import numpy as np

    # Cette fonction cherche si les deux segments [point1,point2] et [point3,point4]
    # s'intersectent
def checkSegmentsIntersection (x1,y1,x2,y2,x3,y3,x4,y4):
    d = (x2-x1)*(y4-y3) - (x4-x3)*(y2-y1)
    if d == 0:
        return False
    u = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / d
    v = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / d

    if isClose (u,1):
        return False
    if isClose (u,0):
        return False
    if isClose (v,1):
        return False
    if isClose (u,0):
        return False

    return (0 < u < 1) and (0 < v < 1)

    # Cette fonction vérfie si x est compris entre x1 et x2
def isBetween(x,x1,x2):
    if ((math.isclose(x,x1,rel_tol=1e-10) or x > x1) and (math.isclose(x,x2,rel_tol=1e-10) or x < x2)) or\
    ((math.isclose(x,x2,rel_tol=1e-10) or x > x2) and (math.isclose(x,x1,rel_tol=1e-10) or x < x1)):
        return True
    else:
        return False

    # Cette fonction regarde si x est égal à x0
def isClose(x,x0):
	return math.isclose(x, x0, rel_tol=1e-10)

    # Cette fonction calcule le point d'intersection entre les deux segments
    # (point1,point2) e (point3,point4)
def findSegmentsIntersection (x1,y1,x2,y2,x3,y3,x4,y4):
    a1 = y2 - y1
    b1 = x1 - x2
    c1 = a1 * x1 + b1 * y1

    a2 = y4 - y3
    b2 = x3 - x4
    c2 = a2 * x3 + b2 * y3

    det = a1 * b2 - a2 * b1
    if det == 0:
        return None

    x = (b2 * c1 - b1 * c2) / det
    y = (a1 * c2 - a2 * c1) / det


    if ( isBetween (x,x1,x2) and isBetween (y,y1,y2)) and isBetween(x,x3,x4) and isBetween(y,y3,y4):
        return (x,y)
    else:
        return None

    # Cette fonction cherche le point le long de l'interface de destination
    #   qui fait un angle alpha avec le rayon incident et la normale à cette interface
    #       x1,y1 : coordonnées du poit de destination
    #       interface : interface de desitination
    #       alpha: angle limite de réfraction

def searchDestInterfacePointWithAngle (x1,y1,interface,alpha):
    n = len (interface.xgrid)
    # cosa = np.cos(alpha)
    sina = np.sin(alpha)
    tga  = np.tan(alpha)

        # on cherche d'abord sur l'extension à gauche de l'interface
    if interface.extendLeft != 0:
        x3 = interface.xgrid[0]-interface.extendLeft
        y3 = interface.ygrid[0]
        x4 = interface.xgrid[0]
        y4 = interface.ygrid[0]
        nx = interface.nx0[0]
        ny = interface.ny0[0]

        incident3 = np.array ( [x1-x3, y1-y3] )
        incident4 = np.array ( [x1-x4, y1-y4] )
        normal = np.array ( [nx, ny])

        cos3 = incident3[0] * nx + incident3[1] * ny
        cos4 = incident4[0] * nx + incident4[1] * ny

        norm3 = np.sqrt ( incident3[0] * incident3[0] + incident3[1] * incident3[1] )
        norm4 = np.sqrt ( incident4[0] * incident4[0] + incident4[1] * incident4[1] )

        cos3 = cos3 / norm3
        cos4 = cos4 / norm4

        sin3 = np.sqrt (1 - cos3*cos3)
        sin4 = np.sqrt (1 - cos4*cos4)

        c3 = np.cross (incident3, normal)
        c4 = np.cross (incident4, normal)

        if c3 < 0:
            sin3 = -sin3

        if c4 < 0:
            sin4 = -sin4

        tg3 = sin3 / cos3
        tg4 = sin4 / cos4

        if isBetween (tga, tg3, tg4):
            x = x3 + (tga-tg3) * (x4-x3) / ( tg4 -  tg3 )
            y = y3 + (tga-tg3) * (y4-y3) / ( tg4 -  tg3 )
            return [ x, y ]

    for i in range(0,n-1):
        x3 = interface.xgrid[i]
        y3 = interface.ygrid[i]
        x4 = interface.xgrid[i+1]
        y4 = interface.ygrid[i+1]
        igrid = interface.igrid[i]

        nx = interface.nx0[igrid]
        ny = interface.ny0[igrid]

        incident3 = np.array ( [x1-x3, y1-y3] )
        incident4 = np.array ( [x1-x4, y1-y4] )
        normal = np.array ( [nx, ny])

        cos3 = incident3[0] * nx + incident3[1] * ny
        cos4 = incident4[0] * nx + incident4[1] * ny

        norm3 = np.sqrt ( incident3[0] * incident3[0] + incident3[1] * incident3[1] )
        norm4 = np.sqrt ( incident4[0] * incident4[0] + incident4[1] * incident4[1] )

        cos3 = cos3 / norm3
        cos4 = cos4 / norm4

        sin3 = np.sqrt (1 - cos3*cos3)
        sin4 = np.sqrt (1 - cos4*cos4)

        c3 = np.cross (incident3, normal)
        c4 = np.cross (incident4, normal)

        if c3 < 0:
            sin3 = -sin3

        if c4 < 0:
            sin4 = -sin4

        tg3 = sin3 / cos3
        tg4 = sin4 / cos4

        if isBetween (tga, tg3, tg4):
            x = x3 + (tga-tg3) * (x4-x3) / ( tg4 -  tg3 )
            y = y3 + (tga-tg3) * (y4-y3) / ( tg4 -  tg3 )
            return [ x, y ]


        # on cherche enfin sur l'extension à droite de l'interface
    if interface.extendRight != 0:
        x3 = interface.xgrid[n-1] + interface.extendRight
        y3 = interface.ygrid[n-1]
        x4 = interface.xgrid[n-1]
        y4 = interface.ygrid[n-1]

        incident3 = np.array ( [x1-x3, y1-y3] )
        incident4 = np.array ( [x1-x4, y1-y4] )
        nx = interface.nx0[n-1]
        ny = interface.ny0[n-1]
        normal = np.array ( [nx, ny])

        cos3 = incident3[0] * nx + incident3[1] * ny
        cos4 = incident4[0] * nx + incident4[1] * ny

        norm3 = np.sqrt ( incident3[0] * incident3[0] + incident3[1] * incident3[1] )
        norm4 = np.sqrt ( incident4[0] * incident4[0] + incident4[1] * incident4[1] )

        cos3 = cos3 / norm3
        cos4 = cos4 / norm4

        sin3 = np.sqrt (1 - cos3*cos3)
        sin4 = np.sqrt (1 - cos4*cos4)

        c3 = np.cross (incident3, normal)
        c4 = np.cross (incident4, normal)

        if c3 < 0:
            sin3 = -sin3

        if c4 < 0:
            sin4 = -sin4

        tg3 = sin3 / cos3
        tg4 = sin4 / cos4

        if isBetween (tga, tg3, tg4):
            x = x3 + (tga-tg3) * (x4-x3) / ( tg4 -  tg3 )
            y = y3 + (tga-tg3) * (y4-y3) / ( tg4 -  tg3 )
            return [ x, y ]



    return False


    # Cette fonction cherche le point le long d'une interface source
    #   qui fait un angle alpha avec le rayon incident et la normale à cette interface
    #       x1, y1 : cooordonnées du point source sur l'interface source
    #       nx1, ny1 : composantes du vecteur normal au point source
    #       interface: interface de destination
    #       alpha : angle limite de réfraction

def searchSrcInterfacePointWithAngle (x1,y1,nx1,ny1,interface,alpha):
    n = len (interface.xgrid)
    sina = np.sin(alpha)
    tga = np.tan(alpha)

        # on cherche d'abord sur l'extension à gauche de l'interface
    if interface.extendLeft != 0:
        x3 = interface.xgrid[0]-interface.extendLeft
        y3 = interface.ygrid[0]
        x4 = interface.xgrid[0]
        y4 = interface.ygrid[0]

        incident3 = np.array ( [x3-x1, y3-y1] )
        incident4 = np.array ( [x4-x1, y4-y1] )
        normal = np.array ( [nx1, ny1])

        cos3 = incident3[0] * nx1 + incident3[1] * ny1
        cos4 = incident4[0] * nx1 + incident4[1] * ny1

        norm3 = np.sqrt ( incident3[0] * incident3[0] + incident3[1] * incident3[1] )
        norm4 = np.sqrt ( incident4[0] * incident4[0] + incident4[1] * incident4[1] )

        cos3 = cos3 / norm3
        cos4 = cos4 / norm4

        sin3 = np.sqrt (1 - cos3*cos3)
        sin4 = np.sqrt (1 - cos4*cos4)

        c3 = np.cross (incident3, normal)
        c4 = np.cross (incident4, normal)

        if c3 < 0:
            sin3 = -sin3

        if c4 < 0:
            sin4 = -sin4

        tg3 = sin3 / cos3
        tg4 = sin4 / cos4

        if isBetween (tga, tg3, tg4):
            x = x3 + (tga-tg3) * (x4-x3) / ( tg4 -  tg3 )
            y = y3 + (tga-tg3) * (y4-y3) / ( tg4 -  tg3 )
            return [ x, y ]


        # recherche sur l'interface de destination
    for i in range(0,n-1):
        x3 = interface.xgrid[i]
        y3 = interface.ygrid[i]
        x4 = interface.xgrid[i+1]
        y4 = interface.ygrid[i+1]
        igrid = interface.igrid[i]

        incident3 = np.array ( [x3-x1, y3-y1] )
        incident4 = np.array ( [x4-x1, y4-y1] )
        normal = np.array ( [nx1, ny1])

        cos3 = incident3[0] * nx1 + incident3[1] * ny1
        cos4 = incident4[0] * nx1 + incident4[1] * ny1

        norm3 = np.sqrt ( incident3[0] * incident3[0] + incident3[1] * incident3[1] )
        norm4 = np.sqrt ( incident4[0] * incident4[0] + incident4[1] * incident4[1] )

        cos3 = cos3 / norm3
        cos4 = cos4 / norm4

        sin3 = np.sqrt (1 - cos3*cos3)
        sin4 = np.sqrt (1 - cos4*cos4)

        c3 = np.cross (incident3, normal)
        c4 = np.cross (incident4, normal)

        if c3 < 0:
            sin3 = -sin3

        if c4 < 0:
            sin4 = -sin4

        tg3 = sin3 / cos3
        tg4 = sin4 / cos4

        if isBetween (tga, tg3, tg4):
            x = x3 + (tga-tg3) * (x4-x3) / ( tg4 -  tg3 )
            y = y3 + (tga-tg3) * (y4-y3) / ( tg4 -  tg3 )
            return [ x, y ]


        # on cherche enfin sur l'extension à droite de l'interface
    if interface.extendRight != 0:
        x3 = interface.xgrid[n-1] + interface.extendRight
        y3 = interface.ygrid[n-1]
        x4 = interface.xgrid[n-1]
        y4 = interface.ygrid[n-1]

        incident3 = np.array ( [x3-x1, y3-y1] )
        incident4 = np.array ( [x4-x1, y4-y1] )
        normal = np.array ( [nx1, ny1])

        cos3 = incident3[0] * nx1 + incident3[1] * ny1
        cos4 = incident4[0] * nx1 + incident4[1] * ny1

        norm3 = np.sqrt ( incident3[0] * incident3[0] + incident3[1] * incident3[1] )
        norm4 = np.sqrt ( incident4[0] * incident4[0] + incident4[1] * incident4[1] )

        cos3 = cos3 / norm3
        cos4 = cos4 / norm4

        sin3 = np.sqrt (1 - cos3*cos3)
        sin4 = np.sqrt (1 - cos4*cos4)

        c3 = np.cross (incident3, normal)
        c4 = np.cross (incident4, normal)

        if c3 < 0:
            sin3 = -sin3

        if c4 < 0:
            sin4 = -sin4

        tg3 = sin3 / cos3
        tg4 = sin4 / cos4

        if isBetween (tga, tg3, tg4):
            x = x3 + (tga-tg3) * (x4-x3) / ( tg4 -  tg3 )
            y = y3 + (tga-tg3) * (y4-y3) / ( tg4 -  tg3 )
            return [ x, y ]

    return False


        # Cette fonction regarde si le rayon sismique
        #   risque d'intersecter l'interface en dehors
        #   de son point cible.
        #   Si tel est le cas, le rayon n'est pas calculé
        #   car la cible se trouve dans une zone d'ombre
def detectIntersectionWithInterface(x1,y1,x2,y2,interface):
    n = len (interface.x)
    for i in range(0,n-1):
        x3 = interface.x[i]
        y3 = interface.y[i]
        x4 = interface.x[i+1]
        y4 = interface.y[i+1]
        res = checkSegmentsIntersection (x1,y1,x2,y2,x3,y3,x4,y4)
        if res==True:
            return res
    return False

        # Cette fonction cherche les coordonnées du point d'intersection
        #   d'un rayon réfléchi ou réfracté défini par le segment (point1,point2)
        #   sur l'interface
def findIntersectionWithInterface(x1,y1,x2,y2,interface):
    n = len (interface.x)
    vectors = []

        # on cherche d'abord sur l'extension à gauche de l'interface
    if interface.extendLeft != 0:
        x3 = interface.x[0] - interface.extendLeft
        y3 = interface.y[0]
        x4 = interface.x[0]
        y4 = interface.y[0]
        res = findSegmentsIntersection (x1,y1,x2,y2,x3,y3,x4,y4)
        if res!=None:
            # si intersection, res contient les coordonnées du point d'intersection
            if not (isClose(res[0], x1) and  isClose(res[1], y1) ) and not (isClose(res[0], x2) and  isClose(res[1], y2) ) :
                vectors.append (res)

        # on parcourt l'interface
    for i in range(0,n-1):
        x3 = interface.x[i]
        y3 = interface.y[i]
        x4 = interface.x[i+1]
        y4 = interface.y[i+1]
        res = findSegmentsIntersection (x1,y1,x2,y2,x3,y3,x4,y4)
        if res!=None :
            if not (isClose(res[0], x1) and  isClose(res[1], y1) ) and not (isClose(res[0], x2) and  isClose(res[1], y2) ) :
                # si intersection, res contient les coordonnées du point d'intersection
                vectors.append (res)

        # on cherche enfin sur l'extension à droite de l'interface
    if interface.extendRight != 0:
        x3 = interface.x[n-1] + interface.extendRight
        y3 = interface.y[n-1]
        x4 = interface.x[n-1]
        y4 = interface.y[n-1]
        res = findSegmentsIntersection (x1,y1,x2,y2,x3,y3,x4,y4)
        if res!=None:
            # si intersection, res contient les coordonnées du point d'intersection
            if not (isClose(res[0], x1) and  isClose(res[1], y1) ) and not (isClose(res[0], x2) and  isClose(res[1], y2) ) :
                vectors.append (res)

    size = len (vectors)    
    if size == 0:
        return None

    if size == 1:
        return vectors[0]

    if size > 1:
        dist = 1e30 
        i = 0
        for k in range (0,size):
            v = vectors[k]
            x = v[0]
            y = v[1]
            d = np.sqrt ((x-x1)*(x-x1)+(y-y1)*(y-y1))
            if d < dist:
                dist = d
                i = k
        return vectors [i]

    return None
