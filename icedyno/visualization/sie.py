import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

import icedyno.preprocess.geolocation


def plot_sie_window(sie: np.array, marker: tuple[int, int] = None) -> None:
    """
    Parameters:
    - SIE is 2D numpy array
    - marker is a tuple of x, y polar sterographic coordinates
    """
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


def plot_binary_model_predictions_with_errors(
    X: np.array, y_true: np.array, y_pred: np.array, year: int, day: int
) -> None:
    """
    Parameters:
     - X: np.array of shape (window_size, window_size, n_forecasts)
     - y_true: np.array of 0,1 (window_size, window_size, 1)
     - y_pred: model output (window_size, window_size, 1)
     - year: Integer year like 2023, for titling plot
     - day: Integer day like 18, for titling plot
    """
    X_cmap = ListedColormap(["#0000FF", "#00FFFF", "#008B8B"])
    binary_cmap = ListedColormap(["#008B8B", "#00FFFF"])

    # Calculate the incorrect predictions (difference between the predicted and true labels)
    incorrect_predictions = np.not_equal(np.round(y_pred), y_true).astype(int)
    num_incorrect = np.sum(incorrect_predictions)
    percent_incorrect = num_incorrect / (X.shape[1] ** 2)

    current_SIE = X[:, :, -1].copy()
    current_SIE[current_SIE == 2] = 0
    change_from_curr_to_next = np.not_equal(current_SIE, y_true[:, :, 0]).astype(int)

    # Plotting the first example of the batch
    fig, axes = plt.subplots(1, 5, figsize=(25, 10))

    # Plot the last channel of input which is the most recent SIE
    im1 = axes[0].imshow(X[:, :, -1], cmap=X_cmap)
    axes[0].set_title("Most Recent SIE Input")
    axes[0].axis("off")

    # Plot the true label for next day's SIE
    im2 = axes[1].imshow(y_true[:, :, 0], cmap=binary_cmap)
    axes[1].set_title("True Next Day's SIE")
    axes[1].axis("off")

    # Plot the predicted next day's SIE
    im3 = axes[2].imshow(y_pred[:, :, 0], cmap=binary_cmap)
    axes[2].set_title("Predicted Next Day's SIE")
    axes[2].axis("off")

    # Plot the incorrect predictions
    axes[3].imshow(incorrect_predictions[:, :, 0], cmap="hot")
    axes[3].set_title("Incorrect Predictions")
    axes[3].axis("off")

    # Plot the SIE change
    axes[4].imshow(change_from_curr_to_next, cmap="hot")
    axes[4].set_title("Change from Current SIE to Next Day")
    axes[4].axis("off")

    # Add a color bar for the SIE plots
    cbar = fig.colorbar(im1, ax=axes[0], fraction=0.046, pad=0.04)
    cbar.set_ticks([0, 1, 2])
    cbar.set_ticklabels(["Open Water", "Sea Ice", "Land"])

    # Add a color bar for the binary SIE plots
    cbar = fig.colorbar(im2, ax=axes[1], fraction=0.046, pad=0.04)
    cbar.set_ticks([0, 1])
    cbar.set_ticklabels(["Not Sea Ice", "Sea Ice"])

    # Add a color bar for the binary SIE plots
    cbar = fig.colorbar(im3, ax=axes[2], fraction=0.046, pad=0.04)
    cbar.set_ticks([0, 1])
    cbar.set_ticklabels(["Not Sea Ice", "Sea Ice"])

    fig.suptitle(
        f"Model Predictions for {year} {day}'s Next Day Forecast\nIncorrectly Classified Pixels: {num_incorrect} pixels, {percent_incorrect}%",
        fontsize=14,
    )

    plt.tight_layout()
    plt.show()


## Visualization for edge metrics ##


def plot_ice_edges_with_metrics(
    observed_edges: np.array,
    model_edges: np.array,
    observed_edges_label: str = "Observed Edges",
    model_edges_label: str = "Predicted Edges",
) -> None:
    """
    Visualize observed and model ice edges on a grid, including the calculation of metrics.
    An example of the expected edge arrays is output of process_binary_edge_image_into_coordinates.

    Parameters:
    - observed_edges: numpy array of observed ice edge points.
    - model_edges: numpy array of model ice edge points.
    """
    # Plotting
    plt.figure(figsize=(8, 8))
    plt.plot(
        observed_edges[:, 0], observed_edges[:, 1], "bo-", label=observed_edges_label
    )
    plt.plot(model_edges[:, 0], model_edges[:, 1], "ro-", label=model_edges_label)

    plt.title("Ice Edge Comparison with Metrics")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.legend()
    plt.grid(True)
    plt.axis("equal")

    plt.show()
