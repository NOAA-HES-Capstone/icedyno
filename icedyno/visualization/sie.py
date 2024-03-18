import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

import icedyno.preprocess.geolocation


def plot_sie_window(sie: np.array, window: int, marker: tuple = None):
    colors = ["#E500E5", "#0066FF", "#01FF00", "#FFC100", "#E50000"]
    cmap = ListedColormap(colors, name="custom_colormap", N=len(colors))

    # Plotting the sea ice extent with the custom colormap
    plt.figure(figsize=(10, 10))
    plt.imshow(sie, cmap=cmap, vmin=0, vmax=len(colors) - 1)
    plt.title("Sea Ice Extent around the Arctic Circle", fontsize=12)
    plt.axis("off")

    # Adding a colorbar with labels for different surface types
    cbar = plt.colorbar(ticks=range(len(colors)))
    cbar.ax.set_yticklabels(
        [
            "Outside Northern Hemisphere",
            "Open Water",
            "Land without Snow",
            "Sea or Lake Ice",
            "Snow Covered Land",
        ]
    )
    cbar.set_label("Surface Type")
    if marker:
        plt.scatter(
            icedyno.preprocess.geolocation.find_closest_index_in_grid(marker[0]),
            icedyno.preprocess.geolocation.find_closest_index_in_grid(marker[1]),
            s=500,
            c="green",
            marker="o",
        )

    plt.show()
