#!/usr/bin/env python2

'''A grating stimulus for psychopy with a luminance pedestal.

This makes it possible for a grating to fluctuate around a background value that
is not mean gray, a.k.a color=0.

This is based on code by Jonathan Peirce, in particular it is based on his
shader code and 'GratingStim' class. The original code carries the following
license:

Part of the PsychoPy library
Copyright (C) 2015 Jonathan Peirce
Distributed under the terms of the GNU General Public License (GPL).

Accordingly, this code is also licensed under the GNU General Public License (3+).

Psychopy can be found here: http://www.psychopy.org/
'''

import pyglet
pyglet.options['debug_gl'] = False
GL = pyglet.gl

from psychopy.visual.basevisual import (BaseVisualStim, ColorMixin,
                                        ContainerMixin, TextureMixin)
from psychopy.visual.grating import GratingStim
from psychopy.tools.attributetools import attributeSetter

import numpy
#from psychopy import _shadersPyglet as _shaders
from psychopy.visual import shaders

# Framgent shader for the gabor stimulus. This is needed to add the pedestal to the
# color values for each location. I'm keeping it in this file to make the stimulus
# fairly self contained and to avoid messing with anything else. Almost a one to
# one copy of the original psychopy shader.
fragSignedColorTexMask_pedestal = '''
    uniform sampler2D texture, mask;
    uniform float pedestal;
    void main() {
        vec4 textureFrag = texture2D(texture,gl_TexCoord[0].st);
        vec4 maskFrag = texture2D(mask,gl_TexCoord[1].st);
        gl_FragColor.a = gl_Color.a*maskFrag.a*textureFrag.a;
        gl_FragColor.rgb =  ((pedestal+1.0)/2.0) + ((textureFrag.rgb* (gl_Color.rgb*2.0-1.0)+1.0)/2.0) -0.5;
    }
    '''

class PedestalGratingStim(GratingStim, TextureMixin, ColorMixin, ContainerMixin):
    """
    A grating stimulus for psychopy that allows a luminance pedestal (e.g. gratings
    that fluctuate around a specified background color).

    Usage is the same as psychopy.visual.grating.GratingStim. See those docs for
    more information. The only extra parameter is:

    pedestal : float
    """
    def __init__(self,  win, tex="sin",
                 mask="none", units="", pos=(0.0, 0.0), size=None,
                 sf=None, ori=0.0, phase=(0.0, 0.0),
                 texRes=128, rgb=None, dkl=None,
                 lms=None, color=(1.0, 1.0, 1.0), colorSpace='rgb',
                 contrast=1.0, opacity=1.0, depth=0,
                 rgbPedestal=(0.0, 0.0, 0.0), interpolate=False, name=None,
                 autoLog=None, autoDraw=False, maskParams=None, pedestal=0.0):

        #initialise parent class
        super(PedestalGratingStim, self).__init__(win, units=units, name=name,
                autoLog=autoLog, tex=tex, mask=mask, pos=pos, size=size, sf=sf,
                ori=ori, phase=phase, texRes=texRes, rgb=rgb, dkl=dkl, lms=lms,
                color=color, colorSpace=colorSpace, contrast=contrast,
                opacity=opacity, depth=depth, rgbPedestal=rgbPedestal,
                interpolate=interpolate, autoDraw=autoDraw, maskParams=maskParams)
        self.pedestal = pedestal

    @attributeSetter
    def pedestal(self, value):
        """
        Luminance pedestal of the grating (e.g. the background around which it
        varies)

        Should a scalar in the range -1:1.
        """
        # Recode phase to numpy array
        self.__dict__['pedestal'] = value
        self._needUpdate = True

    def _updateListShaders(self):
        """
        This method is copied from psychopy.visual.grating.GratingStim, the only
        change is that the pedestal value is made available to the fragment
        shader used for drawing the stimulus.
        """
        self.win._progSignedTexMask = shaders.compileProgram(shaders.vertSimple, fragSignedColorTexMask_pedestal)

        self._needUpdate = False
        GL.glNewList(self._listID,GL.GL_COMPILE)
        #setup the shaderprogram
        _prog = self.win._progSignedTexMask
        GL.glUseProgram(_prog)
        # set the texture to be texture unit 0
        GL.glUniform1i(GL.glGetUniformLocation(_prog, b"texture"), 0)
        # mask is texture unit 1
        GL.glUniform1i(GL.glGetUniformLocation(_prog, b"mask"), 1)
        GL.glUniform1f(GL.glGetUniformLocation(_prog, b"pedestal"), self.pedestal)
        # mask
        # mask
        GL.glActiveTexture(GL.GL_TEXTURE1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._maskID)
        GL.glEnable(GL.GL_TEXTURE_2D)  # implicitly disables 1D

        # main texture
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._texID)
        GL.glEnable(GL.GL_TEXTURE_2D)

        Ltex = (-self._cycles[0] / 2) - self.phase[0] + 0.5
        Rtex = (+self._cycles[0] / 2) - self.phase[0] + 0.5
        Ttex = (+self._cycles[1] / 2) - self.phase[1] + 0.5
        Btex = (-self._cycles[1] / 2) - self.phase[1] + 0.5
        Lmask = Bmask = 0.0
        Tmask = Rmask = 1.0  # mask

        # access just once because it's slower than basic property
        vertsPix = self.verticesPix
        GL.glBegin(GL.GL_QUADS)  # draw a 4 sided polygon
        # right bottom
        GL.glMultiTexCoord2f(GL.GL_TEXTURE0, Rtex, Btex)
        GL.glMultiTexCoord2f(GL.GL_TEXTURE1, Rmask, Bmask)
        GL.glVertex2f(vertsPix[0, 0], vertsPix[0, 1])
        # left bottom
        GL.glMultiTexCoord2f(GL.GL_TEXTURE0, Ltex, Btex)
        GL.glMultiTexCoord2f(GL.GL_TEXTURE1, Lmask, Bmask)
        GL.glVertex2f(vertsPix[1, 0], vertsPix[1, 1])
        # left top
        GL.glMultiTexCoord2f(GL.GL_TEXTURE0, Ltex, Ttex)
        GL.glMultiTexCoord2f(GL.GL_TEXTURE1, Lmask, Tmask)
        GL.glVertex2f(vertsPix[2, 0], vertsPix[2, 1])
        # right top
        GL.glMultiTexCoord2f(GL.GL_TEXTURE0, Rtex, Ttex)
        GL.glMultiTexCoord2f(GL.GL_TEXTURE1, Rmask, Tmask)
        GL.glVertex2f(vertsPix[3, 0], vertsPix[3, 1])
        GL.glEnd()

        # unbind the textures
        GL.glActiveTexture(GL.GL_TEXTURE1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glDisable(GL.GL_TEXTURE_2D)  # implicitly disables 1D
        # main texture
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glDisable(GL.GL_TEXTURE_2D)

        GL.glUseProgram(0)

        GL.glEndList()
