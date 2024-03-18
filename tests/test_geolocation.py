import numpy as np

from icedyno.preprocess import geolocation


def test_xy_to_latlon_inversion():
    """Test that xy to latlon and latlon to xy invert each other"""
    lats = [77.508333, 80, 67, 55]
    lons = [-164.754167, -80, 90, 155]

    for i in range(len(lats)):
        lat = lats[i]
        lon = lons[i]
        xy_converted_coordinates = geolocation.polar_lonlat_to_xy(
            longitude=lon, latitude=lat
        )

        reverted_lat_lon = geolocation.polar_xy_to_lonlat(*xy_converted_coordinates)
        assert np.allclose((lon, lat), reverted_lat_lon)


def test_find_closest_index_in_grid():
    # Grid parameters for IMS data
    start = -12287500.0
    stop = 12287500.0
    grid_resolution = 1000.0
    coordinates = np.arange(start=start, stop=stop + 1000.0, step=grid_resolution)

    test_val = -1400.0
    index = geolocation.find_closest_index_in_grid(test_val)
    assert np.isclose(coordinates[index], -1500.0)

    test_vals = np.random.uniform(start, stop, 10)
    for test_val in test_vals:
        index = geolocation.find_closest_index_in_grid(test_val)
        # If the solution is correct, the target and the found value should never be more than the grid_resolution apart.
        assert abs(coordinates[index] - test_val) < grid_resolution
