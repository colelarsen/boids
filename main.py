import ctypes
from PIL import Image
import time
import numpy as np 
import random
import pyautogui

scaleFactor = 3
width = int(2560/scaleFactor)
height = int(1440/scaleFactor)

groupingChance = 0.9
directionChangeChance = 0.01
groupingDistance = 5
boidSpeed = 8
boidTurningSpeed = 0.3
boidCount = 30






def getMousePosition():
    pos = pyautogui.position()
    
    return np.array([pos[0], pos[1]]) / scaleFactor

def normalize(npArray):
    return  npArray/np.linalg.norm(npArray)

def perpendicular( a ) :
    b = np.empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b

def keepInBounds(npArray):
    npArray[0] = max(npArray[0], 0)
    npArray[1] = max(npArray[1], 0)
    npArray[0] = min(npArray[0], width-5)
    npArray[1] = min(npArray[1], height-5)
    return npArray

class Boid:

    def __init__(self, img, color, position, direction, velocity, turningspeed):
        self.position = position
        self.velocity = velocity
        self.img = img
        self.direction = direction
        self.turningspeed = turningspeed
        self.subDirection = direction
        self.color = color
        self.secondLastPos = position
        self.lastPos = position

        self.wing1 = (0, 0)
        self.wing2 = (0, 0)
        self.counter = 0

        
    
    def drawSelf(self):
        for x in range(0, 4):
            for y in range(0, 4):

                if self.img.getpixel((int(self.lastPos[0]+x), int(self.lastPos[1]+y))) == self.color:
                    self.img.putpixel((int(self.lastPos[0]+x), int(self.lastPos[1]+y)), (0, 0, 0))


                if self.img.getpixel((int(self.wing1[0]+x), int(self.wing1[1]+y))) == self.color:
                    self.img.putpixel((int(self.wing1[0]+x), int(self.wing1[1]+y)), (0, 0, 0))


                if self.img.getpixel((int(self.wing2[0]+x), int(self.wing2[1]+y))) == self.color:
                    self.img.putpixel((int(self.wing2[0]+x), int(self.wing2[1]+y)), (0, 0, 0))


        wingPos = (self.position - self.secondLastPos)
        antiWingPos = perpendicular(wingPos)

        self.wing1 = self.secondLastPos + wingPos*0.7 + antiWingPos*0.4
        self.wing2 = self.secondLastPos + wingPos*0.7 - antiWingPos*0.4

        self.wing1 = keepInBounds(self.wing1)
        self.wing2 = keepInBounds(self.wing2)


        for x in range(0, 4):
            for y in range(0, 4):
                self.img.putpixel((int(self.position[0]+x), int(self.position[1]+y)), self.color)

                self.img.putpixel((int(self.wing1[0]+x), int(self.wing1[1]+y)), self.color)
                self.img.putpixel((int(self.wing2[0]+x), int(self.wing2[1]+y)), self.color)

                
    
    def updateSubDirection(self, forced):
        shouldChangeDirection = random.random() < directionChangeChance
        if shouldChangeDirection or forced:
            self.subDirection = np.array([random.random() - 0.5, random.random() - 0.5])
            self.subDirection = normalize(self.subDirection) * random.random()
        
        self.direction = self.direction + self.subDirection*self.turningspeed
        self.direction = normalize(self.direction)
        

    
    
    def update(self, boids):
        self.counter = self.counter+1
        self.lastPos = self.secondLastPos
        self.secondLastPos = self.position

        self.position = self.position + self.direction*self.velocity
        self.position = keepInBounds(self.position)

        

        NSteps = 20
        positionInNSteps = self.position + (self.direction*self.velocity)*NSteps
        
       # This means boid is close to hitting a wall
        if(positionInNSteps[0] <= 0):
            self.subDirection = np.array([random.random(), self.subDirection[1]])
            self.subDirection = normalize(self.subDirection)

        if(positionInNSteps[0] >= width-5):
            self.subDirection = np.array([random.random()*-1, self.subDirection[1]])
            self.subDirection = normalize(self.subDirection)
        
        if(positionInNSteps[1] <= 0):
            self.subDirection = np.array([self.subDirection[0], random.random()])
            self.subDirection = normalize(self.subDirection)
        if(positionInNSteps[1] >= height-5):
            self.subDirection = np.array([self.subDirection[0], random.random()*-1])
            self.subDirection = normalize(self.subDirection)

        #Head in the same direction as other boids closeby
        for boid in boids:
            #If this boid is not myself
            if(boid.position[0] != self.position[0] and boid.position[1] != self.position[1]):
                distance = np.linalg.norm(boid.position-self.position)
                #If they are within 5 steps
                
                if(distance < self.velocity*groupingDistance):
                    dotProduct=np.dot(boid.direction, self.direction)
                    shouldGroupUp = random.random() < groupingChance
                    #If we are headed in the same direction
                    if(dotProduct > 0.5 and shouldGroupUp):
                        self.subDirection = self.subDirection + boid.subDirection*random.random()
                        self.subDirection = normalize(self.subDirection)
                if(distance < self.velocity*groupingDistance*3):
                    #If we are headed opposite direction
                    dotProduct=np.dot(boid.direction, self.direction)
                    if(dotProduct <= -0.85):
                        self.subDirection = self.subDirection + perpendicular(self.subDirection)*random.random()
                        self.subDirection = normalize(self.subDirection)


        #If heading in direction of mouse cursor
        dotProduct=np.dot(normalize(getMousePosition() - self.position), self.direction)
        distance = np.linalg.norm(getMousePosition()-self.position)

        
        if(dotProduct >= 0.5 and distance < self.velocity*groupingDistance*5 and self.counter > 10):
            self.subDirection = perpendicular(self.subDirection)
            self.subDirection = normalize(self.subDirection)
            self.counter = 0
        
        self.updateSubDirection(False)





def start():
    num = 0
    path = "C:/Users/Cole/Downloads/Programming/Boids/image{}.png".format(num)

    img = Image.new('RGB', (width, height))

    boids = []

    for i in range(0, boidCount):
        boids.append(Boid(img, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), np.array([random.randint(0, width-10), random.randint(0, height-10)]),  normalize(np.array([random.random()-0.5, random.random()-0.5])), boidSpeed, boidTurningSpeed))


    while True:
        for boid in boids:
            boid.update(boids)
            boid.drawSelf()

        try:

            img.save(path)
            ctypes.windll.user32.SystemParametersInfoW(20, 0, path , 0)
        except:
            print("An exception occurred")
            num = num + 1
            if(num == 10):
                num = 1
            path = "C:/Users/Cole/Downloads/Programming/Boids/image{}.png".format(num)

        time.sleep(0.08)







start()