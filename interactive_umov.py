# http://stackoverflow.com/questions/10693256/how-to-accept-keypress-in-command-line-python
import curses
from multiprocessing import Process, Pipe
import pylab as plt
import numpy as np
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)

import umov as umov_mod

def main():
    plt.ion()

    def plot_graph(child_conn):
        umov = umov_mod.main()
        umov.umo.set_cube('w')
        #umov.display_curr_frame()

        child_conn.send('loaded')
        key = '2'
        while key != 'q':
            if key == curses.KEY_UP: 
                umov.umo.next_level()
            elif key == curses.KEY_DOWN: 
                umov.umo.prev_level()
            elif key == curses.KEY_LEFT: 
                umov.umo.prev_time()
            elif key == curses.KEY_RIGHT: 
                umov.umo.next_time()

            plt.show()
            plt.clf()
            umov.display_curr_frame()
            plt.pause(0.1)
            key = child_conn.recv()
        child_conn.close()
        print('leaving child')

    parent_conn, child_conn = Pipe()
    proc = Process(target=plot_graph, args=(child_conn,))
    proc.start()

    stdscr = curses.initscr()
    curses.cbreak()
    stdscr.keypad(1)

    stdscr.addstr(0,10,"Hit 'q' to quit")
    stdscr.addstr(1, 10, 'loading')
    stdscr.refresh()

    status = parent_conn.recv()
    if status == 'loaded':
        stdscr.addstr(1, 10, 'loaded ')
    
    stdscr.refresh()
    key = ''
    while key != ord('q'):
        key = stdscr.getch()
        stdscr.addch(20,25,key)
        stdscr.refresh()

        parent_conn.send(key)
    parent_conn.send('q')
    proc.join()

    curses.endwin()

if __name__ == '__main__':
    main()
