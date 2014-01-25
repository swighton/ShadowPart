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

    img1 = loadImage("img1.png")
    img2 = loadImage("img2.png")
    img3 = loadImage("img3.png")

    pix1 = img1.load()
    pix2 = img2.load()
    pix3 = img3.load()

    #print im.size #Get the width and hight of the image for iterating over
    #print pix[x,y] #Get the RGBA Value of the a pixel of an image
    #pix[x,y] = value # Set the RGBA Value of the image (tuple)

    #print img1.size

    #print pix1[10][10];

    voxels = VoxelVolume([img1.size[0], img1.size[1], 50])
    # for x in range(0, 20):
    #     for y in range(0, 20):
    #         voxels.cutRay(Point(x, y, 0), Point(10, 10, 20))

    for x in range(0, img1.size[0]):
        for y in range(0, img1.size[1]):
            if (pix1[x, y][0] == 0):
                voxels.cutRay(Point(x, y, -10), Point(x, y, 50))

    for x in range(0, img2.size[0]):
        for y in range(0, img2.size[1]):
            if (pix2[x, y][0] == 0):
                voxels.cutRay(Point(x, -10, y), Point(x, 50, y))

    for x in range(0, img3.size[0]):
        for y in range(0, img3.size[1]):
            if (pix3[x, y][0] == 0):
                voxels.cutRay(Point(-10, x, y), Point(50, x, y))

    print 'done cut'
    #voxels.cutRay(Point(0, 0, 0), Point(50, 50, 50))
    #print voxels._vol

    voxels.toSTL("test.stl")

if __name__ == "__main__":
    import sys
    main(sys.argv)
else:
    main()