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
            if self.inRange(point):
                self._vol[point.x()][point.y()][point.z()] = val

    def interpolate(self, startPoint, endPoint):
        delta = endPoint - startPoint
        absDelta = delta.abs()
        max = absDelta.maxVal()
        steps = ceil(max)
        stride = 1.0 / steps

        for i in frange(0, 1.0, stride):
            nextPoint = (startPoint + (delta * i)).floor()
            yield nextPoint

    def inRange(self, point):
        if point.x() < 0: return False
        if point.y() < 0: return False
        if point.z() < 0: return False
        if point.x() >= self.size[0]: return False
        if point.y() >= self.size[1]: return False
        if point.z() >= self.size[2]: return False
        return True


    def toSTL(self, filePath):
        with open(filePath, "wb") as out:

            # 80 bytes of padding
            for i in range(0, 80):
                out.write(struct.pack('c', '0'))

            #out.write(struct.pack('<f', 0))

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

                        #finalTransform = np.dot(transform2, transform)
                        #finalTransform = np.dot(finalTransform, rotMat)
                        #finalTransform = np.dot(transform, rotMat)

                        #finalTransform = Transformations.concatenate_matrices([rotMat, transform, transform2])
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

                            point.append(1)

                            if count % 4 == 0:
                                tx = np.dot(point, txm.T)
                            else:
                                tx = np.dot(point, txm.T)

                            data += struct.pack('<f', tx[0])
                            data += struct.pack('<f', tx[1])
                            data += struct.pack('<f', tx[2])


                            #out.write(struct.pack('<f', tx[0]))
                            #out.write(struct.pack('<f', tx[1]))
                            #out.write(struct.pack('<f', tx[2]))

                            if (count + 1) % 4 == 0:
                                #out.write(struct.pack('<H', 0))
                                data += struct.pack('<H', 0)

                            count += 1

            # Write the face count
            #out.seek(80)
            out.write(struct.pack('<I', faceCount))
            out.write(data)

    def voxelSet(self, coords):
        if self._vol[coords[0]][coords[1]][coords[2]] == 1:
            return True

    def voxelFreeNeighbors(self, coords):
        for vox in self.voxelNeighborhoodIterator(coords, 1):
            if vox[0] == coords[0] and vox[1] == coords[1] and vox[2] == coords[2]:
                continue

            if (vox[0] != coords[0] and vox[1] != coords[1]) or (vox[1] != coords[1] and vox[2] != coords[2]) or (vox[0] != coords[0] and vox[2] != coords[2]):
                continue

            if self.inRange(Point(*vox)):
                if self.voxelSet(vox):
                    yield vox
            else:
                yield vox

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
