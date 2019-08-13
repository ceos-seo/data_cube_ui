import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch

plt.figure(figsize=(5,5))

# Determine the x and y values to use for sample points.
num_edge_pts = 50 # Change this to change the resolution of the result.
xy_rng = (0, 1)
pt_sp = (xy_rng[1] - xy_rng[0]) / (num_edge_pts - 1)
x = np.linspace(xy_rng[0], xy_rng[1] + 0.001, num_edge_pts)
y = np.linspace(xy_rng[0], xy_rng[1] + 0.001, num_edge_pts)
X, Y = np.meshgrid(x, y)
min_x, max_x, min_y, max_y = np.min(x), np.max(x), np.min(y), np.max(y)
median_x = np.median(x)
prm_color_val_func = lambda x, y: 1 - np.sqrt((X-x)**2 + (Y-y)**2) / \
                                      (xy_rng[1] - xy_rng[0])
# The lower left of the triangle is red.
z_red = prm_color_val_func(min_x, min_y)
# The top of the triangle is green.
z_green = prm_color_val_func(median_x, max_y)
# The lower right of the triangle is blue.
z_blue = prm_color_val_func(max_x, min_y)
del x, y, X, Y
Z = np.stack((z_red, z_green, z_blue), axis=-1)
del z_red, z_green, z_blue
# Form the perimeter of the triangle
# (lower left, top, lower right, back to lower left).
path = Path([[min_x, min_y], [median_x, max_y],
             [max_x, min_y], [min_x, min_y]])
patch = PathPatch(path, facecolor='none', alpha=0)
plt.gca().add_patch(patch)

im = plt.imshow(Z, interpolation='nearest',
                origin='lower', extent=[*xy_rng, *xy_rng],
                clip_path=patch)
# Label the corners.
plt.text(min_x+0.03, min_y, "BS", fontsize=24)
plt.text(median_x-0.06, max_y-0.18, "PV", fontsize=24)
plt.text(max_x-0.22, min_y, "NPV", fontsize=24)
plt.axis('off')
plt.title("Fractional Cover Color Scale")
plt.tight_layout()
plt.savefig('fractional_cover_color_scale.png')