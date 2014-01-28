from numpy  import *
from scipy.misc import imread
from pylab import imshow
from VoxelVolume import VoxelVolume
from Point import Point
import PIL.Image


def loadImage(path):
    #return imread(path)
    im = PIL.Image.open(path) #Can be many different formats.
    return im


def projectImage(image, startPos, endPos):
    pass

def main(args=None):
    img1 = loadImage("img_1.png")
    img2 = loadImage("img_2.png")
    img3 = loadImage("img_3.png")

    pix1 = img1.load()
    pix2 = img2.load()
    pix3 = img3.load()

    voxels = VoxelVolume([img1.size[0], img1.size[0], img1.size[1]])

    voxels.projectImage(pix1, img1.size, Point(-1, -1, img1.size[1] / 2), Point(img1.size[0], img1.size[0], img1.size[1] / 2))
    voxels.projectImage(pix2, img2.size, Point(img1.size[0] / 2, -1, img1.size[1] / 2), Point(img1.size[0] / 2, img1.size[0], img1.size[1] / 2))
    voxels.projectImage(pix3, img3.size, Point(-1, img1.size[0] / 2, img1.size[1] / 2), Point(img1.size[0], img1.size[0] / 2, img1.size[1] / 2))

    print 'done cut'
    voxels.toSTL("test.stl")

if __name__ == "__main__":
    import sys
    main(sys.argv)
else:
    main()
