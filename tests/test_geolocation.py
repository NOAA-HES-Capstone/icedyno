import numpy as np

from icedyno.preprocess import geolocation


def test_xy_to_latlon_inversion():
    """Test that xy to latlon and latlon to xy invert each other"""
    lat = -77.508333
    lon = 164.754167

    xy_converted_coordinates = geolocation.polar_lonlat_to_xy(
        longitude=lon, latitude=lat
    )

    print(xy_converted_coordinates)
    reverted_lat_lon = geolocation.polar_xy_to_lonlat(*xy_converted_coordinates)
    print(reverted_lat_lon)
    assert np.allclose((lon, lat), reverted_lat_lon)
