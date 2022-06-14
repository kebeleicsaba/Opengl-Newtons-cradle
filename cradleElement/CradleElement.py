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
			xSize,  ySize, -zSize,  0, 1, 0, 1, 1,
			0,  ySize, -zSize,  0, 1, 0, 1, 0,

			0, 0,   0,  0, -1, 0, 0, 0,
			xSize, 0,   0,  0, -1, 0, 0, 1,
			xSize, 0, -zSize,  0, -1, 0, 1, 1,
			0, 0, -zSize,  0, -1, 0, 1, 0,

			xSize,  0,   0,  1, 0, 0, 0, 0,
			xSize,  0, -zSize,  1, 0, 0, 0, 1,
			xSize, ySize, -zSize,  1, 0, 0, 1, 1,
			xSize, ySize,   0,  1, 0, 0, 1, 0,

			0,  0,   0, -1, 0, 0, 0, 0,
			0,  0, -zSize, -1, 0, 0, 0, 1,
			0, ySize, -zSize, -1, 0, 0, 1, 1,
			0, ySize,   0, -1, 0, 0, 1, 0,

			0,  0,   0, 0, 0, 1, 0, 0,
			xSize, 0,   0, 0, 0, 1, 0, 1,
			xSize, ySize,  0, 0, 0, 1, 1, 1,
			0,  ySize,  0, 0, 0, 1, 1, 0,

			0,  0,  -zSize,  0, 0, -1, 0, 0,
			xSize, 0,  -zSize,  0, 0, -1, 0, 1,
			xSize, ySize, -zSize,  0, 0, -1, 1, 1,
			0, ySize, -zSize,   0, 0, -1, 1, 0
            
            ]

        vertices = numpy.array(vertices, dtype=numpy.float32)
        self.buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        self.setShaders()

        self.textureImg = Texture("./images/wood.jpg")
        
    def render(self, camera, projectionMatrix):
        glUseProgram(self.shader)
        proj_loc = glGetUniformLocation(self.shader, 'projection');
        view_loc = glGetUniformLocation(self.shader, 'view');
        world_loc = glGetUniformLocation(self.shader, 'world');
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projectionMatrix)
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, camera.getMatrix())
        
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer)

        position_loc = glGetAttribLocation(self.shader, 'in_position')
        glEnableVertexAttribArray(position_loc)
        glVertexAttribPointer(position_loc, 3, GL_FLOAT, False, 4 * 8, ctypes.c_void_p(0))

        normal_loc = glGetAttribLocation(self.shader, 'in_normal')
        glEnableVertexAttribArray(normal_loc)
        glVertexAttribPointer(normal_loc, 3, GL_FLOAT, False, 4 * 8, ctypes.c_void_p(12))

        texture_loc = glGetAttribLocation(self.shader, 'in_texture')
        glEnableVertexAttribArray(texture_loc)
        glVertexAttribPointer(texture_loc, 2, GL_FLOAT, False, 4 * 8, ctypes.c_void_p(24))
        
        Texture.enableTexturing()
        self.textureImg.activate()

        transMat = pyrr.matrix44.create_from_translation(pyrr.Vector3([self.x, self.y, self.z]))
        glUniformMatrix4fv(world_loc, 1, GL_FALSE, transMat)
            
        glDrawArrays(GL_QUADS, 0, 24)

        glBindBuffer(GL_ARRAY_BUFFER, 0)

        

            