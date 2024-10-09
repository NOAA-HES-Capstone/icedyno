import glob
import os
import pathlib

import luigi
import numpy as np
import tensorflow as tf
import xarray as xr


def image_batch_to_binary_edge_image(image_batch: np.array) -> np.array:
    """
    Perform Sobel edge detection on an (optionally batched) image
    Image has dimension (batch_size, window_size, window_size).
    """
    binary_ice_no_ice = np.round(image_batch)
    assert np.allclose(np.unique(binary_ice_no_ice), np.array([0, 1]))

    # Sobel expects input to have dimension (batch, window, window, 1)
    batch_tensor = tf.expand_dims(tf.convert_to_tensor(binary_ice_no_ice), axis=-1)

    sobel_edges = tf.image.sobel_edges(batch_tensor)
    sobel_x = sobel_edges[..., 0]
    sobel_y = sobel_edges[..., 1]

    # Apply absolute value, threshold, and sum the results of x and y edges
    edges_x = tf.cast(tf.square(sobel_x) >= 1, tf.float32)
    edges_y = tf.cast(tf.square(sobel_y) >= 1, tf.float32)
    edge_magnitudes = edges_x + edges_y
    return edge_magnitudes.numpy()


def process_binary_edge_image_into_coordinates(activated: np.array) -> np.array:
    """
    Takes a numpy array of edge detected pixels (not SIE).
    Cannot take in a tensorflow tensor, input array must be between 0 and 1.
    Input array is the result of running edge-detection on Ice/No Ice array.

    Parameters:
        activated: Numpy array with >= 0.5 indicating sea-ice edge.

    Returns:
        numpy array of integer indices in input array corresponding to edge pixels. Of shape (N Edges, 2)

    """
    edges = np.where(np.round(activated) >= 1)
    x, y = edges[0], edges[1]
    edge_coordinates = np.stack((x, y), axis=-1)

    return edge_coordinates


class ApplyLakeMaskNetCDF(luigi.Task):
    """
    Also trinarizes the data to
    trinary_sie[sie != 3] = 0

    # Sea and Lake Ice is treated as 1
    trinary_sie[sie == 3] = 1

    # Land and Snow-Covered Land is sent to 2.
    trinary_sie[sie == 2] = 2
    trinary_sie[sie == 4] = 2

    Supports centering the window of the cropped files at different locations.
    See config/preprocess_netcdf.toml for configuration settings.
    """

    input_dir = luigi.Parameter()
    output_dir = luigi.Parameter()

    window_size = luigi.IntParameter(default=4000)
    mask_filepath = luigi.Parameter()

    year = luigi.IntParameter()  # Determined at runtime

    def output(self) -> luigi.LocalTarget:
        return luigi.LocalTarget(
            os.path.join("data", self.output_dir, f"_SUCCESS_{self.year}")
        )

    def run(self) -> None:
        year_output_dir = os.path.join("data", self.output_dir, str(self.year))
        if not os.path.exists(year_output_dir):
            os.makedirs(year_output_dir)

        input_cdf_files = glob.glob(
            os.path.join("data", self.input_dir, str(self.year), "*.nc")
        )

        for cdf_filepath in input_cdf_files:
            # Set output file name and check if the output file already exists on disk.
            output_filename = (
                os.path.join(year_output_dir, pathlib.Path(cdf_filepath).stem) + ".nc"
            )

            # Don't recompute file if the expected filename in the output folder already exists.
            # if os.path.exists(output_filename):
            #     print(cdf_filepath, "already on disk, skipping...")
            #     continue

            with xr.open_dataset(cdf_filepath, engine="h5netcdf") as ds:
                ds = apply_lake_mask_netcdf(
                    ds, os.path.join("data", self.mask_filepath)
                )

                # Write the cropped data to a new NetCDF file
                ds.to_netcdf(output_filename, engine="h5netcdf")


def apply_lake_mask_netcdf(ds: xr.Dataset, mask_filepath: str) -> xr.Dataset:
    """Also sends the data to 0 (open water), 1 (sea ice) and 2 (land)."""
    with xr.open_dataset(mask_filepath, engine="h5netcdf") as mask_ds:
        land_lake_mask = mask_ds.IMS_Surface_Values[0].values.copy()

    unmasked_sie = ds.IMS_Surface_Values[0].values.copy()

    masked_sie = unmasked_sie.copy()
    masked_sie[unmasked_sie != 3] = 0

    # Sea and Lake Ice is treated as 1
    masked_sie[unmasked_sie == 3] = 1

    # Land and Snow-Covered Land is sent to 2.
    masked_sie[unmasked_sie == 2] = 2
    masked_sie[unmasked_sie == 4] = 2

    # Apply lake mask
    land_lake_mask[np.isnan(land_lake_mask)] = 0
    masked_sie[land_lake_mask.astype(bool)] = 2

    masked_sie = masked_sie.reshape((1, masked_sie.shape[0], masked_sie.shape[1]))
    data_xr = xr.DataArray(
        masked_sie,
        coords={"y": ds.y, "x": ds.x, "time": ds.time},
        dims=["time", "y", "x"],
    )
    assert np.sum(np.isnan(data_xr)) == 0

    ds["IMS_Surface_Values"].loc[:, :] = data_xr
    assert np.allclose(np.unique(ds.IMS_Surface_Values.values), np.array([0, 1, 2]))
    assert np.allclose(
        np.where(np.isnan(ds.IMS_Surface_Values.values[0])),
        (np.array([], dtype=np.int64), np.array([], dtype=np.int64)),
    )

    return ds


if __name__ == "__main__":
    os.environ["LUIGI_CONFIG_PARSER"] = "toml"

    config_path = os.path.join("config", "lake_mask.toml")

    config = luigi.configuration.get_config(parser="toml")
    config.read(config_path)

    luigi.configuration.add_config_path(config_path)

    ## Change acording to your number of cores
    n_workers = 10
    years = range(2015, 2025)

    tasks = [ApplyLakeMaskNetCDF(year=year) for year in years]
    luigi.build(tasks, workers=n_workers, local_scheduler=True)
