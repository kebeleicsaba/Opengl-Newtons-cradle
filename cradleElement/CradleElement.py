from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders
import math
import numpy
import pyrr
from texture.Texture import Texture

class CradleElement:
    def setShaders(self):
            with open("./cradleElement/vertex_shader_cradleElement.vert") as f:
                vertex_shader = f.read()
            with open("./cradleElement/fragment_shader_cradleElement.frag") as f:
                fragment_shader = f.read()

            self.shader = OpenGL.GL.shaders.compileProgram(
		    	OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
    	    	OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
		    )

    def __init__(self, x, y, z, xSize, ySize, zSize) -> None:
        self.x = x 
        self.y = y
        self.z = z
        self.xSize = xSize
        self.ySize = ySize
        self.zSize = zSize

        vertices = [
            0,  ySize,   0,  0, 1, 0, 0, 0,
	        xSize,  ySize,   0,  0, 1, 0, 0, 1,
			xSize,  ySize, -ySize,  0, 1, 0, 1, 1,
			0,  ySize, -ySize,  0, 1, 0, 1, 0,

			0, 0,   0,  0, -1, 0, 0, 0,
			xSize, 0,   0,  0, -1, 0, 0, 1,
			xSize, 0, -ySize,  0, -1, 0, 1, 1,
			0, 0, -ySize,  0, -1, 0, 1, 0,

			xSize,  0,   0,  1, 0, 0, 0, 0,
			xSize,  0, -ySize,  1, 0, 0, 0, 1,
			xSize, ySize, -ySize,  1, 0, 0, 1, 1,
			xSize, ySize,   0,  1, 0, 0, 1, 0,

			0,  0,   0, -1, 0, 0, 0, 0,
			0,  0, -ySize, -1, 0, 0, 0, 1,
			0, ySize, -ySize, -1, 0, 0, 1, 1,
			0, ySize,   0, -1, 0, 0, 1, 0,

			0,  0,   0, 0, 0, 1, 0, 0,
			xSize, 0,   0, 0, 0, 1, 0, 1,
			xSize, ySize,  0, 0, 0, 1, 1, 1,
			0,  ySize,  0, 0, 0, 1, 1, 0,

			0,  0,  -ySize,  0, 0, -1, 0, 0,
			xSize, 0,  -ySize,  0, 0, -1, 0, 1,
			xSize, ySize, -ySize,  0, 0, -1, 1, 1,
			0, ySize, -ySize,   0, 0, -1, 1, 0
            
            ]

        vertices = numpy.array(vertices, dtype=numpy.float32)
        self.buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        self.setShaders()

        self.textureImg = Texture("./images/wood.jpg")
        
        def render(self):
            pass
            