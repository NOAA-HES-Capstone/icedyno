import numpy as np


def process_binary_edge_image_into_coordinates(activated: np.array) -> np.array:
    """
    Takes a numpy array of edge detected pixels (not SIE).
    Cannot take in a tensorflow tensor, input array must be between 0 and 1.
    Input array is the result of running edge-detection on Ice/No Ice array.

    Something like:
    sobel_edges = tf.image.sobel_edges(model_prediction)
    activated = Activation('sigmoid')(tf.square(sobel_edges[:, :, :, :, 0]) + tf.square(sobel_edges[:, :, :, :, 1]))

    Parameters:
        activated: Numpy array with >= 0.5 indicating sea-ice edge.

    Returns:
        numpy array of integer indices in input array corresponding to edge pixels. Of shape (N Edges, 2)

    """
    edges = np.where(np.round(activated) >= 1)
    x, y = edges[0], edges[1]
    edge_coordinates = np.stack((x, y), axis=-1)

    return edge_coordinates
