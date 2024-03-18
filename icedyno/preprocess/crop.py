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


class CropRotateNetCDF(luigi.Task):
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
            else:
                x = np.min(np.abs(ds.x))
                y = np.min(np.abs(ds.y))

            window = self.window_size * 1000  # from km to meters

            # Correct the netCDF files with a 90 degree rotation so the xarray x,y grid matches polar stereographic
            ds = rotate_netcdf(ds)

            cropped_ds = ds.sel(
                x=slice(x - window // 2, x + window // 2),
                y=slice(y - window // 2, y + window // 2),
            )
            # Write the cropped data to a new NetCDF file
            cropped_ds.to_netcdf(output_filename, engine="h5netcdf")


def rotate_netcdf(ds: xr.Dataset) -> xr.Dataset:
    """Rotates IMS netcdf's IMS_Surface_Values 90 degrees, which then gets the correct alignment with the typical polar sterographic grid."""

    # Perform rotation on the 2D spatial slice
    rotated_sie = np.rot90(
        ds["IMS_Surface_Values"].values[0], k=1
    )  # Rotate the 2D array

    # Create a new DataArray with the rotated values, specifying the correct dimensions ('y', 'x') and coordinates
    rotated_da = xr.DataArray(
        rotated_sie, dims=("x", "y"), coords={"y": ds["y"], "x": ds["x"]}
    )

    # Since we need to maintain the 'time' dimension when reassigning, use expand_dims to add 'time' back
    rotated_da_expanded = rotated_da.expand_dims("time", axis=0)

    # Correctly update the dataset's variable with the rotated data
    # Use the .data property to assign the numpy array, not the DataArray itself
    ds["IMS_Surface_Values"] = (("time", "y", "x"), rotated_da_expanded.data)

    return ds


if __name__ == "__main__":
    os.environ["LUIGI_CONFIG_PARSER"] = "toml"

    config_path = os.path.join("config", "preprocess_netcdf.toml")

    config = luigi.configuration.get_config(parser="toml")
    config.read(config_path)

    luigi.configuration.add_config_path(config_path)

    ## Change acording to your number of cores
    n_workers = 10
    years = range(2015, 2025)

    tasks = [CropRotateNetCDF(year=year) for year in years]
    luigi.build(tasks, workers=n_workers, local_scheduler=True)
