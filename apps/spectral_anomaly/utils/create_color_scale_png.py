import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from apps.spectral_anomaly.tasks import spectral_indices_range_map, spectral_indices_name_map

num_spec_inds = len(spectral_indices_name_map)

fig = plt.figure(figsize=(12,3.5*num_spec_inds))
# Allocate grid spaces for the colorbar (which spans the width)
# and the spectral indices' value ranges (currently only one per row, but
# there could be more depending on formatting).
gs = GridSpec(1+num_spec_inds, 1, figure=fig)

mpl.rcParams.update({'font.size': 32})

# Show a horizontal colorbar for the change values between the composites.
cbar_ax = fig.add_subplot(gs[0, :])
cb = mpl.colorbar.ColorbarBase(cbar_ax, cmap='RdYlGn', orientation='horizontal')
cbar_ax.set_title("Baseline-Analysis Change Color Scale")
cbar_ax.get_xaxis().set_ticks([0, 0.5, 1])
cbar_ax.get_xaxis().set_ticklabels(["Decrease", "Same",
                                    "Increase"], rotation=25)

# Show a grid of the composite value range and change value range for each
# spectral index.
for i, spec_ind in enumerate(spectral_indices_name_map):
    spec_ind_name = spectral_indices_name_map[spec_ind]
    spec_ind_range = spectral_indices_range_map[spec_ind]

    cmp_cng_val_rng_str = \
        """
        Composite Value Range: ({}, {})
        Change Value Range: ({}, {})
        """.format(spec_ind_range[0], spec_ind_range[1],
                   spec_ind_range[0] - spec_ind_range[1],
                   spec_ind_range[1] - spec_ind_range[0])

    ax = fig.add_subplot(gs[i+1, 0])
    title_text = ax.set_title(spec_ind_name)
    title_text.set_position((0.5, 0.25))
    ax.text(0, -0.5, cmp_cng_val_rng_str)
    ax.axis('off')

fig.savefig('spectral_anomaly_color_scale.png')
