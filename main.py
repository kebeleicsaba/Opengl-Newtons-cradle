import os
from enum import Enum
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders
import math
import numpy
import pyrr
from PIL import Image
from cubemap.SkyBox import SkyBox
from cradleElement.CradleElement import CradleElement
from sphere.Sphere import Sphere
from texture.Texture import Texture
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
# ezekre innentol nincs szukseg, mi magunk allitjuk elo a projekcios matrixot:
#glMatrixMode(GL_PROJECTION)
#glLoadIdentity()
#gluPerspective(45, 1280.0 / 720.0, 0.1, 1000.0)

camera = Camera(0, 0, 50)

with open("./texture/vertex_shader_texture.vert") as f:
	vertex_shader = f.read()
	print(vertex_shader)

with open("./texture/fragment_shader_texture.frag") as f:
	fragment_shader = f.read()
	print(fragment_shader)

# A fajlbol beolvasott stringeket leforditjuk, es a ket shaderbol egy shader programot gyartunk.
shader = OpenGL.GL.shaders.compileProgram(
	OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
    OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER),
	validate=False
)


exitProgram = False

skyBox = SkyBox("./images/right.jpg", "./images/left.jpg", "./images/top.jpg", 
				"./images/bottom.jpg", "./images/front.jpg", "./images/back.jpg")

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
#image = image.transpose(Image.FLIP_TOP_BOTTOM)
img_data = image.convert("RGBA").tobytes()
# img_data = np.array(image.getdata(), np.uint8) # second way of getting the raw image data
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

#vertCount = 6*4
#shapeType = GL_QUADS
#zTranslate = -50

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

#cube = createObject(shader)

# Init Cradle
CradleBase = CradleElement(0, 0, 0, 25, 2, 10, lightX, lightY, lightZ)
CradleStanchion1 = CradleElement(0.5, 1.9, -0.5, 1, 20, 1, lightX, lightY, lightZ)
CradleStanchion2 = CradleElement(23.5, 1.9, -0.5, 1, 20, 1, lightX, lightY, lightZ)
CradleStanchion3 = CradleElement(23.5, 1.9, -8.5, 1, 20, 1, lightX, lightY, lightZ)
CradleStanchion4 = CradleElement(0.5, 1.9, -8.5, 1, 20, 1, lightX, lightY, lightZ)
CradleStanchion5 = CradleElement(0.5, 21, -0.5, 24, 1, 1, lightX, lightY, lightZ)
CradleStanchion6 = CradleElement(0.5, 21, -8.5, 24, 1, 1, lightX, lightY, lightZ)
#CradleStanchion7 = CradleElement(6.5, 21, -5, 2, 2, 2)

# Init Spheres
NUMBER_OF_SPHERES = 4
SPHERE_R = 2
spheres = [
	{"sphere": Sphere(2, -5, lightX, lightY, lightZ),
	 "x": 6.5 + i * (SPHERE_R*2),
	 "y": 8,
	 "rot_x": 6.5 + i * (SPHERE_R*2),
	 "rot_y": 21} for i in range(NUMBER_OF_SPHERES)] 


def cradleRender() -> None:
	CradleBase.render(camera, perspMat)
	CradleStanchion1.render(camera, perspMat)
	CradleStanchion2.render(camera, perspMat)
	CradleStanchion3.render(camera, perspMat)
	CradleStanchion4.render(camera, perspMat)
	CradleStanchion5.render(camera, perspMat)
	CradleStanchion6.render(camera, perspMat)


viewMat = pyrr.matrix44.create_look_at([0.0, 0.0, 0.0], [0.0, 0.0, -1.0], [0.0, 1.0, 0.0])
angle = 0.0

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

	#transMat = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, 0, 0.0]))
	#rotMatY = pyrr.matrix44.create_from_y_rotation(math.radians(angle*0))
	#rotMatX = pyrr.matrix44.create_from_x_rotation(math.radians(angle))
	#rotMat = pyrr.matrix44.multiply(rotMatY, rotMatX)
	#modelMat = pyrr.matrix44.multiply(rotMat, transMat)

	# Render
	skyBox.render(perspMat, camera.getMatrixForCubemap())
	cradleRender()
	for s in spheres:
		x = 14 * math.cos(angle*2*math.pi/32) + s["rot_x"]
		y = 14 * math.sin(angle*2*math.pi/32) + s["rot_y"]
		print(x,y)
		s["sphere"].render(camera, perspMat, x, y)

	# Ez a world helyett
	pyrr.matrix44.create_identity()

	glUseProgram(shader)
	# Innentol kezdve ezekre se lesz szukseg, megoldjuk mashogy:
	#glMatrixMode(GL_MODELVIEW)
	#glLoadIdentity()
	#transMat = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, 0, zTranslate]))
	#rotMatY = pyrr.matrix44.create_from_y_rotation(math.radians(angle*0))
	#rotMatX = pyrr.matrix44.create_from_x_rotation(math.radians(angle))
	#rotMat = pyrr.matrix44.multiply(rotMatY, rotMatX)
	
	# vagy akar a glRotatef-et is helyettesithetjuk
	# FONTOS!! A Vector3 konstruktoraban lathato szamok lebegopontosak legyenek, azaz 
	# mindenkeppen szerepeljen bennuk egy . is, vagy .0 vegzodes (meg ha egeszeket is adunk meg),
	# kulonben hibas lesz a matrix.

	#rotMat = pyrr.matrix44.create_from_axis_rotation(pyrr.Vector3([1., 1., 1.0]), math.radians(angle))
	
	# Ez hibas... just Python things :(
	#rotMat = pyrr.matrix44.create_from_axis_rotation(pyrr.Vector3([1, 1, 1]), math.radians(angle))

	# Ezekre se lesz szukseg, megoldjuk mashogy:
	#glTranslatef(0, 0, -50)
	#glScalef(0.1, 0.1, 0.1)
	#glRotatef(angle, 1, 1, 1)
	angle += -0.05

	glUniform3f(viewPos_loc, camera.x, camera.y, camera.z )	

	#modelMat = pyrr.matrix44.multiply(rotMat, transMat)
	#glUniformMatrix4fv(worldLocation, 1, GL_FALSE, modelMat )
	#glUniformMatrix4fv(viewLocation, 1, GL_FALSE, camera.getMatrix() )

	#viewWorldMatrix = pyrr.matrix44.multiply(modelMat, camera.getMatrix())
	#glUniformMatrix4fv(viewWorldLocation, 1, GL_FALSE, viewWorldMatrix)

	skybox_loc = glGetUniformLocation(shader, "skybox")
	glUniform1i(skybox_loc, 0)
	skyBox.activateCubeMap(shader, 1)
	#renderModel(cube, vertCount, shapeType)

	glfw.swap_buffers(window)
	
glfw.terminate()
