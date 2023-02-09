import argparse
import sys

sys.path.append ("src")


from Scene import Scene



#-------------------------------------------------------------------------
#   Main code
#-------------------------------------------------------------------------

parser = argparse.ArgumentParser(description='Caculate seismic rays')
parser.add_argument('script',  type=str, help='the script file name')
parser.add_argument('rai', type=int, help="Numéro du rai à calculer", nargs='?', default=None)
args = parser.parse_args()
filename = args.script
rayIndex = args.rai

scene = Scene()
scene.rayIndex = rayIndex
scene.buildFromScript(filename)

if scene.isAnimating:
    scene.buildAnimation()
else:
    scene.calculate()
    scene.draw()
    scene.drawHodochrone()

