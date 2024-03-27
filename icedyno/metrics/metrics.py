import matplotlib.pyplot as plt
import numba
import numpy as np

## Visualization for edge metrics ##


def plot_ice_edges_with_metrics(observed_edges, model_edges):
    """
    Visualize observed and model ice edges on a grid, including the calculation of metrics.

    Parameters:
    - observed_edges: numpy array of observed ice edge points.
    - model_edges: numpy array of model ice edge points.
    """
    # Plotting
    plt.figure(figsize=(8, 8))
    plt.plot(observed_edges[:, 0], observed_edges[:, 1], "bo-", label="Example Edge 1")
    plt.plot(model_edges[:, 0], model_edges[:, 1], "ro-", label="Example Edge 2")

    # Enhance plot
    plt.title("Ice Edge Comparison with Metrics")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.legend()
    plt.grid(True)
    plt.axis("equal")

    plt.show()


## Metrics ##


@numba.jit(nopython=True)
def average_ice_edge_displacement(observed_edges, model_edges):
    """
    Calculate the average ice edge displacement (D_AVG_IE) between observed and model ice edges.
    Credit: Validation metrics for ice edge position forecasts, Melsom et al., 2019.

    Parameters:
    - observed_edges: numpy array of shape (N, 2), where N is the number of observed ice edge points,
      and each point is represented by its (x, y) coordinates.
    - model_edges: numpy array of shape (M, 2), where M is the number of model ice edge points,
      and each point is represented by its (x, y) coordinates.

    Returns:
    - D_AVG_IE: The average displacement between the observed and model ice edges.
    """

    # Initialize lists to store minimum distances for each point
    observed_to_model_distances = []
    model_to_observed_distances = []

    # Calculate distances from each observed point to the nearest model point
    for obs_point in observed_edges:
        distances = np.sqrt(np.sum((model_edges - obs_point) ** 2, axis=1))
        observed_to_model_distances.append(np.min(distances))

    # Calculate distances from each model point to the nearest observed point
    for model_point in model_edges:
        distances = np.sqrt(np.sum((observed_edges - model_point) ** 2, axis=1))
        model_to_observed_distances.append(np.min(distances))

    # Calculate the average displacement
    avg_displacement = (
        sum(observed_to_model_distances) / len(observed_to_model_distances)
        + sum(model_to_observed_distances) / len(model_to_observed_distances)
    ) / 2

    return avg_displacement


@numba.jit(nopython=True)
def root_mean_square_ice_edge_displacement(observed_edges, model_edges):
    """
    Calculate the root mean square ice edge displacement (D_RMS_IE) between observed and model ice edges.

    Parameters:
    - observed_edges: numpy array of shape (N, 2), where N is the number of observed ice edge points,
      and each point is represented by its (x, y) coordinates.
    - model_edges: numpy array of shape (M, 2), where M is the number of model ice edge points,
      and each point is represented by its (x, y) coordinates.

    Returns:
    - D_RMS_IE: The root mean square displacement between the observed and model ice edges.
    """

    # Initialize lists to store distances for each point
    observed_to_model_distances = []
    model_to_observed_distances = []

    # Calculate distances from each observed point to the nearest model predicted point
    for obs_point in observed_edges:
        distances = np.sqrt(np.sum((model_edges - obs_point) ** 2, axis=1))
        observed_to_model_distances.append(np.min(distances) ** 2)

    # Calculate distances from each model point to the nearest observed point
    for model_point in model_edges:
        distances = np.sqrt(np.sum((observed_edges - model_point) ** 2, axis=1))
        model_to_observed_distances.append(np.min(distances) ** 2)

    # Calculate the root mean square displacement
    rms_displacement = np.sqrt(
        (sum(observed_to_model_distances) + sum(model_to_observed_distances))
        / (len(observed_to_model_distances) + len(model_to_observed_distances))
    )

    return rms_displacement
