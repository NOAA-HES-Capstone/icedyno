""" 
To run this as a Luigi DAG locally:
``pixi run python icedyno/preprocess/crop.py``

You may have to enable toml support with luigi by setting an variable in your terminal, like ``export LUIGI_CONFIG_PARSER=toml``
"""
import glob
import os
import pathlib

import luigi
import numpy as np
import xarray as xr


class CropFiles(luigi.Task):
    """
    Crop IMS and MASIE NetCDF files from the center of their grids (where x, y == 1/2*sie.shape) based on input window_size.

    Supports centering the window of the cropped files at different locations.
    See config/preprocess_netcdf.toml for configuration settings.
    """

    input_dir = luigi.Parameter()
    output_dir = luigi.Parameter()

    center_coordinates = luigi.Parameter()

    window_size = luigi.IntParameter(default=4000)
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
                os.path.join(year_output_dir, pathlib.Path(cdf_filepath).stem)
                + f"_grid{self.window_size}"
            )
            if self.center_coordinates != "None":
                output_filename += (
                    f"_{self.center_coordinates.replace(' ', '')}center.nc"
                )
            else:
                output_filename += ".nc"

            if os.path.exists(output_filename):
                print(cdf_filepath, "already on disk, skipping...")

            # Open the original NetCDF file
            ds = xr.open_dataset(cdf_filepath, engine="h5netcdf")

            if self.center_coordinates != "None":
                # Expects self.center_coordinates x,y to be "x, y" float values.
                x, y = [float(coord) for coord in self.center_coordinates.split(",")]

                x_coord = x
                y_coord = y
            else:
                x_coord = np.min(np.abs(ds.x))
                y_coord = np.min(np.abs(ds.y))
            window = self.window_size * 1000  # from km to meters

            cropped_ds = ds.sel(
                x=slice(x_coord - window, x_coord + window),
                y=slice(y_coord - window, y_coord + window),
            )
            # Write the cropped data to a new NetCDF file
            cropped_ds.to_netcdf(output_filename, engine="h5netcdf")


def find_closest_index_in_grid(target: float, coordinates: np.array) -> int:
    """
    Given a target coordinate in projected coordinates (x or y) and the list of coordinates, return the index of the closest number in the coordinates.
    Assumes a 1km grid.
    """
    assert np.allclose(coordinates % 1000, 500)
    start = coordinates[
        0
    ]  # Assume that the first element of coordinates is the minimum number in the list
    # -12287500.0 for IMS 1km data.

    # Define the step size
    grid_resolution = 1000  # meters

    # Calculate the index of the closest number
    index = int((target - start) // grid_resolution)

    # If the solution is correct, the target and the found value should never be more than the grid_resolution apart.
    assert abs(coordinates[index] - target) < grid_resolution
    return index


if __name__ == "__main__":
    os.environ["LUIGI_CONFIG_PARSER"] = "toml"

    config_path = os.path.join("config", "preprocess_netcdf.toml")

    config = luigi.configuration.get_config(parser="toml")
    config.read(config_path)

    luigi.configuration.add_config_path(config_path)

    ## Change acording to your number of cores
    n_workers = 10
    years = range(2015, 2025)

    tasks = [CropFiles(year=year) for year in years]
    luigi.build(tasks, workers=n_workers, local_scheduler=True)
