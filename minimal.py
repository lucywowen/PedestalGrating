#!/usr/bin/env python2
'''
Demonstration of pedestal grating stimulus.

Shows two gratings, one with a pedestal, one with the same contrast but without
the pedestal. Both gratings should be similar except for the baseline luminance
level that they fluctuate around.

This allows for Gabor stimuli with different background luminance levels where
the contrast parameter has a meaningful interpretation: The max. deviation from
the background color.

A second window plots the profile of both gratings. Use this to compare the
effect of the pedestal.

Make sure that -1 <= contrast + pedestal <= 1, otherwise clipping occurs.
Contrast values larger/smaller than 1/-1 produce colored Gratings which I
have _not_ tested and I doubt that they work as they should.

Usage:
    python minimal.py contrast pedestal


'''
import sys
from psychopy import event, visual, filters
from pedestal_grating import PedestalGratingStim
import numpy as np
import pylab as plt

if len(sys.argv) < 3:
    print '''USAGE:\n \t python minial.py contrast pedestal\nExample:\n\t python minimal.py 0.5 0.5\n\n Contrast and pedestal in -1:1, contrast + pedestal in -1:1 '''
    sys.exit(1)
contrast = float(sys.argv[1])
background = float(sys.argv[2])


win = visual.Window((500,500),
                    fullscr = False,
                    allowGUI = False,
                    winType = 'pyglet',
                    units='norm')

def  make_grating(win, contrast, background):
	stim = PedestalGratingStim(win,tex='sin',mask="gauss",texRes=256,
           contrast=contrast,
           size=[.5,.5], sf=[2,0], ori = 0, name='gabor1')
	return stim

patch = visual.Rect(win, width=1, height=2, lineWidth=0)
patch.fillColor = background
patch.pos = [-.5,0]
patch.draw()

lum0 = make_grating(win, contrast, background)
lum0.pos = [-.5, 0]
lum0.pedestal = background
lum0.draw()

lum0 = make_grating(win, contrast, 0)
lum0.pos = [+.5, 0]
lum0.draw()

win.flip()

# Plot profile of Gratings.
I = np.array(win.getMovieFrame()).mean(2)

bg = I[0,:]
left = I[250, 0:250]
right = I[250, 250:]
background_color = round(255* (background+1.)/2.)

plt.plot(range(250), left)
a = np.mean(left)
plt.axhline(a, color='r')
plt.axhline(background_color, color='k')

b = np.mean(right)
plt.plot(range(250, 500), right)
plt.axhline(b, color='g')
plt.axhline(round(255* (0+1.)/2.), color='k')
plt.ylim([0, 255])
plt.yticks([0, 255/2., 255], [-1,0, 1])

plt.axhline(round(255* (contrast+1.)/2.), color='k')
plt.axhline(round(255* (contrast+background+1.)/2.), color='k')

plt.show()


#event.waitKeys(maxWait=10000, keyList=['q'])
