try:
    # Python2
    import Tkinter as tk
except ImportError:
    # Python3
    import tkinter as tk

canvas = None
root = None
cell_size = 3
cells = {}

def draw_init(grid):
    global canvas, root
    if not canvas:
        dim = grid.dimensions
        root = tk.Tk()
        root.configure()
        canvas = tk.Canvas(root, width=dim[0] * cell_size, height=dim[1] * cell_size, bg='black')
        canvas.pack()

    if not cells:
        for idx, cell in grid.cells():
            cells[idx] = canvas.create_rectangle(
                idx[0] * cell_size,
                idx[1] * cell_size,
                (idx[0] + 1) * cell_size,
                (idx[1] + 1) * cell_size,
                #fill = 'red',
                fill = heat_to_color(cell.heat)
            )

def draw_grid(grid):
    # 2D grid only.
    for idx, cell in grid.cells():
        canvas.itemconfigure(cells[idx], fill = heat_to_color(cell.heat))
    root.update()
    #tk.mainloop()

import matplotlib.pyplot as plt
color_map = {}
color_steps = 20
def heat_to_color(heat, scale=3.0, cm=plt.cm.hot):
    quant = int(min((heat / scale), 1) * 20)
    if not color_map:
        for step in range(color_steps + 1):
            color_map[step] = "#%02x%02x%02x" % tuple(x * 255 for x in cm(float(step) / color_steps)[:3])
    return color_map[quant]

#tk.mainloop()