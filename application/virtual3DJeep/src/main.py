#!/usr/bin/env python
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, time, random, csv, datetime
import ImportObject
import PIL.Image as Image
import jeep, cone, lightSetting

windowSize = 600
helpWindow = False
helpWin = 0
mainWin = 0
centered = False

beginTime = 0
countTime = 0
score = 0
finalScore = 0
canStart = False
overReason = ""

#for wheel spinning
tickTime = 0

#creating objects
objectArray = []
jeep1Obj = jeep.jeep('p')
jeep2Obj = jeep.jeep('g')
jeep3Obj = jeep.jeep('r')

allJeeps = [jeep1Obj, jeep2Obj, jeep3Obj]
jeepNum = 0
jeepObj = allJeeps[jeepNum]
#personObj = person.person(10.0,10.0)

#concerned with camera
eyeX = 0.0
eyeY = 2.0
eyeZ = 10.0
midDown = False
topView = False
behindView = False

#concerned with panning
nowX = 0.0
nowY = 0.0

angle = 0.0
radius = 10.0
phi = 0.0

#concerned with scene development
land = 20
gameEnlarge = 10

#concerned with obstacles (cones) & rewards (stars)
coneAmount = 15
starAmount = 5 #val = -10 pts
diamondAmount = 1 #val = deducts entire by 1/2
# diamondObj = diamond.diamond(random.randint(-land, land), random.randint(10.0, land*gameEnlarge))
usedDiamond = False

allcones = []
allstars = []
obstacleCoord = []
rewardCoord = []
ckSense = 5.0

#concerned with lighting#########################!!!!!!!!!!!!!!!!##########
applyLighting = False

abcd = False

fov = 30.0
attenuation = 1.0

light0_Position = [0.0, 1.0, 1.0, 1.0]
light0_Intensity = [0.75, 0.75, 0.75, 0.25]

light1_Position = [0.0, 0.0, 0.0, 0.0]
light1_Intensity = [0.25, 0.25, 0.25, 0.25]

matAmbient = [1.0, 1.0, 1.0, 1.0]
matDiffuse = [0.5, 0.5, 0.5, 1.0]
matSpecular = [0.5, 0.5, 0.5, 1.0]
matShininess  = 100.0
 
#mouse control direction variable
mvx = 0.0
mvy = 0.0
mvz = 0.0
oldy = 0.0
oldx = 0.0

lightSet = lightSetting.lightSetting()

#--------------------------------------developing scene---------------
class Scene:
    axisColor = (0.5, 0.5, 0.5, 0.5)
    axisLength = 50   # Extends to positive and negative on all axes
    landColor = (.47, .53, .6, 0.5) #Light Slate Grey
    landLength = land  # Extends to positive and negative on x and y axis
    landW = 1.0
    landH = 0.0
    cont = gameEnlarge
    
    def draw(self):
        self.drawAxis()
        self.drawLand()

    def drawAxis(self):
        glColor4f(self.axisColor[0], self.axisColor[1], self.axisColor[2], self.axisColor[3])
        glBegin(GL_LINES)
        glVertex(-self.axisLength, 0, 0)
        glVertex(self.axisLength, 0, 0)
        glVertex(0, -self.axisLength, 0)
        glVertex(0, self.axisLength, 0)
        glVertex(0, 0, -self.axisLength)
        glVertex(0, 0, self.axisLength)
        glEnd()

    def drawLand(self):
        glEnable(GL_TEXTURE_2D)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        glBindTexture(GL_TEXTURE_2D, roadTextureID)

        glBegin(GL_POLYGON)

        glTexCoord2f(self.landH, self.landH)
        glVertex3f(self.landLength, 0, self.cont * self.landLength)

        glTexCoord2f(self.landH, self.landW)
        glVertex3f(self.landLength, 0, -self.landLength)

        glTexCoord2f(self.landW, self.landW)
        glVertex3f(-self.landLength, 0, -self.landLength)

        glTexCoord2f(self.landW, self.landH)
        glVertex3f(-self.landLength, 0, self.cont * self.landLength)
        glEnd()

        glDisable(GL_TEXTURE_2D)

#--------------------------------------populating scene----------------
def staticObjects():
    global objectArray
    objectArray.append(Scene())
    print "scene appended"


def display():
    global jeepObj, canStart, score, beginTime, countTime
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # position viewpoint based on mouse rotation and keyboard  translation 
    glLoadIdentity()
    #mouse control direction

    glRotatef(mvx, 1.0, 0.0, 0.0)
    glRotatef(mvy, 0.0, 1.0, 0.0)
    glRotatef(mvz, 0.0, 0.0, 1.0)
    lightSet.lightUpdate()
    beginTime = 6-score
    countTime = score-6
    if (score <= 5):
        canStart = False
        glColor3f(1.0,0.0,1.0)
        text3d("Begins in: "+str(beginTime), jeepObj.posX, jeepObj.posY + 3.0, jeepObj.posZ)
    elif (score == 6):
        canStart = True
        glColor(1.0,0.0,1.0)
        text3d("GO!", jeepObj.posX, jeepObj.posY + 3.0, jeepObj.posZ)
    else:
        canStart = True
        glColor3f(0.0,1.0,1.0)
        text3d("Scoring: "+str(countTime), jeepObj.posX, jeepObj.posY + 3.0, jeepObj.posZ)

    for obj in objectArray:
        obj.draw()
    for cone in allcones:
        cone.draw()
    for star in allstars:
        star.draw()
    # if (usedDiamond == False):
    #     diamondObj.draw()
    
    glScalef(mvy/500.0, mvy/500.0, mvy/500.0);
    jeepObj.draw()
    jeepObj.drawW1()
    jeepObj.drawW2()
    jeepObj.drawLight()
    #glEnable(GL_LIGHTING)
    #personObj.draw()
    glutSwapBuffers()

def idle():#--------------with more complex display items like turning wheel---
    global tickTime, prevTime, score
    jeepObj.rotateWheel(-0.1 * tickTime)    
    glutPostRedisplay()
    
    curTime = glutGet(GLUT_ELAPSED_TIME)
    tickTime =  curTime - prevTime
    prevTime = curTime
    score = curTime/1000
    

#---------------------------------setting camera----------------------------
def setView():
    global eyeX, eyeY, eyeZ
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90, 1, 0.1, 100)
    if (topView == True):
        gluLookAt(0, 10, land*gameEnlarge/2, 0, jeepObj.posY, land*gameEnlarge/2, 0, 1, 0)
    elif (behindView ==True):
        gluLookAt(jeepObj.posX, jeepObj.posY + 1.0, jeepObj.posZ - 2.0, jeepObj.posX, jeepObj.posY, jeepObj.posZ, 0, 1, 0) 
    else:
        gluLookAt(eyeX, eyeY, eyeZ, 0, 0, 0, 0, 1, 0)
    glMatrixMode(GL_MODELVIEW)
    
    glutPostRedisplay()    

def setObjView():
    # things to do
    # realize a view following the jeep
    # refer to setview
    pass

#-------------------------------------------user inputs------------------
def mouseHandle(button, state, x, y):
    global midDown
    if (button == GLUT_MIDDLE_BUTTON and state == GLUT_DOWN):
        midDown = True
        print "getting pushed"
    else:
        midDown = False    
        
def motionHandle(x,y):
    global nowX, nowY, angle, eyeX, eyeY, eyeZ, phi
    if (midDown == True):
        pastX = nowX
        pastY = nowY 
        nowX = x
        nowY = y
        if (nowX - pastX > 0):
            angle -= 0.25
        elif (nowX - pastX < 0):
            angle += 0.25
        #elif (nowY - pastY > 0): look into looking over and under object...
            #phi += 1.0
        #elif (nowX - pastY <0):
            #phi -= 1.0
        eyeX = radius * math.sin(angle) 
        eyeZ = radius * math.cos(angle)
        #eyeY = radius * math.sin(phi)
    if centered == False:
        setView()
    elif centered == True:
        setObjView()
    #print eyeX, eyeY, eyeZ, nowX, nowY, radius, angle
    #print "getting handled"

def mouseWheel(button, dir, x, y):
    global eyeX, eyeY, eyeZ, radius
    if (dir > 0): #zoom in
        radius -= 1
        #setView()
       # print "zoom in!"
    elif (dir < 0): #zoom out
        radius += 1
        #setView()
     #   print "zoom out!"
    eyeX = radius * math.sin(angle)
    eyeZ = radius * math.cos(angle)
    if centered == False:
        setView()
    elif centered == True:
        setObjView()


def specialKeys(keypress, mX, mY):
    # things to do
    # this is the function to move the car
    pass

def myKeyboard(key, mX, mY):
    global eyeX, eyeY, eyeZ, angle, radius, helpWindow, centered, helpWin, overReason, topView, behindView
    if key == "h":
        print "h pushed " + str(helpWindow)
        winNum = glutGetWindow()
        if helpWindow == False:
            helpWindow = True
            glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
            glutInitWindowSize(500,300)
            glutInitWindowPosition(600,0)
            helpWin = glutCreateWindow('Help Guide')
            glutDisplayFunc(showHelp)
            glutKeyboardFunc(myKeyboard)
            glutMainLoop()
        elif helpWindow == True and winNum!=1:
            helpWindow = False
            print glutGetWindow()
            glutHideWindow()
            glutMainLoop()

    if key == "r":
        print eyeX, eyeY, eyeZ, angle, radius
        eyeX = 0.0
        eyeY = 2.0
        eyeZ = 10.0
        angle = 0.0
        radius = 10.0
        if centered == False:
            setView()
        elif centered == True:
            setObjView()
    elif key == "h":
        print "h pushed " + str(helpWindow)
        winNum = glutGetWindow()
        if helpWindow == False:
            helpWindow = True
            glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
            glutInitWindowSize(500,300)
            glutInitWindowPosition(600,0)
            helpWin = glutCreateWindow('Help Guide')
            glutDisplayFunc(showHelp)
            glutKeyboardFunc(stdKey)
            glutMainLoop()
        elif helpWindow == True and winNum!=1:
            helpWindow = False
            print glutGetWindow()
            glutHideWindow()
            #glutDestroyWindow(helpWin)
            glutMainLoop()
    elif key == "l":
        print "light triggered!"
        if jeepObj.lightOn == True:
            jeepObj.lightOn = False
        elif jeepObj.lightOn == False:
            jeepObj.lightOn = True
        glutPostRedisplay()
    elif key == "c":
        if centered == True:
            centered = False
            print "non-centered view"
        elif centered == False:
            centered = True
            print "centered view"
    elif key == "t":#top view, like a map ####################!!!!!!
        if (topView == True):
            topView = False
        elif (topView == False):
            topView = True
        if centered == False:
            setView()
        elif centered == True:
            setObjView()
    elif key == "b": #behind the wheel
        if (behindView == True):
            behindView = False
        elif (behindView == False):
            behindView = True
        setView()
    elif key == "q" and canStart == True:
        overReason = "You decided to quit!"
        gameOver()

#-------------------------------------------------tools----------------------       
def drawTextBitmap(string, x, y): #for writing text to display
    glRasterPos2f(x, y)
    for char in string:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def text3d(string, x, y, z):
    glRasterPos3f(x,y,z)
    for char in string:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def dist(pt1, pt2):
    a = pt1[0]
    b = pt1[1]
    x = pt2[0]
    y = pt2[1]
    return math.sqrt((a-x)**2 + (b-y)**2)

def noReshape(newX, newY): #used to ensure program works correctly when resized
    glutReshapeWindow(windowSize,windowSize)

#--------------------------------------------making game more complex--------
def addCone(x,z):
    allcones.append(cone.cone(x,z))
    obstacleCoord.append((x,z))

def collisionCheck():
    global overReason, score, usedDiamond, countTime
    for obstacle in obstacleCoord:
        if dist((jeepObj.posX, jeepObj.posZ), obstacle) <= ckSense:
            overReason = "You hit an obstacle!"
            gameOver()
    if (jeepObj.posX >= land or jeepObj.posX <= -land):
        overReason = "You ran off the road!"
        gameOver()
    for reward in rewardCoord:
        if dist((jeepObj.posX, jeepObj.posZ), reward) <= ckSense:
            print "Star bonus!"
            allstars.pop(rewardCoord.index(reward))
            rewardCoord.remove(reward)
            countTime -= 10
    if (dist((jeepObj.posX, jeepObj.posZ), (diamondObj.posX, diamondObj.posZ)) <= ckSense and usedDiamond ==False):
        print "Diamond bonus!"
        countTime /= 2
        usedDiamond = True
    if (jeepObj.posZ >= land*gameEnlarge):
        gameSuccess()
        
#----------------------------------multiplayer dev (using tracker)-----------
def recordGame():
    with open('results.csv', 'wt') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print st
        spamwriter.writerow([st] + [finalScore])
    
#-------------------------------------developing additional windows/options----
def gameOver():
    global finalScore
    print "Game completed!"
    finalScore = score-6
    #recordGame() #add to excel
    glutHideWindow()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(200,200)
    glutInitWindowPosition(600,100)
    overWin = glutCreateWindow("Game Over!")
    glutDisplayFunc(overScreen)
    glutMainLoop()
    
def gameSuccess():
    global finalScore
    print "Game success!"
    finalScore = score-6
    #recordGame() #add to excel
    glutHideWindow()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(200,200)
    glutInitWindowPosition(600,100)
    overWin = glutCreateWindow("Complete!")
    glutDisplayFunc(winScreen)
    glutMainLoop()

def winScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glColor3f(0.0,1.0,0.0)
    drawTextBitmap("Completed Trial!" , -0.6, 0.85)
    glColor3f(0.0,1.0,0.0)
    drawTextBitmap("Your score is: ", -1.0, 0.0)
    glColor3f(1.0,1.0,1.0)
    drawTextBitmap(str(finalScore), -1.0, -0.15)
    glutSwapBuffers()


def overScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glColor3f(1.0,0.0,1.0)
    drawTextBitmap("Incomplete Trial" , -0.6, 0.85)
    glColor3f(0.0,1.0,0.0)
    drawTextBitmap("Because you..." , -1.0, 0.5)
    glColor3f(1.0,1.0,1.0)
    drawTextBitmap(overReason, -1.0, 0.35)
    glColor3f(0.0,1.0,0.0)
    drawTextBitmap("Your score stopped at: ", -1.0, 0.0)
    glColor3f(1.0,1.0,1.0)
    drawTextBitmap(str(finalScore), -1.0, -0.15)
    glutSwapBuffers()

def showHelp():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glColor3f(1.0,0.0,0.0)
    drawTextBitmap("Help Guide" , -0.2, 0.85)
    glColor3f(0.0,0.0,1.0)
    drawTextBitmap("describe your control strategy." , -1.0, 0.7)
    glutSwapBuffers()

#----------------------------------------------texture development-----------
def loadTexture(imageName):
    texturedImage = Image.open(imageName)
    try:
        imgX = texturedImage.size[0]
        imgY = texturedImage.size[1]
        img = texturedImage.tobytes("raw","RGBX",0,-1)#tostring("raw", "RGBX", 0, -1)
    except Exception, e:
        print "Error:", e
        print "Switching to RGBA mode."
        imgX = texturedImage.size[0]
        imgY = texturedImage.size[1]
        img = texturedImage.tobytes("raw","RGB",0,-1)#tostring("raw", "RGBA", 0, -1)

    tempID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tempID)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, imgX, imgY, 0, GL_RGBA, GL_UNSIGNED_BYTE, img)
    return tempID

def loadSceneTextures():
    global roadTextureID
    roadTextureID = loadTexture("../img/road2.png")
    
#-----------------------------------------------lighting work--------------
def initializeLight():
    glEnable(GL_LIGHTING)                
    glEnable(GL_LIGHT0)                 
    glEnable(GL_DEPTH_TEST)              
    glEnable(GL_NORMALIZE)     

  #  glShadeModel(GL_SMOOTH)
  #  glEnable(GL_CULL_FACE)          
    glClearColor(0.1, 0.1, 0.1, 0.0)


def passivemotion(x,y):
    global mvx, mvy, oldy, oldx
    mvx +=  y - oldy;
    mvy +=  x - oldx;
    oldy = y
    oldx = x
    glutPostRedisplay()

#~~~~~~~~~~~~~~~~~~~~~~~~~the finale!!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main():
    glutInit()

    global prevTime, mainWin
    prevTime = glutGet(GLUT_ELAPSED_TIME)
    
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    # things to do
    # change the window resolution in the game
    glutInitWindowSize(windowSize, windowSize)
    
    glutInitWindowPosition(0, 0)
    mainWin = glutCreateWindow('CS4182')
    glutDisplayFunc(display)
    glutIdleFunc(idle)#wheel turn

    setView()
    glLoadIdentity()
    glEnable(GL_DEPTH_TEST)   

    glutMouseFunc(mouseHandle)
    glutMotionFunc(motionHandle)
    glutMouseWheelFunc(mouseWheel)
    glutPassiveMotionFunc(passivemotion)
    glutSpecialFunc(specialKeys)
    glutKeyboardFunc(myKeyboard)
    glutReshapeFunc(noReshape)
    # things to do
    # add a menu 
    lightSet.createMenu()
    loadSceneTextures()

    jeep1Obj.makeDisplayLists()
    jeep2Obj.makeDisplayLists()
    jeep3Obj.makeDisplayLists()
    #personObj.makeDisplayLists()

    # things to do
    # add a automatic object
    for i in range(coneAmount):#create cones randomly for obstacles, making sure to give a little lag time in beginning by adding 10.0 buffer
        addCone(random.randint(-land, land), random.randint(10.0, land*gameEnlarge))

    # things to do
    # add stars

    for cone in allcones:
        cone.makeDisplayLists()

    for star in allstars:
        star.makeDisplayLists()

    
    # diamondObj.makeDisplayLists()
    
    staticObjects()
    if (applyLighting == True):
        initializeLight()
    glutMainLoop()



    
main()

