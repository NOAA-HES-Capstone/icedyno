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

import icedyno.preprocess.geolocation


class CropRotateNetCDF(luigi.Task):
    """
    Crop IMS and MASIE NetCDF files from the center of their grids (where x, y == 1/2*sie.shape) based on input window_size.

    Supports centering the window of the cropped files at different locations.
    See config/preprocess_netcdf.toml for configuration settings.
    """

    input_dir = luigi.Parameter()
    output_dir = luigi.Parameter()

    center_latitude = luigi.FloatParameter()
    center_longitude = luigi.FloatParameter()

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
            if (self.center_latitude != "None") and (self.center_longitude != "None"):
                output_filename += f"_{str(self.center_latitude).replace('.', ',')}lat_{str(self.center_longitude).replace('.', ',')}lon.nc"
            else:
                output_filename += ".nc"

            # Don't recompute file if the expected filename in the output folder already exists.
            if os.path.exists(output_filename):
                print(cdf_filepath, "already on disk, skipping...")
                continue

            with xr.open_dataset(cdf_filepath, engine="h5netcdf") as ds:
                # If specified, center the window on the lat/lon coordinates provided. Otherwise, center on middle of grid.
                if (self.center_latitude != "None") and (
                    self.center_longitude != "None"
                ):
                    # Project the lat/lon coordinates to the polar stereographic coordinates.
                    x, y = icedyno.preprocess.geolocation.polar_lonlat_to_xy(
                        longitude=self.center_longitude, latitude=self.center_latitude
                    )
                else:
                    x = np.min(np.abs(ds.x))
                    y = np.min(np.abs(ds.y))

                window = self.window_size * 1000  # from km to meters

                center_x = np.min(np.abs(ds.x))
                center_y = np.min(np.abs(ds.y))
                ds = ds.sel(
                    x=slice(center_x - window * 5, center_x + window * 5),
                    y=slice(center_y - window * 5, center_y + window * 5),
                )

                # Correct the netCDF files with a 90 degree rotation so the xarray x,y grid matches polar stereographic
                ds = rotate_netcdf(ds)

                cropped_ds = ds.sel(
                    x=slice(x - window // 2, x + window // 2),
                    y=slice(y - window // 2, y + window // 2),
                )
                assert np.allclose(
                    cropped_ds.IMS_Surface_Values.values.shape,
                    (1, self.window_size, self.window_size),
                )

                # Write the cropped data to a new NetCDF file
                cropped_ds.to_netcdf(output_filename, engine="h5netcdf")


def rotate_netcdf(ds: xr.Dataset) -> xr.Dataset:
    """Rotates IMS netcdf's IMS_Surface_Values 90 degrees, which then gets the correct alignment with the typical polar sterographic grid."""

    # Perform rotation on the 2D spatial slice
    rotated_sie = np.rot90(
        ds["IMS_Surface_Values"].values[0], k=1, axes=(0, 1)
    )  # Rotate the 2D array

    rotated_sie = rotated_sie.reshape((1, rotated_sie.shape[0], rotated_sie.shape[1]))

    # Create a new DataArray with the rotated values, specifying the correct dimensions ('y', 'x') and coordinates
    data_xr = xr.DataArray(
        rotated_sie,
        coords={"y": ds.y, "x": ds.x, "time": ds.time},
        dims=["time", "y", "x"],
    )

    # Update the original xarray dataset with the rotated values
    ds["IMS_Surface_Values"].loc[:, :] = data_xr

    return ds


if __name__ == "__main__":
    os.environ["LUIGI_CONFIG_PARSER"] = "toml"

    config_path = os.path.join("config", "preprocess_netcdf.toml")

    config = luigi.configuration.get_config(parser="toml")
    config.read(config_path)

    luigi.configuration.add_config_path(config_path)

    ## Change acording to your number of cores
    n_workers = 6
    years = range(2015, 2025)

    tasks = [CropRotateNetCDF(year=year) for year in years]
    luigi.build(tasks, workers=n_workers, local_scheduler=True)
