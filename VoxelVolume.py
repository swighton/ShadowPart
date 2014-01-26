from numpy import *
from math import *
from Point import Point
import Transformations
import numpy as np
import struct

def frange(x, y, jump):
  while x < y:
    yield x
    x += jump

class VoxelVolume:
    def __init__(self, dims):
        if len(dims) != 3:
            print 'error - voxel dimensions not three'
        self._vol = ones(dims)
        self.size = dims

    def drawRay(self, startPoint, endPoint):
        self.setRayVal(startPoint, endPoint, 1)

    def cutRay(self, startPoint, endPoint):
        self.setRayVal(startPoint, endPoint, 0)

    def setRayVal(self, startPoint, endPoint, val):
        ''' Assuming coordinates are in voxel space
        '''
        for point in self.interpolate(startPoint, endPoint):
            if self.inRange(point.toList()):
                self._vol[point.x()][point.y()][point.z()] = val

    def interpolate(self, startPoint, endPoint):
        delta = endPoint - startPoint
        absDelta = delta.abs()
        max = absDelta.maxVal()
        steps = ceil(max)
        stride = 1.0 / (max * 1.5) # Serious hack to make sure we hit all voxels. TODO: Revisit interpolation

        next = Point()
        for i in range(0, int(steps)):
            next._x = startPoint._x + delta._x * stride * i
            next._y = startPoint._y + delta._y * stride * i
            next._z = startPoint._z + delta._z * stride * i
            yield next

    def inRange(self, coord):
        if coord[0] < 0: return False
        if coord[1] < 0: return False
        if coord[2] < 0: return False
        if coord[0] >= self.size[0]: return False
        if coord[1] >= self.size[1]: return False
        if coord[2] >= self.size[2]: return False
        return True

    def toSTL(self, filePath):
        with open(filePath, "wb") as out:

            # 80 bytes of padding
            # TODO: More pythonic way of doing this?
            for i in range(0, 80):
                out.write(struct.pack('c', '0'))

            data = ""

            faceCount = 0
            for voxCoords in self.iterVoxelsCoords():
                if self.voxelSet(voxCoords):
                    voxPoint = Point(*voxCoords)
                    for neighborCoords in self.voxelFreeNeighbors(voxCoords):
                        neighborPoint = Point(*neighborCoords)

                        faceCenter = (neighborPoint - voxPoint) #* 0.5

                        optimal = Point(1, 0, 0)
                        rotation = Transformations.quaternion_about_axis(0, optimal.toList())
                        dot = optimal.dot(faceCenter.normalized())
                        if dot > 0.999999:
                            pass
                        elif dot < -0.999999:
                            #rotation = Transformations.quaternion_about_axis(0, (0, 1, 0))
                            rotation = np.array([0, 0, 1, 0])
                        else:
                            cross = optimal.cross(faceCenter)
                            w = sqrt(optimal.lengthSquared() * faceCenter.lengthSquared()) + dot
                            rotation = np.array([w, cross.x(), cross.y(), cross.z()])#Transformations.quaternion_about_axis(w, cross.toList())

                        scale = Transformations.scale_matrix(1)
                        rotMat = Transformations.quaternion_matrix(rotation)
                        transform = Transformations.translation_matrix((voxPoint).toList())
                        transform2 = Transformations.translation_matrix((0.5, 0, 0))

                        txm = np.identity(4)
                        txm = np.dot(txm, scale)
                        txm = np.dot(txm, transform)
                        txm = np.dot(txm, rotMat)
                        txm = np.dot(txm, transform2)


                        points = (
                            # Normal
                            optimal.toList(),
                            # Triangle
                            [0.0, -0.5, -0.5],
                            [0.0, 0.5, -0.5],
                            [0.0, 0.5, 0.5],

                            # Normal
                            optimal.toList(),
                            # Triangle
                            [0.0, -0.5, -0.5],
                            [0.0, 0.5, 0.5],
                            [0.0, -0.5, 0.5]
                        )

                        faceCount += 2

                        count = 0
                        for point in points:

                            point.append(1) # ??? Makes sense for verticies, but not for normals
                            tx = np.dot(point, txm.T)

                            data += struct.pack('<f', tx[0])
                            data += struct.pack('<f', tx[1])
                            data += struct.pack('<f', tx[2])

                            if (count + 1) % 4 == 0:
                                data += struct.pack('<H', 0)

                            count += 1

            # Write the face count
            out.write(struct.pack('<I', faceCount))

            # Write the data
            out.write(data)

    def voxelSet(self, coords):
        if self._vol[coords[0]][coords[1]][coords[2]] == 1:
            return True

    def voxelSetClampedToRange(self, coord):
        if self.inRange(coord):
            if self._vol[coord[0]][coord[1]][coord[2]] == 1:
                return True
        else:
            return False

    def projectImage(self, img, imgSize, fromPoint, toPoint, comparison=None):
        if comparison == None:
            comparison = lambda x: x > 0

        upVector = Point(0, 0, 1)  # Just going to assume up vector
        rightVector = (toPoint - fromPoint).cross(upVector).normalized()
        halfSize = [imgSize[0] / 2, imgSize[1] / 2]
        for x in range(-halfSize[0], halfSize[0]):
            for y in range(-halfSize[1], halfSize[1]):
                delta = upVector * y + rightVector * x
                if (comparison(img[x + halfSize[0], y + halfSize[1]][0])):
                    self.cutRay(fromPoint + delta, toPoint + delta)

    def voxelFreeNeighbors(self, coords):
        coords[0] += 1
        if not self.voxelSetClampedToRange(coords):
            yield coords
        coords[0] -= 2
        if not self.voxelSetClampedToRange(coords):
            yield coords
        coords[0] += 1

        coords[1] += 1
        if not self.voxelSetClampedToRange(coords):
            yield coords
        coords[1] -= 2
        if not self.voxelSetClampedToRange(coords):
            yield coords
        coords[1] += 1

        coords[2] += 1
        if not self.voxelSetClampedToRange(coords):
            yield coords
        coords[2] -= 2
        if not self.voxelSetClampedToRange(coords):
            yield coords
        coords[2] += 1

    def voxelNeighborhoodIterator(self, coords, rad=1):
        for x in range(coords[0] - rad, coords[0] + rad + 1):
            for y in range(coords[1] - rad, coords[1] + rad + 1):
                for z in range(coords[2] - rad, coords[2] + rad + 1):
                    yield [x, y, z]

    def iterVoxelsCoords(self):
        for x in range(0, self.size[0]):
            for y in range(0, self.size[1]):
                for z in range(0, self.size[2]):
                    yield [x, y, z]
