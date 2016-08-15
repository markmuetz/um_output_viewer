# -*- coding: utf-8 -*-
"""
Demonstrates use of GLScatterPlotItem with rapidly-updating plots.

"""

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np
from umov import main

umov = main()

app = QtGui.QApplication([])
w = gl.GLViewWidget()
w.opts['distance'] = 20
w.show()
w.setWindowTitle('pyqtgraph example: GLScatterPlotItem')

g = gl.GLGridItem()
w.addItem(g)

##
##  Second example shows a volume of points with rapidly updating color
##  and pxMode=True
##

cube_index = 0
cube = umov.umo.curr_cube[cube_index]

def get_pos(data):
    d = (data > 1)
    size = data[d] * 0.5
    pos = np.array(np.roll(np.array(np.where(d)).T, -1, axis=1), dtype=np.float64)
    pos *= [20./data.shape[1], 20./data.shape[2], 20./data.shape[0]]
    pos -= [10, 10, 0]
    #pos *= [10,10,10]
    #size = np.ones(pos.shape[0])*10

    return pos, size

pos, size = get_pos(cube.data)
sp2 = gl.GLScatterPlotItem(pos=pos, color=(1,1,1,1), size=size)
w.addItem(sp2)

def update():
    global umov, sp2, cube_index
    cube_index += 1
    cube_index %= umov.umo.curr_cube.shape[0]

    cube = umov.umo.curr_cube[cube_index]
    pos, size = get_pos(cube.data)

    w.removeItem(sp2)
    sp2 = gl.GLScatterPlotItem(pos=pos, color=(1,1,1,1), size=size)
    w.addItem(sp2)

    #sp2.setData(pos=pos)
    
    
t = QtCore.QTimer()
t.timeout.connect(update)
t.start(50)


## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

