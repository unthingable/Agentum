try:
    # Python2
    import Tkinter as tk
except ImportError:
    # Python3
    import tkinter as tk

canvas = None
root = None
cell_size = 3
def draw_grid(grid):
    # 2D grid only.
    global canvas, root
    if not canvas:
        dim = grid.dimensions
        root = tk.Tk()
        root.configure()
        canvas = tk.Canvas(root, width=dim[0] * cell_size, height=dim[1] * cell_size, bg='black')
        canvas.pack()

    for idx, cell in grid.cells():
        canvas.create_rectangle(
            idx[0] * cell_size,
            idx[1] * cell_size,
            (idx[0] + 1) * cell_size,
            (idx[1] + 1) * cell_size,
            #fill = 'red',
            fill = heat_to_color(cell.heat)
        )
    root.update()
    #tk.mainloop()

import matplotlib.pyplot as plt
def heat_to_color(heat, scale=3.0, cm=plt.cm.hot):
    return "#%02x%02x%02x" % tuple(x * 255 for x in cm(heat / scale)[:3])

#tk.mainloop()