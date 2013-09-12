# Q&D ascii gui prorotype, no networking
'''
Cursed forest. Press any key to advance, ESC to get out.

Usage: forest_curses.py [-f FILL] [-i IGNITION]

-h --help       print this page
-f FILL         tree growth probability
-i IGNITION     ignition probability
'''

import curses
from docopt import docopt
import sys

from forest_fire import ForestFire
from agentum.worker import WorkerSerial as Worker
from agentum import protocol


def forest_loop(options):
    protocol.push = lambda x: 1
    worker = Worker(ForestFire)

    idx = dict(e=0, o=1, b=2)
    chars = ' *#'

    screen = curses.initscr()
    width = screen.getmaxyx()[1]
    height = screen.getmaxyx()[0]

    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, 0)
    curses.init_pair(2, curses.COLOR_YELLOW, 0)

    screen.leaveok(1)

    try:
        worker.sim.dimensions = "%s %s" % (width, height-1)  # fix this crazyness
        worker.sim.fill = options['-f'] or 0.1
        worker.sim.ignition = options['-i'] or 0.1
        worker.sim.setup()
        worker.step()

        while True:
            for cell in worker.sim.space.cells():
                # TODO: formalize this hack
                # this skips redrawing if the state has not changed
                if 'state' in cell._fields_previous:
                    screen.addch(cell.point[1], cell.point[0],
                                 chars[idx[cell.state[0]]],
                                 curses.color_pair(idx[cell.state[0]]))
                cell._fields_previous.clear()
            key = screen.getch()
            if key == 27:
                break
            else:
                worker.step()
    except:
        curses.endwin()
        raise

    curses.endwin()

if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')
    forest_loop(arguments)
