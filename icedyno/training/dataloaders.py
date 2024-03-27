import os

import numpy as np
import tensorflow as tf
import xarray as xr


def load_sie_data(year: int, day: int, data_root: str, WINDOW_SIZE: int) -> np.array:
    """Returns a 2D numpy array copy of the IMS surface values"""
    return (
        load_nc_file(year, day, data_root, WINDOW_SIZE)
        .IMS_Surface_Values[0]
        .values.copy()
    )


def load_target_sie_data(
    year: int, day: int, data_root: str, WINDOW_SIZE: int
) -> np.array:
    """Returns a 2D numpy array copy of the IMS surface values"""
    ds = load_nc_file(year, day, data_root, WINDOW_SIZE)
    sie = ds.IMS_Surface_Values[0].values.copy()
    binary_sie = sie.copy()
    binary_sie[sie != 3] = 0

    # Sea and Lake Ice is treated as 1
    binary_sie[sie == 3] = 1
    return binary_sie


def binarize_data(sie: np.array) -> np.array:
    """
    New SIE:
    0: Open water/out of bounds
    1: Sea ice or lake ice (lake mask not applied)
    2: Land
    """
    binary_sie = sie.copy()
    binary_sie[sie != 3] = 0

    # Sea and Lake Ice is treated as 1
    binary_sie[sie == 3] = 1

    # Land and Snow-Covered Land is sent to 2.
    binary_sie[sie == 2] = 2
    binary_sie[sie == 4] = 2
    return binary_sie


def load_nc_file(year: int, day: int, data_root: str, WINDOW_SIZE: int) -> xr.Dataset:
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


class BinaryTargetNetCDFGenerator(tf.keras.utils.Sequence):
    """
    Generator for Keras training to allow multiprocessing and training on batches with only the
    batch itself being loaded into memory.

    Targets a binary image (ice/no ice).
    """

    def __init__(
        self,
        filenames: list[str],
        batch_size: int = 2,
        dim: tuple = (8000, 8000, 5),
        shuffle: bool = True,
    ):
        self.filenames = sorted(filenames)
        self.years = self.years_from_filenames()
        self.days = self.days_from_filenames()
        self.batch_size = batch_size
        self.dim = dim  # (height, width, channel)
        self.shuffle = True
        self.data_IDs = self._get_data_ids()
        self.on_epoch_end()

    def years_from_filenames(self):
        years = [
            int(file.split("/")[-1].split("ims")[1][:4]) for file in self.filenames
        ]
        return years

    def days_from_filenames(self):
        days = [int(file.split("/")[-1].split("_")[0][-3:]) for file in self.filenames]
        return days

    def _get_data_ids(self):
        return list(zip(self.years, self.days))

    def get_years_days_of_batch(self, index: int):
        """Given a batch index, return a list of the year and days for that batch"""
        years = self.years[index * self.batch_size : (index + 1) * self.batch_size]
        days = self.days[index * self.batch_size : (index + 1) * self.batch_size]
        return list(zip(years, days))

    def __len__(self):
        """Number of batches per epoch"""
        return len(self.data_IDs) // self.batch_size

    def __getitem__(self, index):
        """Generate one batch of data"""
        # Collect data IDs for this batch number
        batch_data_ids = self.data_IDs[
            index * self.batch_size : (index + 1) * self.batch_size
        ]

        # Generate data
        X, y = self._data_generation(batch_data_ids)

        return X.astype("float16"), y.astype("int32")

    def on_epoch_end(self):
        """Updates indexes after each epoch"""
        if self.shuffle:
            np.random.shuffle(self.data_IDs)

    def load_n_day_chunk(self, i, n):
        """Starts at year, day and returns the next n days of processed SIE."""
        days = self.days[i : i + n]
        years = self.years[i : i + n]

        sie_chunk = []
        for year, day in zip(years, days):
            sie = binarize_data(load_sie_data(year, day))
            sie_chunk.append(sie)

        assert len(sie_chunk) == n
        # Use np.stack to stack the individual 2D arrays along a new third axis, resulting in (height, width, channels)
        return np.stack(sie_chunk, axis=-1)

    def _data_generation(self, batch_data_ids):
        """Generates data containing batch_size samples"""
        X = np.empty((self.batch_size, *self.dim), dtype="float16")
        y = np.empty((self.batch_size, self.dim[0], self.dim[1], 1), dtype="int32")

        for i, (year, day) in enumerate(batch_data_ids):
            # Load a 5-day chunk as the input
            X[i,] = self.load_n_day_chunk(i, self.dim[2])
            # Load the next day as the target
            y[i,] = np.expand_dims(
                load_target_sie_data(
                    self.years[i + self.dim[2]], self.days[i + self.dim[2]]
                ),
                axis=-1,
            )

        return X, y
