# Path-tracer for Numwork Calculator.
# Do not expect to make a render during your
# maths class, imo, it will takes at least
# 10 hours per render hahahaha

import math
import random
import kandinsky

class Utils:

    @staticmethod
    def random(min, max):
        return random.uniform(min, max)

class PathTracer:
    imageWidth = 320
    imageHeight = 240

    samplePerPixel = 1

class Vec3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def dot(self, vec3):
        return self.x * vec3.x + self.y * vec3.y + self.z * vec3.z

    def magnitude(self):
        return math.sqrt(self.dot(self))

    def normalize(self):
        mag = self.magnitude()
        return Vec3(self.x / mag, self.y / mag, self.z / mag)

    def add(self, vec3):
        return Vec3(self.x + vec3.x, self.y + vec3.y, self.z + vec3.z)

    def scale(self, x:float):
        return Vec3(self.x * x, self.y * x, self.z * x)

    def mult(self, vec3):
        return Vec3(self.x * vec3.x, self.y * vec3.y, self.z * vec3.z)

    @staticmethod
    def random():
        return Vec3(Utils.random(-1, 1), Utils.random(-1, 1), Utils.random(-1, 1))
    
    @staticmethod
    def randomInUnitSphere():
        while(True):
            rand = Vec3.random()
            if(rand.dot(rand) < 0):
                continue

            return rand


class Ray:
    def __init__(self, origin:Vec3, direction:Vec3):
        self.origin = origin
        self.direction = direction

    def at(self, t:float):
        return self.origin.add(self.direction.scale(t))

class Material:
    def __init__(self, color:Vec3):
        self.color = color

class Diffuse(Material):
    def __init__(self, color:Vec3):
        super().__init__(color)

    def getScatterDirection(self, normal:Vec3, direction:Vec3):
        return normal.add(Vec3.randomInUnitSphere()).normalize()

class Sphere:
    def __init__(self, position:Vec3, radius:float, material):
        self.position = position
        self.radius = radius

        self.material = material

class HitWorld:
    def __init__(self, intersection:bool, point:Vec3, sphere:Sphere):
        self.intersection = intersection
        self.point = point
        self.sphere = sphere


class World:
    def __init__(self):
        self.sphere = []

    def add(self, sphere:list):
        for i in range(len(sphere)):
            self.sphere.append(sphere[i])

    def hit(self, ray:Ray):
        intersection = False
        nearestT = 1000
        nearestS = self.sphere[0]

        for i in range(len(self.sphere)):
            sphere = self.sphere[i]
            distanceFromCenter = ray.origin.add(sphere.position.scale(-1))

            b = 2 * distanceFromCenter.dot(ray.direction)
            c = distanceFromCenter.dot(distanceFromCenter) - sphere.radius ** 2

            delta = b * b - 4 * c

            if(delta <= 0):
                continue

            t = (- b - math.sqrt(delta)) / 2

            if(t < 0.001 or t > nearestT):
                continue

            intersection = True
            nearestT = t
            nearestS = sphere

        return HitWorld(intersection, ray.at(nearestT), nearestS)

    def getSky(self, x:int, y:int):
        ratio = y / PathTracer.imageHeight

        return Vec3(1, 1, 1).scale(1.0 - ratio).add(Vec3(0.5, 0.7, 1.0)).scale(ratio)

class Camera:
    def __init__(self, position:Vec3):
        self.position = position
        self.focal = 3

    def render(self, world:World):
        for y in range(PathTracer.imageHeight):
            for x in range(PathTracer.imageWidth):

                invertY = PathTracer.imageHeight - y

                r = 0
                g = 0
                b = 0

                for sample in range(PathTracer.samplePerPixel):

                    u = x + (sample / PathTracer.imageWidth)
                    v = invertY + (sample / PathTracer.imageHeight)

                    direction = Vec3(
                        (u - PathTracer.imageWidth/2) / PathTracer.imageHeight, 
                        (v - PathTracer.imageHeight/2) / PathTracer.imageHeight,
                        -self.focal
                    ).add(self.position.scale(-1)).normalize()

                    ray = Ray(self.position, direction)
                    color = self.getColor(u, v, ray, world, 50)

                    # gamma correction
                    r += math.sqrt(color.x)
                    g += math.sqrt(color.y)
                    b += math.sqrt(color.z)

                r /= PathTracer.samplePerPixel
                g /= PathTracer.samplePerPixel
                b /= PathTracer.samplePerPixel

                kandColor = kandinsky.color(
                    max(min(round(color.x * 255), 255), 0), 
                    max(min(round(color.y * 255), 255), 0), 
                    max(min(round(color.z * 255), 255), 0)
                )

                kandinsky.fill_rect(x, y, 1, 1, kandColor)

    def getColor(self, x:int, y:int, ray:Ray, world:World, depth:int):
        hitWorld = world.hit(ray)

        if(depth <= 0):
            return Vec3(0, 0, 0)

        if(not hitWorld.intersection):
            return world.getSky(x, y)

        normal = hitWorld.point.add(hitWorld.sphere.position.scale(-1))
        normal = normal.normalize()

        #return normal.add(Vec3(1, 1, 1)).scale(1/2)

        bounceRay = Ray(hitWorld.point, hitWorld.sphere.material.getScatterDirection(normal, ray.direction))
        return self.getColor(x, y, bounceRay, world, depth - 1).mult(hitWorld.sphere.material.color)

class Main:
    def __init__(self):

        world = World()

        sphere = Sphere(Vec3(0, 0, -5), 0.5, Diffuse(Vec3(0.7, 0.3, 0.3)))
        floor = Sphere(Vec3(0, -100.5, -5), 100, Diffuse(Vec3(0.5, 0.5, 0.5)))

        world.add([sphere, floor])

        camera = Camera(Vec3(0, 0, 0))
        camera.render(world)

Main()

kandinsky.display()
