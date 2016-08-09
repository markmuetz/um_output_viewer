# Inspiration taken from these two questions.
# http://stackoverflow.com/questions/10693256/how-to-accept-keypress-in-command-line-python
# http://stackoverflow.com/a/458246/54557
import curses
from multiprocessing import Process, Pipe
import pylab as plt
import warnings
import matplotlib.cbook
#warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)

import umov as umov_mod

def main():
    # Think this has to be done before child process started.
    plt.ion()

    def plot_graph(child_conn):
        umov = umov_mod.main()
        umov.umo.set_cube_from_conf_name('w')

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
            elif key == ord('n'):
                umov.umo.next_cube()
            elif key == ord('p'):
                umov.umo.next_cube()

            child_conn.send(umov.umo.curr_cube.name())
            plt.clf()
            umov.display_curr_frame()
            plt.pause(0.1)
            plt.show()

            key = child_conn.recv()
        child_conn.close()

    # Spawn child proc.
    parent_conn, child_conn = Pipe()
    proc = Process(target=plot_graph, args=(child_conn,))
    proc.start()

    stdscr = curses.initscr()
    curses.cbreak()
    stdscr.keypad(1)

    stdscr.addstr(0, 10, "Hit 'q' to quit")
    stdscr.addstr(1, 10, 'loading')
    stdscr.refresh()

    status = parent_conn.recv()
    if status == 'loaded':
        stdscr.addstr(1, 10, 'loaded ')
    
    stdscr.refresh()
    key = ''
    while key != ord('q'):
        key = stdscr.getch()
        stdscr.addch(20, 25, key)
        stdscr.refresh()

        parent_conn.send(key)
        status = parent_conn.recv()
        # TODO: Out of step with imshow.
        stdscr.addstr(1, 3, 'var: {0:<80}'.format(status))
        stdscr.refresh()

    parent_conn.send('q')
    proc.join()

    curses.endwin()

if __name__ == '__main__':
    main()
