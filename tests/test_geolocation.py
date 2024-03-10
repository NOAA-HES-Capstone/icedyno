import numpy as np

from icedyno.preprocess import geolocation


def test_xy_to_latlon_inversion():
    """Test that xy to latlon and latlon to xy invert each other"""
    lat = 60  # -77.508333
    lon = -80  # 164.754167

    xy_converted_coordinates = geolocation.latlon_to_xy(lat=lat, lon=lon)
    reverted_lat_lon = geolocation.xy_to_latlon(*xy_converted_coordinates)

    assert np.allclose((lon, lat), reverted_lat_lon)
