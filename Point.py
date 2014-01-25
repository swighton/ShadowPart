from math import floor
from math import sqrt

class Point:
    def __init__(self, x = 0, y = 0, z = 0):
        self._x = x
        self._y = y
        self._z = z

    def __add__(self, other):
        res = Point()
        res._x = self._x + other._x
        res._y = self._y + other._y
        res._z = self._z + other._z
        return res

    def __sub__(self, other):
        res = Point()
        res._x = self._x - other._x
        res._y = self._y - other._y
        res._z = self._z - other._z
        return res

    def __mul__(self, other):
        res = Point()
        res._x = self._x * other
        res._y = self._y * other
        res._z = self._z * other
        return res

    def __div__(self, other):
        res = Point()
        res._x = self._x / other
        res._y = self._y / other
        res._z = self._z / other
        return res

    def x(self):
        return self._x

    def y(self):
        return self._y

    def z(self):
        return self._z

    def abs(self):
        res = Point()
        res._x = abs(self._x)
        res._y = abs(self._y)
        res._z = abs(self._z)
        return res

    def maxVal(self):
        maxVal = self._x
        if maxVal < self._y: maxVal = self._y
        if maxVal < self._z: maxVal = self._z
        return maxVal

    def floor(self):
        res = Point()
        res._x = floor(self._x)
        res._y = floor(self._y)
        res._z = floor(self._z)
        return res

    def toList(self):
        return [self._x, self._y, self._z]

    def dot(self, point):
        return point._x * self._x + point._y * self._y + point._z * self._z

    def cross(self, point):
        return Point(
            (self.y() * point.z()) - (point.y() * self.z()),
            (self.z() * point.x()) - (point.z() * self.x()),
            (self.x() * point.y()) - (point.x() * self.y())
        )

    def normalized(self):
        return self / self.length()

    def length(self):
        return sqrt(self.lengthSquared())

    def lengthSquared(self):
        return self.x() * self.x() + self.y() * self.y() + self.z() * self.z()

    def __str__(self):
        return "X: " + str(self._x) + " Y: " +  str(self._y) + " Z: " + str(self._z);