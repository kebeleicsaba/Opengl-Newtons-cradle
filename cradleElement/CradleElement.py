from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders
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

    def __init__(self, x, y, z, xSize, ySize, zSize, lightX, lightY, lightZ) -> None:
        self.x = x 
        self.y = y
        self.z = z
        self.xSize = xSize
        self.ySize = ySize
        self.zSize = zSize
        self.lightX = lightX 
        self.lightY = lightY 
        self.lightZ = lightZ

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


        materialAmbientColor_loc = glGetUniformLocation(self.shader, "materialAmbientColor")
        materialDiffuseColor_loc = glGetUniformLocation(self.shader, "materialDiffuseColor")
        materialSpecularColor_loc = glGetUniformLocation(self.shader, "materialSpecularColor")
        materialEmissionColor_loc = glGetUniformLocation(self.shader, "materialEmissionColor")
        materialShine_loc = glGetUniformLocation(self.shader, "materialShine")
        glUniform3f(materialAmbientColor_loc, 0.25, 0.25, 0.25)
        glUniform3f(materialDiffuseColor_loc, 0.4, 0.4, 0.4)
        glUniform3f(materialSpecularColor_loc, 0.774597, 0.774597, 0.774597)
        glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
        glUniform1f(materialShine_loc, 76.8)

        lightAmbientColor_loc = glGetUniformLocation(self.shader, "lightAmbientColor")
        lightDiffuseColor_loc = glGetUniformLocation(self.shader, "lightDiffuseColor")
        lightSpecularColor_loc = glGetUniformLocation(self.shader, "lightSpecularColor")

        glUniform3f(lightAmbientColor_loc, 1.0, 1.0, 1.0)
        glUniform3f(lightDiffuseColor_loc, 1.0, 1.0, 1.0)
        glUniform3f(lightSpecularColor_loc, 1.0, 1.0, 1.0)

        lightPos_loc = glGetUniformLocation(self.shader, 'lightPos')
        viewPos_loc = glGetUniformLocation(self.shader, 'viewPos')
        glUniform3f(lightPos_loc, self.lightX, self.lightY, self.lightZ)
        glUniform3f(viewPos_loc, camera.x, camera.y, camera.z)


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

        

            