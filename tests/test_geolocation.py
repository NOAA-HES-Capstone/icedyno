import numpy as np

from icedyno.preprocess import geolocation


def test_xy_to_latlon_inversion():
    """Test that xy to latlon and latlon to xy invert each other"""
    lat = 60  # -77.508333
    lon = -80  # 164.754167

    xy_converted_coordinates = geolocation.polar_lonlat_to_xy(
        longitude=lon, latitude=lat
    )
    reverted_lat_lon = geolocation.polar_xy_to_latlon(*xy_converted_coordinates)

    assert np.allclose((lon, lat), reverted_lat_lon)