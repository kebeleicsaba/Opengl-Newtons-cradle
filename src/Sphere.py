from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders
from texture.Texture import Texture
import math
import numpy
import pyrr

class Sphere:
    def setShaders(self):
        with open("./cradleElement/vertex_shader_cradleElement.vert") as f:
            vertex_shader = f.read()
        with open("./cradleElement/fragment_shader_cradleElement.frag") as f:
            fragment_shader = f.read()

        self.shader = OpenGL.GL.shaders.compileProgram(
			OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
    		OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
		    )

    def __init__(self, radius:int, z:int, lightX, lightY, lightZ) -> None:
        self.radius = radius
        self.z = z
        self.lightX = lightX 
        self.lightY = lightY 
        self.lightZ = lightZ

        vertices = self.createSphere(50, 50)
        vertices = numpy.array(vertices, dtype=numpy.float32)
        self.sphereVertCount = int(len(vertices) / 6)
       
        self.sphereBuffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.sphereBuffer)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        self.setShaders()

        self.texture = Texture("./images/metal.jpg")

    def getSpherePoint(self, vertIndex:int, horizIndex:int, vertSlices:int, horizSlices:int) -> list:
        # eszaki sark:
        tx = 1.0 - horizIndex / horizSlices
        if vertIndex == 0:
            return [0.0, self.radius, 0.0, 0.0, 1.0, 0.0, tx, 0.0]
        # deli sark:
        if vertIndex == vertSlices - 1:
            return [0.0, -self.radius, 0.0, 0.0, -1.0, 0.0, tx, 1.0]
        alpha = math.radians(180 * (vertIndex / vertSlices))
        beta = math.radians(360 * (horizIndex / horizSlices))
        x = self.radius * math.sin(alpha) * math.cos(beta)
        y = self.radius * math.cos(alpha)
        z = self.radius * math.sin(alpha) * math.sin(beta)
        l = math.sqrt(x**2 + y**2 + z**2)
        nx = x / l
        ny = y / l
        nz = z / l
        ty = vertIndex / vertSlices
        return [x, y, z, nx, ny, nz, tx, ty]

    def createSphere(self, vertSlices:int, horizSlices:int) -> list:
        vertList = []
        for i in range(vertSlices):
    	    for j in range(horizSlices):
                vert1 = self.getSpherePoint(i, j, vertSlices, horizSlices)
                vert2 = self.getSpherePoint(i + 1, j, vertSlices, horizSlices)
                vert3 = self.getSpherePoint(i + 1, j + 1, vertSlices, horizSlices)
                vert4 = self.getSpherePoint(i, j + 1, vertSlices, horizSlices)
                vertList.extend(vert1)
                vertList.extend(vert2)
                vertList.extend(vert3)
                vertList.extend(vert4)
        return vertList

    def render(self, camera, projectionMatrix, x, y):
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
        
        glBindBuffer(GL_ARRAY_BUFFER, self.sphereBuffer)

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
        self.texture.activate()

        transMat = pyrr.matrix44.create_from_translation(pyrr.Vector3([x, y, self.z]))
        glUniformMatrix4fv(world_loc, 1, GL_FALSE, transMat)

        glDrawArrays(GL_QUADS, 0, self.sphereVertCount)

        glBindBuffer(GL_ARRAY_BUFFER, 0)


    
        