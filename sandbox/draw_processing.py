import matplotlib.pyplot as plt

cell_size = 3
color_scale = 3.0
is_set = False
cm = plt.cm.hot

pr = None
grid = None

def draw_init(grid):
    global pr
    import pyprocessing
    pr = pyprocessing
    pr.noStroke()

    dim = grid.dimensions
    pr.size(dim[0] * cell_size, dim[1] * cell_size)

def draw():
    for idx, cell in grid.cells():
        pr.fill(pr.color(cm(cell.heat / color_scale)))
        pr.rect(idx[0] * cell_size, idx[1] * cell_size, 3, 3)
    #tk.mainloop()
    #pr.redraw()

def draw_grid(g):
    global grid
    grid = g
    pr.redraw()

color_map = {}
color_steps = 20
def heat_to_color(heat, scale=3.0, cm=plt.cm.hot):
    quant = int(min((heat / scale), 1) * 20)
    if not color_map:
        for step in range(color_steps + 1):
            color_map[step] = "#%02x%02x%02x" % tuple(x * 255 for x in cm(float(step) / color_steps)[:3])
    return color_map[quant]

#tk.mainloop()
