""" 
To run this as a Luigi DAG locally:
``pixi run python icedyno/preprocess/crop.py``

You may have to enable toml support with luigi by setting an variable in your terminal, like ``export LUIGI_CONFIG_PARSER=toml``
"""
import glob
import os
import pathlib

import luigi
import xarray as xr


class CropFiles(luigi.Task):
    """
    Crop IMS and MASIE NetCDF files from the center of their grids (where x, y == 1/2*sie.shape) based on input window_size.

    """

    input_dir = luigi.Parameter()
    output_dir = luigi.Parameter()

    window_size = luigi.IntParameter(default=4000)
    year = luigi.IntParameter()

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
            output_filename = (
                os.path.join(year_output_dir, pathlib.Path(cdf_filepath).stem)
                + f"_grid{self.window_size}.nc"
            )
            if os.path.exists(output_filename):
                print(cdf_filepath, "already on disk, skipping...")

            # Open the original NetCDF file
            ds = xr.open_dataset(cdf_filepath, engine="h5netcdf")

            x_coord = ds["x"].shape[0] // 2
            y_coord = ds["y"].shape[0] // 2
            window = self.window_size * 1000

            cropped_ds = ds.sel(
                x=slice(x_coord - window, x_coord + window),
                y=slice(y_coord - window, y_coord + window),
            )

            # Write the cropped data to a new NetCDF file
            cropped_ds.to_netcdf(output_filename, engine="h5netcdf")


if __name__ == "__main__":
    os.environ["LUIGI_CONFIG_PARSER"] = "toml"

    config_path = os.path.join("config", "preprocess_netcdf.toml")

    config = luigi.configuration.get_config(parser="toml")
    config.read(config_path)

    luigi.configuration.add_config_path(config_path)

    ## Change acording to your number of cores
    n_workers = 10
    years = range(2014, 2025)

    tasks = [CropFiles(year=year) for year in years]
    luigi.build(tasks, workers=n_workers, local_scheduler=True)
