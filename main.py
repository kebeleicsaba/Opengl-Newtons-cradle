import os
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders
import math
import pyrr
import numpy as np
from PIL import Image
from cubemap.SkyBox import SkyBox
from cradleElement.CradleElement import CradleElement
from sphere.Sphere import Sphere
from Camera import Camera

xPosPrev = 0
yPosPrev = 0
firstCursorCallback = True
sensitivity = 0.05

def cursorCallback(window, xPos, yPos):
	global firstCursorCallback
	global sensitivity
	global xPosPrev, yPosPrev
	if firstCursorCallback:
		firstCursorCallback = False	
	else:
		xDiff = xPos - xPosPrev
		yDiff = yPosPrev - yPos
		camera.rotateUpDown(yDiff * sensitivity)
		camera.rotateRightLeft(xDiff * sensitivity)

	xPosPrev = xPos
	yPosPrev = yPos

# Atallitjuk az eleresi utat az aktualis fajlhoz
os.chdir(os.path.dirname(os.path.abspath(__file__)))

if not glfw.init():
	raise Exception("glfw init hiba")
	
window = glfw.create_window(1280, 720, "OpenGL window", 
	None, None)

if not window:
	glfw.terminate()
	raise Exception("glfw window init hiba")

glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
glfw.set_cursor_pos_callback(window, cursorCallback)	

glfw.make_context_current(window)
glEnable(GL_DEPTH_TEST)
glViewport(0, 0, 1280, 720)

camera = Camera(0, 0, 50)

with open("./texture/vertex_shader_texture.vert") as f:
	vertex_shader = f.read()

with open("./texture/fragment_shader_texture.frag") as f:
	fragment_shader = f.read()

# A fajlbol beolvasott stringeket leforditjuk, es a ket shaderbol egy shader programot gyartunk.
shader = OpenGL.GL.shaders.compileProgram(
	OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
    OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER),
	validate=False
)


exitProgram = False

skyBox = SkyBox("./images/right.png", "./images/left.png", "./images/top.png", 
				"./images/bottom.png", "./images/front.png", "./images/back.png")

texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture)

# Set the texture wrapping parameters
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
# Set texture filtering parameters
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

# load image
image = Image.open("./images/wood.jpg")
img_data = image.convert("RGBA").tobytes()
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)


perspMat = pyrr.matrix44.create_perspective_projection_matrix(45.0, 1280.0 / 720.0, 0.1, 100.0)

# Kijeloljuk, hogy melyik shader programot szeretnenk hasznalni. Tobb is lehet a programunkban,
# ha esetleg a programunk kulonbozo tipusu anyagokat szeretne megjeleniteni.
glUseProgram(shader)


lightX = -200.0
lightY = 200.0
lightZ = 100.0
lightPos_loc = glGetUniformLocation(shader, 'lightPos');
viewPos_loc = glGetUniformLocation(shader, 'viewPos');

glUniform3f(lightPos_loc, lightX, lightY, lightZ)
glUniform3f(viewPos_loc, camera.x, camera.y, camera.z )

materialAmbientColor_loc = glGetUniformLocation(shader, "materialAmbientColor")
materialDiffuseColor_loc = glGetUniformLocation(shader, "materialDiffuseColor")
materialSpecularColor_loc = glGetUniformLocation(shader, "materialSpecularColor")
materialEmissionColor_loc = glGetUniformLocation(shader, "materialEmissionColor")
materialShine_loc = glGetUniformLocation(shader, "materialShine")

lightAmbientColor_loc = glGetUniformLocation(shader, "lightAmbientColor")
lightDiffuseColor_loc = glGetUniformLocation(shader, "lightDiffuseColor")
lightSpecularColor_loc = glGetUniformLocation(shader, "lightSpecularColor")

glUniform3f(lightAmbientColor_loc, 1.0, 1.0, 1.0)
glUniform3f(lightDiffuseColor_loc, 1.0, 1.0, 1.0)
glUniform3f(lightSpecularColor_loc, 1.0, 1.0, 1.0)


# Lekerdezzuk a shaderben levo 'projection' es 'modelView' matrixok helyet, hogy majd 
# innen kivulrol fel tudjuk tolteni oket adatokkal.
perspectiveLocation = glGetUniformLocation(shader, "projection")
worldLocation = glGetUniformLocation(shader, "world")
viewLocation = glGetUniformLocation(shader, "view")
viewWorldLocation = glGetUniformLocation(shader, "viewWorld")

# Eloallitunk egy projekcios matrixot, a parameterezes ugyanaz, mint a gluPerspective-nek
perspMat = pyrr.matrix44.create_perspective_projection_matrix(45.0, 1280.0 / 720.0, 0.1, 1000.0)
# Atadjuk az eloallitott matrixot a shader-ben levo 'projection' matrixnak
glUniformMatrix4fv(perspectiveLocation, 1, GL_FALSE, perspMat)


# Init Cradle
CradleBase = CradleElement(0, 0, 0, 25, 2, 10, lightX, lightY, lightZ)
CradleStanchion1 = CradleElement(0.5, 1.9, -0.5, 1, 20, 1, lightX, lightY, lightZ)
CradleStanchion2 = CradleElement(23.5, 1.9, -0.5, 1, 20, 1, lightX, lightY, lightZ)
CradleStanchion3 = CradleElement(23.5, 1.9, -8.5, 1, 20, 1, lightX, lightY, lightZ)
CradleStanchion4 = CradleElement(0.5, 1.9, -8.5, 1, 20, 1, lightX, lightY, lightZ)
CradleStanchion5 = CradleElement(0.5, 21, -0.5, 24, 1, 1, lightX, lightY, lightZ)
CradleStanchion6 = CradleElement(0.5, 21, -8.5, 24, 1, 1, lightX, lightY, lightZ)

# Init Spheres
NUMBER_OF_SPHERES = 4
SPHERE_R = 2
G = 9.8
LENGTH = 14
INITIAL_ANGLE = 0.8
spheres = []
spheres = [
	{"sphere": Sphere(2, -5, lightX, lightY, lightZ),
	 "x": LENGTH*np.sin(0) + (25/2 -NUMBER_OF_SPHERES/2*SPHERE_R-SPHERE_R) + i * (SPHERE_R*2),
	 "y": -LENGTH*np.cos(0) + 21,
	 "axis_x": (25/2 -NUMBER_OF_SPHERES/2*SPHERE_R-SPHERE_R) + i * (SPHERE_R*2),
	 "axis_y": 21} for i in range(NUMBER_OF_SPHERES)] 


def position(right, t):
    #theta(t) = theta 0*cos(sqrt(g/L)*t)
    theta = INITIAL_ANGLE*np.cos((G/LENGTH)**(1/2)*t)
 
    if not right:
        spheres[0]["x"] = LENGTH * np.sin(theta) + spheres[0]["axis_x"]  
        spheres[0]["y"] = -LENGTH * np.cos(theta) + spheres[0]["axis_y"]
    else:
        spheres[-1]["x"] = LENGTH * np.sin(theta) + spheres[-1]["axis_x"]  
        spheres[-1]["y"] = -LENGTH * np.cos(theta) + spheres[-1]["axis_y"]
 
    if theta <= 0:
        return False 
    else:
        return True

def cradleRender() -> None:
	CradleBase.render(camera, perspMat)
	CradleStanchion1.render(camera, perspMat)
	CradleStanchion2.render(camera, perspMat)
	CradleStanchion3.render(camera, perspMat)
	CradleStanchion4.render(camera, perspMat)
	CradleStanchion5.render(camera, perspMat)
	CradleStanchion6.render(camera, perspMat)


viewMat = pyrr.matrix44.create_look_at([0.0, 0.0, 0.0], [0.0, 0.0, -1.0], [0.0, 1.0, 0.0])
i = 0.0
right = True

while not glfw.window_should_close(window) and not exitProgram:
	glfw.poll_events()

	if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
		exitProgram = True

	direction = 0
	if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
		direction = -0.5
	if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
		direction = 0.5
	camera.move(direction)

	glClearDepth(1.0)
	glClearColor(0, 0.1, 0.1, 1)
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

	# Render
	skyBox.render(perspMat, camera.getMatrixForCubemap())
	cradleRender()
	for s in spheres:
		s["sphere"].render(camera, perspMat, s["x"], s["y"])


	glUseProgram(shader)
	right = position(right, i)
	i += 0.037

	glUniform3f(viewPos_loc, camera.x, camera.y, camera.z )	

	skybox_loc = glGetUniformLocation(shader, "skybox")
	glUniform1i(skybox_loc, 0)
	skyBox.activateCubeMap(shader, 1)

	glfw.swap_buffers(window)
	
glfw.terminate()
