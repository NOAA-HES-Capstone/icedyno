import os

import numpy as np
import tensorflow as tf
import xarray as xr

## Not ideal, but sets the relative data path and the dataset to use
WINDOW_SIZE = 2000  # km
try:
    IN_COLAB = True
except ModuleNotFoundError:
    IN_COLAB = False
data_root = "ims_netcdf_1km_cropped_2_000km_window_74lat_-170lon/"
if not IN_COLAB:
    data_root = os.path.join("..", "data", data_root)
##################################################################


def load_sie_data(year: int, day: int) -> np.array:
    """Returns a 2D numpy array copy of the IMS surface values"""
    return (
        load_nc_file(year, day, data_root, WINDOW_SIZE)
        .IMS_Surface_Values[0]
        .values.copy()
    )


def load_binary_sie_data(year, day) -> np.array:
    """Returns a 2D numpy array copy of the IMS surface values"""
    sie = load_sie_data(year, day)
    binary_sie = sie.copy()
    binary_sie[sie != 3] = 0

    # Sea and Lake Ice is treated as 1
    binary_sie[sie == 3] = 1
    return binary_sie


def trinarize_data(sie: np.array) -> np.array:
    """
    New SIE:
    0: Open water/out of bounds
    1: Sea ice or lake ice (lake mask not applied)
    2: Land
    """
    trinary_sie = sie.copy()
    trinary_sie[sie != 3] = 0

    # Sea and Lake Ice is treated as 1
    trinary_sie[sie == 3] = 1

    # Land and Snow-Covered Land is sent to 2.
    trinary_sie[sie == 2] = 2
    trinary_sie[sie == 4] = 2
    return trinary_sie


def load_nc_file(year: int, day: int) -> xr.Dataset:
    """
    Loads the cropped, grid-corrected netcdf files on the Beaufort Sea with 74,0lat_-170,0lon
    Loads a single .nc file for a given year and day
    """
    # Generate the file path based on the year and day
    file_path = os.path.join(
        data_root,
        str(year),
        f"ims{year}{day:03d}_1km_v1.3_grid{WINDOW_SIZE}_74,0lat_-170,0lon.nc",
    )

    # Load the .nc file using xarray
    with xr.open_dataset(file_path) as dataset:
        return dataset


class BinaryTargetGenerator(tf.keras.utils.Sequence):
    """
    Generator for Keras training to allow multiprocessing and training on batches with only the
    batch itself being loaded into memory.

    """

    def __init__(
        self,
        filenames: list[str],
        batch_size: int = 2,
        dim: tuple = (8000, 8000, 5),
    ):
        self.batch_size = batch_size
        self.dim = dim  # (height, width, channel)

        self.filenames = sorted(filenames)
        self.years = self.years_from_filenames()
        self.days = self.days_from_filenames()

        # Dictionary to look up where the year day (2022, 151) is in self.years and self.days
        self.index_of_year_day = {
            year_day: index for index, year_day in enumerate(zip(self.years, self.days))
        }

        self.data_IDs = self._get_data_ids(
            self.years[: -self.dim[2]], self.days[: -self.dim[2]]
        )

    def years_from_filenames(self) -> list[int]:
        years = [
            int(file.split("/")[-1].split("ims")[1][:4]) for file in self.filenames
        ]
        return years

    def days_from_filenames(self) -> list[int]:
        days = [int(file.split("/")[-1].split("_")[0][-3:]) for file in self.filenames]
        return days

    def _get_data_ids(self, years: list[int], days: list[int]) -> list[tuple]:
        return list(zip(years, days))

    def get_years_days_of_batch(self, index: int) -> list[tuple]:
        """Given a batch index, return a list of the year and days for that batch"""
        years = self.years[index * self.batch_size : (index + 1) * self.batch_size]
        days = self.days[index * self.batch_size : (index + 1) * self.batch_size]
        return list(zip(years, days))

    def __len__(self):
        """Number of batches per epoch"""
        return len(self.data_IDs) // self.batch_size

    def __getitem__(self, index: int) -> tuple[np.array, np.array]:
        """Generate one batch of data"""
        # Collect data IDs for this batch number
        batch_data_ids = self.data_IDs[
            index * self.batch_size : (index + 1) * self.batch_size
        ]

        # Generate data
        X, y = self._data_generation(batch_data_ids)

        return X.astype("float16"), y.astype("float16")

    def load_n_day_chunk(self, year: int, day: int, n: int) -> np.array:
        """Starts at year, day and returns the next n days of processed SIE."""
        i = self.index_of_year_day[(year, day)]
        days = self.days[i : i + n]
        years = self.years[i : i + n]

        sie_chunk = []
        for year, day in zip(years, days):
            sie = trinarize_data(load_sie_data(year, day))
            sie_chunk.append(sie)

        assert len(sie_chunk) == n
        # Use np.stack to stack the individual 2D arrays along a new third axis, resulting in (height, width, channels)
        return np.stack(sie_chunk, axis=-1)

    def load_binary_y_for_day(self, year: int, day: int, n: int) -> np.array:
        """If the initial X data day is 10 with offset 3, load day 13, binarize it, and return the shape expected of y data"""
        i = self.index_of_year_day[(year, day)]
        y_data = np.expand_dims(
            load_binary_sie_data(
                self.years[i + self.dim[2]], self.days[i + self.dim[2]]
            ),
            axis=-1,
        )
        return y_data

    def _data_generation(self, batch_data_ids):
        """Generates data containing batch_size samples"""
        X = np.empty((self.batch_size, *self.dim), dtype="float16")
        y = np.empty((self.batch_size, self.dim[0], self.dim[1], 1), dtype="float16")

        for i, (year, day) in enumerate(batch_data_ids):
            # Load a n-day chunk as the input
            X[i] = self.load_n_day_chunk(year, day, self.dim[2])

            # Load the next day as the target
            y[i] = self.load_binary_y_for_day(year, day, self.dim[2])

        return X, y
